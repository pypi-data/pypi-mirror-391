#!/usr/bin/env python3
"""
spec-cli: AI 规则仓库自动配置工具
功能：下载 airules 仓库并根据 AI 工具类型配置规则文件
支持的工具：Cursor、ClaudeCode
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import click


# 颜色定义
class Colors:
    """ANSI 颜色代码"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


# 默认仓库地址
DEFAULT_REPO_URL = ""


def print_info(message: str):
    """打印信息消息"""
    click.echo(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")


def print_warning(message: str):
    """打印警告消息"""
    click.echo(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message: str):
    """打印错误消息"""
    click.echo(f"{Colors.RED}[ERROR]{Colors.NC} {message}", err=True)


def check_requirements() -> None:
    """检查必要的命令"""
    print_info("检查前置条件...")
    
    # 检查 git 命令是否存在
    if not shutil.which("git"):
        print_error("未找到 git 命令，请先安装 git")
        sys.exit(1)
    
    print_info("前置条件检查通过")


def select_ai_tool() -> str:
    """选择 AI 工具"""
    click.echo("")
    click.echo("请选择您使用的 AI 客户端工具：")
    click.echo("1) Cursor")
    click.echo("2) ClaudeCode")
    click.echo("")
    
    while True:
        choice = click.prompt("请输入选项 [1-2]", type=int)
        if choice == 1:
            ai_tool = "cursor"
            print_info("您选择了: Cursor")
            return ai_tool
        elif choice == 2:
            ai_tool = "claudecode"
            print_info("您选择了: ClaudeCode")
            return ai_tool
        else:
            print_warning("无效选项，请重新输入")


def download_rules_repo(temp_dir: Path, repo_url: str) -> None:
    """下载规则仓库"""
    print_info(f"开始下载规则仓库: {repo_url}")
    
    # 如果临时目录已存在，先删除
    if temp_dir.exists():
        print_warning("临时目录已存在，正在清理...")
        shutil.rmtree(temp_dir)
    
    # 克隆仓库
    try:
        subprocess.run(
            ["git", "clone", repo_url, str(temp_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print_info("仓库下载成功")
    except subprocess.CalledProcessError as e:
        print_error("仓库下载失败，请检查网络连接或仓库地址")
        print_error(f"错误详情: {e.stderr}")
        sys.exit(1)


def copy_rules(tool: str, target_dir: Path, temp_dir: Path) -> None:
    """拷贝规则文件"""
    print_info(f"目标配置目录: {target_dir}")
    
    # 创建目标目录（如果不存在）
    if not target_dir.exists():
        print_info(f"创建配置目录: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查源文件夹是否存在
    rules_source = temp_dir / "rules"
    commands_source = temp_dir / "commands"
    
    if not rules_source.exists():
        print_error("源仓库中未找到 rules 文件夹")
        cleanup(temp_dir)
        sys.exit(1)
    
    if not commands_source.exists():
        print_error("源仓库中未找到 commands 文件夹")
        cleanup(temp_dir)
        sys.exit(1)
    
    # 拷贝文件
    print_info("正在拷贝 rules 文件夹...")
    rules_target = target_dir / "rules"
    if rules_target.exists():
        shutil.rmtree(rules_target)
    shutil.copytree(rules_source, rules_target)
    
    print_info("正在拷贝 commands 文件夹...")
    commands_target = target_dir / "commands"
    if commands_target.exists():
        shutil.rmtree(commands_target)
    shutil.copytree(commands_source, commands_target)
    
    print_info("文件拷贝完成！")
    click.echo("")
    print_info(f"配置文件已安装到: {target_dir}")
    print_info(f"  - rules 目录: {target_dir / 'rules'}")
    print_info(f"  - commands 目录: {target_dir / 'commands'}")


def cleanup(temp_dir: Path) -> None:
    """清理临时文件"""
    if not temp_dir.exists():
        return
    
    print_info("清理临时文件...")
    
    # Windows 上删除 Git 仓库时可能遇到文件锁定问题
    # 使用更健壮的删除方法
    try:
        # 首先尝试修改文件权限（Windows 上可能需要）
        def handle_remove_readonly(func, path, exc):
            """处理只读文件的删除"""
            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)
        
        # 尝试删除，如果失败则修改权限后重试
        try:
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
        except (PermissionError, OSError) as e:
            # 如果仍然失败，尝试延迟删除（Windows 上文件可能仍被占用）
            print_warning(f"无法立即删除临时文件: {str(e)}")
            print_warning("临时文件将在系统清理时自动删除")
            # 在 Windows 上，可以尝试使用系统命令强制删除
            if sys.platform == "win32":
                try:
                    # 使用 Windows 的 rmdir 命令（需要管理员权限）
                    subprocess.run(
                        ["cmd", "/c", "rmdir", "/s", "/q", str(temp_dir)],
                        check=False,
                        timeout=5,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                except Exception:
                    # 如果还是失败，就忽略（临时文件会被系统自动清理）
                    pass
    except Exception as e:
        # 如果所有方法都失败，记录警告但不中断程序
        print_warning(f"清理临时文件时出现错误: {str(e)}")
        print_warning("临时文件将在系统清理时自动删除")


@click.group()
def cli():
    """spec-cli: AI 规则仓库自动配置工具"""
    pass


@cli.command()
@click.option(
    '--target-dir',
    '-d',
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help='目标安装目录（默认为当前工作目录）'
)
@click.option(
    '--template-repository',
    '--templateRepository',
    type=str,
    required=True,
    help='模板仓库地址（必填）'
)
def init(target_dir: Optional[Path], template_repository: str) -> None:
    """
    初始化 AI 规则配置
    
    下载 airules 仓库并根据选择的 AI 工具类型配置规则文件。
    支持的工具：Cursor、ClaudeCode
    """
    # 验证模板仓库地址
    if not template_repository or not template_repository.strip():
        print_error("请指定规则模板仓库地址")
        print_error("使用方法: spec init --template-repository <仓库地址>")
        sys.exit(1)
    
    template_repository = template_repository.strip()
    
    # 确定目标目录
    if target_dir is None:
        target_dir = Path.cwd()
    else:
        target_dir = target_dir.resolve()
    
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp(prefix="airules_"))
    
    try:
        click.echo("==========================================")
        click.echo("  AI 规则仓库自动配置脚本")
        click.echo("==========================================")
        click.echo("")
        
        print_info(f"目标安装目录: {target_dir}")
        print_info(f"模板仓库地址: {template_repository}")
        click.echo("")
        
        # 检查前置条件
        check_requirements()
        
        # 选择工具
        ai_tool = select_ai_tool()
        
        # 下载仓库
        download_rules_repo(temp_dir, template_repository)
        
        # 确定目标配置目录
        if ai_tool == "cursor":
            config_dir = target_dir / ".cursor"
        elif ai_tool == "claudecode":
            config_dir = target_dir / ".claude"
        else:
            print_error(f"未知的工具类型: {ai_tool}")
            sys.exit(1)
        
        # 拷贝文件
        copy_rules(ai_tool, config_dir, temp_dir)
        
        # 清理临时文件
        cleanup(temp_dir)
        
        click.echo("")
        click.echo("==========================================")
        print_info("配置完成！请重启您的 AI 工具以使配置生效")
        click.echo("==========================================")
    
    except KeyboardInterrupt:
        print_warning("\n操作被用户中断")
        cleanup(temp_dir)
        sys.exit(1)
    except Exception as e:
        print_error(f"发生错误: {str(e)}")
        cleanup(temp_dir)
        sys.exit(1)


def main():
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()

