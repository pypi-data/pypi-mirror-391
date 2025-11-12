import tomllib
from pathlib import Path

import typer
from platformdirs import user_config_path

from .deploy import compress_dir, deploy_blog
from .gen import generate_blog, init_new_blog, init_new_post
from .log_config import log_init, app_logger

log_init()

logger = app_logger

app = typer.Typer()

CONFIG_FILE_PATH = user_config_path(appname='djhx-blogger', appauthor='djhx') / 'config.toml'


def read_config() -> dict:

    CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    """
    读取用户配置文件。如果文件不存在，则返回空字典。
    """
    if CONFIG_FILE_PATH.is_file():
        try:
            with open(CONFIG_FILE_PATH, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            logger.warning(f"读取配置文件失败：{e}")
            return {}
    return {}


@app.command()
def run(
    # origin: Path = typer.Argument(..., exists=True, readable=True, help="原始博客内容目录（必填）"),
    origin: Path = typer.Option(
        None,
        "--origin", '-o',
        help='静态模块目录源地址',
    ),
    target: Path = typer.Option(
        None,
        "--target", "-t",
        help="生成的静态博客输出目录，默认为当前目录。",
    ),
    server: str = typer.Option(
        None,
        "--server", "-s",
        help="目标服务器（域名或 IP 地址），可选。",
    ),
    server_target: str = typer.Option(
        None,
        "--server-target", "-T",
        help="目标服务器的部署路径"
    ),
    deploy: bool = typer.Option(
        False,
        "--deploy", "-d",
        help="是否将静态博客部署到远程服务器。",
    ),
    new_blog: Path = typer.Option(
        None,
        "--new-blog", "-n",
        help="生成一个简单的示例博客",
    ),
    new_post: str = typer.Option(
        None,
        "--new-post", "-p",
        help="新建一篇文章",
    ),
    show_config_path: bool = typer.Option(
        False,
        "--config-path", "-c",
        help="查看配置文件路径",
    ),
):
    config = read_config()

    # 从配置文件中获取默认值（命令行优先）

    if not origin:
        config_origin = config.get('local', {}).get('origin')
        if config_origin:
            origin = Path(config_origin)

    target = target or Path(config.get("local", {}).get("target", Path.cwd()))
    server = server or config.get("deploy", {}).get("server")
    server_target = server_target or config.get("deploy", {}).get("target")

    typer.echo(f"原始目录: {origin}")
    typer.echo(f"输出目录: {target}")
    typer.echo(f"目标服务器: {server or '(未指定)'}")
    typer.echo(f"目标服务器部署地址: {server_target}")
    typer.echo(f"是否部署: {'是' if deploy else '否'}")

    if show_config_path:
        logger.info(f'配置文件路径: {CONFIG_FILE_PATH}')
        return

    if new_blog:
        logger.info(f'在 {new_blog} 下生成一个新的博客目录')
        init_new_blog(str(new_blog))
        return

    if new_post:
        if not origin:
            logger.warning(f'需要指定博客根目录')
            return
        logger.info(f'创建新的文章: {new_post}')
        init_new_post(str(origin), new_post)
        return

    if not origin:
        logger.warning(f'需要指定 origin')
        return

    root_node = generate_blog(str(origin), str(target))

    if deploy and server and server_target:
        tar_path = compress_dir(root_node.destination_path)
        deploy_blog(server, tar_path, server_target)