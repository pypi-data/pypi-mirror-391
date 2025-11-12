"""
AutoML Summary - 训练结果摘要对象

对齐 Databricks AutoML 的 AutoMLSummary 类
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AutoMLSummary:
    """
    AutoML 训练结果摘要
    
    对齐 Databricks AutoML 的 AutoMLSummary 类
    
    Attributes:
        experiment_id: MLflow 实验 ID
        run_id: 主 run ID
        best_trial_run_id: 最佳 trial 的 run ID
        model_uri: 模型 URI (格式: runs:/<run_id>/model)
        model_version: 注册的模型版本号（如果注册了）
        metrics: 评估指标字典
        best_estimator: 最佳估计器名称
        best_params: 最佳超参数
        artifacts: 产物路径字典
    """
    experiment_id: str
    run_id: str
    best_trial_run_id: str
    model_uri: str
    model_version: Optional[int] = None
    metrics: Optional[Dict[str, float]] = None
    best_estimator: Optional[str] = None
    best_params: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, str]] = None
    
    def __repr__(self) -> str:
        """字符串表示"""
        lines = [
            "AutoMLSummary:",
            f"  Experiment ID: {self.experiment_id}",
            f"  Run ID: {self.run_id}",
            f"  Best Trial Run ID: {self.best_trial_run_id}",
            f"  Model URI: {self.model_uri}",
        ]
        
        if self.model_version is not None:
            lines.append(f"  Model Version: {self.model_version}")
        
        if self.best_estimator:
            lines.append(f"  Best Estimator: {self.best_estimator}")
        
        if self.metrics:
            lines.append("  Metrics:")
            for key, value in self.metrics.items():
                lines.append(f"    {key}: {value:.4f}")
        
        if self.best_params:
            lines.append("  Best Params:")
            for key, value in self.best_params.items():
                lines.append(f"    {key}: {value}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "best_trial_run_id": self.best_trial_run_id,
            "model_uri": self.model_uri,
            "model_version": self.model_version,
            "metrics": self.metrics,
            "best_estimator": self.best_estimator,
            "best_params": self.best_params,
            "artifacts": self.artifacts,
        }

