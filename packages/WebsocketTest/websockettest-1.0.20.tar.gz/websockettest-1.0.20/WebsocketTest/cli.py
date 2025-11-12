import argparse
from pathlib import Path
from importlib import import_module

def main():
    parser = argparse.ArgumentParser(description="WebSocket Test CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # 动态加载子命令
    commands_dir = Path(__file__).parent / "commands"
    for cmd_file in commands_dir.glob("*.py"):
        if cmd_file.stem != "__init__":
            cmd_name = cmd_file.stem
            module = import_module(f"WebsocketTest.commands.{cmd_name}")
            cmd_parser = subparsers.add_parser(cmd_name, help=module.__doc__)
            if hasattr(module, 'configure_parser'):
                module.configure_parser(cmd_parser)
            # 关键：绑定执行函数
            if hasattr(module, 'func'):
                cmd_parser.set_defaults(func=module.func)
    # 只解析已知参数，保留剩余参数
    args, remaining_args = parser.parse_known_args()
    args.func(args, remaining_args)  # 调用子命令的执行函数

 
if __name__ == "__main__":
    main()