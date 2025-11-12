import shutil
from pathlib import Path


def configure_parser(parser):
    """配置子命令参数"""
    parser.add_argument("project_name", help="项目名称")
    parser.add_argument("-t", "--template", 
                       choices=["basic", "advanced"], 
                       default="basic")
    parser.add_argument("--force", action="store_true", 
                       help="覆盖已存在目录")

def execute(args,others):
    """执行项目创建"""
    template_dir = Path(__file__).parent.parent / "templates" / args.template
    target_dir = Path.cwd() / args.project_name
    
    if target_dir.exists():
        if not args.force:
            raise FileExistsError(f"目录已存在: {target_dir}")
        shutil.rmtree(target_dir)
    
    shutil.copytree(template_dir, target_dir)
    print(f"项目创建成功: {target_dir}")

# 注册到主CLI
func = execute