"""
MySQL Database Connection Manager
Conecta diretamente às tabelas padrão do Unopim (unopim_products, unopim_attributes, unopim_categories)
"""
import aiomysql
import os
from typing import Optional, Dict, Any, List
import logging
import json
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MySQLDatabase:
    """Async MySQL database connection manager - Direct Unopim tables"""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
        self.config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', ''),
            'db': os.environ.get('MYSQL_DATABASE', 'unopim'),
            'charset': 'utf8mb4',
            'autocommit': True,
            'minsize': 1,
            'maxsize': 10
        }
    
    async def connect(self):
        """Create connection pool"""
        try:
            self.pool = await aiomysql.create_pool(**self.config)
            logger.info(f"Connected to MySQL database: {self.config['db']} (Direct Unopim mode)")
            logger.info(f"Using tables: unopim_products, unopim_attributes, unopim_categories")
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("MySQL connection pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Get database connection from pool"""
        async with self.pool.acquire() as conn:
            yield conn
    
    # ==========================================
    # PRODUCT OPERATIONS (unopim_products)
    # ==========================================
    
    async def find_products(self, filters: Optional[Dict] = None, limit: int = 1000) -> List[Dict]:
        """
        Find products from unopim_products table
        Transforms Unopim format to frontend-compatible format on-the-fly
        """
        query = "SELECT * FROM unopim_products"
        params = []
        conditions = []
        
        if filters:
            for key, value in filters.items():
                if key == 'status':
                    # Map status: 'active' -> 1, 'inactive' -> 0
                    if value == 'active':
                        conditions.append("status = %s")
                        params.append(1)
                    elif value == 'inactive':
                        conditions.append("status = %s")
                        params.append(0)
                elif key == 'sku':
                    conditions.append("sku = %s")
                    params.append(value)
                elif key == 'type':
                    conditions.append("type = %s")
                    params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY updated_at DESC LIMIT {limit}"
        
        logger.debug(f"[SOURCE: unopim_products] Query: {query}")
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                
                # Transform each product to frontend format
                transformed = []
                for row in results:
                    product = self._transform_unopim_product(row)
                    if product:
                        transformed.append(product)
                
                logger.debug(f"[SOURCE: unopim_products] Found {len(transformed)} products")
                return transformed
    
    async def find_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Find single product by SKU"""
        query = "SELECT * FROM unopim_products WHERE sku = %s"
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (sku,))
                result = await cursor.fetchone()
                
                if result:
                    return self._transform_unopim_product(result)
                return None
    
    async def find_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Find single product by ID"""
        query = "SELECT * FROM unopim_products WHERE id = %s"
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (product_id,))
                result = await cursor.fetchone()
                
                if result:
                    return self._transform_unopim_product(result)
                return None
    
    async def count_products(self, filters: Optional[Dict] = None) -> int:
        """Count products with optional filters"""
        query = "SELECT COUNT(*) as total FROM unopim_products"
        params = []
        conditions = []
        
        if filters:
            for key, value in filters.items():
                if key == 'status':
                    if value == 'active':
                        conditions.append("status = %s")
                        params.append(1)
                    elif value == 'inactive':
                        conditions.append("status = %s")
                        params.append(0)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchone()
                return result[0] if result else 0
    
    async def search_products(self, search_term: str, status: str = 'active', limit: int = 50) -> List[Dict]:
        """Search products by SKU, name or attributes"""
        status_value = 1 if status == 'active' else 0
        search_pattern = f"%{search_term}%"
        
        query = """
            SELECT * FROM unopim_products 
            WHERE status = %s 
            AND (
                sku LIKE %s 
                OR JSON_EXTRACT(values, '$.common.nome_medidor') LIKE %s
                OR JSON_EXTRACT(values, '$.common.modelo_medidor') LIKE %s
                OR JSON_EXTRACT(values, '$.common.fabricante_medidor') LIKE %s
            )
            ORDER BY updated_at DESC
            LIMIT %s
        """
        
        params = [status_value, search_pattern, search_pattern, search_pattern, search_pattern, limit]
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                
                transformed = []
                for row in results:
                    product = self._transform_unopim_product(row)
                    if product:
                        transformed.append(product)
                
                return transformed
    
    # ==========================================
    # ATTRIBUTES OPERATIONS (unopim_attributes)
    # ==========================================
    
    async def find_attributes(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Find attribute definitions from unopim_attributes
        Returns fields that can be used as filters/topics
        """
        query = "SELECT * FROM unopim_attributes"
        params = []
        conditions = []
        
        if filters:
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY position ASC, code ASC"
        
        logger.debug(f"[SOURCE: unopim_attributes] Query: {query}")
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                logger.debug(f"[SOURCE: unopim_attributes] Found {len(results)} attributes")
                return results
    
    async def find_filterable_attributes(self) -> List[Dict]:
        """Find attributes marked as filterable"""
        query = """
            SELECT * FROM unopim_attributes 
            WHERE is_filterable = 1 OR is_filterable = TRUE
            ORDER BY position ASC, code ASC
        """
        
        logger.debug(f"[SOURCE: unopim_attributes] Finding filterable attributes")
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                results = await cursor.fetchall()
                logger.debug(f"[SOURCE: unopim_attributes] Found {len(results)} filterable attributes")
                return results
    
    # ==========================================
    # CATEGORIES OPERATIONS (unopim_categories)
    # ==========================================
    
    async def find_categories(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Find categories from unopim_categories"""
        query = "SELECT * FROM unopim_categories"
        params = []
        conditions = []
        
        if filters:
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY id ASC"
        
        logger.debug(f"[SOURCE: unopim_categories] Query: {query}")
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                logger.debug(f"[SOURCE: unopim_categories] Found {len(results)} categories")
                return results
    
    # ==========================================
    # TRANSFORMATION HELPERS
    # ==========================================
    
    def _transform_unopim_product(self, row: Dict) -> Optional[Dict]:
        """
        Transform Unopim product to frontend-compatible format
        
        Unopim format:
        - id, sku, status (1/0), type, values (JSON with common), created_at, updated_at
        
        Frontend format:
        - unopim_id, sku, status ('active'/'inactive'), product_type, title,
          attributes, relationships, categories, graph_node, graph_edges
        """
        try:
            # Parse values JSON
            values = row.get('values')
            if isinstance(values, str):
                try:
                    values = json.loads(values)
                except json.JSONDecodeError:
                    values = {}
            elif values is None:
                values = {}
            
            common = values.get('common', {})
            categories = values.get('categories', [])
            
            # If categories is a string, try to parse
            if isinstance(categories, str):
                try:
                    categories = json.loads(categories)
                except:
                    categories = [categories] if categories else []
            
            # Extract attributes and relationships
            attributes, relationships = self._extract_attributes_and_relationships(common)
            
            # Map status
            status = 'active' if row.get('status') == 1 else 'inactive'
            
            # Generate title
            title = self._generate_title(row.get('sku', ''), common)
            
            # Build graph data
            graph_node = self._build_graph_node(row, attributes, relationships, categories)
            graph_edges = self._build_graph_edges(row.get('sku', ''), relationships)
            
            return {
                'id': row.get('id'),
                'unopim_id': row.get('id'),
                'sku': row.get('sku', ''),
                'status': status,
                'product_type': row.get('type', 'simple'),
                'title': title,
                'attributes': attributes,
                'relationships': relationships,
                'categories': categories,
                'graph_node': graph_node,
                'graph_edges': graph_edges,
                'completeness_score': row.get('avg_completeness_score', 0),
                'created_at': row.get('created_at'),
                'updated_at': row.get('updated_at')
            }
        except Exception as e:
            logger.error(f"Error transforming product {row.get('sku')}: {str(e)}")
            return None
    
    def _extract_attributes_and_relationships(self, common: Dict) -> tuple:
        """
        Extract attributes and relationships from common values
        
        Relationship fields are those that contain comma-separated values
        or are known relationship types
        """
        relationship_fields = [
            'protocolos', 'protocolo', 'protocolo_comunicao',
            'tipo_medicao', 'nics', 'remotas', 'comunicacao',
            'mdcs', 'tipo_integracao', 'hemera', 'mobii',
            'caractersticas_medidor', 'caracterssticas',
            'modulos_hemera', 'modulos',
            'compativel_medidores', 'compativel_remotas', 'compativel_mdc',
            'funcionalidades', 'integracao', 'formato_dados'
        ]
        
        attributes = {}
        relationships = {}
        
        for key, value in common.items():
            if value is None:
                continue
                
            # Check if it's a relationship field
            is_relationship = (
                key in relationship_fields or
                key.startswith('compativel_') or
                (isinstance(value, str) and ',' in value)
            )
            
            if is_relationship:
                # Parse comma-separated values
                if isinstance(value, str):
                    values_list = [v.strip() for v in value.split(',') if v.strip()]
                elif isinstance(value, list):
                    values_list = value
                else:
                    values_list = [str(value)]
                
                if values_list:
                    relationships[key] = values_list
            else:
                attributes[key] = value
        
        return attributes, relationships
    
    def _generate_title(self, sku: str, common: Dict) -> str:
        """Generate human-readable title"""
        nome = common.get('nome_medidor', '')
        if nome:
            return nome
        
        modelo = common.get('modelo_medidor', '')
        if modelo:
            return f"{sku} - {modelo}"
        
        tipo_software = common.get('tipo_software', '')
        if tipo_software:
            return f"{sku} - {tipo_software.upper()}"
        
        return sku
    
    def _build_graph_node(self, product: Dict, attributes: Dict, relationships: Dict, categories: List) -> Dict:
        """Build 3D graph node representation"""
        node_type = categories[0] if categories else 'produto'
        
        color_map = {
            'medidores': '#00ff88',
            'remotas': '#ff6b6b',
            'software': '#4ecdc4',
            'mdc': '#45b7d1',
            'integracao': '#f7b731',
            'hardwares': '#5f27cd',
            'nics': '#fd79a8'
        }
        
        relationship_count = sum(len(v) for v in relationships.values())
        
        return {
            'id': product.get('sku', ''),
            'label': product.get('sku', ''),
            'type': node_type,
            'x': 0,
            'y': 0,
            'z': 0,
            'size': 1.0 + (relationship_count * 0.1),
            'color': color_map.get(node_type, '#95a5a6'),
            'metadata': {
                **attributes,
                'relationship_count': relationship_count
            }
        }
    
    def _build_graph_edges(self, source_sku: str, relationships: Dict) -> List[Dict]:
        """Build graph edges from relationships"""
        edges = []
        
        for rel_type, targets in relationships.items():
            for target in targets:
                edges.append({
                    'source': source_sku,
                    'target': target,
                    'relationship_type': rel_type,
                    'strength': 1.0
                })
        
        return edges
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    async def get_unique_values_for_field(self, field_name: str) -> List[str]:
        """
        Get all unique values for a specific field across all active products
        Useful for building dynamic filters/topics
        """
        query = """
            SELECT DISTINCT 
                JSON_UNQUOTE(JSON_EXTRACT(values, CONCAT('$.common.', %s))) as field_value
            FROM unopim_products 
            WHERE status = 1
            AND JSON_EXTRACT(values, CONCAT('$.common.', %s)) IS NOT NULL
        """
        
        logger.debug(f"[SOURCE: unopim_products] Getting unique values for field: {field_name}")
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (field_name, field_name))
                results = await cursor.fetchall()
                
                unique_values = set()
                for row in results:
                    if row[0]:
                        # Handle comma-separated values
                        values = row[0].split(',')
                        for v in values:
                            v = v.strip()
                            if v:
                                unique_values.add(v)
                
                return sorted(list(unique_values))
    
    async def get_products_by_field_value(self, field_name: str, field_value: str, limit: int = 50) -> List[Dict]:
        """
        Get products that have a specific value in a field
        Handles both exact matches and comma-separated values
        """
        query = """
            SELECT * FROM unopim_products 
            WHERE status = 1
            AND (
                JSON_UNQUOTE(JSON_EXTRACT(values, CONCAT('$.common.', %s))) = %s
                OR JSON_UNQUOTE(JSON_EXTRACT(values, CONCAT('$.common.', %s))) LIKE %s
                OR JSON_UNQUOTE(JSON_EXTRACT(values, CONCAT('$.common.', %s))) LIKE %s
                OR JSON_UNQUOTE(JSON_EXTRACT(values, CONCAT('$.common.', %s))) LIKE %s
            )
            ORDER BY updated_at DESC
            LIMIT %s
        """
        
        params = [
            field_name, field_value,
            field_name, f"{field_value},%",
            field_name, f"%,{field_value},%",
            field_name, f"%,{field_value}",
            limit
        ]
        
        logger.debug(f"[SOURCE: unopim_products] Finding products with {field_name}={field_value}")
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                
                transformed = []
                for row in results:
                    product = self._transform_unopim_product(row)
                    if product:
                        transformed.append(product)
                
                return transformed


# Global database instance
db = MySQLDatabase()
