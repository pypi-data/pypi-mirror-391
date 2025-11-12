"""
测试常量配置
对应Java版本的 com.qinsilk.scm.openapi.sdk.util.Constant
"""
import os
from dotenv import load_dotenv

# 尝试加载环境变量
try:
    load_dotenv()
except ImportError:
    pass

# 测试常量 - 与Java版本保持一致
# API_URL = os.getenv('SCM_SERVER_URL', 'http://localhost:9000')
# # API_URL = os.getenv('SCM_SERVER_URL', 'https://devscm.qinsilk.com')
# CLIENT_ID = os.getenv('SCM_CLIENT_ID', '9c501e39e4814a88be1e3c4c78b9e93d')
# CLIENT_SECRET = os.getenv('SCM_CLIENT_SECRET', 'a0a7a451eddc43ed959f36c3c932c73f')

API_URL = os.getenv('SCM_SERVER_URL', 'https://scm.qinsilk.com')
CLIENT_ID = os.getenv('SCM_CLIENT_ID', '50f08b1c8cab4f26afea3e0653b6bca4')
CLIENT_SECRET = os.getenv('SCM_CLIENT_SECRET', 'dc14bbb92716482597fc2560a6afd81b')
HTTP_PROXY = os.getenv('HTTP_PROXY', 'http://localhost:18080')

# 测试配置
TEST_TIMEOUT = 30  # 秒
TEST_RETRY_COUNT = 3