"""
MySQL Database Connection Manager
Replaces MongoDB Motor with aiomysql for async MySQL operations
"""
import aiomysql
import os
from typing import Optional, Dict, Any, List
import logging
import json
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MySQLDatabase:
    """Async MySQL database connection manager"""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
        self.config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', ''),
            'db': os.environ.get('MYSQL_DATABASE', 'ecoh_db'),
            'charset': 'utf8mb4',
            'autocommit': True,
            'minsize': 1,
            'maxsize': 10
        }
    
    async def connect(self):
        """Create connection pool"""
        try:
            self.pool = await aiomysql.create_pool(**self.config)
            logger.info(f"Connected to MySQL database: {self.config['db']}")
            
            # Initialize schema
            await self.init_schema()
            
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}")
            raise
    
    async def init_schema(self):
        """Initialize database schema if not exists"""
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if not os.path.exists(schema_file):
            logger.warning("Schema file not found, skipping initialization")
            return
        
        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split by ; and execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    for statement in statements:
                        if statement:
                            await cursor.execute(statement)
            
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing schema: {str(e)}")
            # Don't raise - tables might already exist
    
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
    
    # Product operations
    async def find_products(self, filters: Optional[Dict] = None, limit: int = 1000) -> List[Dict]:
        """Find products with optional filters"""
        query = "SELECT * FROM hemera_products"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += f" LIMIT {limit}"
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                
                # Parse JSON fields
                for row in results:
                    self._parse_json_fields(row)
                
                return results
    
    async def find_product_by_id(self, unopim_id: int) -> Optional[Dict]:
        """Find single product by unopim_id"""
        query = "SELECT * FROM hemera_products WHERE unopim_id = %s"
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (unopim_id,))
                result = await cursor.fetchone()
                
                if result:
                    self._parse_json_fields(result)
                
                return result
    
    async def insert_product(self, product: Dict) -> int:
        """Insert new product"""
        # Serialize JSON fields
        product = self._serialize_json_fields(product.copy())
        
        columns = ', '.join(product.keys())
        placeholders = ', '.join(['%s'] * len(product))
        query = f"INSERT INTO hemera_products ({columns}) VALUES ({placeholders})"
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, list(product.values()))
                return cursor.lastrowid
    
    async def update_product(self, unopim_id: int, updates: Dict) -> bool:
        """Update product by unopim_id"""
        # Serialize JSON fields
        updates = self._serialize_json_fields(updates.copy())
        
        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"UPDATE hemera_products SET {set_clause} WHERE unopim_id = %s"
        values = list(updates.values()) + [unopim_id]
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
                return cursor.rowcount > 0
    
    async def upsert_product(self, product: Dict) -> bool:
        """Insert or update product"""
        existing = await self.find_product_by_id(product['unopim_id'])
        
        if existing:
            # Remove unchangeable fields
            updates = {k: v for k, v in product.items() if k not in ['id', 'unopim_id']}
            return await self.update_product(product['unopim_id'], updates)
        else:
            await self.insert_product(product)
            return True
    
    async def delete_products(self, filters: Dict) -> int:
        """Delete products matching filters"""
        conditions = []
        params = []
        
        for key, value in filters.items():
            conditions.append(f"{key} = %s")
            params.append(value)
        
        query = f"DELETE FROM hemera_products WHERE " + " AND ".join(conditions)
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return cursor.rowcount
    
    # ACF Schema operations
    async def find_acf_schema(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Find ACF schema definitions"""
        query = "SELECT * FROM acf_schema"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                results = await cursor.fetchall()
                
                for row in results:
                    if 'options' in row and row['options']:
                        row['options'] = json.loads(row['options']) if isinstance(row['options'], str) else row['options']
                
                return results
    
    async def upsert_acf_field(self, field: Dict) -> bool:
        """Insert or update ACF field definition"""
        query = """
            INSERT INTO acf_schema (code, label, type, is_relationship, is_required, is_filterable, position, options, detected_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                label = VALUES(label),
                type = VALUES(type),
                is_relationship = VALUES(is_relationship),
                is_required = VALUES(is_required),
                is_filterable = VALUES(is_filterable),
                position = VALUES(position),
                options = VALUES(options)
        """
        
        options_json = json.dumps(field.get('options', [])) if field.get('options') else None
        
        values = (
            field['code'],
            field.get('label', field['code']),
            field['type'],
            field.get('is_relationship', False),
            field.get('is_required', False),
            field.get('is_filterable', True),
            field.get('position', 0),
            options_json,
            field.get('detected_at')
        )
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
                return True
    
    # Status checks operations
    async def insert_status_check(self, status: Dict) -> bool:
        """Insert status check"""
        query = "INSERT INTO status_checks (id, client_name, timestamp) VALUES (%s, %s, %s)"
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (status['id'], status['client_name'], status['timestamp']))
                return True
    
    async def find_status_checks(self, limit: int = 1000) -> List[Dict]:
        """Find status checks"""
        query = f"SELECT * FROM status_checks ORDER BY timestamp DESC LIMIT {limit}"
        
        async with self.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                return await cursor.fetchall()
    
    # Webhook events operations
    async def insert_webhook_event(self, event: Dict) -> int:
        """Insert webhook event"""
        query = """
            INSERT INTO webhook_events (event_type, entity_type, entity_id, data, checksum, timestamp, processed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        data_json = json.dumps(event.get('data', {}))
        
        values = (
            event['event_type'],
            event['entity_type'],
            event['entity_id'],
            data_json,
            event.get('checksum'),
            event['timestamp'],
            event.get('processed', False)
        )
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
                return cursor.lastrowid
    
    # Sync logs operations
    async def insert_sync_log(self, log: Dict) -> int:
        """Insert sync log"""
        query = """
            INSERT INTO sync_logs (product_id, action, status, message, duration_ms, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        values = (
            log.get('product_id'),
            log['action'],
            log['status'],
            log.get('message'),
            log.get('duration_ms'),
            log['timestamp']
        )
        
        async with self.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
                return cursor.lastrowid
    
    # Helper methods
    def _parse_json_fields(self, row: Dict):
        """Parse JSON string fields back to Python objects"""
        json_fields = ['attributes', 'relationships', 'categories', 'graph_node', 'graph_edges']
        
        for field in json_fields:
            if field in row and row[field]:
                if isinstance(row[field], str):
                    try:
                        row[field] = json.loads(row[field])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON field: {field}")
                        row[field] = None
    
    def _serialize_json_fields(self, data: Dict) -> Dict:
        """Serialize Python objects to JSON strings"""
        json_fields = ['attributes', 'relationships', 'categories', 'graph_node', 'graph_edges']
        
        for field in json_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], str):
                    data[field] = json.dumps(data[field])
        
        return data


# Global database instance
db = MySQLDatabase()
