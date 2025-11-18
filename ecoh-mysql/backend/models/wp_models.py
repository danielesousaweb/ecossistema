from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class WPPost(BaseModel):
    """WordPress custom post type representation"""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_type: str = "hemera_product"  # Custom post type
    post_status: str = "publish"  # publish, draft, archived
    post_title: str
    post_name: str  # slug
    post_content: str = ""
    post_excerpt: str = ""
    
    # Custom fields (ACF)
    acf_fields: Dict[str, Any] = {}
    
    # Taxonomies
    taxonomies: Dict[str, List[str]] = {}  # taxonomy_name: [term_ids]
    
    # Metadata
    meta: Dict[str, Any] = {}
    
    # Timestamps
    post_date: datetime
    post_modified: datetime

class ACFFieldGroup(BaseModel):
    """ACF field group definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    key: str
    fields: List[Dict[str, Any]] = []
    location_rules: List[Dict[str, Any]] = []
    active: bool = True
    
class WPTaxonomy(BaseModel):
    """WordPress taxonomy"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    taxonomy: str
    name: str
    slug: str
    description: str = ""
    parent: Optional[str] = None
    count: int = 0
    
class WPTerm(BaseModel):
    """Taxonomy term"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    taxonomy: str
    term: str
    slug: str
    parent: Optional[str] = None
    
class WPRestResponse(BaseModel):
    """Standardized REST API response"""
    success: bool = True
    data: Any = None
    message: str = ""
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None