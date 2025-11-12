"""Shopline API 数据模型 - Job"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Ref_DataConfig(BaseModel):
    """Configuration model for ref_data"""
    result_file: Optional[str] = None
    """URL of file contains the job result"""

class Job(BaseModel):
    id: Optional[str] = None
    """ID"""
    name: Optional[str] = None
    """Name of job"""
    type: Optional[str] = None
    """Related resource of the job"""
    status: Optional[Union[Literal['pending', 'in_progress', 'done', 'failed'], str]] = None
    """Job status"""
    created_at: Optional[str] = None
    """Job created time"""
    start_time: Optional[str] = None
    """Job started time"""
    finish_time: Optional[str] = None
    """Job completed time"""
    expiry_time: Optional[str] = None
    """Job expire time"""
    total_count: Optional[int] = None
    """Number of data processed in total"""
    successful_count: Optional[int] = None
    """Number of data succeed"""
    failed_count: Optional[int] = None
    """Number of data failed"""
    ref_data: Optional[Ref_DataConfig] = None
    """Job started time"""
    created_by: Optional[str] = None
    """Source of job"""
    performer_name: Optional[str] = None
    """The name of user performed the job"""
    performer_type: Optional[str] = None
    """The type of user performed the job"""
    performer_id: Optional[str] = None
    """The ID of user performed the job"""
    performing_application_id: Optional[str] = None
    """The ID of application performed the job"""