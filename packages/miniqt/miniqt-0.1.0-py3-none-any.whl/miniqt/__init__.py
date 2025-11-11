# -*- coding: utf-8 -*-
"""
miniqt: 量化交易可视化界面
=====================================
miniqt(MiniQuantTrader) 是基于 PyQt5 与 Fluent Widgets 构建的量化交易可视化界面，
为 minibt 量化交易库提供现代化的图形操作界面，简化策略开发、回测分析和实盘监控的全流程。

核心功能:
- 策略代码编辑与管理，支持语法高亮和自动补全
- 回测结果可视化分析，多维度展示性能指标
- 实时行情监控与图表展示，动态更新市场数据
- 策略参数配置与优化，图形化调参界面
- 交易执行监控，实时显示持仓和订单状态

技术栈:
- 界面框架: PyQt5 / PySide6
- UI组件: Fluent Widgets (现代化设计)
- 图表可视化: Lightweight Charts
- 量化核心: minibt 回测引擎

版本信息: v0.1.0
许可证: MIT License
项目仓库: https://github.com/MiniQtMaster/miniqt
联系邮箱: 407841129@qq.com
"""

from .app.view.main_window import MainWindow
from .app.common.config import cfg
from .cli import cli, run
import os
import sys

# ------------------------------
# 包元数据
# ------------------------------
__author__ = "owen"
__copyright__ = "Copyright (c) 2025 miniqt开发团队"
__license__ = "MIT"
__version__ = "0.1.0"
__version_info__ = (0, 1, 0)
__description__ = "MiniQuantTrader量化交易可视化界面，基于PyQt5与Fluent Widgets"

# ------------------------------
# 环境配置与初始化
# ------------------------------

# 设置环境变量，禁用QFluentWidgets提示
os.environ["QFluentWidgets_DISABLE_TIPS"] = "1"

# 高DPI支持配置
if sys.platform == "win32":
    if hasattr(sys, '_MEIPASS'):
        # 打包后的可执行文件环境
        os.environ["QT_SCALE_FACTOR"] = "1"
    else:
        # 开发环境
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# ------------------------------
# 核心模块导入
# ------------------------------

# CLI命令行接口

# 配置管理

# 主界面窗口

# 如果还有其他需要导出的核心组件，可以在这里添加
# from .app.view.strategy_editor import StrategyEditor
# from .app.view.backtest_analyzer import BacktestAnalyzer
# from .app.view.market_monitor import MarketMonitor

# ------------------------------
# 便捷启动函数
# ------------------------------


def launch():
    """
    快速启动miniqt图形界面

    示例:
        >>> import miniqt
        >>> miniqt.launch()
    """
    run()


def start():
    """
    launch()的别名，提供多种启动方式
    """
    launch()


# ------------------------------
# 公共接口导出（__all__定义）
# 仅暴露需要用户直接使用的类/函数/常量，隐藏内部实现
# ------------------------------
__all__ = [
    # 核心功能
    'cli', 'run', 'launch', 'start',

    # 配置与界面
    'cfg', 'MainWindow',

    # 元数据
    '__version__', '__author__', '__description__'
]

# ------------------------------
# 包初始化完成提示（仅开发模式）
# ------------------------------
if __name__ == "__main__":
    print(f"miniqt {__version__} 初始化完成")
    print("使用方式:")
    print("  命令行: miniqt run 或 miniqt launch")
    print("  Python: import miniqt; miniqt.launch()")
