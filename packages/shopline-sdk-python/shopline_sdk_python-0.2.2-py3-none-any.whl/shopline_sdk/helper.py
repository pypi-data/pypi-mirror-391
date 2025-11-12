import hashlib
import hmac
import json
from typing import Any, Dict


def _sort_dict_by_keys(obj: Any) -> Any:
    """
    递归地对字典按键排序
    
    Args:
        obj: 需要排序的对象，可以是dict、list或其他类型
    
    Returns:
        排序后的对象
    """
    if isinstance(obj, dict):
        # 对字典按键排序，并递归处理嵌套的字典和列表
        sorted_dict = {}
        for key in sorted(obj.keys()):
            sorted_dict[key] = _sort_dict_by_keys(obj[key])
        return sorted_dict
    elif isinstance(obj, list):
        # 对列表中的每个元素递归处理
        return [_sort_dict_by_keys(item) for item in obj]
    else:
        # 其他类型直接返回
        return obj


def _serialize_payload(payload: Dict[str, Any]) -> str:
    """
    序列化payload，确保排序和格式与SHOPLINE一致
    
    Args:
        payload: 需要序列化的payload
    
    Returns:
        序列化后的字符串
    """
    # 按键排序
    sorted_payload = _sort_dict_by_keys(payload)

    # 序列化为JSON字符串，确保没有多余的空格
    # separators参数确保紧凑格式，与SHOPLINE保持一致
    return json.dumps(sorted_payload, separators=(',', ':'), ensure_ascii=False)


def verify_webhook_request(payload: Dict[str, Any], signature: str, secret: str, timestamp: str) -> bool:
    """
    Webhook 请求验签（根据SHOPLINE最新文档实现）
    
    根据SHOPLINE最新文档实现的验签方法：
    1. 获取timestamp和payload
    2. 对payload按键排序
    3. 序列化payload
    4. 组合message: timestamp + ":" + serialized_payload
    5. 使用HMAC-SHA256生成签名
    6. 与提供的签名比较
    
    Args:
        payload: 请求体解析后的JSON对象
        signature: 查询参数中的签名
        secret: 应用密钥
        timestamp: 请求头中的timestamp
    
    Returns:
        bool: 验签是否成功
    """
    if not secret or not signature or not timestamp:
        return False

    # 序列化payload
    serialized_payload = _serialize_payload(payload)

    # 组合message
    message = f"{timestamp}:{serialized_payload}"

    # 生成签名
    mac = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    expected_signature = mac.hexdigest()

    # 比较签名（不区分大小写）
    return expected_signature.lower() == signature.lower()
