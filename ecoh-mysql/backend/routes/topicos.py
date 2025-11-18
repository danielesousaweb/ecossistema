from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topicos", tags=["topicos"])

# Mapeamento de tópicos em português
TOPICOS_CONFIG = {
    "medidores": {
        "nome": "Medidores",
        "tipo": "categoria",
        "campos": ["fabricante_medidor", "modelo_medidor", "senha_medidor"]
    },
    "protocolos": {
        "nome": "Protocolos",
        "tipo": "grupo",
        "campo_relacionamento": "protocolo",
        "valores": ["abnt", "modbus", "ansi", "dlms", "ion", "iec", "pima", "irda"]
    },
    "caracteristicas": {
        "nome": "Características",
        "tipo": "grupo",
        "campo_relacionamento": "caracterssticas",
        "valores": [
            "registrador", "fasorial", "memoria_massa", "eventos",
            "tarifa_branca", "qualidade", "gd", "parametrizacao",
            "corte_religue", "comandos_smc"
        ]
    },
    "mdcs": {
        "nome": "MDCs",
        "tipo": "grupo",
        "campo_relacionamento": "mdcs",
        "valores": ["mdc_iris", "sanplat", "orca", "command_center", "ims", "sade"]
    },
    "tipo_integracao": {
        "nome": "Tipo de Integração",
        "tipo": "grupo",
        "campo_relacionamento": "tipo_integracao",
        "valores": ["int_cas", "cas_appia_json", "int_iec61698", "int_terceiros"]
    },
    "hemera": {
        "nome": "Hemera",
        "tipo": "grupo",
        "campo_relacionamento": "modulos_hemera",
        "valores": ["CI", "R", "RS", "F"]
    },
    "mobii": {
        "nome": "MOBii",
        "tipo": "atributo",
        "campo": "mobii"
    },
    "comunicacao": {
        "nome": "Comunicação",
        "tipo": "grupo",
        "campo_relacionamento": "comunicacao",
        "valores": ["4g", "wifi", "ethernet", "gprs", "lora"]
    }
}

def setup_routes(db, sync_engine, graph_builder):
    """Setup routes with dependencies"""
    
    @router.get("", response_model=WPRestResponse)
    async def listar_todos_topicos():
        """
        Lista todos os tópicos disponíveis dinamicamente
        Analisa produtos no banco e gera lista unificada
        """
        try:
            topicos_dinamicos = []
            
            # Buscar todos os produtos ativos
            products = await db.hemera_products.find({"status": "active"}).to_list(1000)
            
            # Extrair valores únicos de todos os campos de relacionamento
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
                if 'protocolo' in relationships:
                    valores_encontrados['protocolos'].update(relationships['protocolo'])
                
                # Características
                if 'caracterssticas' in relationships:
                    valores_encontrados['caracteristicas'].update(relationships['caracterssticas'])
                
                # MDCs
                if 'mdcs' in relationships:
                    valores_encontrados['mdcs'].update(relationships['mdcs'])
                
                # Tipo Integração
                if 'tipo_integracao' in relationships:
                    valores_encontrados['tipo_integracao'].update(relationships['tipo_integracao'])
                
                # Hemera
                if 'modulos_hemera' in relationships:
                    valores_encontrados['hemera'].update(relationships['modulos_hemera'])
                
                # Comunicação
                if 'comunicacao' in relationships:
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
        nome: str = Query(..., description="Nome do tópico ou valor"),
        categoria: Optional[str] = Query(None, description="Categoria do tópico"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """
        Retorna produtos associados a um tópico específico
        """
        try:
            nome_lower = nome.lower()
            query = {"status": "active"}
            
            # Construir query baseada no tópico
            if categoria == "protocolos":
                query["relationships.protocolo"] = {"$in": [nome_lower]}
            elif categoria == "caracteristicas":
                query["relationships.caracterssticas"] = {"$in": [nome_lower]}
            elif categoria == "mdcs":
                query["relationships.mdcs"] = {"$regex": nome_lower, "$options": "i"}
            elif categoria == "tipo_integracao":
                query["relationships.tipo_integracao"] = {"$in": [nome_lower]}
            elif categoria == "hemera":
                query["relationships.modulos_hemera"] = {"$in": [nome_lower.upper()]}
            elif categoria == "comunicacao":
                query["relationships.comunicacao"] = {"$in": [nome_lower]}
            elif categoria == "fabricante":
                query["attributes.fabricante_medidor"] = {"$regex": nome_lower, "$options": "i"}
            elif categoria == "modelo":
                query["attributes.modelo_medidor"] = {"$regex": nome_lower, "$options": "i"}
            elif categoria == "mobii":
                query["attributes.mobii"] = "true"
            else:
                # Busca genérica em todos os campos
                query["$or"] = [
                    {"relationships.protocolo": {"$in": [nome_lower]}},
                    {"relationships.caracterssticas": {"$in": [nome_lower]}},
                    {"relationships.mdcs": {"$regex": nome_lower, "$options": "i"}},
                    {"relationships.tipo_integracao": {"$in": [nome_lower]}},
                    {"relationships.comunicacao": {"$in": [nome_lower]}},
                    {"attributes.fabricante_medidor": {"$regex": nome_lower, "$options": "i"}},
                    {"attributes.modelo_medidor": {"$regex": nome_lower, "$options": "i"}},
                    {"sku": {"$regex": nome, "$options": "i"}},
                    {"title": {"$regex": nome, "$options": "i"}}
                ]
            
            # Contar total
            total = await db.hemera_products.count_documents(query)
            
            # Buscar produtos paginados
            skip = (page - 1) * per_page
            products = await db.hemera_products.find(query, {"_id": 0}).skip(skip).limit(per_page).to_list(per_page)
            
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
        """
        Busca global em produtos e tópicos
        """
        try:
            q_lower = q.lower()
            
            # Busca em produtos
            query = {
                "status": "active",
                "$or": [
                    {"sku": {"$regex": q, "$options": "i"}},
                    {"title": {"$regex": q, "$options": "i"}},
                    {"attributes.fabricante_medidor": {"$regex": q_lower, "$options": "i"}},
                    {"attributes.modelo_medidor": {"$regex": q_lower, "$options": "i"}},
                    {"relationships.protocolo": {"$in": [q_lower]}},
                    {"relationships.caracterssticas": {"$in": [q_lower]}},
                    {"relationships.mdcs": {"$regex": q_lower, "$options": "i"}},
                    {"relationships.tipo_integracao": {"$in": [q_lower]}},
                    {"relationships.comunicacao": {"$in": [q_lower]}}
                ]
            }
            
            # Contar e buscar
            total = await db.hemera_products.count_documents(query)
            skip = (page - 1) * per_page
            products = await db.hemera_products.find(query, {"_id": 0}).skip(skip).limit(per_page).to_list(per_page)
            
            # Buscar em tópicos também
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
