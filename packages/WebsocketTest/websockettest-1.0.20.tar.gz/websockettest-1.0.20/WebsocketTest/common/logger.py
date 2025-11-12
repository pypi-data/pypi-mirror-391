import logging

# 配置全局日志记录设置
# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
    ]
)
# 创建一个记录器实例
logger = logging.getLogger()