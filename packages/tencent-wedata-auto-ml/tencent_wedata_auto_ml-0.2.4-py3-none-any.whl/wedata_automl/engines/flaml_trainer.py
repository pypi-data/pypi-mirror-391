"""
FLAMLTrainer - FLAML 训练器

封装 FLAML 训练逻辑，支持 Databricks 风格的参数
"""
from typing import Any, Dict, List, Optional, Union
import logging
import time
import pandas as pd
import numpy as np
import mlflow
from sklearn.pipeline import Pipeline as SkPipe

# Robust import for FLAML
try:
    from flaml import AutoML
    import flaml as flaml_pkg
except ImportError:
    try:
        from flaml.automl.automl import AutoML
        import flaml as flaml_pkg
    except ImportError as e:
        raise ImportError(
            "Cannot import AutoML from flaml. "
            "Please install flaml with AutoML support: pip install 'flaml[automl]==2.3.6'"
        ) from e

from wedata_automl.summary import AutoMLSummary
from wedata_automl.utils.sk_pipeline import build_numeric_preprocessor
from wedata_automl.utils.spark_utils import compute_split_and_weights
from wedata_automl.utils.print_utils import safe_print, print_separator, print_header

logger = logging.getLogger(__name__)


# ============================================================================
# MLflow Artifact 日志记录辅助函数
# ============================================================================

def log_feature_list(features: List[str]):
    """记录特征列表到 MLflow"""
    import json
    mlflow.log_dict({"features": features}, "feature_list.json")


def log_best_config_overall(config: Dict[str, Any]):
    """记录最佳配置到 MLflow"""
    import json
    mlflow.log_dict(config, "best_config_overall.json")


def log_best_config_per_estimator(config: Dict[str, Any]):
    """记录每个估计器的最佳配置到 MLflow"""
    import json
    mlflow.log_dict(config, "best_config_per_estimator.json")


def log_engine_meta(meta: Dict[str, Any]):
    """记录引擎元数据到 MLflow"""
    import json
    mlflow.log_dict(meta, "engine_meta.json")


class TrialLogger:
    """
    FLAML Trial 日志记录器

    用于记录每个 trial 的详细信息到 MLflow
    """

    def __init__(self, parent_run_id: str, features: List[str], task: str, metric: str):
        """
        初始化 Trial Logger

        Args:
            parent_run_id: 父 run 的 ID
            features: 特征列表
            task: 任务类型
            metric: 评估指标
        """
        self.parent_run_id = parent_run_id
        self.features = features
        self.task = task
        self.metric = metric
        self.trial_count = 0
        self.trial_runs = []  # 存储所有 trial 的信息

    def log_trial(self, config: Dict[str, Any], estimator: str, val_loss: float, train_time: float):
        """
        记录单个 trial 到 MLflow

        Args:
            config: 超参数配置
            estimator: 估计器名称
            val_loss: 验证集损失
            train_time: 训练时间
        """
        self.trial_count += 1

        # 创建嵌套 run
        with mlflow.start_run(run_name=f"trial_{self.trial_count}_{estimator}", nested=True) as trial_run:
            trial_run_id = trial_run.info.run_id

            # 记录参数
            mlflow.log_param("estimator", estimator)
            mlflow.log_param("trial_number", self.trial_count)
            mlflow.log_param("parent_run_id", self.parent_run_id)

            # 记录超参数
            for key, value in config.items():
                try:
                    mlflow.log_param(f"hp_{key}", value)
                except Exception:
                    # 某些值可能无法序列化
                    mlflow.log_param(f"hp_{key}", str(value))

            # 记录指标
            mlflow.log_metric("val_loss", val_loss)
            mlflow.log_metric("train_time", train_time)

            # 如果是分类任务，val_loss 是负的准确率，转换回来
            if self.task == "classification" and self.metric in ["accuracy", "roc_auc", "f1"]:
                val_metric = -val_loss  # FLAML 使用负值表示损失
                mlflow.log_metric(f"val_{self.metric}", val_metric)

            # 记录特征列表
            log_feature_list(self.features)

            # 存储 trial 信息
            trial_info = {
                "run_id": trial_run_id,
                "trial_number": self.trial_count,
                "estimator": estimator,
                "val_loss": val_loss,
                "train_time": train_time,
                "config": config,
            }
            self.trial_runs.append(trial_info)

            safe_print(f"  Trial {self.trial_count:3d} | {estimator:15s} | val_loss={val_loss:.6f} | time={train_time:.2f}s")

    def get_best_trial(self) -> Dict[str, Any]:
        """
        获取最佳 trial

        Returns:
            最佳 trial 的信息字典
        """
        if not self.trial_runs:
            return None

        # 按 val_loss 排序（越小越好）
        best_trial = min(self.trial_runs, key=lambda x: x["val_loss"])
        return best_trial


class FLAMLTrainer:
    """
    FLAML 训练器
    
    封装 FLAML 训练逻辑，支持 Databricks 风格的参数
    """
    
    def __init__(
        self,
        task: str,
        target_col: str,
        timeout_minutes: int = 5,
        max_trials: Optional[int] = None,
        metric: str = "auto",
        exclude_cols: Optional[List[str]] = None,
        exclude_frameworks: Optional[List[str]] = None,
        sample_weight_col: Optional[str] = None,
        pos_label: Optional[Union[str, int]] = None,
        data_split_col: Optional[str] = None,
        experiment_name: Optional[str] = None,
        experiment_id: Optional[str] = None,
        run_name: Optional[str] = None,
        register_model: bool = True,
        model_name: Optional[str] = None,
        **kwargs
    ):
        """
        初始化 FLAML 训练器
        
        Args:
            task: 任务类型 ("classification" 或 "regression")
            target_col: 目标列名
            timeout_minutes: 超时时间（分钟）
            max_trials: 最大试验次数
            metric: 评估指标
            exclude_cols: 排除的列
            exclude_frameworks: 排除的框架
            sample_weight_col: 样本权重列
            pos_label: 正类标签（二分类）
            data_split_col: 数据划分列
            experiment_name: MLflow 实验名称
            experiment_id: MLflow 实验 ID
            run_name: MLflow run 名称
            register_model: 是否注册模型
            model_name: 模型名称
            **kwargs: 其他参数
        """
        self.task = task
        self.target_col = target_col
        self.timeout_minutes = timeout_minutes
        self.max_trials = max_trials
        self.metric = metric if metric != "auto" else self._get_default_metric(task)
        self.exclude_cols = exclude_cols or []
        self.exclude_frameworks = exclude_frameworks or []
        self.sample_weight_col = sample_weight_col
        self.pos_label = pos_label
        self.data_split_col = data_split_col
        self.experiment_name = experiment_name or "wedata_automl"
        self.experiment_id = experiment_id
        self.run_name = run_name or f"flaml_automl_{task}"
        self.register_model = register_model
        self.model_name = model_name
        self.kwargs = kwargs
        
        # 内部状态
        self.automl = None
        self.pipeline = None
        self.features = None
        self.preprocessor = None
    
    def _get_default_metric(self, task: str) -> str:
        """获取默认指标"""
        if task == "classification":
            return "log_loss"
        elif task == "regression":
            return "deviance"
        elif task == "":
            return
        else:
            return "accuracy"
    
    def _get_estimator_list(self) -> List[str]:
        """获取估计器列表"""
        all_estimators = ["lgbm", "xgboost", "rf", "extra_tree"]
        if self.task == "classification":
            all_estimators.append("lrl1")

        # 排除指定的框架
        estimators = [e for e in all_estimators if e not in self.exclude_frameworks]
        return estimators

    def _evaluate_model(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        X_val: pd.DataFrame,
        y_val: np.ndarray,
        X_test: pd.DataFrame,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        评估模型

        Returns:
            评估指标字典
        """
        metrics = {}

        if self.task == "classification":
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

            for name, X, y_true in [
                ("train", X_train, y_train),
                ("val", X_val, y_val),
                ("test", X_test, y_test),
            ]:
                pred = self.pipeline.predict(X)

                acc = float(accuracy_score(y_true, pred))
                f1 = float(f1_score(y_true, pred, average='weighted', zero_division=0))
                precision = float(precision_score(y_true, pred, average='weighted', zero_division=0))
                recall = float(recall_score(y_true, pred, average='weighted', zero_division=0))

                metrics[f"{name}_accuracy"] = acc
                metrics[f"{name}_f1"] = f1
                metrics[f"{name}_precision"] = precision
                metrics[f"{name}_recall"] = recall

                mlflow.log_metric(f"{name}_accuracy", acc)
                mlflow.log_metric(f"{name}_f1", f1)
                mlflow.log_metric(f"{name}_precision", precision)
                mlflow.log_metric(f"{name}_recall", recall)

                safe_print(f"{name.capitalize():5s} Set - Accuracy: {acc:.4f} | F1: {f1:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f}")

        elif self.task == "regression":
            from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

            for name, X, y_true in [
                ("train", X_train, y_train),
                ("val", X_val, y_val),
                ("test", X_test, y_test),
            ]:
                pred = self.pipeline.predict(X)

                r2 = float(r2_score(y_true, pred))
                mse = float(mean_squared_error(y_true, pred))
                mae = float(mean_absolute_error(y_true, pred))
                rmse = float(np.sqrt(mse))

                metrics[f"{name}_r2"] = r2
                metrics[f"{name}_mse"] = mse
                metrics[f"{name}_mae"] = mae
                metrics[f"{name}_rmse"] = rmse

                mlflow.log_metric(f"{name}_r2", r2)
                mlflow.log_metric(f"{name}_mse", mse)
                mlflow.log_metric(f"{name}_mae", mae)
                mlflow.log_metric(f"{name}_rmse", rmse)

                safe_print(f"{name.capitalize():5s} Set - R²: {r2:.4f} | MSE: {mse:.4f} | MAE: {mae:.4f} | RMSE: {rmse:.4f}")

        return metrics
    
    def _prepare_data(
        self,
        pdf: pd.DataFrame
    ) -> tuple:
        """
        准备数据
        
        Returns:
            (X_train, y_train, X_val, y_val, X_test, y_test, features)
        """
        # 确定特征列
        disable_cols = set(self.exclude_cols) | {self.target_col}
        if self.sample_weight_col:
            disable_cols.add(self.sample_weight_col)
        if self.data_split_col:
            disable_cols.add(self.data_split_col)
        
        self.features = [c for c in pdf.columns if c not in disable_cols]

        safe_print(f"Target column: '{self.target_col}'")
        safe_print(f"Feature columns: {len(self.features)} columns")
        if len(self.features) <= 20:
            safe_print(f"  Features: {', '.join(self.features)}")
        else:
            safe_print(f"  First 10 features: {', '.join(self.features[:10])}")
            safe_print(f"  ... and {len(self.features) - 10} more")
        
        # 数据划分
        safe_print("", show_timestamp=False, show_level=False)
        if self.data_split_col and self.data_split_col in pdf.columns:
            # 使用用户提供的划分列
            pdf["_automl_split_col"] = pdf[self.data_split_col]
            safe_print(f"✅ Using user-provided split column: '{self.data_split_col}'")
        else:
            # 自动划分
            safe_print(f"Auto-generating train/val/test split (60%/20%/20%)")
            if self.task == "classification":
                safe_print(f"  Using stratified split for classification")
            split_col, sample_weights = compute_split_and_weights(
                y=pdf[self.target_col].values,
                task=self.task,
                train_ratio=0.6,
                val_ratio=0.2,
                test_ratio=0.2,
                stratify=True if self.task == "classification" else False,
                random_state=42,
            )
            pdf["_automl_split_col"] = split_col.values
            pdf["_automl_sample_weight"] = sample_weights.values
            safe_print("✅ Split generated successfully")
        
        # 分割数据
        train_df = pdf[pdf["_automl_split_col"] == 0]
        val_df = pdf[pdf["_automl_split_col"] == 1]
        test_df = pdf[pdf["_automl_split_col"] == 2]
        
        X_train = train_df[self.features]
        y_train = train_df[self.target_col].values
        
        X_val = val_df[self.features]
        y_val = val_df[self.target_col].values
        
        X_test = test_df[self.features]
        y_test = test_df[self.target_col].values

        safe_print("", show_timestamp=False, show_level=False)
        safe_print(f"Data split summary:")
        safe_print(f"  Train: {len(train_df):,} samples ({len(train_df)/len(pdf)*100:.1f}%)")
        safe_print(f"  Val:   {len(val_df):,} samples ({len(val_df)/len(pdf)*100:.1f}%)")
        safe_print(f"  Test:  {len(test_df):,} samples ({len(test_df)/len(pdf)*100:.1f}%)")
        safe_print(f"  Total: {len(pdf):,} samples")

        # 显示目标变量分布（分类任务）
        if self.task == "classification":
            safe_print("", show_timestamp=False, show_level=False)
            safe_print(f"Target distribution in training set:")
            train_dist = pd.Series(y_train).value_counts().sort_index()
            for label, count in train_dist.items():
                safe_print(f"  Class {label}: {count:,} samples ({count/len(y_train)*100:.1f}%)")

        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def train(
        self,
        dataset: Union[pd.DataFrame, Any],
        spark=None
    ) -> AutoMLSummary:
        """
        训练模型
        
        Args:
            dataset: 数据集（Pandas DataFrame 或 Spark DataFrame）
            spark: Spark session（如果 dataset 是表名）
            
        Returns:
            AutoMLSummary 对象
        """
        # 转换为 Pandas DataFrame
        if isinstance(dataset, str):
            # 表名
            if spark is None:
                raise ValueError("Spark session is required when dataset is a table name")
            pdf = spark.read.table(dataset).toPandas()
        elif hasattr(dataset, "toPandas"):
            # Spark DataFrame
            pdf = dataset.toPandas()
        else:
            # Pandas DataFrame
            pdf = dataset
        
        print_separator()
        safe_print("📊 Data Loading", show_timestamp=False, show_level=False)
        print_separator()
        safe_print(f"Dataset shape: {pdf.shape} (rows × columns)")
        safe_print(f"Memory usage: {pdf.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # 准备数据
        safe_print("", show_timestamp=False, show_level=False)
        print_separator()
        safe_print("🔧 Data Preparation", show_timestamp=False, show_level=False)
        print_separator()
        X_train, y_train, X_val, y_val, X_test, y_test = self._prepare_data(pdf)
        
        # 构建预处理器
        safe_print("", show_timestamp=False, show_level=False)
        print_separator()
        safe_print(f"⚙️  Feature Preprocessing")
        print_separator()
        self.preprocessor = build_numeric_preprocessor(self.features)
        X_train_num = self.preprocessor.fit_transform(X_train)
        X_val_num = self.preprocessor.transform(X_val)
        X_test_num = self.preprocessor.transform(X_test)

        safe_print(f"Preprocessor fitted successfully")
        safe_print(f"  - Train set: {X_train_num.shape}")
        safe_print(f"  - Val set:   {X_val_num.shape}")
        safe_print(f"  - Test set:  {X_test_num.shape}")
        
        # 获取或创建 MLflow 实验
        safe_print("", show_timestamp=False, show_level=False)
        print_separator()
        safe_print(f"📝 MLflow Experiment Setup")
        print_separator()
        if self.experiment_id:
            experiment = mlflow.get_experiment(self.experiment_id)
            experiment_name = experiment.name
            safe_print(f"Using experiment by ID: {self.experiment_id}")
        else:
            experiment_name = self.experiment_name
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                safe_print(f"✅ Created new experiment: '{experiment_name}' (ID: {experiment_id})")
                # 重新获取 experiment 对象
                experiment = mlflow.get_experiment(experiment_id)
            else:
                experiment_id = experiment.experiment_id
                safe_print(f"✅ Using existing experiment: '{experiment_name}' (ID: {experiment_id})")

        mlflow.set_experiment(experiment_name)

        # 开始 MLflow run
        with mlflow.start_run(run_name=self.run_name) as parent_run:
            parent_run_id = parent_run.info.run_id
            safe_print(f"Run name: '{self.run_name}'")
            safe_print(f"Run ID: {parent_run_id}")
            
            # 记录参数
            mlflow.log_params({
                "task": self.task,
                "target_col": self.target_col,
                "timeout_minutes": self.timeout_minutes,
                "metric": self.metric,
                "n_rows": len(pdf),
                "n_features": len(self.features),
            })
            
            log_feature_list(self.features)
            log_engine_meta({"engine": "flaml", "version": getattr(flaml_pkg, "__version__", "unknown")})
            
            # FLAML 设置
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print(f"🤖 AutoML Training Configuration")
            print_separator()
            self.automl = AutoML()
            estimator_list = self._get_estimator_list()

            settings = {
                "task": self.task,
                "metric": self.metric,
                "time_budget": int(self.timeout_minutes * 60),  # 转换为秒
                "eval_method": "holdout",
                "ensemble": False,
                "verbose": 0,  # 抑制日志
                "estimator_list": estimator_list,
                "seed": 42,
                "log_file_name": None,
                "mlflow_logging": False,  # 禁用 FLAML 的自动 MLflow 记录，我们手动控制
            }

            if self.max_trials:
                settings["max_iter"] = self.max_trials

            safe_print(f"Task: {self.task}")
            safe_print(f"Metric: {self.metric}")
            safe_print(f"Time budget: {self.timeout_minutes} minutes ({int(self.timeout_minutes * 60)} seconds)")
            safe_print(f"Max trials: {self.max_trials if self.max_trials else 'unlimited'}")
            safe_print(f"Estimators: {', '.join(estimator_list)}")
            safe_print(f"Evaluation method: holdout")
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print("🚀 Starting AutoML Training...", show_timestamp=False, show_level=False)
            print_separator()
            
            # 抑制 FLAML 和 MLflow 子 run 的 debug 日志
            import logging as py_logging
            flaml_logger = py_logging.getLogger("flaml.automl.logger")
            flaml_automl_logger = py_logging.getLogger("flaml.automl")
            mlflow_logger = py_logging.getLogger("mlflow.tracking._tracking_service.client")
            mlflow_utils_logger = py_logging.getLogger("mlflow.utils")

            original_flaml_level = flaml_logger.level
            original_flaml_automl_level = flaml_automl_logger.level
            original_mlflow_level = mlflow_logger.level
            original_mlflow_utils_level = mlflow_utils_logger.level

            # 设置为 WARNING 级别，只显示警告和错误
            flaml_logger.setLevel(py_logging.WARNING)
            flaml_automl_logger.setLevel(py_logging.WARNING)
            mlflow_logger.setLevel(py_logging.WARNING)
            mlflow_utils_logger.setLevel(py_logging.WARNING)

            safe_print("Training in progress... (FLAML debug logs suppressed)")
            
            start_time = time.time()
            
            try:
                # 训练
                self.automl.fit(
                    X_train=X_train_num,
                    y_train=y_train,
                    X_val=X_val_num,
                    y_val=y_val,
                    **settings,
                )
            finally:
                # 恢复日志级别
                flaml_logger.setLevel(original_flaml_level)
                flaml_automl_logger.setLevel(original_flaml_automl_level)
                mlflow_logger.setLevel(original_mlflow_level)
                mlflow_utils_logger.setLevel(original_mlflow_utils_level)

            elapsed_time = time.time() - start_time
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print("✅ AutoML Training Completed", show_timestamp=False, show_level=False)
            print_separator()
            safe_print(f"Total training time: {elapsed_time:.1f}s ({elapsed_time/60:.2f} minutes)")

            # 记录所有 trials 到 MLflow
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print("📝 Logging All Trials to MLflow", show_timestamp=False, show_level=False)
            print_separator()

            trial_logger = TrialLogger(
                parent_run_id=parent_run_id,
                features=self.features,
                task=self.task,
                metric=self.metric
            )

            # 获取所有 trials 的历史记录
            # FLAML 的 config_history 格式: {trial_id: (estimator_name, config_dict, time)}
            if hasattr(self.automl, "config_history"):
                config_history = self.automl.config_history

                # config_history 是一个字典: {trial_id: (estimator, config, time)}
                for trial_id, trial_data in config_history.items():
                    if isinstance(trial_data, tuple) and len(trial_data) >= 2:
                        estimator = trial_data[0]
                        config_dict = trial_data[1] if len(trial_data) > 1 else {}

                        # 从 AutoML 对象获取该 trial 的损失值
                        # FLAML 内部存储了每个配置的验证损失
                        val_loss = config_dict.get("val_loss", float('inf'))
                        train_time = config_dict.get("time_total_s", 0.0)

                        # 过滤掉内部字段
                        config = {k: v for k, v in config_dict.items()
                                 if k not in ["val_loss", "time_total_s", "trained_estimator", "learner"]}

                        trial_logger.log_trial(
                            config=config,
                            estimator=estimator,
                            val_loss=val_loss,
                            train_time=train_time
                        )

            safe_print(f"Total trials logged: {trial_logger.trial_count}")

            # 获取最佳 trial
            best_trial = trial_logger.get_best_trial()
            if best_trial:
                safe_print(f"Best trial: #{best_trial['trial_number']} ({best_trial['estimator']})")
                safe_print(f"Best val_loss: {best_trial['val_loss']:.6f}")
                best_trial_run_id = best_trial['run_id']
            else:
                best_trial_run_id = parent_run_id

            # 记录最佳配置到父 run
            best_est = self.automl.best_estimator
            best_cfg = self.automl.best_config
            log_best_config_overall(best_cfg)
            if getattr(self.automl, "best_config_per_estimator", None):
                log_best_config_per_estimator(self.automl.best_config_per_estimator)

            mlflow.log_param("best_estimator", best_est)
            mlflow.log_param("best_trial_run_id", best_trial_run_id)
            mlflow.log_param("total_trials", trial_logger.trial_count)

            safe_print("", show_timestamp=False, show_level=False)
            safe_print(f"Best estimator: {best_est}")
            safe_print(f"Best config: {best_cfg}")
            
            # 构建服务管道
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print(f"🔨 Building Serving Pipeline")
            print_separator()
            clf = self.automl.model
            self.pipeline = SkPipe([("preprocess", self.preprocessor), ("clf", clf)])
            self.pipeline.fit(X_train, y_train)
            safe_print("Pipeline built: [Preprocessor] -> [Classifier/Regressor]")

            # 评估
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print(f"📊 Model Evaluation")
            print_separator()
            metrics = self._evaluate_model(
                X_train, y_train, X_val, y_val, X_test, y_test
            )
            
            # 注册模型
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print(f"💾 Model Registration")
            print_separator()
            model_uri = f"runs:/{parent_run_id}/model"
            model_version = None

            if self.register_model and self.model_name:
                mlflow.sklearn.log_model(self.pipeline, "model")
                safe_print(f"Model logged to MLflow")
                result = mlflow.register_model(model_uri, self.model_name)
                model_version = result.version
                safe_print(f"✅ Model registered: '{self.model_name}' version {model_version}")
            else:
                mlflow.sklearn.log_model(self.pipeline, "model")
                safe_print(f"Model logged to MLflow (not registered)")
            
            # 创建 AutoMLSummary
            summary = AutoMLSummary(
                experiment_id=experiment.experiment_id,
                run_id=parent_run_id,
                best_trial_run_id=best_trial_run_id,  # 使用最佳 trial 的 run_id
                model_uri=model_uri,
                model_version=model_version,
                metrics=metrics,
                best_estimator=best_est,
                best_params=best_cfg,
            )

            # 最终总结
            safe_print("", show_timestamp=False, show_level=False)
            print_separator()
            safe_print(f"🎉 Training Pipeline Completed Successfully!")
            print_separator()
            safe_print(f"Experiment: {experiment_name} (ID: {experiment.experiment_id})")
            safe_print(f"Run ID: {parent_run_id}")
            safe_print(f"Best Model: {best_est}")
            if self.register_model and self.model_name:
                safe_print(f"Registered Model: {self.model_name} v{model_version}")
            safe_print(f"Model URI: {model_uri}")

            # 显示最佳性能指标
            if self.task == "classification":
                test_acc = metrics.get("test_accuracy", 0)
                test_f1 = metrics.get("test_f1", 0)
                safe_print(f"Test Accuracy: {test_acc:.4f}")
                safe_print(f"Test F1 Score: {test_f1:.4f}")
            elif self.task == "regression":
                test_r2 = metrics.get("test_r2", 0)
                test_rmse = metrics.get("test_rmse", 0)
                safe_print(f"Test R²: {test_r2:.4f}")
                safe_print(f"Test RMSE: {test_rmse:.4f}")

            print_separator()

            return summary

