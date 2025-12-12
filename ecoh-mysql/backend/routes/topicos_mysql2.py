from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
import json

from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topicos", tags=["topicos"])

def setup_routes(db, sync_engine, graph_builder):
    """Setup routes with dependencies"""
    
    @router.get("", response_model=WPRestResponse)
    async def listar_todos_topicos():
        """Lista todos os tópicos disponíveis dinamicamente"""
        try:
            # Buscar todos os produtos ativos
            products = await db.find_products({"status": "active"})
            
            # Extrair valores únicos
            valores_encontrados = {
                "protocolos": set(),
                "caracteristicas": set(),
                "mdcs": set(),
                "tipo_integracao": set(),
                "hemera": set(),
                "comunicacao": set(),
                "fabricantes": set(),
                "modelos": set()
            }
            
            for product in products:
                relationships = product.get('relationships', {})
                attributes = product.get('attributes', {})
                
                # Protocolos
                if 'protocolo' in relationships and relationships['protocolo']:
                    valores_encontrados['protocolos'].update(relationships['protocolo'])
                
                # Características
                if 'caracterssticas' in relationships and relationships['caracterssticas']:
                    valores_encontrados['caracteristicas'].update(relationships['caracterssticas'])
                
                # MDCs
                if 'mdcs' in relationships and relationships['mdcs']:
                    valores_encontrados['mdcs'].update(relationships['mdcs'])
                
                # Tipo Integração
                if 'tipo_integracao' in relationships and relationships['tipo_integracao']:
                    valores_encontrados['tipo_integracao'].update(relationships['tipo_integracao'])
                
                # Hemera
                if 'modulos_hemera' in relationships and relationships['modulos_hemera']:
                    valores_encontrados['hemera'].update(relationships['modulos_hemera'])
                
                # Comunicação
                if 'comunicacao' in relationships and relationships['comunicacao']:
                    valores_encontrados['comunicacao'].update(relationships['comunicacao'])
                
                # Fabricantes e Modelos
                if 'fabricante_medidor' in attributes:
                    valores_encontrados['fabricantes'].add(attributes['fabricante_medidor'])
                if 'modelo_medidor' in attributes:
                    valores_encontrados['modelos'].add(attributes['modelo_medidor'])
            
            # Construir estrutura de tópicos
            topicos_estruturados = {
                "medidores": {
                    "id": "medidores",
                    "nome": "Medidores",
                    "tipo": "categoria",
                    "icone": "📟",
                    "cor": "#00ff88",
                    "subtopicos": [
                        {
                            "id": "fabricantes",
                            "nome": "Fabricantes",
                            "valores": sorted(list(valores_encontrados['fabricantes'])),
                            "count": len(valores_encontrados['fabricantes'])
                        },
                        {
                            "id": "modelos",
                            "nome": "Modelos",
                            "valores": sorted(list(valores_encontrados['modelos'])),
                            "count": len(valores_encontrados['modelos'])
                        }
                    ]
                },
                "protocolos": {
                    "id": "protocolos",
                    "nome": "Protocolos",
                    "tipo": "grupo",
                    "icone": "🔌",
                    "cor": "#4ecdc4",
                    "valores": sorted(list(valores_encontrados['protocolos'])),
                    "count": len(valores_encontrados['protocolos'])
                },
                "caracteristicas": {
                    "id": "caracteristicas",
                    "nome": "Características",
                    "tipo": "grupo",
                    "icone": "⚡",
                    "cor": "#f7b731",
                    "valores": sorted(list(valores_encontrados['caracteristicas'])),
                    "count": len(valores_encontrados['caracteristicas'])
                },
                "mdcs": {
                    "id": "mdcs",
                    "nome": "MDCs",
                    "tipo": "grupo",
                    "icone": "🖥️",
                    "cor": "#45b7d1",
                    "valores": sorted(list(valores_encontrados['mdcs'])),
                    "count": len(valores_encontrados['mdcs'])
                },
                "tipo_integracao": {
                    "id": "tipo_integracao",
                    "nome": "Tipo de Integração",
                    "tipo": "grupo",
                    "icone": "🔗",
                    "cor": "#a55eea",
                    "valores": sorted(list(valores_encontrados['tipo_integracao'])),
                    "count": len(valores_encontrados['tipo_integracao'])
                },
                "hemera": {
                    "id": "hemera",
                    "nome": "Hemera",
                    "tipo": "grupo",
                    "icone": "🌟",
                    "cor": "#ff6b6b",
                    "valores": sorted(list(valores_encontrados['hemera'])),
                    "count": len(valores_encontrados['hemera'])
                },
                "comunicacao": {
                    "id": "comunicacao",
                    "nome": "Comunicação",
                    "tipo": "grupo",
                    "icone": "📡",
                    "cor": "#26de81",
                    "valores": sorted(list(valores_encontrados['comunicacao'])),
                    "count": len(valores_encontrados['comunicacao'])
                },
                "mobii": {
                    "id": "mobii",
                    "nome": "MOBii",
                    "tipo": "feature",
                    "icone": "📱",
                    "cor": "#fd79a8"
                }
            }
            
            return WPRestResponse(
                success=True,
                data=topicos_estruturados
            )
        
        except Exception as e:
            logger.error(f"Erro ao listar tópicos: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/produtos-por-topico", response_model=WPRestResponse)
    async def buscar_produtos_por_topico(
        campo: str = Query(..., description="Campo do tópico (ex: protocolo, mdcs)"),
        valor: Optional[str] = Query(None, description="Valor específico do campo"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """Busca produtos que possuem um determinado tópico/valor"""
        try:
            if not valor:
                return WPRestResponse(
                    success=True,
                    data=[],
                    total=0
                )
            
            # Buscar produtos que contêm o valor no campo especificado
            # Pode estar em relationships ou attributes
            query = """
                SELECT * FROM hemera_products 
                WHERE status = 'active' 
                AND (
                    JSON_SEARCH(relationships, 'one', %s, NULL, CONCAT('$.', %s)) IS NOT NULL
                    OR JSON_SEARCH(attributes, 'one', %s) IS NOT NULL
                    OR sku LIKE %s
                    OR title LIKE %s
                )
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """
            
            valor_pattern = f"%{valor}%"
            skip = (page - 1) * per_page
            params = [valor, campo, valor, valor_pattern, valor_pattern, per_page, skip]
            
            products = []
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    columns = [desc[0] for desc in cursor.description]
                    rows = await cursor.fetchall()
                    
                    for row in rows:
                        product = dict(zip(columns, row))
                        db._parse_json_fields(product)
                        products.append(product)
            
            # Contar total
            count_query = """
                SELECT COUNT(*) as total FROM hemera_products 
                WHERE status = 'active' 
                AND (
                    JSON_SEARCH(relationships, 'one', %s, NULL, CONCAT('$.', %s)) IS NOT NULL
                    OR JSON_SEARCH(attributes, 'one', %s) IS NOT NULL
                    OR sku LIKE %s
                    OR title LIKE %s
                )
            """
            count_params = [valor, campo, valor, valor_pattern, valor_pattern]
            
            total = 0
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(count_query, count_params)
                    result = await cursor.fetchone()
                    total = result[0] if result else 0
            
            return WPRestResponse(
                success=True,
                data=products,
                total=total,
                page=page,
                per_page=per_page
            )
        
        except Exception as e:
            logger.error(f"Erro ao buscar produtos por tópico: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/busca-global", response_model=WPRestResponse)
    async def busca_global(
        q: str = Query(..., description="Termo de busca"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """Busca global em produtos e tópicos"""
        try:
            q_lower = q.lower()
            
            # Busca simples por SKU e título
            search_pattern = f"%{q}%"
            where_clause = "status = 'active' AND (sku LIKE %s OR title LIKE %s)"
            params = [search_pattern, search_pattern]
            
            # Contar total
            count_query = f"SELECT COUNT(*) as total FROM hemera_products WHERE {where_clause}"
            total = 0
            
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(count_query, params)
                    result = await cursor.fetchone()
                    total = result[0] if result else 0
            
            # Buscar produtos paginados
            skip = (page - 1) * per_page
            query = f"SELECT * FROM hemera_products WHERE {where_clause} ORDER BY updated_at DESC LIMIT %s OFFSET %s"
            params_with_limit = params + [per_page, skip]
            
            products = []
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params_with_limit)
                    columns = [desc[0] for desc in cursor.description]
                    rows = await cursor.fetchall()
                    
                    for row in rows:
                        product = dict(zip(columns, row))
                        db._parse_json_fields(product)
                        products.append(product)
            
            # Buscar em tópicos
            topicos_response = await listar_todos_topicos()
            topicos = topicos_response.data
            
            topicos_match = []
            for key, topico in topicos.items():
                if q_lower in topico['nome'].lower():
                    topicos_match.append(topico)
                elif 'valores' in topico:
                    for valor in topico['valores']:
                        if q_lower in valor.lower():
                            topicos_match.append({
                                **topico,
                                "valor_encontrado": valor
                            })
                            break
            
            return WPRestResponse(
                success=True,
                data={
                    "produtos": products,
                    "topicos": topicos_match,
                    "total_produtos": total,
                    "total_topicos": len(topicos_match)
                },
                total=total + len(topicos_match),
                page=page,
                per_page=per_page
            )
        
        except Exception as e:
            logger.error(f"Erro na busca global: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
