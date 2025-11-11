#!/usr/bin/env python3

import click
import os
import sys


# 如果你修改了 cli.py 文件，可能需要重新安装：

# bash
# # 只有修改了入口点相关的代码才需要
# pip install -e . --force-reinstall

# 如果添加了新包到 pyproject.toml：

# bash
# pip install -e .
# 1. 初始安装
# pip install -e .

# 2. 开发过程中（修改代码后）
# miniqt serve  # 直接运行，自动使用最新代码

# 3. 如果遇到奇怪的问题（清除缓存）
# python -c "import miniqt.cli; import importlib; importlib.reload(miniqt.cli)"


def start_qt_application():
    """启动Qt应用程序的核心逻辑"""
    import contextlib
    from io import StringIO  # 内存字符串流（捕获TqSdk的冗余日志）
    # 临时重定向stderr到StringIO，避免TqApi初始化时打印无关日志
    f = StringIO()
    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        from miniqt.app.view.main_window import MainWindow
        from miniqt.app.common.config import cfg
        from qfluentwidgets import FluentTranslator, qconfig
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QTranslator
    # 高DPI适配配置
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 应用初始化
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    # 国际化配置
    locale = cfg.get(cfg.language).value
    translator = FluentTranslator(locale)
    galleryTranslator = QTranslator()
    galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")
    app.installTranslator(translator)
    app.installTranslator(galleryTranslator)

    # 启动主窗口
    w = MainWindow()
    w.show()
    w.setMicaEffectEnabled(False)

    return app.exec_()


@click.group()
def cli():
    """miniqt - 量化交易可视化界面"""
    pass


@cli.command()
@click.option('--debug', is_flag=True, help='调试模式')
def run(debug):
    """启动miniqt图形界面"""
    if debug:
        print("🔧 调试模式")

    print("🚀 启动miniqt界面...")
    exit_code = start_qt_application()
    sys.exit(exit_code)


@cli.command()
def version():
    """显示版本信息"""
    from miniqt import __version__
    print(f"miniqt version {__version__}")


# 设置默认命令为 run
@cli.command()
@click.pass_context
@click.option('--debug', is_flag=True, help='调试模式')
def default(ctx, debug):
    """默认命令 - 启动miniqt图形界面"""
    ctx.invoke(run, debug=debug)


if __name__ == "__main__":
    cli()

# 添加热重载功能（高级）：
# 你可以在 CLI 中添加开发模式，自动监视文件变化：
# @cli.command()
# @click.option('--watch', is_flag=True, help='监视文件变化自动重启')
# def serve(watch):
#     """启动miniqt界面服务"""
#     if watch:
#         print("👀 开发模式：监视文件变化...")
#         # 可以使用 watchdog 库实现文件监视
#         # pip install watchdog
#         try:
#             from watchdog.observers import Observer
#             from watchdog.events import FileSystemEventHandler
#             import threading
#             import time

#             class RestartHandler(FileSystemEventHandler):
#                 def on_modified(self, event):
#                     if event.src_path.endswith('.py'):
#                         print("🔄 检测到文件变化，请重启服务...")

#             event_handler = RestartHandler()
#             observer = Observer()
#             observer.schedule(event_handler, path='.', recursive=True)
#             observer.start()

#             print("开始监视文件变化...按 Ctrl+C 停止")
#             try:
#                 while True:
#                     time.sleep(1)
#             except KeyboardInterrupt:
#                 observer.stop()
#             observer.join()

#         except ImportError:
#             print("⚠️  安装 watchdog 包以获得自动重启功能: pip install watchdog")
#             # 降级到普通模式
#             start_qt_application()
#     else:
#         start_qt_application()
