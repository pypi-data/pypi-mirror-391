
from WebsocketTest.run_tests import AllureRunner


def configure_parser(parser):
    """配置子命令参数"""
    parser.add_argument("--port", type=int, default=8883, help="Allure report port")
    parser.add_argument("--report_dir", default="allure_report", help="Allure report directory")

def execute(args,others):
    """执行test"""
    allure_runner = AllureRunner(args)
    exit(allure_runner.run())
# 注册到主CLI
func = execute