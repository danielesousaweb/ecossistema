from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
import logging
import json
import asyncio
from datetime import datetime

from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")

manager = ConnectionManager()

def setup_routes(db, sync_engine, graph_builder):
    """Setup routes with dependencies"""
    
    @router.get("/complete", response_model=WPRestResponse)
    async def get_complete_graph():
        """Get complete graph structure for 3D visualization"""
        try:
            graph = await graph_builder.build_complete_graph()
            return WPRestResponse(
                success=True,
                data=graph
            )
        except Exception as e:
            logger.error(f"Error building graph: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/node/{node_id}", response_model=WPRestResponse)
    async def get_node_details(node_id: str):
        """Get detailed information about a specific node"""
        try:
            details = await graph_builder.get_node_details(node_id)
            if not details:
                raise HTTPException(status_code=404, detail="Node not found")
            
            return WPRestResponse(
                success=True,
                data=details
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching node {node_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/clusters", response_model=WPRestResponse)
    async def get_clusters():
        """Get graph clusters for filtering"""
        try:
            graph = await graph_builder.build_complete_graph()
            return WPRestResponse(
                success=True,
                data=graph['clusters']
            )
        except Exception as e:
            logger.error(f"Error fetching clusters: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket for real-time graph updates"""
        await manager.connect(websocket)
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                # Echo back for now (in production, handle specific commands)
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            manager.disconnect(websocket)
    
    # Helper function to broadcast graph updates
    async def broadcast_graph_update(update_type: str, data: dict):
        """Broadcast graph updates to all connected clients"""
        await manager.broadcast({
            "type": "graph_update",
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    # Store broadcast function for use in webhooks
    router.broadcast_graph_update = broadcast_graph_update
    
    return router
