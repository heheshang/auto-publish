


import requests
import json
from typing import Dict, Any
import hashlib
from collections import OrderedDict
import time

api_app_key="724bebf3d9079f1b18f0ea69e51fc187"
api_app_secret = "6d73acbb33f2e5b058ca2d082a09b079"
x_client_id='2ed2415237a65e0d5f0b6c0e4cbb8bc3'
api_url = "https://vcms-api-third-test.local.opentide.com.cn/third/ebidding/brief/save"
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

class BriefDetail:
    def __init__(self, 
                 briefSubject:str,
                 creator:str,
                 isQtOpening:bool,
                 dept:str,
                 eBiddingTime:str,
                 briefType:str,
                 jobNo:str,
                 briefNo:str,
                 company:str,
                 currency:str,
                 endTime:str,
                 syncType:str,
                 vendorJsonData:str,approvalData:str
                 ):
        self.briefSubject = briefSubject
        self.creator = creator
        self.isQtOpening = isQtOpening
        self.dept = dept
        self.eBiddingTime = eBiddingTime
        self.briefType = briefType
        self.jobNo = jobNo
        self.briefNo = briefNo
        self.company = company
        self.currency = currency
        self.endTime = endTime
        self.syncType = syncType
        self.vendorJsonData = vendorJsonData
        self.approvalData = approvalData
    def to_dict(self):
        """将对象转换为字典"""
        return {
            "briefSubject": self.briefSubject,
            "creator": self.creator,
            "isQtOpening": self.isQtOpening,
            "dept": self.dept,
            "eBiddingTime": self.eBiddingTime,
            "briefType": self.briefType,
            "jobNo": self.jobNo,
            "briefNo": self.briefNo,
            "company": self.company,
            "currency": self.currency,
            "endTime": self.endTime,
            "syncType": self.syncType,
            "vendorJsonData": self.vendorJsonData,
            "approvalData": self.approvalData
        }

def build_request_body(
                briefSubject:str,
                briefNo:str,
                eBiddingTime:str="2025-09-11T03:14:43.9659213Z",
                endTime:str="2025-09-30T03:03:31Z",
                syncType:str="ebidding_win",
                vendorJsonData:str="[{\"vendorName\":\"Samsung Electronics Co.,Ltd.\",\"vendorNo\":\"A0000001_L6B3\"}]",
                approvalData:str=""
                       ) -> BriefDetail:
    """构建请求体"""
    return BriefDetail(
        briefSubject,
        "T0150397",
        False,
        "EZ010445",
        eBiddingTime,
        "M0500000",
        "C7P19027002",
        briefNo,
        "LFB3",
        "CNY",
        endTime,
        syncType,
        vendorJsonData,
        approvalData
    )
 

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
                               syncType:str="ebidding_win",
                               vendorJsondata=""
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
        syncType=syncType,
        vendorJsonData=vendorJsondata
        
        
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
            timeout=30
        )
        return response
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        raise

def send_ebidding_create(briefSubject:str,briefNo:str,endTime:str,syncType:str="ebidding_create"):
    try:
        response = send_request_with_requests(
            briefSubject=briefSubject,
            briefNo=briefNo,
            endTime=endTime,
            syncType=syncType
        )
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析后的JSON响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"发生错误: {e}")

def send_ebidding_invite(briefSubject:str,briefNo:str,endTime:str,syncType:str="ebidding_invite"):
    try:
        response = send_request_with_requests(
            briefSubject=briefSubject,
            briefNo=briefNo,
            endTime=endTime,
            syncType=syncType,
            vendorJsondata="[{\"vendorName\":\"Samsung Electronics Co.,Ltd.\",\"vendorNo\":\"A0000001_L6B3\"},{\"vendorName\":\"三星(中国)投资有限公司上海分公司\",\"vendorNo\":\"A0000046_L6B3\"},{\"vendorName\":\"中国消费者报社\",\"vendorNo\":\"A0068806_L6B3\"}]"
            
        )
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析后的JSON响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"发生错误: {e}")
def send_ebidding_timeout(briefSubject:str,briefNo:str,endTime:str,syncType:str="ebidding_timeout"):
    try:
        response = send_request_with_requests(
            briefSubject=briefSubject,
            briefNo=briefNo,
            endTime=endTime,
            syncType=syncType,
            vendorJsondata="[{\"vendorName\":\"Samsung Electronics Co.,Ltd.\",\"vendorNo\":\"A0000001_L6B3\"},{\"vendorName\":\"三星(中国)投资有限公司上海分公司\",\"vendorNo\":\"A0000046_L6B3\"},{\"vendorName\":\"中国消费者报社\",\"vendorNo\":\"A0068806_L6B3\"}]"

        )
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析后的JSON响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"发生错误: {e}")

def send_ebidding_win(briefSubject:str,briefNo:str,endTime:str,syncType:str="ebidding_win"):
    try:
        response = send_request_with_requests(
            briefSubject=briefSubject,
            briefNo=briefNo,
            endTime=endTime,
            syncType=syncType,
            vendorJsondata="[{\"vendorName\":\"Samsung Electronics Co.,Ltd.\",\"vendorNo\":\"A0000001_L6B3\"}]",
        )
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析后的JSON响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"发生错误: {e}")
# 使用示例
if __name__ == "__main__":

        briefSubject="EB测试"+time.strftime("%Y%m%d%H%M%S",time.gmtime())
        briefNo="EB"+time.strftime("%Y%m%d%H%M%S",time.gmtime())
        endTime=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time()+15*24*3600))
        send_ebidding_create(briefSubject,briefNo,endTime)
        send_ebidding_invite(briefSubject,briefNo,endTime)
        # send_ebidding_timeout(briefSubject,briefNo,endTime)
        # send_ebidding_win(briefSubject,briefNo,endTime)
        
     