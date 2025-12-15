from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Import database (direct Unopim connection)
from database import db

# Import services
from services.unopim_connector import UopimConnector
from services.sync_engine import SyncEngine
from services.graph_builder import GraphBuilder

# Import routes
from routes import products, graph, webhooks, topicos

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize services (will be set after db connection)
unopim_connector = None
sync_engine = None
graph_builder = None

# Create the main app
app = FastAPI(
    title="CAS Tecnologia Ecosystem API - Direct Unopim",
    description="API conectada diretamente às tabelas do Unopim (unopim_products, unopim_attributes, unopim_categories)",
    version="3.0.0-direct"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Basic routes
@api_router.get("/")
async def root():
    return {
        "message": "CAS Tecnologia Ecosystem API - Direct Unopim Connection",
        "version": "3.0.0-direct",
        "database": "MySQL (Direct Unopim Tables)",
        "tables": {
            "products": "unopim_products",
            "attributes": "unopim_attributes",
            "categories": "unopim_categories"
        },
        "endpoints": {
            "products": "/api/products",
            "graph": "/api/graph",
            "webhooks": "/api/webhooks",
            "topicos": "/api/topicos"
        }
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        products_count = await db.count_products()
        return {
            "status": "healthy",
            "database": "connected",
            "mode": "direct_unopim",
            "products_count": products_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    """Create a status check (in-memory only, no database table needed)"""
    status_obj = StatusCheck(
        client_name=input.client_name,
        timestamp=datetime.now(timezone.utc)
    )
    return status_obj

@api_router.get("/status")
async def get_status():
    """Get API status"""
    return {
        "api_version": "3.0.0-direct",
        "mode": "direct_unopim",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    global unopim_connector, sync_engine, graph_builder
    
    logger = logging.getLogger(__name__)
    logger.info("========================================")
    logger.info("Starting CAS Ecosystem API - Direct Unopim Mode")
    logger.info("========================================")
    
    # Connect to MySQL (Unopim database)
    await db.connect()
    logger.info("MySQL connection established to Unopim database")
    logger.info("Using tables: unopim_products, unopim_attributes, unopim_categories")
    
    # Initialize services
    unopim_connector = UopimConnector()
    await unopim_connector.connect()
    
    sync_engine = SyncEngine(db)
    graph_builder = GraphBuilder(db)
    
    # Setup feature routes with dependencies
    products_router = products.setup_routes(db, sync_engine, graph_builder)
    graph_router = graph.setup_routes(db, sync_engine, graph_builder)
    webhooks_router = webhooks.setup_routes(db, sync_engine, graph_builder, unopim_connector)
    topicos_router = topicos.setup_routes(db, sync_engine, graph_builder)
    
    # Include all routers
    api_router.include_router(products_router)
    api_router.include_router(graph_router)
    api_router.include_router(webhooks_router)
    api_router.include_router(topicos_router)
    
    logger.info("All services initialized successfully")
    logger.info("API ready to serve requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db.close()


# Include the main router in the app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
