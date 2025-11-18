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

# Import database
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
    title="CAS Tecnologia Ecosystem API - MySQL Edition",
    description="WordPress-compatible API for Unopim product synchronization with MySQL backend",
    version="2.0.0-mysql"
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
        "message": "CAS Tecnologia Ecosystem API - MySQL Edition",
        "version": "2.0.0-mysql",
        "database": "MySQL 8.0",
        "endpoints": {
            "products": "/api/products",
            "graph": "/api/graph",
            "webhooks": "/api/webhooks",
            "topicos": "/api/topicos"
        }
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict for database
    doc = status_obj.model_dump()
    
    # Insert to MySQL
    await db.insert_status_check(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Get from MySQL
    status_checks = await db.find_status_checks()
    
    # Convert to response models
    result = []
    for check in status_checks:
        result.append(StatusCheck(**check))
    
    return result


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    global unopim_connector, sync_engine, graph_builder
    
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")
    
    # Connect to MySQL
    await db.connect()
    logger.info("MySQL connection established")
    
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
