
from WebsocketTest.run_tests import PytestRunner


def configure_parser(parser):
    """配置子命令参数"""
    parser.add_argument("--env", required=True, help="Test environment")
    parser.add_argument("--app", required=True, help="Application ID")
    parser.add_argument("--service", required=True, help="Service name")
    parser.add_argument("--project", required=True, help="Project name")

def execute(args,others):
    """执行test"""
    test_runner = PytestRunner(args,others)
    exit(test_runner.run())
# 注册到主CLI
func = execute