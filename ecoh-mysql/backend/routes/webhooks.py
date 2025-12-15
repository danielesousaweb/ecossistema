from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime, timezone

from models.unopim_models import SyncEvent
from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def setup_routes(db, sync_engine, graph_builder, unopim_connector):
    """
    Setup webhook routes
    
    Note: With direct Unopim integration, webhooks are simplified.
    Data is always fresh from unopim_products table.
    Webhooks are kept for cache invalidation notifications only.
    """
    
    @router.post("/unopim", response_model=WPRestResponse)
    async def unopim_webhook(event: SyncEvent):
        """
        Webhook endpoint for Unopim notifications
        
        With direct Unopim integration, this is used only for:
        - Cache invalidation (if implemented)
        - Logging/auditing
        - Real-time update notifications
        """
        try:
            logger.info(f"[WEBHOOK] Received: {event.event_type} for {event.entity_type} {event.entity_id}")
            
            # Just acknowledge - data is read directly from Unopim
            return WPRestResponse(
                success=True,
                message=f"Webhook received: {event.event_type} for {event.entity_type}"
            )
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/sync-status", response_model=WPRestResponse)
    async def get_sync_status():
        """
        Get current database status
        With direct Unopim integration, shows live stats from unopim_products
        """
        try:
            logger.info("[WEBHOOK] Getting sync status")
            
            # Get product stats directly from unopim_products
            total_products = await db.count_products()
            active_products = await db.count_products({"status": "active"})
            
            # Get attributes count
            try:
                attributes = await db.find_attributes()
                total_attributes = len(attributes)
            except:
                total_attributes = 0
            
            # Get categories count
            try:
                categories = await db.find_categories()
                total_categories = len(categories)
            except:
                total_categories = 0
            
            logger.info(f"[SOURCE: unopim_products] Stats: {total_products} total, {active_products} active")
            
            return WPRestResponse(
                success=True,
                data={
                    "mode": "direct_unopim",
                    "description": "Lendo diretamente das tabelas do Unopim",
                    "tables": {
                        "products": "unopim_products",
                        "attributes": "unopim_attributes",
                        "categories": "unopim_categories"
                    },
                    "stats": {
                        "total_products": total_products,
                        "active_products": active_products,
                        "total_attributes": total_attributes,
                        "total_categories": total_categories
                    },
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error fetching sync status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/trigger-sync", response_model=WPRestResponse)
    async def trigger_manual_sync():
        """
        With direct Unopim integration, sync is not needed.
        This endpoint just returns current status.
        """
        logger.info("[WEBHOOK] Sync not needed - using direct Unopim connection")
        
        return WPRestResponse(
            success=True,
            message="Sync não é necessário - dados são lidos diretamente do Unopim",
            data={
                "mode": "direct_unopim",
                "sync_required": False
            }
        )
    
    return router
