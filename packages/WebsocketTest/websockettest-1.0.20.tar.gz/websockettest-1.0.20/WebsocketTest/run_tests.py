import subprocess,pytest,sys
import argparse
import shutil
import time
import webbrowser
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path
from WebsocketTest.common.logger import logger

class AllureRunner:
    def __init__(self,args):
        self.port = args.port
        self.report_dir = args.report_dir
        self.allure_path = shutil.which("allure")
        if not self.allure_path:
            raise RuntimeError("Allure command line tool not found in PATH")
        self.allure_results = str(Path.cwd().joinpath("allure_results"))


    def is_server_running(self) -> bool:
        """检查Allure服务是否已在运行"""
        try:
            with urlopen(f"http://localhost:{self.port}") as response:
                return response.status == 200
        except URLError:
            return False

    def start_server(self) -> bool:
        """启动Allure服务"""
        try:
            cmd = [self.allure_path, "open", self.report_dir, "-p", str(self.port)]
            # logger.info(f"start_server Executing: {' '.join(cmd)}")
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            time.sleep(1)  # 等待服务启动
            return True
        except Exception as e:
            logger.error(f"Failed to start Allure server: {e}")
            return False

    def refresh_browser_tab(self) -> bool:
        """尝试刷新已打开的Allure标签页"""
        url = f"http://localhost:{self.port}"
        
        # 方法1: 使用JavaScript刷新（需要浏览器支持）
        try:
            webbrowser.open_new_tab("javascript:location.reload(true);")
            return True
        except Exception as e:
            logger.warning(f"JavaScript refresh failed: {e}")
        
        # 方法2: 使用webbrowser直接打开（会聚焦到已有标签页）
        try:
            browser = webbrowser.get() # 获取系统默认浏览器控制器
            if hasattr(browser, 'open_new_tab'):
                browser.open_new_tab(url)  # 大多数浏览器会聚焦到已有标签页
                return True
        except Exception as e:
            logger.error(f"Browser refresh failed: {e}")
        
        return False

    def generate_allure_report(self) -> bool:
        """生成 Allure 报告（自动保留历史数据）"""
        try:
            # # 1. 复制旧报告的 history 到新结果目录
            old_history_dir = Path(self.report_dir) / "history"
            new_history_dir = Path(self.allure_results) / "history"
            
            if old_history_dir.exists():
                shutil.rmtree(new_history_dir, ignore_errors=True)
                shutil.copytree(old_history_dir, new_history_dir)
                logger.info(f"复制历史数据: {old_history_dir} → {new_history_dir}")
            else:
                logger.warning("无旧报告 history 目录，可能首次运行？")

            # 2. 生成报告（--clean 会清理报告目录，但 history 已提前复制）
            cmd = [
                self.allure_path,
                "generate",
                self.allure_results,
                "-o",
                self.report_dir,
                "--clean"
            ]
            logger.info("正在整理报告目录，生成Allure报告.....")
            subprocess.run(cmd, check=True, timeout=300)
            
            logger.info("Allure 报告生成成功，History已更新")
        except Exception as e:
            logger.error(f"生成报告失败: {e}")


    def _handle_allure_report(self) -> bool:
        """Handle Allure report serving and browser opening."""
        if  self.is_server_running():
            logger.info("Refreshing existing Allure report tab...")
            if not self.refresh_browser_tab():
                logger.info("Opening new report...")
                webbrowser.open(f"http://localhost:{self.port}")
        else:
            logger.info("Starting new Allure server...")
            self.start_server()
    def run(self):
        # 2. 生成报告数据
        self.generate_allure_report()

        # 3. 启动Allure服务
        self._handle_allure_report()
        logger.info(f"http://localhost:{self.port}")
        return 0


class PytestRunner:
    def __init__(self, args,pytest_args):
        """直接存储args对象"""
        self.args = args
        self.pytest_args = pytest_args
        self.allure_results = str(Path.cwd().joinpath("allure_results"))

        

    def run(self) -> bool:
        """执行pytest测试"""  
        # 构建基础命令列表
        base_cmd = [
            "-m", self.args.service.split('_')[0],
            "--env", self.args.env,
            "--app", self.args.app,
            "--service", self.args.service,
            "--project", self.args.project,
            "--alluredir", self.allure_results
        ]
        cmd = base_cmd + self.pytest_args

        try:
            # logger.info(f"run_pytest_tests Executing: {' '.join(cmd)}")
            # 设置环境变量（供pytest使用）
            import os
            os.environ["PROJECT"] = self.args.project
            os.environ["SERVICE"] = self.args.service
            # 调用 pytest
            pytest.main(cmd)
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
        return 0
    

if __name__ == "__main__":
    try:
        """解析核心参数，返回剩余参数给 pytest"""
        parser = argparse.ArgumentParser(description="运行测试并生成Allure报告")
        
        # pytest参数
        pytest_group = parser.add_argument_group('pytest参数')
        pytest_group.add_argument("--env", help="测试环境")
        pytest_group.add_argument("--app", help="应用名称")
        pytest_group.add_argument("--service", help="服务名称")
        pytest_group.add_argument("--project", help="项目名称")
        
        # allure参数
        allure_group = parser.add_argument_group('allure参数')
        allure_group.add_argument("--report", action="store_true", help="生成Allure报告")
        allure_group.add_argument("--allure-port", type=int, default=8883, dest="port", help="Allure报告端口")
        allure_group.add_argument("--allure-dir", default="allure_report", dest="report_dir", help="报告输出目录")
        
        args, remaining_args = parser.parse_known_args()
        
        # 参数使用说明
        # pytest参数: args.env, args.app, args.service, args.project + remaining_args
        # allure参数: args.port, args.report_dir
        
        if args.report:
            logger.info("Allure操作开始...")
            allure_runner = AllureRunner(args)
            result = allure_runner.run()
        else:
            # 验证pytest必要参数
            if not all([args.env, args.app, args.service, args.project]):
                parser.error("执行测试需要提供 --env, --app, --service, --project 参数")
            
            logger.info("开始执行pytest测试...")
            test_runner = PytestRunner(args, remaining_args)
            result = test_runner.run()
        
        exit(result)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        exit(1)  