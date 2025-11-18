from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime

from models.unopim_models import SyncEvent
from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def setup_routes(db, sync_engine, graph_builder, unopim_connector):
    """Setup routes with dependencies"""
    
    @router.post("/unopim", response_model=WPRestResponse)
    async def unopim_webhook(event: SyncEvent, background_tasks: BackgroundTasks):
        """
        Webhook endpoint for Unopim real-time sync
        
        Unopim should send POST requests here when:
        - Product created
        - Product updated
        - Product deleted
        - Attribute schema changed
        """
        try:
            logger.info(f"Received webhook: {event.event_type} for {event.entity_type} {event.entity_id}")
            
            # Process in background to respond quickly
            background_tasks.add_task(
                process_webhook_event,
                event,
                db,
                sync_engine,
                graph_builder,
                unopim_connector
            )
            
            return WPRestResponse(
                success=True,
                message=f"Webhook received and processing in background"
            )
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/trigger-sync", response_model=WPRestResponse)
    async def trigger_manual_sync(background_tasks: BackgroundTasks):
        """Manually trigger full sync from Unopim"""
        try:
            logger.info("Manual sync triggered")
            
            background_tasks.add_task(
                perform_full_sync,
                db,
                sync_engine,
                unopim_connector
            )
            
            return WPRestResponse(
                success=True,
                message="Full sync initiated"
            )
        except Exception as e:
            logger.error(f"Error triggering sync: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/sync-status", response_model=WPRestResponse)
    async def get_sync_status():
        """Get current sync status"""
        try:
            # Get last sync info
            last_sync = await db.sync_logs.find_one(
                {},
                sort=[("started_at", -1)]
            )
            
            # Get stats
            total_products = await db.hemera_products.count_documents({})
            active_products = await db.hemera_products.count_documents({"status": "active"})
            
            return WPRestResponse(
                success=True,
                data={
                    "last_sync": last_sync,
                    "stats": {
                        "total_products": total_products,
                        "active_products": active_products
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error fetching sync status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router

async def process_webhook_event(
    event: SyncEvent,
    db,
    sync_engine,
    graph_builder,
    unopim_connector
):
    """Process webhook event in background"""
    try:
        if event.entity_type == "product":
            if event.event_type in ["create", "update"]:
                # Fetch product data from Unopim
                product_data = event.data
                
                # Sync product
                result = await sync_engine.sync_product(product_data)
                
                # Rebuild graph (could be optimized to only update affected nodes)
                # For now, we'll just log it
                logger.info(f"Product {product_data.get('sku')} synced")
                
                # In production, broadcast to WebSocket clients
                # await graph_router.broadcast_graph_update("product_updated", result)
                
            elif event.event_type == "delete":
                # Mark as discontinued
                await sync_engine.handle_discontinued_product(event.entity_id)
                logger.info(f"Product {event.entity_id} marked discontinued")
        
        # Log event
        await db.webhook_events.insert_one({
            "event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "processed_at": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook event: {str(e)}")
        # Log error
        await db.webhook_events.insert_one({
            "event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "processed_at": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        })

async def perform_full_sync(db, sync_engine, unopim_connector):
    """Perform full sync from Unopim"""
    try:
        start_time = datetime.now()
        logger.info("Starting full sync")
        
        # Log sync start
        sync_log_id = await db.sync_logs.insert_one({
            "started_at": start_time.isoformat(),
            "status": "running"
        })
        
        # Fetch all products from Unopim
        products = await unopim_connector.fetch_products()
        
        # Sync all products
        results = await sync_engine.sync_all_products(products)
        
        # Update sync log
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        await db.sync_logs.update_one(
            {"_id": sync_log_id.inserted_id},
            {"$set": {
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed",
                "results": results
            }}
        )
        
        logger.info(f"Full sync completed in {duration}s: {results}")
        
    except Exception as e:
        logger.error(f"Error during full sync: {str(e)}")
        # Update sync log with error
        await db.sync_logs.update_one(
            {"_id": sync_log_id.inserted_id},
            {"$set": {
                "status": "failed",
                "error": str(e)
            }}
        )