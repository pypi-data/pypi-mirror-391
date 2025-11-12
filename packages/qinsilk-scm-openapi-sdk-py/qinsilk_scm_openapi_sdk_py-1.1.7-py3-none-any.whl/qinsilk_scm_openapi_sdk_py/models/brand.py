"""
品牌相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


class BrandSaveDTO:
    """品牌保存数据传输对象"""
    
    def __init__(self, name=None, bland_code=None, logo_url=None, description=None, url=None, 
                 show_order=None, status=None, is_show=None, is_default=None, remark=None):
        self.name = name  # 名称（必填）
        self.bland_code = bland_code  # 品牌代码（必填）
        self.logo_url = logo_url  # 品牌商标url
        self.description = description  # 品牌描述
        self.url = url  # 官网
        self.show_order = show_order  # 排序
        self.status = status  # 启用状态，1-启用，0-不启用
        self.is_show = is_show  # 是否显示，1-显示，0-不显示
        self.is_default = is_default  # 是否默认，1：是，0否（必填）
        self.remark = remark  # 备注

    def to_dict(self):
        return {
            'name': self.name,
            'blandCode': self.bland_code,
            'logoUrl': self.logo_url,
            'description': self.description,
            'url': self.url,
            'showOrder': self.show_order,
            'status': self.status,
            'isShow': self.is_show,
            'isDefault': self.is_default,
            'remark': self.remark
        }


class BrandUpdateDTO:
    """品牌更新数据传输对象"""
    
    def __init__(self, id=None, name=None, bland_code=None, logo_url=None, description=None, url=None, 
                 show_order=None, status=None, is_show=None, is_default=None, remark=None):
        self.id = id  # 品牌ID（必填）
        self.name = name  # 名称
        self.bland_code = bland_code  # 品牌代码
        self.logo_url = logo_url  # 品牌商标url
        self.description = description  # 品牌描述
        self.url = url  # 官网
        self.show_order = show_order  # 排序
        self.status = status  # 启用状态，1-启用，0-不启用
        self.is_show = is_show  # 是否显示，1-显示，0-不显示
        self.is_default = is_default  # 是否默认，1：是，0否
        self.remark = remark  # 备注

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'blandCode': self.bland_code,
            'logoUrl': self.logo_url,
            'description': self.description,
            'url': self.url,
            'showOrder': self.show_order,
            'status': self.status,
            'isShow': self.is_show,
            'isDefault': self.is_default,
            'remark': self.remark
        }


class BrandDetail:
    """品牌详情"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.brand_code = data.get('blandCode')
        self.logo_url = data.get('logoUrl')
        self.description = data.get('description')
        self.url = data.get('url')
        self.show_order = data.get('showOrder')
        self.status = data.get('status')
        self.is_show = data.get('isShow')
        self.is_default = data.get('isDefault')
        self.remark = data.get('remark')
        self.gmt_create = data.get('gmtCreate')
        self.gmt_modified = data.get('gmtModified')


class BrandSaveRequest(BaseRequest):
    """新增品牌请求"""
    
    def __init__(self):
        super().__init__()
        self.brand_save_dto = None

    def get_api_url(self):
        return "api/open/bland/base/add"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BrandDetailResponse

    def get_request_body(self):
        if self.brand_save_dto:
            return {"blandSaveDto": self.brand_save_dto.to_dict()}
        return {}


class BrandUpdateRequest(BaseRequest):
    """更新品牌请求"""
    
    def __init__(self):
        super().__init__()
        self.brand_update_dto = None

    def get_api_url(self):
        return "api/open/bland/base/update"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BrandDetailResponse

    def get_request_body(self):
        if self.brand_update_dto:
            return {"blandUpdateDto": self.brand_update_dto.to_dict()}
        return {}


class BrandDetailRequest(BaseRequest):
    """品牌详情请求"""
    
    def __init__(self):
        super().__init__()
        self.brand_id = None

    def get_api_url(self):
        return "api/open/bland/base/get"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BrandDetailResponse

    def get_request_body(self):
        return {"blandId": self.brand_id}


class BrandDeleteRequest(BaseRequest):
    """删除品牌请求"""
    
    def __init__(self):
        super().__init__()
        self.ids = None  # 主键集合（必填）

    def get_api_url(self):
        return "api/open/bland/base/delete"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        from .base import BaseResponse
        return BaseResponse

    def get_request_body(self):
        return {"ids": self.ids}


class BrandListRequest(BaseRequest):
    """品牌列表请求"""
    
    def __init__(self):
        super().__init__()
        self.name = None  # 品牌名称
        self.bland_code = None  # 品牌代码
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/bland/base/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return BrandListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.name:
            body["name"] = self.name
        if self.bland_code:
            body["blandCode"] = self.bland_code
        return body


class BrandDetailResponse(BaseResponse):
    """品牌详情响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = BrandDetail(response_data['data'])
        else:
            self.data = None


class BrandListResponse(BaseResponse):
    """品牌列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = [BrandDetail(item) for item in response_data['data']]
        else:
            self.data = []