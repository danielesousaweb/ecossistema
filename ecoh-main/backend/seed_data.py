#!/usr/bin/env python3
"""
Seed database with mock Unopim data
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

from services.unopim_connector import UopimConnector
from services.sync_engine import SyncEngine
from services.graph_builder import GraphBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

async def seed_database():
    """Seed database with mock data"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        logger.info("Connected to MongoDB")
        
        # Clear existing data
        logger.info("Clearing existing data...")
        await db.hemera_products.delete_many({})
        await db.acf_schema.delete_many({})
        await db.webhook_events.delete_many({})
        await db.sync_logs.delete_many({})
        
        # Initialize services
        unopim_connector = UopimConnector()
        await unopim_connector.connect()
        
        sync_engine = SyncEngine(db)
        graph_builder = GraphBuilder(db)
        
        # Fetch mock products
        logger.info("Fetching mock products from Unopim...")
        products = await unopim_connector.fetch_products()
        logger.info(f"Fetched {len(products)} products")
        
        # Sync all products
        logger.info("Syncing products...")
        results = await sync_engine.sync_all_products(products)
        logger.info(f"Sync results: {results}")
        
        # Build initial graph
        logger.info("Building graph structure...")
        graph = await graph_builder.build_complete_graph()
        logger.info(f"Graph built: {graph['stats']}")
        
        # Display summary
        print("\n" + "="*60)
        print("DATABASE SEEDED SUCCESSFULLY")
        print("="*60)
        print(f"Products synced: {results['synced']}")
        print(f"New fields detected: {len(results['new_fields'])}")
        print(f"Graph nodes: {graph['stats']['total_nodes']}")
        print(f"Graph edges: {graph['stats']['total_edges']}")
        print(f"Clusters: {graph['stats']['total_clusters']}")
        print("="*60 + "\n")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database())