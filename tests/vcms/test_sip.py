


import requests
import json
from typing import Dict, Any
import hashlib
from collections import OrderedDict
import time
from typing import List, Optional
from decimal import Decimal

api_app_key="7d71382be017cf4002d25bd14ca36a97"
api_app_secret = "97b3c76de8b4ddcd713040844f563221"
x_client_id='2ed2415237a65e0d5f0b6c0e4cbb8bc3'
api_url = "https://vcms-api-third.opentide.com.cn/third/sip/brief/receive-qt"



class UploadedFile:
    """
    文件路径
    """
    def __init__(self, flag: Optional[str] = None, url: Optional[str] = None, salt: Optional[str] = None):
        # SIP file 分类
        self.flag = flag
        # 文件路径
        self.url = url
        # 文件唯一标识
        self.salt = salt

class QtDetail:
    """
    报价明细
    """
    def __init__(self, 
                 qtGroupCode: Optional[str] = None,
                 qtGroupName: Optional[str] = None,
                 qtItemCode: Optional[str] = None,
                 qtItemName: Optional[str] = None,
                 qtItemSpecial: Optional[str] = None,
                 qtItemStyle: Optional[str] = None,
                 qtItemDesc: Optional[str] = None,
                 qtItemUnit: Optional[str] = None,
                 qtItemQty: Optional[Decimal] = None,
                 qtItemQty1: Optional[Decimal] = None,
                 qtItemPrice: Optional[Decimal] = None,
                 qtItemPriceStandard: Optional[Decimal] = None,
                 qtItemRemark: Optional[str] = None,
                 qtTplItemRemark: Optional[str] = None,
                 serviceTaxRate: Optional[Decimal] = None,
                 isGroup: Optional[bool] = None,
                 qtItemRegion: Optional[str] = None):
        # 分组编码
        self.qtGroupCode = qtGroupCode
        # 分组名称
        self.qtGroupName = qtGroupName
        # 条目编码
        self.qtItemCode = qtItemCode
        # 条目名称
        self.qtItemName = qtItemName
        # 规格&参数
        self.qtItemSpecial = qtItemSpecial
        # 工艺&风格
        self.qtItemStyle = qtItemStyle
        # 详细描述
        self.qtItemDesc = qtItemDesc
        # 计量单位
        self.qtItemUnit = qtItemUnit
        # 数量1
        self.qtItemQty = qtItemQty
        self.qtItemQty1 = qtItemQty1
        # 单价
        self.qtItemPrice = qtItemPrice
        # 单价
        self.qtItemPriceStandard = qtItemPriceStandard
        # 备注
        self.qtItemRemark = qtItemRemark
        # 模板备注
        self.qtTplItemRemark = qtTplItemRemark
        # 服务税率
        self.serviceTaxRate = serviceTaxRate
        # 是否为报价组
        self.isGroup = isGroup
        # 区域
        self.qtItemRegion = qtItemRegion

class SipBriefDetail:
    """
    SIP简报详情
    """
    def __init__(self,
                 company: Optional[str] = None,
                 dept: Optional[str] = None,
                 jobNo: Optional[str] = None,
                 jobSubject: Optional[str] = None,
                 jobType: Optional[str] = None,
                 docNo: Optional[str] = None,
                 briefNo: Optional[str] = None,
                 briefSubject: Optional[str] = None,
                 briefType: Optional[str] = None,
                 briefCurrency: Optional[str] = None,
                 qtType: Optional[str] = None,
                 qtOpening: Optional[bool] = None,
                 vendorNo: Optional[str] = None,
                 vendorName: Optional[str] = None,
                 briefCreator: Optional[str] = None,
                 jobCreator: Optional[str] = None,
                 jobStartDate: Optional[str] = None,
                 jobEndDate: Optional[str] = None,
                 briefEndTime: Optional[str] = None,
                 qtDetails: Optional[List[QtDetail]] = None,
                 attaches: Optional[List[UploadedFile]] = None,
                 vendorUserName: Optional[str] = None,
                 vendorUserEmail: Optional[str] = None,
                 business: Optional[str] = None,
                 branch: Optional[str] = None,
                 agency: Optional[str] = None,
                 knoxId: Optional[str] = None):
        # 法人
        self.company = company
        # 部门
        self.dept = dept
        # Job编号
        self.jobNo = jobNo
        # Job名称
        self.jobSubject = jobSubject
        # Job类型
        self.jobType = jobType
        # 文书编号
        self.docNo = docNo
        # Brief编号
        self.briefNo = briefNo
        # Brief标题
        self.briefSubject = briefSubject
        # Brief类型
        self.briefType = briefType
        # Brief货币
        self.briefCurrency = briefCurrency
        # 报价类型
        self.qtType = qtType
        # 报价是否开放
        self.qtOpening = qtOpening
        # 供应商编号
        self.vendorNo = vendorNo
        # 供应商名称
        self.vendorName = vendorName
        # Brief创建人
        self.briefCreator = briefCreator
        # Job创建人
        self.jobCreator = jobCreator
        # Job开始日期
        self.jobStartDate = jobStartDate
        # Job结束日期
        self.jobEndDate = jobEndDate
        # Brief结束日期
        self.briefEndTime = briefEndTime
        # 报价明细
        self.qtDetails = qtDetails if qtDetails is not None else []
        # 文件路径数组
        self.attaches = attaches if attaches is not None else []
        # 用户名
        self.vendorUserName = vendorUserName
        # 邮箱
        self.vendorUserEmail = vendorUserEmail
        # sip 业务分类
        self.business = business
        # sip 分公司
        self.branch = branch
        # sip 分公司-办事处
        self.agency = agency
        # knoxId
        self.knoxId = knoxId

    def to_dict(self):
        """
        将对象转换为字典
        """
        data = {}
        if self.company is not None:
            data['company'] = self.company
        if self.dept is not None:
            data['dept'] = self.dept
        if self.jobNo is not None:
            data['jobNo'] = self.jobNo
        if self.jobSubject is not None:
            data['jobSubject'] = self.jobSubject
        if self.jobType is not None:
            data['jobType'] = self.jobType
        if self.docNo is not None:
            data['docNo'] = self.docNo
        if self.briefNo is not None:
            data['briefNo'] = self.briefNo
        if self.briefSubject is not None:
            data['briefSubject'] = self.briefSubject
        if self.briefType is not None:
            data['briefType'] = self.briefType
        if self.briefCurrency is not None:
            data['briefCurrency'] = self.briefCurrency
        if self.qtType is not None:
            data['qtType'] = self.qtType
        if self.qtOpening is not None:
            data['qtOpening'] = self.qtOpening
        if self.vendorNo is not None:
            data['vendorNo'] = self.vendorNo
        if self.vendorName is not None:
            data['vendorName'] = self.vendorName
        if self.briefCreator is not None:
            data['briefCreator'] = self.briefCreator
        if self.jobCreator is not None:
            data['jobCreator'] = self.jobCreator
        if self.jobStartDate is not None:
            data['jobStartDate'] = self.jobStartDate
        if self.jobEndDate is not None:
            data['jobEndDate'] = self.jobEndDate
        if self.briefEndTime is not None:
            data['briefEndTime'] = self.briefEndTime
        if self.qtDetails is not None:
            data['qtDetails'] = [qt_detail.__dict__ for qt_detail in self.qtDetails]
        if self.attaches is not None:
            data['attaches'] = [attach.__dict__ for attach in self.attaches]
        if self.vendorUserName is not None:
            data['vendorUserName'] = self.vendorUserName
        if self.vendorUserEmail is not None:
            data['vendorUserEmail'] = self.vendorUserEmail
        if self.business is not None:
            data['business'] = self.business
        if self.branch is not None:
            data['branch'] = self.branch
        if self.agency is not None:
            data['agency'] = self.agency
        if self.knoxId is not None:
            data['knoxId'] = self.knoxId
        return data

def build_headers(
    x_app_key: str,
    x_language: str,
    x_client_id: str,
    x_timestamp: str,
    sign: str
) -> Dict[str, str]:
    """构建请求头"""
    headers = {
        "X-App-Key": x_app_key,
        "X-Language": x_language,
        "X-Vendor-Code": None,
        "X-Token": "",
        "X-Client-Id": x_client_id,
        "X-Timestamp": x_timestamp,
        "X-Signature": sign,
        "Content-Type": "application/json"
    }
    return headers
def build_request_body(
                briefSubject:str,
                briefNo:str,
                eBiddingTime:str="2025-09-11T03:14:43.9659213Z",
                endTime:str="2025-09-30T03:03:31Z",
                       ) -> SipBriefDetail:
    """构建请求体"""
    def custom_object_hook(d):
        # 如果是 UploadedFile 对象
        if 'flag' in d or 'url' in d or 'salt' in d:
            return UploadedFile(**d)
        # 如果是 QtDetail 对象
        elif 'qtItemCode' in d or 'qtItemName' in d:
            return QtDetail(**d)
        # 其他情况直接返回字典
        return d
    
    with open('sip_data.json', 'r', encoding='utf-8') as file:
        data_dict  = json.load(file, object_hook=custom_object_hook)
    
        # 创建 SipBriefDetail 对象
    data = SipBriefDetail()
    
    # 将从文件加载的数据赋值给对象属性
    for key, value in data_dict.items():
        if hasattr(data, key):
            setattr(data, key, value)
    
    # 更新特定字段
    data.briefSubject = briefSubject
    data.briefNo = briefNo
    data.jobStartDate = eBiddingTime
    data.briefEndTime = endTime
    return data

 

def generate_signature(params:Any, data: Any, 
                      x_app_key: str, x_language: str, x_client_id: str, 
                      x_timestamp: str, api_app_secret: str) -> str:
    """
    生成API签名
    
    Args:
        params: 参数字典
        data: 数据对象
        x_app_key: 应用密钥
        x_language: 语言设置
        x_client_id: 客户端ID
        x_timestamp: 时间戳
        api_app_secret: API应用密钥
    
    Returns:
        str: 生成的MD5签名
    """
    # 创建有序字典（相当于Java的TreeMap）
    tree_map = OrderedDict()
    tree_map["appKey"] = x_app_key
    tree_map["clientId"] = x_client_id
    if data:
        tree_map["data"] = json.dumps(data, ensure_ascii=True, separators=(', ', ': '))
    tree_map["language"] = x_language
    if params:
        tree_map["params"] = json.dumps(params, ensure_ascii=True, separators=(', ', ': '))
    else:
        tree_map["params"] = '{}'
    tree_map["timestamp"] = x_timestamp
    tree_map["token"] = ""
  

 
    
    # 拼接签名源数据
    source_signature_parts = []
    for key, value in tree_map.items():
        try:
            source_signature_parts.append(f"{key}={value}")
        except Exception:
            # 如果出现异常，跳过该键值对
            continue
    
    # 构建完整的签名源字符串
    source_signature_str = "&".join(source_signature_parts)
    full_signature_str = f"{api_app_secret}{source_signature_str}&{api_app_secret}"
    
    # 转换为小写
    full_signature_str = full_signature_str.lower()
    print(f"签名源字符串: {full_signature_str}")
    
    # 使用MD5加密并转换为大写
    md5_hash = hashlib.md5(full_signature_str.encode('utf-8'))
    md5_signature = md5_hash.hexdigest().upper()
    
    return md5_signature

def send_request_with_requests(
                               briefSubject:str,
                               briefNo:str,
                               endTime:str,
                
                               ) -> requests.Response:
    """使用requests库发送POST请求"""
    x_timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())

    print(f"请求时间戳: {x_timestamp}")

    eBiddingTime=time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

    data = build_request_body(
        briefSubject=briefSubject,
        briefNo=briefNo,
        eBiddingTime=eBiddingTime,
        endTime=endTime,
        
        
    )
    params = {}
    sign= generate_signature(params, data.to_dict(),
                       api_app_key,
                       "zh-CN",
                       x_client_id,
                       x_timestamp,
                       api_app_secret)
    headers = build_headers(api_app_key,
                            "zh-CN",
                             x_client_id,
                            x_timestamp,
                            sign
                            )
    
    try:
        print("data.to_dict",json.dumps(data.to_dict(), ensure_ascii=True, separators=(', ', ': ')))
        response = requests.post(
            url=api_url,
            headers=headers,
            json=data.to_dict(),
            timeout=3000
        )
        return response
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        raise

def send_sip(briefSubject:str,briefNo:str,endTime:str,syncType:str="ebidding_create"):
    try:
        response = send_request_with_requests(
            briefSubject=briefSubject,
            briefNo=briefNo,
            endTime=endTime,
        )
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析后的JSON响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":

        briefSubject="SIP测试"+time.strftime("%Y%m%d%H%M%S",time.gmtime())
        briefNo="SIP"+time.strftime("%Y%m%d%H%M%S",time.gmtime())
        endTime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()+15*24*3600))
        send_sip(briefSubject,briefNo,endTime)
 
        
     