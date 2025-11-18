from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    ARCHIVED = "archived"

class ProductType(str, Enum):
    SIMPLE = "simple"
    CONFIGURABLE = "configurable"
    BUNDLE = "bundle"

class UopimProduct(BaseModel):
    """Unopim product model matching the SQL schema"""
    model_config = ConfigDict(extra="allow")
    
    id: int
    sku: str
    status: int = 1  # 1=active, 0=inactive
    type: str = "simple"
    parent_id: Optional[int] = None
    attribute_family_id: Optional[int] = None
    values: Dict[str, Any]  # JSON column with dynamic data
    additional: Optional[Dict[str, Any]] = None
    avg_completeness_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
class TransformedProduct(BaseModel):
    """Transformed product for WordPress/MongoDB storage"""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    unopim_id: int
    sku: str
    status: ProductStatus
    product_type: str
    title: str
    
    # Normalized attributes from JSON
    attributes: Dict[str, Any] = {}
    
    # Relationships (extracted from values.common)
    relationships: Dict[str, List[str]] = {}
    
    # Categories
    categories: List[str] = []
    
    # Metadata
    checksum: str  # MD5 of values JSON for change detection
    completeness_score: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    synced_at: datetime
    
    # Graph data
    graph_node: Optional[Dict[str, Any]] = None
    graph_edges: List[Dict[str, Any]] = []

class AttributeDefinition(BaseModel):
    """Dynamic attribute definition (simulating ACF)"""
    code: str
    label: str
    type: str  # text, select, multiselect, boolean, etc.
    is_relationship: bool = False
    options: List[str] = []
    is_required: bool = False
    is_filterable: bool = True
    position: int = 0
    
class SyncEvent(BaseModel):
    """Webhook event from Unopim"""
    event_type: str  # create, update, delete
    entity_type: str  # product, category, attribute
    entity_id: int
    data: Dict[str, Any]
    timestamp: datetime
    checksum: Optional[str] = None

class GraphNode(BaseModel):
    """3D graph node representation"""
    id: str
    label: str
    type: str  # product, integration, protocol, etc.
    sku: Optional[str] = None
    
    # 3D position (calculated by force-directed algorithm)
    x: float = 0
    y: float = 0
    z: float = 0
    
    # Visual properties
    size: float = 1.0
    color: str = "#00ff88"
    
    # Data
    metadata: Dict[str, Any] = {}
    
class GraphEdge(BaseModel):
    """Connection between nodes"""
    source: str  # node id
    target: str  # node id
    relationship_type: str
    strength: float = 1.0
    
import uuid