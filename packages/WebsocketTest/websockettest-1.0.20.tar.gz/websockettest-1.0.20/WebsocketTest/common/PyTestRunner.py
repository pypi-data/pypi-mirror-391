from functools import cached_property
from WebsocketTest.common.utils import *
import allure
from pathlib import Path
from WebsocketTest.common.Assertion import Assert
import pytest
import traceback
class PyTestRunner:
    # 定义需要子类实现的属性
    TEST_TYPE = "API自动化测试"  # 默认值，可被子类覆盖
    CASE_PATH = Path.cwd().resolve().joinpath("data/case_data.xlsx")
    

    @cached_property
    def API_TEST_RUNNER_CLASS(self):
        """动态加载对应的测试运行器类（自动缓存）"""
        class_prefix = self.__class__.__name__[4:]  # TestGateway -> Gateway
        module_path = f"WebsocketTest.caseScript.{class_prefix}"
        
        try:
            module = __import__(module_path, fromlist=['ApiTestRunner'])
            return module.ApiTestRunner
        except ImportError as e:
            raise ImportError(
                f"无法加载 {module_path}.ApiTestRunner，"
                "请检查模块路径和类命名是否符合规范"
            ) from e
    
    SHEET_NAME = f"{os.getenv('PROJECT')}-{os.getenv('SERVICE')}"
    @pytest.mark.parametrize('case', gen_case_suite(CASE_PATH,sheet_name=SHEET_NAME))
    def test(self, case, setup_env):
        """测试用例执行模板"""
        try:
            # 1. 合并参数
            params = merge_dicts(case, setup_env)
            
            # 2. 执行测试
            runner = self.API_TEST_RUNNER_CLASS(**params)
            runner.run()
            
            # 3. 记录报告数据
            self._record_allure_report(runner)
            
            # 4. 执行断言，并记录断言结果
            self._execute_assertions(runner)
            
        except Exception as e:
            self._record_error(e)
            # logger.error(f"Case failed: {str(e)}")
            pytest.fail(f"Case failed: {str(e)}")
    
    def _record_allure_report(self, runner):
        """记录Allure测试报告"""
        allure.dynamic.epic(
            f"【{runner.env}】"
            f"【{runner.project}】"
            f"【{runner.service}】"
            f"{self.TEST_TYPE}"
        )
        allure.dynamic.story(runner.appId + " - " +runner.app)
        allure.attach(runner.url, 'URL', allure.attachment_type.URI_LIST)
        allure.attach(
            f"{convert_to_json(runner.request)}", 
            'API请求', 
            allure.attachment_type.JSON
        )
        allure.attach(
            f"{convert_to_json(runner.response)}", 
            'API响应', 
            allure.attachment_type.JSON
        )
    def _execute_assertions(self, runner):
        """执行断言逻辑"""
        with allure.step(f'【断言】{runner.number}_{runner.casename}'):
            Assert(runner.request, runner.response, runner.UniversalAssert,runner.ArrayAssert,runner.URLAssert)
    def _record_error(self, error):
        """记录测试错误信息"""
        allure.attach(
            str(error),
            '异常信息',
            allure.attachment_type.TEXT
        )
        allure.attach(
            traceback.format_exc(),
            '异常堆栈',
            allure.attachment_type.TEXT
        )