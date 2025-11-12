"""Shopline API 数据模型 - SearchProductsBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class SearchProductsBody(BaseModel):
    """Parameters for searching products"""
    page: Optional[int] = None
    """Page Number 頁數（第n頁）"""
    per_page: Optional[int] = None
    """每頁顯示 n 筆資料，建議最多 50 筆 If there're many products, set per_page to 50"""
    query: Optional[str] = None
    """支援 product_name、sku、barcode 的模糊查詢"""
    id: Optional[str] = None
    """商品 ID，支援等於、不等於、in 多筆查詢"""
    category_id: Optional[str] = None
    """商品分類 ID，支援以逗號分隔多筆"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    """商品狀態"""
    sort_type: Optional[Union[Literal['created_at', 'lowest_price', 'quantity_sold', 'custom_sorting'], str]] = None
    """排序類型，預設為 created_at"""
    sort_by: Optional[Union[Literal['asc', 'desc'], str]] = None
    """排序方向，預設為 desc。當 sort_type 為 quantity_sold 時只能為 desc。"""
    sku: Optional[str] = None
    """商品貨號，支援等於、不等於、in 多筆查詢"""
    barcode: Optional[str] = None
    """條碼，支援等於、不等於、in 多筆查詢"""
    is_preorder: Optional[bool] = None
    """是否為預購商品"""
    quantity: Optional[str] = None
    """規格數量，支援 lt/lte/gt/gte/not 等查詢"""
    variation_quantity: Optional[str] = None
    """Variation 數量查詢條件，語法同 quantity"""
    unlimited_quantity: Optional[bool] = None
    """是否為無限數量"""
    created_at: Optional[str] = None
    """建立時間，支援比較運算子（gt/gte/lt/lte）"""
    updated_at: Optional[str] = None
    """更新時間，支援比較運算子"""
    title_translations: Optional[str] = None
    """標題關鍵字（多語系）"""
    summary_translations: Optional[str] = None
    """摘要關鍵字（多語系）"""
    tags: Optional[str] = None
    """標籤關鍵字"""
    excludes: Optional[List[str]] = None
    """要排除的欄位"""
    fields: Optional[List[str]] = None
    """僅顯示的欄位"""
    include_fields: Optional[List[Union[Literal['labels'], str]]] = None
    """要額外包含的欄位"""
    retail_status: Optional[Union[Literal['active', 'draft'], str]] = None
    """POS 商品上架狀態"""
    with_product_set: Optional[bool] = None
    """是否包含組合商品"""
    purchasable: Optional[bool] = None
    """是否可購買"""
    root_product: Optional[bool] = None
    """是否為 Root Product 查詢模式（僅看 supplier_id 和 pos_category_id）"""
    supplier_id: Optional[str] = None
    """供應商 ID（root_product 為 true 時使用）"""
    pos_category_id: Optional[str] = None
    """POS 分類 ID（root_product 為 true 時使用）"""
    type: Optional[str] = None
    """商品類型（如 product_set）"""
    previous_id: Optional[str] = None
    """上一頁最後一筆的 ID（用於 cursor-based 分頁）"""
    allow_gift: Optional[bool] = None
    """是否允許作為贈品"""