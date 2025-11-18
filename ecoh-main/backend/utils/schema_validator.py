from typing import Dict, Any, List, Optional
import json
import jsonschema
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)

class DynamicSchemaValidator:
    """Validates and auto-generates schema for dynamic Unopim JSON data"""
    
    def __init__(self):
        self.known_schemas = {}
    
    def validate_product_values(self, values: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate product values JSON
        Returns (is_valid, error_message)
        """
        try:
            # Basic structure validation
            if not isinstance(values, dict):
                return False, "Values must be a dictionary"
            
            # Required top-level keys
            if 'common' not in values:
                return False, "Missing 'common' key in values"
            
            common = values['common']
            if not isinstance(common, dict):
                return False, "'common' must be a dictionary"
            
            # SKU is required
            if 'sku' not in common:
                return False, "Missing 'sku' in common attributes"
            
            return True, None
        
        except Exception as e:
            return False, str(e)
    
    def infer_schema_from_value(self, value: Any) -> Dict[str, Any]:
        """Infer JSON schema from a value"""
        if isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, str):
            return {"type": "string"}
        elif isinstance(value, list):
            if value:
                # Infer from first item
                item_schema = self.infer_schema_from_value(value[0])
                return {
                    "type": "array",
                    "items": item_schema
                }
            return {"type": "array"}
        elif isinstance(value, dict):
            properties = {}
            for k, v in value.items():
                properties[k] = self.infer_schema_from_value(v)
            return {
                "type": "object",
                "properties": properties
            }
        else:
            return {}
    
    def generate_schema_from_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON schema from product example"""
        values = product.get('values', {})
        return self.infer_schema_from_value(values)
    
    def detect_field_changes(self, old_schema: Dict, new_data: Dict) -> Dict[str, List[str]]:
        """Detect schema changes between old and new data"""
        changes = {
            "added": [],
            "removed": [],
            "type_changed": []
        }
        
        old_fields = set(old_schema.get('properties', {}).keys())
        new_fields = set(new_data.keys())
        
        changes['added'] = list(new_fields - old_fields)
        changes['removed'] = list(old_fields - new_fields)
        
        # Check for type changes
        for field in old_fields & new_fields:
            old_type = old_schema['properties'][field].get('type')
            new_value = new_data[field]
            new_type = self.infer_schema_from_value(new_value).get('type')
            
            if old_type != new_type:
                changes['type_changed'].append(field)
        
        return changes