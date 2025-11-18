import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class UopimConnector:
    """Handles connection and data retrieval from Unopim database"""
    
    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """
        Initialize connector
        
        For production, db_config should contain:
        - host, port, database, user, password for MySQL/PostgreSQL
        
        For now, we'll work with mock data
        """
        self.db_config = db_config
        self.connected = False
        
    async def connect(self):
        """Establish database connection"""
        if self.db_config:
            # In production, connect to actual Unopim database
            # import aiomysql or asyncpg
            pass
        self.connected = True
        logger.info("Unopim connector initialized (mock mode)")
        
    async def fetch_products(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Fetch products from Unopim
        
        In production, this would query:
        SELECT id, sku, status, type, parent_id, attribute_family_id, 
               values, additional, created_at, updated_at
        FROM products
        WHERE status = 1
        """
        # Mock implementation returns sample data
        return self._get_mock_products()
    
    async def fetch_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single product by ID"""
        products = await self.fetch_products()
        for p in products:
            if p['id'] == product_id:
                return p
        return None
    
    async def fetch_attributes(self) -> List[Dict[str, Any]]:
        """
        Fetch attribute definitions
        
        SELECT code, type, is_required, is_unique, is_filterable, position
        FROM attributes
        """
        return self._get_mock_attributes()
    
    async def fetch_categories(self) -> List[Dict[str, Any]]:
        """
        Fetch category tree
        
        SELECT id, code, parent_id, additional_data
        FROM categories
        """
        return self._get_mock_categories()
    
    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate MD5 checksum of JSON data for change detection"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _get_mock_products(self) -> List[Dict[str, Any]]:
        """Mock product data based on Unopim schema"""
        return [
            {
                "id": 1,
                "sku": "E750G2",
                "status": 1,
                "type": "simple",
                "parent_id": None,
                "attribute_family_id": 4,
                "values": {
                    "common": {
                        "sku": "E750G2",
                        "mdcs": "mdc_iris",
                        "nics": "nic_cas",
                        "mobii": "true",
                        "Remotas": "rs2000",
                        "protocolo": "abnt",
                        "comunicacao": "4g",
                        "tipo_medicao": "MCI",
                        "senha_medidor": "true",
                        "modelo_medidor": "8721",
                        "modulos_hemera": "CI,RS,F",
                        "caracterssticas": "registrador,fasorial,memoria_massa,eventos,tarifa_branca,qualidade,gd,parametrizacao,corte_religue",
                        "tipo_integracao": "int_cas,int_iec61698",
                        "fabricante_medidor": "ladisgyr"
                    },
                    "categories": ["medidores"]
                },
                "additional": None,
                "avg_completeness_score": 95,
                "created_at": "2025-11-05T22:59:58Z",
                "updated_at": "2025-11-05T23:18:58Z"
            },
            {
                "id": 2,
                "sku": "E650G3",
                "status": 1,
                "type": "simple",
                "parent_id": None,
                "attribute_family_id": 4,
                "values": {
                    "common": {
                        "sku": "E650G3",
                        "mdcs": "mdc_iris,mdc_hemera",
                        "nics": "nic_cas,nic_terceiros",
                        "mobii": "false",
                        "Remotas": "rs2000,rs3000",
                        "protocolo": "abnt,iec",
                        "comunicacao": "wifi,ethernet",
                        "tipo_medicao": "MCI,MCF",
                        "senha_medidor": "true",
                        "modelo_medidor": "8722",
                        "modulos_hemera": "CI,RS,F,M",
                        "caracterssticas": "registrador,fasorial,memoria_massa,eventos,tarifa_branca",
                        "tipo_integracao": "int_cas,int_terceiros",
                        "fabricante_medidor": "nansen"
                    },
                    "categories": ["medidores", "hardwares"]
                },
                "additional": None,
                "avg_completeness_score": 88,
                "created_at": "2025-11-04T15:30:00Z",
                "updated_at": "2025-11-05T10:22:15Z"
            },
            {
                "id": 3,
                "sku": "RS2000-PRO",
                "status": 1,
                "type": "simple",
                "parent_id": None,
                "attribute_family_id": 5,
                "values": {
                    "common": {
                        "sku": "RS2000-PRO",
                        "tipo_remota": "concentrador",
                        "protocolo": "abnt,modbus",
                        "comunicacao": "4g,ethernet",
                        "compativel_medidores": "E750G2,E650G3",
                        "modulos": "gateway,storage,relay",
                        "caracterssticas": "tempo_real,armazenamento,relatorio"
                    },
                    "categories": ["remotas", "hardwares"]
                },
                "additional": None,
                "avg_completeness_score": 92,
                "created_at": "2025-11-03T08:15:30Z",
                "updated_at": "2025-11-04T14:45:22Z"
            },
            {
                "id": 4,
                "sku": "MDC-IRIS-V2",
                "status": 1,
                "type": "simple",
                "parent_id": None,
                "attribute_family_id": 6,
                "values": {
                    "common": {
                        "sku": "MDC-IRIS-V2",
                        "tipo_software": "mdc",
                        "compativel_medidores": "E750G2,E650G3",
                        "compativel_remotas": "RS2000-PRO",
                        "protocolo": "abnt,iec61698",
                        "funcionalidades": "leitura,parametrizacao,eventos,qualidade,gd",
                        "integracao": "api_rest,mqtt,webhook"
                    },
                    "categories": ["software", "mdc"]
                },
                "additional": None,
                "avg_completeness_score": 90,
                "created_at": "2025-11-02T11:20:00Z",
                "updated_at": "2025-11-05T09:30:45Z"
            },
            {
                "id": 5,
                "sku": "NIC-CAS-PLUS",
                "status": 1,
                "type": "simple",
                "parent_id": None,
                "attribute_family_id": 7,
                "values": {
                    "common": {
                        "sku": "NIC-CAS-PLUS",
                        "tipo_software": "nic",
                        "compativel_mdc": "MDC-IRIS-V2,mdc_hemera",
                        "protocolo": "iec61968,iec61970",
                        "funcionalidades": "integracao_sgbd,sincronizacao,export_import",
                        "formato_dados": "xml,json,csv"
                    },
                    "categories": ["software", "integracao"]
                },
                "additional": None,
                "avg_completeness_score": 85,
                "created_at": "2025-11-01T16:45:10Z",
                "updated_at": "2025-11-03T13:22:30Z"
            }
        ]
    
    def _get_mock_attributes(self) -> List[Dict[str, Any]]:
        """Mock attribute definitions"""
        return [
            {"code": "sku", "type": "text", "is_required": True, "is_relationship": False},
            {"code": "fabricante_medidor", "type": "select", "is_required": True, "is_relationship": False},
            {"code": "modelo_medidor", "type": "text", "is_required": False, "is_relationship": False},
            {"code": "protocolo", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "comunicacao", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "mdcs", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "nics", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "Remotas", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "tipo_integracao", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "modulos_hemera", "type": "multiselect", "is_required": False, "is_relationship": True},
            {"code": "caracterssticas", "type": "multiselect", "is_required": False, "is_relationship": False},
            {"code": "mobii", "type": "boolean", "is_required": False, "is_relationship": False},
            {"code": "senha_medidor", "type": "boolean", "is_required": False, "is_relationship": False},
        ]
    
    def _get_mock_categories(self) -> List[Dict[str, Any]]:
        """Mock category tree"""
        return [
            {"id": 1, "code": "medidores", "parent_id": None, "name": "Medidores"},
            {"id": 2, "code": "remotas", "parent_id": None, "name": "Remotas"},
            {"id": 3, "code": "software", "parent_id": None, "name": "Software"},
            {"id": 4, "code": "hardwares", "parent_id": None, "name": "Hardwares"},
            {"id": 5, "code": "mdc", "parent_id": 3, "name": "MDC"},
            {"id": 6, "code": "integracao", "parent_id": 3, "name": "Integração"},
        ]