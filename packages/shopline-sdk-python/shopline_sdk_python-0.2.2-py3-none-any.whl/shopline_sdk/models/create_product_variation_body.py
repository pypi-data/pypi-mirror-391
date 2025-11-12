"""Shopline API 数据模型 - CreateProductVariationBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class Variant_OptionsItem(BaseModel):
    """Item model for variant_options"""
    name_translations: Translatable
    type: Union[Literal['color', 'size', 'custom_1', 'custom_2', 'custom_3'], str]
    media_id: Optional[str] = None
    """ID of the image to represent the variation 用以表達該商品規枱的圖片ID"""

class CreateProductVariationBody(BaseModel):
    """Payload for creating product variation"""
    ignore_product_media_errors: Optional[bool] = None
    """Will ignore errors when media upload failed. 圖像上傳失敗時將忽略錯誤。"""
    default_show_image_selector: Optional[bool] = None
    """Show variation photos. 展示商品規格圖像。"""
    variant_options: Optional[List[Variant_OptionsItem]] = None
    """Product Variations 商品規格 -  *Maximum allows 3 types of variant option for a product, type allow (color, size, custom_1, custom_2, custom_3)  最多支援三種不同的規格種類，支援color, size, custom_1, custom_2, custom_3"""