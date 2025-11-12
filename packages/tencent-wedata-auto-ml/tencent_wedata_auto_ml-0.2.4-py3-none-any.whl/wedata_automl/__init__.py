__version__ = "0.2.4"

# 导入便捷函数（对齐 Databricks）
from .api import classify, regress, forecast

# 导入任务类（对齐 Databricks）
from .tasks import Classifier, Regressor, Forecast

# 导入 AutoMLSummary
from .summary import AutoMLSummary

# 导入 Driver（通用驱动程序）
from .driver import AutoMLDriver, run_automl

__all__ = [
    # 便捷函数
    "classify",
    "regress",
    "forecast",
    # 任务类
    "Classifier",
    "Regressor",
    "Forecast",
    # 返回对象
    "AutoMLSummary",
    # 驱动程序
    "AutoMLDriver",
    "run_automl",
]

