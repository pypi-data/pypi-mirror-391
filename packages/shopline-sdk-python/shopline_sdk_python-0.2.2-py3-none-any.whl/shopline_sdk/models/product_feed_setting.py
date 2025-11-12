"""Shopline API 数据模型 - ProductFeedSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class ProductFeedSetting(BaseModel):
    id: Optional[str] = None
    owner_id: Optional[str] = None
    kind: Optional[str] = None
    format: Optional[str] = None
    path: Optional[str] = None
    event_tracker_id: Optional[str] = None
    single_variation: Optional[bool] = None
    unique_ids: Optional[bool] = None
    preorder_period: Optional[float] = None
    force_adult_age_groups: Optional[Dict[str, Any]] = None
    enabled_fb_product_category: Optional[bool] = None
    with_adult: Optional[bool] = None
    with_identifier_exists_value: Optional[str] = None
    with_mpn: Optional[bool] = None
    with_gtin: Optional[bool] = None
    use_color: Optional[bool] = None
    with_custom_label: Optional[bool] = None
    schedule_group: Optional[str] = None
    last_triggered_at: Optional[str] = None
    last_triggered_by: Optional[str] = None
    last_consumed_at: Optional[str] = None
    last_generated_at: Optional[str] = None
    last_uploaded_at: Optional[str] = None
    enabled: Optional[bool] = None
    last_enabled_at: Optional[str] = None
    last_disabled_at: Optional[str] = None
    title: Optional[str] = None
    total_product_count: Optional[float] = None
    with_out_of_stock_product: Optional[bool] = None
    with_preorder_product: Optional[bool] = None
    category_ids: Optional[Dict[str, Any]] = None
    main_product_image_select: Optional[float] = None
    variant_product_image_select: Optional[float] = None
    locale: Optional[str] = None
    updated_at: Optional[str] = None
    removed_at: Optional[str] = None
    created_at: Optional[str] = None