from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

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
            # Build query
            query = {}
            if status:
                query['status'] = status
            if category:
                query['categories'] = category
            if search:
                query['$or'] = [
                    {'sku': {'$regex': search, '$options': 'i'}},
                    {'title': {'$regex': search, '$options': 'i'}}
                ]
            
            # Get total count
            total = await db.hemera_products.count_documents(query)
            
            # Get paginated results
            skip = (page - 1) * per_page
            products = await db.hemera_products.find(query, {'_id': 0}).skip(skip).limit(per_page).to_list(per_page)
            
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
            product = await db.hemera_products.find_one({"sku": sku}, {'_id': 0})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return WPRestResponse(
                success=True,
                data=product
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
            product = await db.hemera_products.find_one({"sku": sku}, {'_id': 0})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Get all related products
            related_products = []
            for rel_type, targets in product.get('relationships', {}).items():
                for target_sku in targets:
                    related = await db.hemera_products.find_one({"sku": target_sku}, {'_id': 0})
                    if related:
                        related_products.append({
                            "sku": target_sku,
                            "relationship_type": rel_type,
                            "data": related
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
            # Get unique categories from products
            pipeline = [
                {"$unwind": "$categories"},
                {"$group": {
                    "_id": "$categories",
                    "count": {"$sum": 1}
                }}
            ]
            
            categories = await db.hemera_products.aggregate(pipeline).to_list(100)
            
            return WPRestResponse(
                success=True,
                data=[{
                    "slug": cat['_id'],
                    "name": cat['_id'].replace('_', ' ').title(),
                    "count": cat['count']
                } for cat in categories]
            )
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router