"""
品牌保存测试
对应Java版本：BlandSaveRequestTest.java
"""
import pytest

from qinsilk_scm_openapi_sdk_py.models.brand import BrandSaveRequest, BrandSaveDTO
from .test_base import TestBase


class TestBrandSave(TestBase):
    """品牌保存测试类"""
    
    def test_add_brand(self):
        """
        测试添加品牌
        对应Java版本：testAddBland()方法
        """
        # 创建品牌保存请求
        request = BrandSaveRequest()
        
        # 生成随机数用于测试数据
        num = self.generate_random_number()
        
        # 设置品牌保存DTO
        brand_save_dto = BrandSaveDTO()
        brand_save_dto.name = f"测试品牌{num}"
        brand_save_dto.bland_code = f"TEST{num}"
        brand_save_dto.logo_url = "https://example.com/logo.png"
        brand_save_dto.description = "测试品牌描述"
        brand_save_dto.url = "https://example.com"
        brand_save_dto.show_order = 100
        brand_save_dto.is_show = 1
        brand_save_dto.is_default = 0
        request.brand_save_dto = brand_save_dto
        
        # 执行请求
        http_request, response = self.execute_request(request)
        
        # 断言请求成功
        self.assert_response_code(response, "0")
        
        # 生成新的随机数进行二次测试（对应Java版本的行为）
        num = self.generate_random_number()
        brand_save_dto.name = f"测试品牌{num}"
        brand_save_dto.bland_code = f"TEST{num}"
        
        print(f"品牌保存测试完成，品牌代码: {brand_save_dto.bland_code}")


# 提供测试实例的fixture
@pytest.fixture
def brand_save_test():
    """提供品牌保存测试实例的fixture"""
    return TestBrandSave()


# 集成测试函数
def test_brand_save_integration(brand_save_test):
    """集成测试：品牌保存完整流程"""
    brand_save_test.test_add_brand()


if __name__ == '__main__':
    # 直接运行测试
    test_instance = TestBrandSave()
    test_instance.test_add_brand()
    print("✅ 品牌保存测试通过")