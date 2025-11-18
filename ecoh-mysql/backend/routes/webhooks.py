from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime, timezone

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
            # Get last sync log from MySQL
            query = "SELECT * FROM sync_logs ORDER BY timestamp DESC LIMIT 1"
            last_sync = None
            
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    row = await cursor.fetchone()
                    if row:
                        last_sync = dict(zip(columns, row))
            
            # Get product stats
            count_query = "SELECT COUNT(*) as total FROM hemera_products"
            active_query = "SELECT COUNT(*) as active FROM hemera_products WHERE status = 'active'"
            
            total_products = 0
            active_products = 0
            
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(count_query)
                    result = await cursor.fetchone()
                    total_products = result[0] if result else 0
                    
                    await cursor.execute(active_query)
                    result = await cursor.fetchone()
                    active_products = result[0] if result else 0
            
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
                
                logger.info(f"Product {product_data.get('sku')} synced")
                
            elif event.event_type == "delete":
                # Mark as discontinued
                await sync_engine.handle_discontinued_product(event.entity_id)
                logger.info(f"Product {event.entity_id} marked discontinued")
        
        # Log event to MySQL
        await db.insert_webhook_event({
            "event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "data": event.data,
            "timestamp": datetime.now(timezone.utc),
            "processed": True
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook event: {str(e)}")
        # Log error
        await db.insert_webhook_event({
            "event_type": event.event_type,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "data": {"error": str(e)},
            "timestamp": datetime.now(timezone.utc),
            "processed": False
        })

async def perform_full_sync(db, sync_engine, unopim_connector):
    """Perform full sync from Unopim"""
    start_time = datetime.now(timezone.utc)
    try:
        logger.info("Starting full sync")
        
        # Log sync start
        sync_log_id = await db.insert_sync_log({
            "product_id": None,
            "action": "full_sync",
            "status": "running",
            "message": "Starting full sync",
            "duration_ms": None,
            "timestamp": start_time
        })
        
        # Fetch all products from Unopim
        products = await unopim_connector.fetch_products()
        
        # Sync all products
        results = await sync_engine.sync_all_products(products)
        
        # Calculate duration
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Update sync log
        query = "UPDATE sync_logs SET status = %s, message = %s, duration_ms = %s WHERE id = %s"
        async with db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (
                    "completed",
                    f"Synced {results['synced']} products",
                    duration_ms,
                    sync_log_id
                ))
        
        logger.info(f"Full sync completed in {duration_ms}ms: {results}")
        
    except Exception as e:
        logger.error(f"Error during full sync: {str(e)}")
        # Log error
        await db.insert_sync_log({
            "product_id": None,
            "action": "full_sync",
            "status": "failed",
            "message": str(e),
            "duration_ms": None,
            "timestamp": datetime.now(timezone.utc)
        })
