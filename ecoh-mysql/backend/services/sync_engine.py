import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import re

logger = logging.getLogger(__name__)

class SyncEngine:
    """Transforms Unopim data into WordPress-compatible structure"""
    
    def __init__(self, db):
        self.db = db
        self.relationship_fields = [
            'mdcs', 'nics', 'Remotas', 'protocolo', 'comunicacao',
            'tipo_integracao', 'modulos_hemera', 'compativel_medidores',
            'compativel_remotas', 'compativel_mdc'
        ]
    
    async def sync_product(self, unopim_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Unopim product to WordPress structure
        Returns transformed product data
        """
        logger.info(f"Syncing product: {unopim_product['sku']}")
        
        # Calculate checksum
        checksum = self._calculate_checksum(unopim_product['values'])
        
        # Check if already synced with same checksum
        existing = await self.db.find_product_by_id(unopim_product['id'])
        if existing and existing.get('checksum') == checksum:
            logger.info(f"Product {unopim_product['sku']} unchanged, skipping")
            return existing
        
        # Transform data
        transformed = await self._transform_product(unopim_product, checksum)
        
        # Upsert to database
        await self.db.upsert_product(transformed)
        
        logger.info(f"Product {unopim_product['sku']} synced successfully")
        return transformed
    
    async def _transform_product(self, product: Dict[str, Any], checksum: str) -> Dict[str, Any]:
        """Transform Unopim product structure"""
        values = product.get('values', {})
        common = values.get('common', {})
        categories = values.get('categories', [])
        
        # Extract relationships dynamically
        relationships = {}
        attributes = {}
        
        for key, value in common.items():
            if self._is_relationship_field(key, value):
                # Parse comma-separated values or arrays
                relationships[key] = self._parse_relationship_value(value)
            else:
                # Regular attribute
                attributes[key] = value
        
        # Build graph data
        graph_node = self._build_graph_node(product, attributes, relationships)
        graph_edges = self._build_graph_edges(product['sku'], relationships)
        
        # Status mapping
        status_map = {1: 'active', 0: 'inactive'}
        
        # Parse datetime strings
        created_at = product['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        updated_at = product['updated_at']
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        transformed = {
            "unopim_id": product['id'],
            "sku": product['sku'],
            "status": status_map.get(product['status'], 'inactive'),
            "product_type": product['type'],
            "title": self._generate_title(product['sku'], attributes),
            "attributes": attributes,
            "relationships": relationships,
            "categories": categories,
            "checksum": checksum,
            "completeness_score": product.get('avg_completeness_score'),
            "created_at": created_at,
            "updated_at": updated_at,
            "synced_at": datetime.now(timezone.utc),
            "graph_node": graph_node,
            "graph_edges": graph_edges
        }
        
        return transformed
    
    def _is_relationship_field(self, key: str, value: Any) -> bool:
        """Detect if a field represents relationships"""
        # Known relationship fields
        if key in self.relationship_fields:
            return True
        
        # Detect by pattern: comma-separated, array, or 'compativel_' prefix
        if isinstance(value, str) and ',' in value:
            return True
        if isinstance(value, list):
            return True
        if key.startswith('compativel_'):
            return True
        
        return False
    
    def _parse_relationship_value(self, value: Any) -> List[str]:
        """Parse relationship value into list"""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [v.strip() for v in value.split(',') if v.strip()]
        return []
    
    def _build_graph_node(self, product: Dict, attributes: Dict, relationships: Dict) -> Dict:
        """Build 3D graph node representation"""
        # Determine node type from categories or attributes
        categories = product.get('values', {}).get('categories', [])
        node_type = categories[0] if categories else 'produto'
        
        # Color mapping by type
        color_map = {
            'medidores': '#00ff88',
            'remotas': '#ff6b6b',
            'software': '#4ecdc4',
            'mdc': '#45b7d1',
            'integracao': '#f7b731',
            'hardwares': '#5f27cd'
        }
        
        return {
            "id": product['sku'],
            "label": product['sku'],
            "type": node_type,
            "x": 0,  # Will be calculated by force-directed algorithm
            "y": 0,
            "z": 0,
            "size": 1.0 + (len(relationships) * 0.2),  # Larger nodes have more connections
            "color": color_map.get(node_type, '#95a5a6'),
            "metadata": {
                **attributes,
                "relationship_count": sum(len(v) for v in relationships.values())
            }
        }
    
    def _build_graph_edges(self, source_sku: str, relationships: Dict) -> List[Dict]:
        """Build graph edges from relationships"""
        edges = []
        
        for rel_type, targets in relationships.items():
            for target in targets:
                edges.append({
                    "source": source_sku,
                    "target": target,
                    "relationship_type": rel_type,
                    "strength": 1.0
                })
        
        return edges
    
    def _generate_title(self, sku: str, attributes: Dict) -> str:
        """Generate human-readable title"""
        if 'modelo_medidor' in attributes:
            return f"{sku} - {attributes['modelo_medidor']}"
        if 'tipo_software' in attributes:
            return f"{sku} - {attributes['tipo_software'].upper()}"
        return sku
    
    def _calculate_checksum(self, data: Dict) -> str:
        """Calculate MD5 checksum for change detection"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    async def detect_schema_changes(self, new_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect new fields in product JSON that don't match existing schema
        Returns dict of new fields with inferred types
        """
        values = new_product.get('values', {}).get('common', {})
        
        # Get existing schema
        existing_fields = await self.db.find_acf_schema()
        existing_codes = {f['code'] for f in existing_fields}
        
        new_fields = {}
        for key, value in values.items():
            if key not in existing_codes:
                field_type = self._infer_field_type(value)
                new_fields[key] = {
                    "code": key,
                    "type": field_type,
                    "is_relationship": self._is_relationship_field(key, value),
                    "detected_at": datetime.now(timezone.utc)
                }
        
        return new_fields
    
    def _infer_field_type(self, value: Any) -> str:
        """Infer field type from value"""
        if isinstance(value, bool) or value in ['true', 'false']:
            return 'boolean'
        if isinstance(value, list):
            return 'multiselect'
        if isinstance(value, str) and ',' in value:
            return 'multiselect'
        if isinstance(value, (int, float)):
            return 'number'
        return 'text'
    
    async def handle_discontinued_product(self, unopim_id: int):
        """Mark product as discontinued when removed from Unopim"""
        await self.db.update_product(
            unopim_id,
            {
                "status": "discontinued",
                "updated_at": datetime.now(timezone.utc)
            }
        )
        logger.info(f"Product {unopim_id} marked as discontinued")
    
    async def sync_all_products(self, unopim_products: List[Dict]) -> Dict[str, Any]:
        """Bulk sync all products"""
        results = {
            "synced": 0,
            "unchanged": 0,
            "errors": 0,
            "new_fields": {}
        }
        
        for product in unopim_products:
            try:
                # Check for schema changes
                new_fields = await self.detect_schema_changes(product)
                if new_fields:
                    results['new_fields'].update(new_fields)
                    # Store new field definitions
                    for field_data in new_fields.values():
                        await self.db.upsert_acf_field(field_data)
                
                # Sync product
                result = await self.sync_product(product)
                if result:
                    results['synced'] += 1
                else:
                    results['unchanged'] += 1
            except Exception as e:
                logger.error(f"Error syncing product {product.get('sku')}: {str(e)}")
                results['errors'] += 1
        
        return results
