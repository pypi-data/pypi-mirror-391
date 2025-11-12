"""
时序预测任务类

对齐 Databricks AutoML 的 Forecast 类
"""
from typing import Any, List, Optional, Union
import pandas as pd
import logging

from wedata_automl.summary import AutoMLSummary
from wedata_automl.tasks.base import BaseAutoML
from wedata_automl.engines.flaml_trainer import FLAMLTrainer

logger = logging.getLogger(__name__)


class Forecast(BaseAutoML):
    """
    时序预测任务类
    
    对齐 Databricks AutoML 的 Forecast 类
    
    Example:
        >>> from wedata_automl.tasks import Forecast
        >>> forecast = Forecast()
        >>> summary = forecast.fit(
        ...     dataset=spark.table("demo.sales_data"),
        ...     target_col="sales",
        ...     time_col="date",
        ...     horizon=30,
        ...     frequency="D",
        ...     timeout_minutes=10,
        ...     max_trials=100
        ... )
    """
    
    def fit(
        self,
        dataset: Union[pd.DataFrame, Any, str],
        target_col: str,
        time_col: str,
        horizon: int,
        frequency: str = "D",
        identity_col: Optional[List[str]] = None,
        timeout_minutes: int = 60,
        max_trials: Optional[int] = 100,
        metric: str = "smape",
        exclude_cols: Optional[List[str]] = None,
        exclude_frameworks: Optional[List[str]] = None,
        data_split_col: Optional[str] = None,
        experiment_name: Optional[str] = None,
        experiment_id: Optional[str] = None,
        run_name: Optional[str] = None,
        register_model: bool = True,
        model_name: Optional[str] = None,
        max_concurrent_trials: int = 1,
        spark=None,
        **kwargs
    ) -> AutoMLSummary:
        """
        训练时序预测模型
        
        Args:
            dataset: 数据集（Pandas DataFrame 或 Spark DataFrame 或表名）
            target_col: 目标列名（要预测的值）
            time_col: 时间列名
            horizon: 预测时间范围（预测未来多少个时间点）
            frequency: 时间频率（D=天, W=周, M=月, H=小时等）
            identity_col: 标识列（用于多时间序列预测），默认 None
            timeout_minutes: 超时时间（分钟），默认 60
            max_trials: 最大试验次数，默认 100
            metric: 评估指标，默认 "smape"
                - smape: Symmetric Mean Absolute Percentage Error（默认）
                - mse: Mean Squared Error
                - rmse: Root Mean Squared Error
                - mae: Mean Absolute Error
                - mdape: Median Absolute Percentage Error
            exclude_cols: 排除的列，默认 None
            exclude_frameworks: 排除的框架，默认 None
                - prophet: Prophet
                - arima: ARIMA
                - deepar: Deep-AR
            data_split_col: 数据划分列，默认 None
            experiment_name: MLflow 实验名称，默认 None
            experiment_id: MLflow 实验 ID，默认 None
            run_name: MLflow run 名称，默认 None
            register_model: 是否注册模型，默认 True
            model_name: 模型名称，默认 None
            max_concurrent_trials: 最大并发试验数，默认 1，最大 100
            spark: Spark session，默认 None
            **kwargs: 其他参数
            
        Returns:
            AutoMLSummary 对象
            
        Example:
            >>> forecast = Forecast()
            >>> summary = forecast.fit(
            ...     dataset=spark.table("demo.sales_data"),
            ...     target_col="sales",
            ...     time_col="date",
            ...     horizon=30,
            ...     frequency="D",
            ...     timeout_minutes=10,
            ...     max_trials=100,
            ...     metric="smape",
            ...     exclude_frameworks=["deepar"],
            ...     experiment_name="sales_forecasting",
            ...     register_model=True,
            ...     model_name="sales_forecast_model"
            ... )
            >>> print(summary)
        """
        logger.info(f"Starting forecast task with target_col={target_col}, time_col={time_col}, horizon={horizon}")
        
        # 验证参数
        if max_concurrent_trials < 1 or max_concurrent_trials > 100:
            raise ValueError("max_concurrent_trials must be between 1 and 100")
        
        # 验证评估指标
        valid_metrics = ["smape", "mse", "rmse", "mae", "mdape"]
        if metric not in valid_metrics:
            raise ValueError(f"metric must be one of {valid_metrics}, got {metric}")
        
        # 创建 FLAMLTrainer
        trainer = FLAMLTrainer(
            task="forecast",
            target_col=target_col,
            timeout_minutes=timeout_minutes,
            max_trials=max_trials,
            metric=metric,
            exclude_cols=exclude_cols,
            exclude_frameworks=exclude_frameworks,
            data_split_col=data_split_col,
            experiment_name=experiment_name,
            experiment_id=experiment_id,
            run_name=run_name or "forecast",
            register_model=register_model,
            model_name=model_name,
            max_concurrent_trials=max_concurrent_trials,
            # 时序预测特有参数
            time_col=time_col,
            horizon=horizon,
            frequency=frequency,
            identity_col=identity_col,
            **kwargs
        )
        
        # 训练
        summary = trainer.train(dataset, spark=spark)
        
        logger.info(f"Forecast task completed. Best estimator: {summary.best_estimator}")
        
        return summary

