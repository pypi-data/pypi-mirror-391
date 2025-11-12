import ast
import os
import re
import sys
from pathlib import Path
from typing import Set, List, Union

import pathspec
from Cython.Build import cythonize
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext


def load_gitignore_patterns(gitignore_path: Union[bool, str] = ".gitignore"):
    """读取 .gitignore 文件，返回忽略模式列表
    :param gitignore_path 默认是 .gitignore 文件，如果是字符串则为自定义路径
    """

    if not gitignore_path:
        return []

    if gitignore_path is True:
        gitignore_path = ".gitignore"

    patterns = []
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            patterns = f.readlines()
    except Exception as e:
        print(f"[警告] 无法读取 .gitignore 文件: {e}")
    return patterns


def load_exclude_patterns(exclude: Union[str, list], exclude_file: Union[bool, str] = True) -> List[str]:
    """ 加载排除模式
    排除方法使用的是和 .gitignore 一样的算法，所以需要符合 .gitignore 格式要求
    """
    exclude_patterns = []

    if isinstance(exclude, list):
        exclude_patterns = exclude
    elif isinstance(exclude, str):
        exclude_patterns = exclude.splitlines()

    # 如果是通过代码方式启动的，则排除对应的启动文件，比如: setup_pyd.py
    startup_file = sys.argv[0]
    is_startup_file = os.path.isfile(startup_file)
    if is_startup_file:
        exclude_patterns.append('/' + os.path.basename(startup_file))
        print(f'自动排除启动文件:{os.path.basename(startup_file)}')

    if exclude_file:
        exclude_patterns.extend(load_gitignore_patterns(exclude_file))

    re_compile = re.compile(r'^\.+([\\|/])')

    exclude_patterns_ = []
    for path in exclude_patterns:
        if path.strip():
            path = re_compile.sub(r'\g<1>', path).strip()  # 替换多余的./ ../
            exclude_patterns_.append(path)

    print("排除模式:", exclude_patterns_)
    return exclude_patterns_


def get_module_name_ext(py_file: Path):
    """ 单个文件的 extension """
    print(f"准备文件:{py_file}")

    # 生成模块名：src/utils/helper.py → src.utils.helper
    module_name = ".".join(py_file.with_suffix('').parts)

    ext = Extension(
        name=module_name,
        sources=[str(py_file)],
    )
    return ext


def get_matching_files(source_root, exclude_patterns: list):
    """扫描源文件并生成需要的文件列表（带排除逻辑）

    :param source_root: 源文件目录
    :param exclude_patterns: 排除模式列表
    :return:  文件路径列表
    """
    module_names_ext = []
    source_root = Path(source_root)
    # 创建匹配器
    spec = pathspec.PathSpec.from_lines('gitwildmatch', exclude_patterns)

    # 收集所有 .py 和 .pyx 文件
    for ext_pattern in ["**/*.py", "**/*.pyx"]:
        for py_file in source_root.glob(ext_pattern):
            if spec.match_file(py_file):
                # print(f"跳过(被排除): {py_file}")
                continue

            ext = get_module_name_ext(py_file)
            module_names_ext.append(ext)

    return module_names_ext


def get_file_imports(file_path: Union[str, Path]) -> Set[str]:
    """
    解析 Python 文件，提取所有 import 和 from ... import 语句的文本表示(非字符串中的)。
    注意：不解析动态导入（如 __import__('os')）或字符串中的 import。

    :param file_path: Python 源文件路径
    :return: 导入语句字符串列表，例如 ['import os', 'from sys import argv']
    """
    file_path = Path(file_path)
    unique_imports = set()

    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return unique_imports

    with file_path.open('r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source, filename=str(file_path))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # 处理 `import xxx [as alias]`
            for name in node.names:
                import_str = f"import {name.name}"
                unique_imports.add(import_str)

        elif isinstance(node, ast.ImportFrom):
            # 处理 `from xxx import yyy [as alias]`
            module = node.module
            # 可能为 None，代码中没有导入任何模块。
            if module:
                full_module = module
                # 相对导入情况， 通过 '.' 层级层级计算出真实父目录路径作为导入模块
                if node.level > 0:
                    ancestor = file_path
                    for _ in range(node.level):
                        ancestor = ancestor.parent

                    full_module = f"{ancestor.name}.{module}"

                for name in node.names:
                    # alias.asname 才是 as别名，这里不需要
                    if name.name == '*':
                        import_str = f"from {full_module} import *"
                    else:
                        import_str = f"from {full_module} import {name.name}"
                    unique_imports.add(import_str)

    if unique_imports:
        print(f"[{file_path.name}] 导入的模块: {unique_imports}")
    else:
        print(f"[{file_path.name}] 没有导入任何模块")

    return unique_imports


def write_imports_to_file(import_list: Set[str], build_dirname: str) -> None:
    """ 将全部导入的模块存入文件

    :param import_list: 一个包含了所有模块的列表
    :param build_dirname: 生成.pyd文件的根目录
    """
    import_list = list(import_list)
    if not import_list:
        return

    import_list.sort()

    with open(Path(build_dirname, 'hidden_import.py'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(import_list))


class BuildExt(_build_ext):
    """自定义 build_ext：控制 .pyd 输出路径"""
    pyd_output_dir = ''

    def get_ext_fullpath(self, ext_name):
        parts = ext_name.split('.')
        filename = self.get_ext_filename(parts[-1])  # 带版本号的文件名 test_xx.cp38-win_amd64.pyd

        # 删除中间的.cp38-win_amd64 版本信息名
        name_split = filename.split('.')
        filename = f'{name_split[0]}.{name_split[2]}'

        fullpath = Path(self.pyd_output_dir).joinpath(*parts[:-1], filename)
        return str(fullpath)


# 编译
def run_setup(files: list, c_files_dir: str, pyd_output_dir: str):
    # 改下输出目录
    BuildExt.pyd_output_dir = pyd_output_dir

    setup(
        name="project",
        ext_modules=cythonize(
            files,
            language_level=3,
            build_dir=c_files_dir,
            compiler_directives={
                'binding': True,
                'boundscheck': False,
            },
            # nthreads=4,  # 可选：并行编译。。有问题。导致一直在重复这个文件。。估计是windows下多进程问题
        ),
        cmdclass={'build_ext': BuildExt},
        options={
            'build_ext': {
                'build_temp': c_files_dir,
                'inplace': False
            }
        },
        # 非常关键 相当于在命令行加入 build_ext 命令。当然也可以添加其他命令，以后在这里添加
        script_args=['build_ext'],
        # 显式声明不使用 pyproject.toml 等配置,避免打包时自动读取 pyproject.toml 文件,导致的无法打包.
        py_modules=[]

    )


def heddle_imports(module_names_ext, pyd_output_dir):
    """
    收集所有待编译 Python 文件中的 import 和 from ... import 语句，
    并将它们汇总写入到指定目录下的 hidden_import.py 文件中。

    :param module_names_ext: Extension 对象列表，每个对象包含一个源文件路径
    :param pyd_output_dir: str, 用于存放输出 .pyd 文件的目录，也是 hidden_import.py 的输出目录
    """
    import_set = set()
    for ext in module_names_ext:
        import_set.update(get_file_imports(ext.sources[0]))

    write_imports_to_file(import_set, pyd_output_dir)


def to_pyd(
        files: list = None,
        exclude: Union[str, list] = None,
        exclude_file: Union[bool, str] = '.gitignore',
        source_root: str = ".",
        pyd_output_dir: str = "build_pyd",
        c_files_dir: str = 'build/c_files',
        write_hidden_import: bool = True,
        alone: bool = False
):
    """
    一键编译Python源文件为pyd/so文件（Cython扩展模块）。

    该函数会递归扫描指定目录下的所有 .py 和 .pyx 文件，根据排除规则过滤后，
    使用 Cython 将其编译为二进制的 .pyd 文件（Windows）或 .so 文件（Linux/macOS），
    同时支持将编译后的文件按原始目录结构输出，并可选地提取所有源文件的导入依赖。

    :param files:  要编译的源文件列表。如果为 None，则默认为当前目录下的所有 .py 和 .pyx 文件。
    :param exclude: 自定义排除规则，支持通配符（如 *.pyc, test_*, temp/ 等）。
                    如果为字符串，则按行分割为列表。默认为 None。
    :param exclude_file: 自定义排除规则的文件路径。默认为使用当前目录中的.gitignore 文件进行排除。False为不使用文件
    :param source_root:  要编译的源代码根目录路径。默认为当前目录 "."。
    :param pyd_output_dir:  编译后 .pyd/.so 文件的输出目录。默认为 "build_pyd"。
    :param c_files_dir:  Cython 生成的中间 .c 文件存放目录。默认为 "build/c_files"。
    :param write_hidden_import:  是否收集所有源文件中的 import 语句并写入 hidden_import.py 文件。
                                 用于 PyInstaller 等工具打包时避免遗漏pyd中的隐式导入。默认为 True。
    :param alone:  独立文件编译, 玄学 , 防止出现中文 字节码 等异常. 单独一个文件分开编译就没问题,能跑就行
    """

    if files:
        module_names_ext = [get_module_name_ext(Path(file_path)) for file_path in files]
        write_hidden_import = False
    else:
        module_names_ext = get_matching_files(source_root, load_exclude_patterns(exclude, exclude_file=exclude_file))

    if not module_names_ext:
        print("未找到任何可编译的文件，请检查路径和排除规则。")
        return

    print(f"找到 {len(module_names_ext)} 个文件准备编译...")

    # 创建输出目录
    Path(c_files_dir).mkdir(parents=True, exist_ok=True)
    Path(pyd_output_dir).mkdir(parents=True, exist_ok=True)

    if alone:
        for ext in module_names_ext:
            run_setup([ext], c_files_dir, pyd_output_dir)
    else:
        heddle_imports(module_names_ext, pyd_output_dir)

    run_setup(module_names_ext, c_files_dir, pyd_output_dir)

    if write_hidden_import:
        heddle_imports(module_names_ext, pyd_output_dir)




def to_pyd_with_pyinstaller(files: list = None,
                            exclude: Union[str, list] = None,
                            exclude_file: Union[bool, str] = '.gitignore',
                            source_root: str = ".",
                            pyd_output_dir: str = "build_pyd",
                            c_files_dir: str = 'build/c_files',
                            write_hidden_import: bool = True):
    """
    一键编译Python源文件为pyd/so文件，并使用PyInstaller进行打包。

    :param files:  要编译的源文件列表。如果为 None，则默认为当前目录下的所有 .py 和 .pyx 文件
    """
    # 还没想好,主要思路是生成spce文件,填写进入spce文件,然后添加 datas 数据..主要是pyd文件无法自动读取pyd里的导入进行模块分析.
    pass


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    print("未处理的异常：", exc_type, exc_value)
    print("崩了而已。大概率是中文文件名 包含中文路径 代码中包含中文，总之非英文路径。玄学！")
    print("可以使用 -f 报错的文件.py 或者使用 -alone选项 单独进行打包解决!  ")


sys.excepthook = handle_uncaught_exception
