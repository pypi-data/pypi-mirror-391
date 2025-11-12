import os
import sys
import zipfile
import subprocess
import winreg
from pathlib import Path
import shutil

# 配置参数
ALLURE_VERSION = "2.30.0"
PACKAGE_NAME = "WebsocketTest"  # 您的包名
LOCAL_ZIP_RELATIVE_PATH = os.path.join("libs", f"allure-{ALLURE_VERSION}.zip")  # 包内相对路径
INSTALL_DIR = os.path.expanduser("~/.allure")  # 安装到用户目录
ALLURE_BIN_DIR = os.path.join(INSTALL_DIR, f"allure-{ALLURE_VERSION}", "bin")

def is_allure_installed():
    """检查Allure是否在PATH中且版本匹配
    Returns:
        Tuple[bool, str]: (是否安装正确, 版本信息或错误消息)
    """
    # 1. 首先检查allure命令是否存在
    allure_cmd = "allure"
    if not shutil.which(allure_cmd):
        return False
    
    # 2. 获取版本信息
    try:
        result = subprocess.run(
            [allure_cmd, "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=5  # 添加超时防止卡住
        )
        installed_version = result.stdout.strip()
        
        # 3. 验证版本
        if ALLURE_VERSION not in installed_version:
            print(f"Allure版本不匹配: 已安装 {installed_version} (需要 {ALLURE_VERSION})")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        return False, f"Allure版本检查失败: {e.stderr}"
    except Exception as e:
        return False, f"检查Allure时发生意外错误: {str(e)}"

def get_local_zip_path():
    """获取ZIP文件的绝对路径（兼容开发模式和正式安装）"""
    # 正式安装模式
    try:
        from importlib.resources import files
        # Python 3.9+ 标准方式
        resource = files(PACKAGE_NAME).joinpath(LOCAL_ZIP_RELATIVE_PATH)
        if Path(str(resource)).exists():
            return str(resource)
    except Exception as e:
        pass

    # 备选搜索路径（按优先级排序）
    search_paths = [
        # 1. 当前脚本所在目录的子目录（开发模式）
        Path(__file__).parent / LOCAL_ZIP_RELATIVE_PATH,
        
        # # 2. 当前工作目录的包子目录
        Path.cwd() / PACKAGE_NAME / LOCAL_ZIP_RELATIVE_PATH,
        
        # # 3. Python安装目录下的包子目录
        Path(sys.prefix) /"Lib/site-packages" / PACKAGE_NAME / LOCAL_ZIP_RELATIVE_PATH,
        
        # # 4. 直接尝试相对路径（适用于打包后的exe等情况）
        # Path(LOCAL_ZIP_RELATIVE_PATH)
    ]
    # 回退方案：从当前工作目录查找

    for _path in search_paths:
        if os.path.exists(_path):
            return _path
    
    raise FileNotFoundError(f"Allure ZIP文件未在任何位置找到: {LOCAL_ZIP_RELATIVE_PATH}")

def install_allure():
    """从本地ZIP安装Allure"""
    try:
        zip_path = get_local_zip_path()
        print(f"🔍 找到Allure ZIP文件: {zip_path}")

        # 创建安装目录
        os.makedirs(INSTALL_DIR, exist_ok=True)
        print(f"📦 解压到: {INSTALL_DIR}")

        # 解压ZIP文件（使用更安全的提取方法）
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                # 防止Zip Slip攻击
                safe_path = os.path.join(INSTALL_DIR, *file.split('/'))
                if file.endswith('/'):
                    os.makedirs(safe_path, exist_ok=True)
                else:
                    with open(safe_path, 'wb') as f:
                        f.write(zip_ref.read(file))

        # 设置权限（特别是Linux/macOS）
        # if sys.platform != "win32":
        #     os.chmod(os.path.join(ALLURE_BIN_DIR, "allure"), 0o755)

        # 更新PATH
        add_to_user_path(ALLURE_BIN_DIR)
        return True
    except Exception as e:
        print(f"❌ 安装失败: {type(e).__name__}: {e}", file=sys.stderr)
        return False

def add_to_user_path(path):
    path = os.path.normpath(path)  # 规范化路径（去除多余的斜杠）
    """添加到用户级PATH环境变量"""
    try:
        if sys.platform == "win32":
            # Windows注册表操作
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            ) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
                if path in current_path.split(os.pathsep):
                    print(f"⏩ path中路径已存在: {path}")
                    return False
                
                new_path = f"{current_path}{os.pathsep}{path}" if current_path else path
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            # 刷新时只更新用户 PATH，不携带系统 PATH
            subprocess.run(
                f'powershell -command "[Environment]::SetEnvironmentVariable(\'Path\', \'{new_path}\', \'User\')"',
                shell=True,
                check=True
            )
            print(f"✅ 已添加PATH: {path}")
            return True
    except PermissionError:
        print("❌ 需要管理员权限！")
    except Exception as e:
        print(f"⚠️ 添加PATH失败: {e}\n请手动添加 {path} 到环境变量", file=sys.stderr)
        return False

def ensure_allure():
    """确保Allure已安装"""
    if is_allure_installed():
        print(f"✅ Allure {ALLURE_VERSION} 已安装")
        return True
    
    print("🔧 检测到Allure未安装，开始自动安装...")
    if install_allure():
        if not is_allure_installed():
            print("""
            \n⚠️ 安装成功但Allure仍未识别，可能是因为：
            1. 需要重启终端使PATH生效
            2. 尝试手动运行: {}
            """.format(os.path.join(ALLURE_BIN_DIR, "allure" + (".bat" if sys.platform == "win32" else ""))))
            return False
        print(f"✅ Allure {ALLURE_VERSION} 安装安装成功")
        return True
    else:
        print(f"""
        \n❌ 自动安装失败，请手动操作：
        1. 解压 {get_local_zip_path()} 到任意目录（推荐 {INSTALL_DIR}）
        2. 将解压后的bin目录添加到PATH:
           - Windows: 添加 {ALLURE_BIN_DIR} 到系统环境变量
           - Linux/macOS: 在~/.bashrc或~/.zshrc中添加:
             export PATH="$PATH:{ALLURE_BIN_DIR}"
        3. 运行 `allure --version` 验证
        """)
        return False

if __name__ == "__main__":
    if ensure_allure():
        sys.exit(0)
    sys.exit(1)