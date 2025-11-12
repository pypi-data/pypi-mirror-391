import os
import shutil
from PyInstaller import __main__ as pyi_main


def get_add_data_paths():
    """
    定义需要添加的数据文件/目录
    返回格式: [(源路径, 目标路径), ...]
    相当于命令行中的 --add-data "源路径;目标路径" (Windows) 或 "--add-data 源路径:目标路径" (Unix)
    """
    add_data = []

    # 添加单个文件
    if os.path.exists("config.ini"):
        add_data.append(("config.ini", "."))  # 复制到根目录

    # 添加整个目录
    if os.path.exists("assets"):
        add_data.append(("assets", "assets"))  # 复制assets目录到输出的assets目录

    # 可以根据条件动态添加
    if os.environ.get("INCLUDE_TEST_DATA") == "1":
        add_data.append(("test_data", "test_data"))

    return add_data


def clean_dist():
    """清理之前的构建结果"""
    for dir in ["dist", "build", "*.spec"]:
        if os.path.isdir(dir):
            shutil.rmtree(dir, ignore_errors=True)
        elif os.path.isfile(dir):
            os.remove(dir)


def build_executable():
    # 清理旧构建
    clean_dist()

    # 获取要添加的数据
    add_data = get_add_data_paths()

    # 构建PyInstaller命令参数
    args = [
        "main.py",  # 你的主程序
        "--name", "my_app",  # 输出的可执行文件名
        "--onefile",  # 打包成单个文件
        # "--windowed",  # 如果是GUI程序，取消注释此行
    ]

    # 添加数据文件参数
    # 根据操作系统处理分隔符
    sep = ";" if os.name == "nt" else ":"
    for src, dst in add_data:
        args.extend(["--add-data", f"{src}{sep}{dst}"])

    # 执行打包
    print(f"执行打包命令: {' '.join(args)}")
    pyi_main.run(args)


if __name__ == "__main__":
    build_executable()
    print("打包完成！可执行文件在 dist 目录下")
