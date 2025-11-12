import click

from .toPYD import to_pyd


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("欢迎使用 toPYD！ 请使用 'setup' 或 'installer' 子命令。")
        # click.echo(cli.get_help(ctx))

        click.echo("=" * 60)
        click.echo("可用命令：\n")

        for subcommand_name, subcommand_obj in cli.commands.items():
            # 获取子命令的帮助文本
            help_text = subcommand_obj.get_help(ctx)

            # 提取第一行作为简要说明（description）
            short_desc = subcommand_obj.get_short_help_str()
            if short_desc:
                short_desc = f'({short_desc.strip()})'
            else:
                short_desc = ""

            click.echo(f"• {subcommand_name} {short_desc}")

            # print(help_text)
            # continue
            # 提取帮助文本中的选项部分（从 "Options:" 开始）
            lines = help_text.splitlines()
            in_options = False
            for line in lines:
                if line.strip().startswith("Options:") or line.strip().startswith("选项:"):  # 支持中文 Click
                    in_options = True
                    continue
                if in_options and line.strip() == "":
                    break  # 空行结束选项
                if in_options and line.strip():
                    if '--help' in line:
                        continue
                    # 缩进显示选项
                    click.echo(f"     {line}")

            click.echo()
        click.echo("提示：使用 topyd <command> --help 查看详细帮助")


@cli.command()
@click.option('--files', '-f', multiple=True, help='指定文件，可指定多个')
@click.option('--all', '-a', is_flag=True, help='根目录下的全部 [py/pyx] 文件，与 -f [file_path] 任选其一')
@click.option('--exclude', '-e', multiple=True, help='排除的目录或文件，与`gitignore`语法规则一致，可指定多个')
@click.option('--exclude-file', '-ef', default="True",
              help='自定义排除规则的文件路径。默认为True 使用当前目录中的.gitignore文件， 输入[f/false/False]表示不使用gitignore排除规则')
@click.option('--source-root', '-s', default='.', help='源代码根目录，默认为(.)当前目录')
@click.option('--output-dir', '-o', default='build_pyd', help='编译后文件输出目录，默认为 build_pyd')
@click.option('--c-files-dir', '-c', default='build/c_files', help='Cython中间文件目录，默认为 build/c_files')
@click.option('--hidden-import', default=True, help='生成 hidden_import.py 文件。默认 True 仅-a方式生成')
@click.option('--alone', default=False, help='单独文件的方式编译,玄学打包。默认 False')
def setup(files, all, exclude, exclude_file, source_root, output_dir, c_files_dir, hidden_import, alone):
    """
    将Python源文件编译为pyd/so文件
    """
    if not files and not all:
        raise click.UsageError("必须提供 -f [file_path] 或 -a 中的至少一个。")
    if files and all:
        raise click.UsageError("-f 和 -a 不能同时使用。")

    # 处理gitignore选项
    if exclude_file in ['f', 'false', 'False']:
        gitignore_use = False
    elif exclude_file in ['t', 'true', 'True']:
        gitignore_use = True
    else:
        gitignore_use = exclude_file

    # 调用to_pyd函数
    to_pyd(
        files=list(files) if files else None,
        exclude=list(exclude) if exclude else None,
        exclude_file=gitignore_use,
        source_root=source_root,
        pyd_output_dir=output_dir,
        c_files_dir=c_files_dir,
        write_hidden_import=False if files else hidden_import,
        alone=alone
    )


@cli.command()
@click.option('--main-file', '-m', type=click.Path(exists=True), required=True, help='启动文件')
def installer():
    """
    将编译为pyd/so的文件，通过 pyinstaller 打包
    """
    print('installer （暂时没做，目前计划的是尽量和 pyinstaller 一样的指令）')
