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
        status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
        category: Optional[str] = Query(None, description="Filter by category"),
        search: Optional[str] = Query(None, description="Search in SKU or title"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """
        Get all products from unopim_products table
        WordPress REST API compatible
        """
        try:
            logger.info(f"[PRODUCTS] Getting products - status={status}, category={category}, search={search}")
            
            # Build filters
            filters = {}
            if status:
                filters['status'] = status
            
            # Get products
            if search:
                # Use search function
                all_products = await db.search_products(search, status=status or 'active', limit=1000)
            else:
                all_products = await db.find_products(filters, limit=1000)
            
            # Filter by category if specified
            if category:
                all_products = [
                    p for p in all_products 
                    if category in (p.get('categories') or [])
                ]
            
            # Paginate
            total = len(all_products)
            start = (page - 1) * per_page
            end = start + per_page
            products = all_products[start:end]
            
            logger.info(f"[SOURCE: unopim_products] Found {total} products, returning page {page}")
            
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
    
    @router.get("/categories/list", response_model=WPRestResponse)
    async def get_categories():
        """
        Get all categories from unopim_categories or extracted from products
        """
        try:
            logger.info("[PRODUCTS] Getting categories")
            
            categories = []
            
            # Try to get from unopim_categories first
            try:
                cat_list = await db.find_categories()
                for cat in cat_list:
                    categories.append({
                        "id": cat.get('id'),
                        "slug": cat.get('code', cat.get('slug', '')),
                        "name": cat.get('name', cat.get('code', '')).replace('_', ' ').title(),
                        "parent_id": cat.get('parent_id'),
                        "count": 0
                    })
                logger.info(f"[SOURCE: unopim_categories] Found {len(categories)} categories")
            except Exception as e:
                logger.warning(f"Could not fetch from unopim_categories: {str(e)}")
            
            # If no categories found, extract from products
            if not categories:
                products = await db.find_products({"status": "active"})
                category_counts = {}
                
                for product in products:
                    for cat in (product.get('categories') or []):
                        if cat:
                            category_counts[cat] = category_counts.get(cat, 0) + 1
                
                for slug, count in category_counts.items():
                    categories.append({
                        "slug": slug,
                        "name": slug.replace('_', ' ').title(),
                        "count": count
                    })
                
                logger.info(f"[SOURCE: unopim_products] Extracted {len(categories)} categories from products")
            
            return WPRestResponse(
                success=True,
                data=categories
            )
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{sku}", response_model=WPRestResponse)
    async def get_product(sku: str):
        """Get single product by SKU from unopim_products"""
        try:
            logger.info(f"[PRODUCTS] Getting product by SKU: {sku}")
            
            product = await db.find_product_by_sku(sku)
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            logger.info(f"[SOURCE: unopim_products] Found product: {sku}")
            
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
            logger.info(f"[PRODUCTS] Getting relationships for: {sku}")
            
            product = await db.find_product_by_sku(sku)
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Get related products (those referenced in relationships)
            related_products = []
            for rel_type, targets in product.get('relationships', {}).items():
                for target_sku in targets:
                    # Try to find the target product
                    target_product = await db.find_product_by_sku(target_sku)
                    if target_product:
                        related_products.append({
                            "sku": target_sku,
                            "relationship_type": rel_type,
                            "data": target_product
                        })
                    else:
                        # Virtual relationship (not a product SKU)
                        related_products.append({
                            "sku": target_sku,
                            "relationship_type": rel_type,
                            "data": {
                                "id": target_sku,
                                "sku": target_sku,
                                "title": target_sku.replace('_', ' ').upper(),
                                "type": "virtual"
                            }
                        })
            
            logger.info(f"[SOURCE: unopim_products] Found {len(related_products)} relationships for {sku}")
            
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
    
    return router
