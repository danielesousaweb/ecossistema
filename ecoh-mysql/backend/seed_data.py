#!/usr/bin/env python3
"""
Seed MySQL database with mock Unopim data
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import db
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
        # Connect to MySQL
        await db.connect()
        logger.info("Connected to MySQL")
        
        # Clear existing data
        logger.info("Clearing existing data...")
        async with db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM hemera_products")
                await cursor.execute("DELETE FROM acf_schema")
                await cursor.execute("DELETE FROM webhook_events")
                await cursor.execute("DELETE FROM sync_logs")
                await cursor.execute("DELETE FROM status_checks")
        
        logger.info("Database cleared")
        
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
        
        await db.close()
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(seed_database())
