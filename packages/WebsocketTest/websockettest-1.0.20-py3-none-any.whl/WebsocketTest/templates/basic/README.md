# WebSocket 接口自动化测试工具 (WebSocketTest)

#### 介绍

这是一个基于 WebSocket 协议的接口自动化测试工具。它可以用于自动化测试 WebSocket 接口，确保接口的稳定性和可靠性。

#### 系统要求

**Python 3.10+**：确保你的系统上已经安装了 Python 3.10（推荐使用最新稳定版）。


#### 安装步骤

**1.安装 Python：**
确保你的系统上已经安装了 Python 3.10 或更高版本。你可以从 [Python 官方网站 ](https://www.python.org/downloads/?spm=5176.28103460.0.0.40f75d27PnqPkU)下载并安装。
**2.安装 WebSocketTest 工具：**

```
pip install WebsocketTest
```

**3.安装allure 工具：**
```
install-allure
<!-- 注：allure安装完，会自动配置环境变量，需要重启终端才能生效 -->
```
**4.创建测试项目：**
```
<!-- 一次性操作，yourtestProject创建成功以后，测试直接cd到yourtestProject下，进行ws test -->
ws startproject yourtestProject
cd yourtestProject
```

**5.运行测试：**
  在命令行中运行以下命令：

```
<!-- 安徽5.0链路aqua测试： -->
ws test --env uat --app vwa5.0  --service aqua --project vwa
ws test --env live --app vwa5.0  --service aqua --project vwa
ws test --env uat --app meb4.0  --service aqua --project vwa

<!-- 安徽5.4链路sds_gateway测试： -->
ws test --env uat --app ids5.4  --service gateway_5.4 --project vwa
ws test --env live --app ids5.4  --service gateway_5.4 --project vwa
<!-- 安徽5.0链路sds_gateway测试： -->
ws test --env uat --app vwa5.0  --service gateway_5.0 --project vwa
ws test --env live --app vwa5.0  --service gateway_5.0 --project vwa
<!-- 奥迪aqua测试： -->
ws test --env uat --app audipp  --service aqua --project audi
ws test --env live --app audipp  --service aqua --project audi
<!-- 上汽5.0链路sds_gateway测试： -->
ws test --env uat --app gp  --service gateway_5.0 --project svw
ws test --env live --app gp  --service gateway_5.0 --project svw
<!-- 上汽5.0链路aqua测试： -->
ws test --env uat --app abcar  --service aqua --project svw
ws test --env live --app abcar  --service aqua --project svw


<!-- 指定Gatewaycase -->
ws test --env uat --app ids5.4  --service gateway_5.4 --project vwa  testcase/testAll.py::TestGateway::test[case0]
<!-- 指定Aquacase -->
ws test --env uat --app vwa5.0  --service aqua --project vwa  testcase/testAll.py::TestAqua::test[case0]
<!-- --reruns 2失败的所有用例自动重跑2次 （不加默认不会重跑） -->
 ... --reruns 2
<!-- reruns-delay 重跑间隔1s，(不加默认0s) -->
... --reruns-delay 1
```
**6.清空历史报告数据：**
直接清空yourtestProject\allure_results

#### 其他
```
<!-- 本地开发模式调试 -->
pip install -e . 

<!-- 打包 -->
python setup.py sdist bdist_wheel
<!-- 上传 -->
twine upload --repository pypi setup_temp/dist/*
<!-- 卸载 -->
pip uninstall WebsocketTest
<!-- 安装 -->
pip install WebsocketTest==1.0.14

<!-- 关闭allure进程 -->
netstat -ano | findstr "8883"
taskkill  /F /PID xxID

<!-- 安装虚拟环境 -->
python -m venv venv   
<!-- 激活venv虚拟环境 -->
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\venv\Scripts\Activate.ps1
<!-- 退出venv -->
deactivate
```