"""
报表相关的API请求和响应模型
"""
from .base import BaseRequest, BaseResponse


# ===== 生产单报表 =====

class ProduceOrderDTO:
    """生产单查询条件"""
    
    def __init__(self, orders_sn=None,
                 business_time_begin=None,
                 business_time_end=None,
                 state_list=None,
                 ):
        self.orders_sn = orders_sn  # 单号
        self.business_time_begin = business_time_begin  # 单号
        self.business_time_end = business_time_end  # 单号
        self.state_list = state_list  # 单号

    def to_dict(self):
        return {
            'ordersSn': self.orders_sn,
            'businessTimeBegin':self.business_time_begin,
            'businessTimeEnd':self.business_time_end,
            'stateList':self.state_list,
        }


class ProduceDetailReportListRequest(BaseRequest):
    """生产单明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.produce = None  # ProduceOrderDTO
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/produce/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceDetailReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.produce:
            body['produce'] = self.produce.to_dict()
        return body


class ProduceDetailReportListResponse(BaseResponse):
    """生产单明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


class ProduceWorkProcessListRequest(BaseRequest):
    """生产单工序列表请求"""
    
    def __init__(self):
        super().__init__()
        self.produce = None  # ProduceOrderDTO
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/produce/workprocess/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return ProduceWorkProcessListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.produce:
            body['produce'] = self.produce.to_dict()
        return body


class ProduceWorkProcessListResponse(BaseResponse):
    """生产单工序列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 商品工序报表 =====

class GoodsWorkProcessDetailListRequest(BaseRequest):
    """商品工序明细列表请求"""
    
    def __init__(self):
        super().__init__()
        self.goods_ids = None  # 商品id集合（必填）
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/goods/workprocess/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return GoodsWorkProcessDetailListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size,
            "goodsIds": self.goods_ids
        }
        return body


class GoodsWorkProcessDetailListResponse(BaseResponse):
    """商品工序明细列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 薪资计件报表 =====

class SalaryDetailReportListRequest(BaseRequest):
    """薪资计件明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.business_begin_time = None  # 业务起始时间（必填）
        self.business_end_time = None  # 业务结束时间（必填）
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/salary/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return SalaryDetailReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size,
            "businessBeginTime": self.business_begin_time,
            "businessEndTime": self.business_end_time
        }
        return body


class SalaryDetailReportListResponse(BaseResponse):
    """薪资计件明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 采购单报表 =====

class MaterialPurchaseDetailReportListRequest(BaseRequest):
    """物料采购明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.purchase_orders_sn = None  # 采购单号
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/material/purchase/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialPurchaseDetailReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        if self.purchase_orders_sn:
            body['purchaseOrdersSn'] = self.purchase_orders_sn
        return body


class MaterialPurchaseDetailReportListResponse(BaseResponse):
    """物料采购明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 领料单报表 =====

class MaterialPickDetailReportListRequest(BaseRequest):
    """领料单明细报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.page = 1
        self.size = 10

    def get_api_url(self):
        return "api/open/report/pick/detail/list"

    def get_version(self):
        return "1.0"
    
    def response_class(self):
        return MaterialPickDetailReportListResponse

    def get_request_body(self):
        return {
            "page": self.page,
            "size": self.size
        }


class MaterialPickDetailReportListResponse(BaseResponse):
    """领料单明细报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []


# ===== 商品入库报表 =====

class GoodsStoreInReportListRequestDTO:
    """商品入库报表查询参数DTO"""
    
    def __init__(self, search_key=None, query_produce=None, produce_key=None, business_time_begin=None, 
                 business_time_end=None, goods_ids=None, storehouse_ids=None, handler_ids=None, 
                 client_ids=None, supplier_ids=None, remark=None):
        self.search_key = search_key  # 搜索关键字
        self.query_produce = query_produce  # 查询生产单
        self.produce_key = produce_key  # 生产单关键字
        self.business_time_begin = business_time_begin  # 业务开始时间
        self.business_time_end = business_time_end  # 业务结束时间
        self.goods_ids = goods_ids  # 商品ID集合
        self.storehouse_ids = storehouse_ids  # 仓库ID集合
        self.handler_ids = handler_ids  # 创建人ID集合
        self.client_ids = client_ids  # 客户ID集合
        self.supplier_ids = supplier_ids  # 加工厂ID集合
        self.remark = remark  # 备注关键字

    def to_dict(self):
        result = {}
        
        if self.search_key is not None:
            result['searchKey'] = self.search_key
            
        if self.query_produce is not None:
            result['queryProduce'] = self.query_produce
            
        if self.produce_key is not None:
            result['produceKey'] = self.produce_key
            
        if self.business_time_begin is not None:
            result['businessTimeBegin'] = self.business_time_begin
            
        if self.business_time_end is not None:
            result['businessTimeEnd'] = self.business_time_end
            
        if self.goods_ids is not None:
            result['goodsIds'] = self.goods_ids
            
        if self.storehouse_ids is not None:
            result['storehouseIds'] = self.storehouse_ids
            
        if self.handler_ids is not None:
            result['handlerIds'] = self.handler_ids
            
        if self.client_ids is not None:
            result['clientIds'] = self.client_ids
            
        if self.supplier_ids is not None:
            result['supplierIds'] = self.supplier_ids
            
        if self.remark is not None:
            result['remark'] = self.remark
            
        return result


class GoodsStoreInReportListRequest(BaseRequest):
    """商品入库报表列表请求"""
    
    def __init__(self):
        super().__init__()
        self.request = None  # GoodsStoreInReportListRequestDTO
        self.page = 1
        self.size = 10
        self.order_by_list = None  # 排序列表

    def get_api_url(self):
        return "api/open/report/goods/storein/list"

    def get_version(self):
        return "1.3"
    
    def response_class(self):
        return GoodsStoreInReportListResponse

    def get_request_body(self):
        body = {
            "page": self.page,
            "size": self.size
        }
        
        if self.request is not None:
            body['request'] = self.request.to_dict()
            
        if self.order_by_list is not None:
            body['orderByList'] = self.order_by_list
            
        return body


class GoodsStoreInReportListResponse(BaseResponse):
    """商品入库报表列表响应"""
    
    def __init__(self, response_data=None):
        super().__init__(response_data)
        if response_data and 'data' in response_data:
            self.data = response_data['data']
        else:
            self.data = []
