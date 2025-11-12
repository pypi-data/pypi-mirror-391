"""
pytest 配置文件
统一配置测试环境和fixtures
"""

import pytest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.test_base import TestBase

@pytest.fixture(scope="session")
def test_base():
    """提供全局测试基础实例"""
    return TestBase()

@pytest.fixture
def test_client(test_base):
    """提供测试客户端实例"""
    return test_base.open_client