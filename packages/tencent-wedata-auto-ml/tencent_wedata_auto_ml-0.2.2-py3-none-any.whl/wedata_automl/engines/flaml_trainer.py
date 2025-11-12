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

                logger.info(f"{name} metrics: accuracy={acc:.4f}, f1={f1:.4f}, precision={precision:.4f}, recall={recall:.4f}")

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

                logger.info(f"{name} metrics: r2={r2:.4f}, mse={mse:.4f}, mae={mae:.4f}, rmse={rmse:.4f}")

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
        
        logger.info(f"Selected {len(self.features)} feature columns")
        logger.info(f"Target column: {self.target_col}")
        
        # 数据划分
        if self.data_split_col and self.data_split_col in pdf.columns:
            # 使用用户提供的划分列
            pdf["_automl_split_col"] = pdf[self.data_split_col]
            logger.info(f"Using user-provided split column: {self.data_split_col}")
        else:
            # 自动划分
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
            logger.info("Auto-generated train/val/test split")
        
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
        
        logger.info(f"Split counts: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
        
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
        
        logger.info(f"Loaded data with shape={pdf.shape}")
        
        # 准备数据
        X_train, y_train, X_val, y_val, X_test, y_test = self._prepare_data(pdf)
        
        # 构建预处理器
        self.preprocessor = build_numeric_preprocessor(self.features)
        X_train_num = self.preprocessor.fit_transform(X_train)
        X_val_num = self.preprocessor.transform(X_val)
        X_test_num = self.preprocessor.transform(X_test)
        
        logger.info(f"Preprocessor fitted. Transformed shapes: X_train={X_train_num.shape}, X_val={X_val_num.shape}")
        
        # 获取或创建 MLflow 实验
        if self.experiment_id:
            experiment = mlflow.get_experiment(self.experiment_id)
            experiment_name = experiment.name
        else:
            experiment_name = self.experiment_name
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new MLflow experiment: {experiment_name} (ID: {experiment_id})")
                # 重新获取 experiment 对象
                experiment = mlflow.get_experiment(experiment_id)
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing MLflow experiment: {experiment_name} (ID: {experiment_id})")

        mlflow.set_experiment(experiment_name)
        
        # 开始 MLflow run
        with mlflow.start_run(run_name=self.run_name) as parent_run:
            parent_run_id = parent_run.info.run_id
            logger.info(f"MLflow parent run started: run_id={parent_run_id}")
            
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
            }
            
            if self.max_trials:
                settings["max_iter"] = self.max_trials
            
            logger.info(f"FLAML settings: {settings}")
            logger.info(f"Starting AutoML training...")
            
            # 抑制 FLAML 和 MLflow 子 run 日志
            import logging as py_logging
            flaml_logger = py_logging.getLogger("flaml.automl.logger")
            mlflow_logger = py_logging.getLogger("mlflow.tracking._tracking_service.client")
            original_flaml_level = flaml_logger.level
            original_mlflow_level = mlflow_logger.level
            
            flaml_logger.setLevel(py_logging.WARNING)
            mlflow_logger.setLevel(py_logging.WARNING)
            
            start_time = time.time()
            
            try:
                # 训练
                self.automl.fit(
                    X_train=X_train_num,
                    y_train=y_train,
                    X_val=X_val_num,
                    y_val=y_val,
                    mlflow_logging=True,
                    **settings,
                )
            finally:
                # 恢复日志级别
                flaml_logger.setLevel(original_flaml_level)
                mlflow_logger.setLevel(original_mlflow_level)
            
            elapsed_time = time.time() - start_time
            logger.info(f"AutoML training completed in {elapsed_time:.1f}s")
            
            # 记录最佳配置
            best_est = self.automl.best_estimator
            best_cfg = self.automl.best_config
            log_best_config_overall(best_cfg)
            if getattr(self.automl, "best_config_per_estimator", None):
                log_best_config_per_estimator(self.automl.best_config_per_estimator)
            
            mlflow.log_param("best_estimator", best_est)
            logger.info(f"Best estimator: {best_est}")
            
            # 构建服务管道
            clf = self.automl.model
            self.pipeline = SkPipe([("preprocess", self.preprocessor), ("clf", clf)])
            self.pipeline.fit(X_train, y_train)
            
            # 评估
            metrics = self._evaluate_model(
                X_train, y_train, X_val, y_val, X_test, y_test
            )
            
            # 注册模型
            model_uri = f"runs:/{parent_run_id}/model"
            model_version = None
            
            if self.register_model and self.model_name:
                mlflow.sklearn.log_model(self.pipeline, "model")
                result = mlflow.register_model(model_uri, self.model_name)
                model_version = result.version
                logger.info(f"Model registered: {self.model_name} version {model_version}")
            else:
                mlflow.sklearn.log_model(self.pipeline, "model")
            
            # 创建 AutoMLSummary
            summary = AutoMLSummary(
                experiment_id=experiment.experiment_id,
                run_id=parent_run_id,
                best_trial_run_id=parent_run_id,  # TODO: 获取最佳 trial 的 run_id
                model_uri=model_uri,
                model_version=model_version,
                metrics=metrics,
                best_estimator=best_est,
                best_params=best_cfg,
            )
            
            return summary

