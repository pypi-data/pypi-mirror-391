from setuptools import find_packages, setup
from setuptools.command.sdist import sdist
from setuptools.command.bdist_wheel import bdist_wheel
# 自定义安装命令
from setuptools.command.install import install
import sys
class CustomSdist(sdist):
    def initialize_options(self):
        super().initialize_options()
        self.dist_dir = "setup_temp/dist"

class CustomBdistWheel(bdist_wheel):
    def initialize_options(self):
        super().initialize_options()
        self.dist_dir = "setup_temp/dist"
class PostInstallCommand(install):
    def run(self):
        install.run(self)
        check_and_install_allure()
# Allure检查安装逻辑（独立模块）
def check_and_install_allure():
    try:
        from WebsocketTest.allure_installer import ensure_allure
        ensure_allure()
    except Exception as e:
        print(f"⚠️ Allure安装失败: {e}", file=sys.stderr)
setup(
    cmdclass={
        'install': PostInstallCommand,
        'sdist': CustomSdist,
        'bdist_wheel': CustomBdistWheel
    },
    name="WebsocketTest",
    version="1.0.20",
    packages=find_packages(exclude=[
        "WebsocketTest.allure_report", 
        "WebsocketTest.logs", 
        "WebsocketTest.allure_results",  
        "WebsocketTest.config", 
        "WebsocketTest.data",
        "WebsocketTest.testcase"
    ]),
    include_package_data=True,  # 这行很重要，会读取MANIFEST.in
    description="websocket api autotest",
    install_requires = [
        "allure-pytest>=2.13.5",
        "pandas>=2.2.3",
        "pytest>=8.2.2",
        "PyYAML>=6.0.2",
        "websockets>=12.0",
        "pytest-rerunfailures>=15.0"
    ],
    entry_points={
        'console_scripts': [
            "ws=WebsocketTest.cli:main",
            'install-allure=WebsocketTest.allure_installer:ensure_allure'
        ]
    }
)
# import shutil
# # # 清理 .egg-info 文件夹
# shutil.rmtree('WebsocketTest.egg-info', ignore_errors=True)