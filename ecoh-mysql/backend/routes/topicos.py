from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from models.wp_models import WPRestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topicos", tags=["topicos"])

# Mapeamento de campos para labels amigáveis
FIELD_LABELS = {
    'protocolos': 'Protocolos',
    'protocolo': 'Protocolos',
    'protocolo_comunicao': 'Protocolos',
    'tipo_medicao': 'Tipo de Medição',
    'nics': 'NICs',
    'remotas': 'Remotas',
    'comunicacao': 'Comunicação',
    'mdcs': 'MDCs',
    'tipo_integracao': 'Tipo de Integração',
    'hemera': 'Hemera',
    'mobii': 'MOBii',
    'caractersticas_medidor': 'Características',
    'caracterssticas': 'Características',
    'modulos_hemera': 'Módulos Hemera',
    'fabricante_medidor': 'Fabricantes',
    'modelo_medidor': 'Modelos'
}

# Lista fixa de fallback caso o banco esteja vazio
FALLBACK_TOPICOS = {
    "protocolos": {
        "id": "protocolos",
        "nome": "Protocolos",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#4ecdc4",
        "valores": ["abnt", "modbus", "ansi", "dlms", "ion", "iec", "pima", "irda"],
        "count": 8
    },
    "tipo_medicao": {
        "id": "tipo_medicao",
        "nome": "Tipo de Medição",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#f7b731",
        "valores": ["smi", "smc", "mci", "smlc"],
        "count": 4
    },
    "comunicacao": {
        "id": "comunicacao",
        "nome": "Comunicação",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#26de81",
        "valores": ["3g", "4g", "nb", "ethernet", "satelite", "wisun", "gridstream"],
        "count": 7
    },
    "mdcs": {
        "id": "mdcs",
        "nome": "MDCs",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#45b7d1",
        "valores": ["iris", "sanplat", "orca", "command_center", "ims", "sade"],
        "count": 6
    },
    "hemera": {
        "id": "hemera",
        "nome": "Hemera",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#ff6b6b",
        "valores": ["ci", "residencial", "residencial_smart", "fronteira"],
        "count": 4
    },
    "caracteristicas": {
        "id": "caracteristicas",
        "nome": "Características",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#a55eea",
        "valores": ["registrador", "fasorial", "memoria_massa", "eventos", "tarifa_branca", "qualidade", "gd", "parametrizacao", "corte_religue"],
        "count": 9
    },
    "tipo_integracao": {
        "id": "tipo_integracao",
        "nome": "Tipo de Integração",
        "tipo": "grupo",
        "icone": "🔵",
        "cor": "#fd79a8",
        "valores": ["cas", "cas_appia_json", "iec_61698", "terceiros"],
        "count": 4
    },
    "mobii": {
        "id": "mobii",
        "nome": "MOBii",
        "tipo": "feature",
        "icone": "🔵",
        "cor": "#00cec9"
    }
}

def setup_routes(db, sync_engine, graph_builder):
    """Setup routes with dependencies"""
    
    @router.get("", response_model=WPRestResponse)
    async def listar_todos_topicos():
        """
        Lista todos os tópicos disponíveis dinamicamente
        Lê diretamente das tabelas do Unopim (unopim_products, unopim_attributes)
        """
        try:
            logger.info("[TOPICOS] Buscando tópicos dinâmicos das tabelas Unopim")
            
            topicos_dinamicos = {}
            
            # 1. Tentar buscar atributos filtráveis da tabela unopim_attributes
            try:
                atributos = await db.find_filterable_attributes()
                logger.info(f"[SOURCE: unopim_attributes] Encontrados {len(atributos)} atributos filtráveis")
                
                for attr in atributos:
                    code = attr.get('code', '')
                    if code and code not in ['sku', 'nome_medidor', 'modelo_medidor']:
                        label = FIELD_LABELS.get(code, code.replace('_', ' ').title())
                        topicos_dinamicos[code] = {
                            "id": code,
                            "nome": label,
                            "tipo": "grupo" if attr.get('type') in ['multiselect', 'select'] else "atributo",
                            "icone": "🔵",
                            "cor": _get_color_for_field(code),
                            "valores": [],
                            "count": 0,
                            "source": "unopim_attributes"
                        }
            except Exception as e:
                logger.warning(f"[SOURCE: unopim_attributes] Erro ao buscar atributos: {str(e)}")
            
            # 2. Buscar valores únicos dos produtos ativos
            try:
                products = await db.find_products({"status": "active"})
                logger.info(f"[SOURCE: unopim_products] Encontrados {len(products)} produtos ativos")
                
                # Extrair valores únicos de todos os campos de relacionamento
                valores_por_campo = {}
                
                for product in products:
                    relationships = product.get('relationships', {})
                    attributes = product.get('attributes', {})
                    
                    # Processar relationships
                    for field, values in relationships.items():
                        if field not in valores_por_campo:
                            valores_por_campo[field] = set()
                        if isinstance(values, list):
                            valores_por_campo[field].update(values)
                        elif values:
                            valores_por_campo[field].add(str(values))
                    
                    # Processar alguns atributos específicos
                    for field in ['fabricante_medidor', 'modelo_medidor']:
                        if field in attributes and attributes[field]:
                            if field not in valores_por_campo:
                                valores_por_campo[field] = set()
                            valores_por_campo[field].add(str(attributes[field]))
                
                # Construir tópicos a partir dos valores encontrados
                for field, values in valores_por_campo.items():
                    values_list = sorted([v for v in values if v])
                    if not values_list:
                        continue
                    
                    # Normalizar nome do campo
                    normalized_field = _normalize_field_name(field)
                    label = FIELD_LABELS.get(field, FIELD_LABELS.get(normalized_field, field.replace('_', ' ').title()))
                    
                    if normalized_field in topicos_dinamicos:
                        topicos_dinamicos[normalized_field]['valores'] = values_list
                        topicos_dinamicos[normalized_field]['count'] = len(values_list)
                    else:
                        topicos_dinamicos[normalized_field] = {
                            "id": normalized_field,
                            "nome": label,
                            "tipo": "grupo",
                            "icone": "🔵",
                            "cor": _get_color_for_field(normalized_field),
                            "valores": values_list,
                            "count": len(values_list),
                            "source": "unopim_products"
                        }
                
                logger.info(f"[TOPICOS] Gerados {len(topicos_dinamicos)} tópicos dinâmicos")
                
            except Exception as e:
                logger.warning(f"[SOURCE: unopim_products] Erro ao buscar produtos: {str(e)}")
            
            # 3. Se não encontrou nada, usar fallback
            if not topicos_dinamicos:
                logger.warning("[TOPICOS] Nenhum tópico dinâmico encontrado, usando fallback")
                topicos_dinamicos = FALLBACK_TOPICOS.copy()
            
            return WPRestResponse(
                success=True,
                data=topicos_dinamicos
            )
        
        except Exception as e:
            logger.error(f"Erro ao listar tópicos: {str(e)}")
            # Retornar fallback em caso de erro
            return WPRestResponse(
                success=True,
                data=FALLBACK_TOPICOS
            )
    
    @router.get("/produtos-por-topico", response_model=WPRestResponse)
    async def buscar_produtos_por_topico(
        campo: str = Query(..., description="Campo do tópico (ex: protocolo, mdcs)"),
        valor: Optional[str] = Query(None, description="Valor específico do campo"),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """
        Retorna produtos associados a um tópico específico
        Busca diretamente na tabela unopim_products
        """
        try:
            if not valor:
                return WPRestResponse(
                    success=True,
                    data=[],
                    total=0
                )
            
            logger.info(f"[TOPICOS] Buscando produtos com {campo}={valor}")
            
            # Mapear campo normalizado para possíveis variações
            field_variations = _get_field_variations(campo)
            
            all_products = []
            for field in field_variations:
                products = await db.get_products_by_field_value(field, valor, limit=per_page * 2)
                all_products.extend(products)
            
            # Remover duplicatas por SKU
            seen_skus = set()
            unique_products = []
            for p in all_products:
                if p['sku'] not in seen_skus:
                    seen_skus.add(p['sku'])
                    unique_products.append(p)
            
            # Paginar resultados
            total = len(unique_products)
            start = (page - 1) * per_page
            end = start + per_page
            paginated = unique_products[start:end]
            
            logger.info(f"[SOURCE: unopim_products] Encontrados {total} produtos para {campo}={valor}")
            
            return WPRestResponse(
                success=True,
                data=paginated,
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
        Busca diretamente na tabela unopim_products
        """
        try:
            q_lower = q.lower().strip()
            
            logger.info(f"[TOPICOS] Busca global: {q}")
            
            # Busca em produtos
            products = await db.search_products(q, status='active', limit=per_page * 2)
            
            total = len(products)
            start = (page - 1) * per_page
            end = start + per_page
            paginated = products[start:end]
            
            # Buscar em tópicos
            topicos_response = await listar_todos_topicos()
            topicos = topicos_response.data
            
            topicos_match = []
            for key, topico in topicos.items():
                if q_lower in topico.get('nome', '').lower():
                    topicos_match.append(topico)
                elif 'valores' in topico:
                    for valor in topico['valores']:
                        if q_lower in valor.lower():
                            topicos_match.append({
                                **topico,
                                "valor_encontrado": valor
                            })
                            break
            
            logger.info(f"[SOURCE: unopim_products] Busca global encontrou {total} produtos e {len(topicos_match)} tópicos")
            
            return WPRestResponse(
                success=True,
                data={
                    "produtos": paginated,
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


# Helper functions
def _get_color_for_field(field: str) -> str:
    """Retorna cor para cada tipo de campo"""
    color_map = {
        'protocolos': '#4ecdc4',
        'protocolo': '#4ecdc4',
        'protocolo_comunicao': '#4ecdc4',
        'tipo_medicao': '#f7b731',
        'nics': '#fd79a8',
        'remotas': '#ff6b6b',
        'comunicacao': '#26de81',
        'mdcs': '#45b7d1',
        'tipo_integracao': '#a55eea',
        'hemera': '#ff6b6b',
        'mobii': '#00cec9',
        'caracteristicas': '#f7b731',
        'caractersticas_medidor': '#f7b731',
        'fabricante_medidor': '#00ff88',
        'modelo_medidor': '#00ff88'
    }
    return color_map.get(field, '#95a5a6')


def _normalize_field_name(field: str) -> str:
    """Normaliza variações de nomes de campos"""
    normalizations = {
        'protocolo': 'protocolos',
        'protocolo_comunicao': 'protocolos',
        'caractersticas_medidor': 'caracteristicas',
        'caracterssticas': 'caracteristicas'
    }
    return normalizations.get(field, field)


def _get_field_variations(campo: str) -> List[str]:
    """Retorna todas as variações possíveis de um nome de campo"""
    variations = {
        'protocolos': ['protocolos', 'protocolo', 'protocolo_comunicao'],
        'caracteristicas': ['caracteristicas', 'caractersticas_medidor', 'caracterssticas'],
        'hemera': ['hemera', 'modulos_hemera'],
        'comunicacao': ['comunicacao', 'midia_comunicacao']
    }
    return variations.get(campo, [campo])
