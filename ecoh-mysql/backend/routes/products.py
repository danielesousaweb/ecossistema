from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json

from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

def setup_routes(db, sync_engine, graph_builder):
    """Setup routes with dependencies"""
    
    @router.get("", response_model=WPRestResponse)
    async def get_products(
        status: Optional[str] = Query(None, description="Filter by status"),
        category: Optional[str] = Query(None, description="Filter by category"),
        search: Optional[str] = Query(None, description="Search in SKU or title"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """Get all products (WordPress REST API compatible)"""
        try:
            # Build query parts
            where_clauses = []
            params = []
            
            if status:
                where_clauses.append("status = %s")
                params.append(status)
            
            if category:
                where_clauses.append("JSON_CONTAINS(categories, %s)")
                params.append(f'"{category}"')
            
            if search:
                where_clauses.append("(sku LIKE %s OR title LIKE %s)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern])
            
            where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM hemera_products{where_clause}"
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(count_query, params)
                    result = await cursor.fetchone()
                    total = result[0] if result else 0
            
            # Get paginated results
            skip = (page - 1) * per_page
            query = f"SELECT * FROM hemera_products{where_clause} ORDER BY updated_at DESC LIMIT %s OFFSET %s"
            params.extend([per_page, skip])
            
            products = []
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    columns = [desc[0] for desc in cursor.description]
                    rows = await cursor.fetchall()
                    
                    for row in rows:
                        product = dict(zip(columns, row))
                        db._parse_json_fields(product)
                        products.append(product)
            
            return WPRestResponse(
                success=True,
                data=products,
                total=total,
                page=page,
                per_page=per_page
            )
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{sku}", response_model=WPRestResponse)
    async def get_product(sku: str):
        """Get single product by SKU"""
        try:
            products = await db.find_products({"sku": sku})
            if not products:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return WPRestResponse(
                success=True,
                data=products[0]
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching product {sku}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{sku}/relationships", response_model=WPRestResponse)
    async def get_product_relationships(sku: str):
        """Get product relationships (for graph visualization)"""
        try:
            products = await db.find_products({"sku": sku})
            if not products:
                raise HTTPException(status_code=404, detail="Product not found")
            
            product = products[0]
            
            # Get all related products
            related_products = []
            for rel_type, targets in product.get('relationships', {}).items():
                for target_sku in targets:
                    related_list = await db.find_products({"sku": target_sku})
                    if related_list:
                        related_products.append({
                            "sku": target_sku,
                            "relationship_type": rel_type,
                            "data": related_list[0]
                        })
            
            return WPRestResponse(
                success=True,
                data={
                    "product": product,
                    "relationships": related_products
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching relationships for {sku}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/categories/list", response_model=WPRestResponse)
    async def get_categories():
        """Get all categories"""
        try:
            # Query to get unique categories with counts
            query = """
                SELECT 
                    JSON_UNQUOTE(JSON_EXTRACT(categories, CONCAT('$[', numbers.n, ']'))) as category,
                    COUNT(*) as count
                FROM hemera_products
                CROSS JOIN (
                    SELECT 0 as n UNION ALL SELECT 1 UNION ALL SELECT 2 
                    UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
                ) numbers
                WHERE JSON_UNQUOTE(JSON_EXTRACT(categories, CONCAT('$[', numbers.n, ']'))) IS NOT NULL
                GROUP BY category
            """
            
            categories = []
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
                    
                    for row in rows:
                        categories.append({
                            "slug": row[0],
                            "name": row[0].replace('_', ' ').title(),
                            "count": row[1]
                        })
            
            return WPRestResponse(
                success=True,
                data=categories
            )
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
