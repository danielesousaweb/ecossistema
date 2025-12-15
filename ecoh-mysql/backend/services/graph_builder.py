from typing import Dict, Any, List, Optional
import logging
import math
import random

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Builds unified graph structure for 3D visualization
    Uses data directly from unopim_products table
    """
    
    def __init__(self, db):
        self.db = db
    
    async def build_complete_graph(self) -> Dict[str, Any]:
        """
        Build complete graph with all nodes and edges
        Returns structure ready for Three.js force-directed layout
        """
        logger.info("[GRAPH] Building complete graph structure from Unopim data")
        
        # Get all active products from unopim_products
        products = await self.db.find_products({"status": "active"})
        
        logger.info(f"[SOURCE: unopim_products] Found {len(products)} active products for graph")
        
        # Collect all unique nodes
        nodes_dict = {}
        edges_list = []
        
        # Add product nodes
        for product in products:
            node = product.get('graph_node', {})
            if node and node.get('id'):
                nodes_dict[node['id']] = node
                
                # Add product edges
                for edge in product.get('graph_edges', []):
                    edges_list.append(edge)
        
        # Create nodes for all relationship targets (even if not products)
        for edge in edges_list:
            target_id = edge['target']
            if target_id not in nodes_dict:
                # Create virtual node for relationship target
                nodes_dict[target_id] = self._create_virtual_node(
                    target_id,
                    edge['relationship_type']
                )
        
        # Calculate force-directed positions
        nodes_list = list(nodes_dict.values())
        self._calculate_3d_positions(nodes_list, edges_list)
        
        # Build graph clusters
        clusters = self._identify_clusters(nodes_list, edges_list)
        
        graph = {
            "nodes": nodes_list,
            "edges": edges_list,
            "clusters": clusters,
            "stats": {
                "total_nodes": len(nodes_list),
                "total_edges": len(edges_list),
                "total_clusters": len(clusters)
            }
        }
        
        logger.info(f"[GRAPH] Built graph: {len(nodes_list)} nodes, {len(edges_list)} edges")
        return graph
    
    def _create_virtual_node(self, node_id: str, relationship_type: str) -> Dict:
        """Create virtual node for non-product entities"""
        # Infer node type from ID pattern
        node_type = 'integration'
        color = '#95a5a6'
        
        if node_id.startswith('mdc_') or relationship_type == 'mdcs':
            node_type = 'mdc'
            color = '#45b7d1'
        elif node_id.startswith('nic_') or relationship_type == 'nics':
            node_type = 'nic'
            color = '#f7b731'
        elif node_id.startswith('rs') or relationship_type == 'remotas':
            node_type = 'remota'
            color = '#ff6b6b'
        elif node_id.startswith('int_') or relationship_type == 'tipo_integracao':
            node_type = 'integration'
            color = '#a55eea'
        elif relationship_type in ['protocolo', 'protocolos', 'protocolo_comunicao']:
            node_type = 'protocolo'
            color = '#26de81'
        elif relationship_type == 'comunicacao':
            node_type = 'comunicacao'
            color = '#fd79a8'
        elif relationship_type == 'hemera' or relationship_type == 'modulos_hemera':
            node_type = 'hemera'
            color = '#00cec9'
        elif relationship_type in ['caracteristicas', 'caractersticas_medidor', 'mobii']:
            node_type = 'caracteristica'
            color = '#f7b731'
        
        return {
            "id": node_id,
            "label": node_id.replace('_', ' ').upper(),
            "type": node_type,
            "x": 0,
            "y": 0,
            "z": 0,
            "size": 0.7,
            "color": color,
            "is_virtual": True,
            "metadata": {}
        }
    
    def _calculate_3d_positions(self, nodes: List[Dict], edges: List[Dict], iterations: int = 100):
        """
        Force-directed graph layout in 3D space
        Modifies nodes in-place
        """
        # Initialize random positions
        for node in nodes:
            node['x'] = random.uniform(-10, 10)
            node['y'] = random.uniform(-10, 10)
            node['z'] = random.uniform(-10, 10)
        
        # Build adjacency for faster lookup
        node_indices = {node['id']: i for i, node in enumerate(nodes)}
        
        # Force-directed algorithm parameters
        repulsion = 15.0
        attraction = 0.1
        damping = 0.85
        
        for iteration in range(iterations):
            # Calculate forces
            forces = [[0, 0, 0] for _ in nodes]
            
            # Repulsion between all nodes
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes):
                    if i >= j:
                        continue
                    
                    dx = node2['x'] - node1['x']
                    dy = node2['y'] - node1['y']
                    dz = node2['z'] - node1['z']
                    
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz) + 0.01
                    force = repulsion / (dist * dist)
                    
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force
                    fz = (dz / dist) * force
                    
                    forces[i][0] -= fx
                    forces[i][1] -= fy
                    forces[i][2] -= fz
                    forces[j][0] += fx
                    forces[j][1] += fy
                    forces[j][2] += fz
            
            # Attraction along edges
            for edge in edges:
                if edge['source'] not in node_indices or edge['target'] not in node_indices:
                    continue
                
                i = node_indices[edge['source']]
                j = node_indices[edge['target']]
                
                dx = nodes[j]['x'] - nodes[i]['x']
                dy = nodes[j]['y'] - nodes[i]['y']
                dz = nodes[j]['z'] - nodes[i]['z']
                
                dist = math.sqrt(dx*dx + dy*dy + dz*dz) + 0.01
                force = attraction * dist
                
                fx = (dx / dist) * force
                fy = (dy / dist) * force
                fz = (dz / dist) * force
                
                forces[i][0] += fx
                forces[i][1] += fy
                forces[i][2] += fz
                forces[j][0] -= fx
                forces[j][1] -= fy
                forces[j][2] -= fz
            
            # Apply forces with damping
            for i, node in enumerate(nodes):
                node['x'] += forces[i][0] * damping
                node['y'] += forces[i][1] * damping
                node['z'] += forces[i][2] * damping
        
        logger.debug("[GRAPH] 3D positions calculated")
    
    def _identify_clusters(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Identify node clusters by type and connections"""
        clusters_by_type = {}
        
        for node in nodes:
            node_type = node.get('type', 'other')
            if node_type not in clusters_by_type:
                clusters_by_type[node_type] = []
            clusters_by_type[node_type].append(node['id'])
        
        clusters = []
        for cluster_type, node_ids in clusters_by_type.items():
            if node_ids:
                # Calculate cluster centroid
                cluster_nodes = [n for n in nodes if n['id'] in node_ids]
                cx = sum(n['x'] for n in cluster_nodes) / len(node_ids)
                cy = sum(n['y'] for n in cluster_nodes) / len(node_ids)
                cz = sum(n['z'] for n in cluster_nodes) / len(node_ids)
                
                clusters.append({
                    "type": cluster_type,
                    "nodes": node_ids,
                    "count": len(node_ids),
                    "centroid": {"x": cx, "y": cy, "z": cz},
                    "color": cluster_nodes[0]['color'] if cluster_nodes else '#95a5a6'
                })
        
        return clusters
    
    async def get_node_details(self, node_id: str) -> Optional[Dict]:
        """Get detailed information about a specific node"""
        logger.info(f"[GRAPH] Getting node details for: {node_id}")
        
        # Try to find product by SKU
        product = await self.db.find_product_by_sku(node_id)
        
        if product:
            logger.info(f"[SOURCE: unopim_products] Found product node: {node_id}")
            return {
                "id": node_id,
                "sku": product['sku'],
                "title": product['title'],
                "type": product['product_type'],
                "status": product['status'],
                "attributes": product['attributes'],
                "relationships": product['relationships'],
                "categories": product['categories'],
                "completeness_score": product.get('completeness_score'),
                "updated_at": product.get('updated_at')
            }
        
        # Return virtual node info
        logger.info(f"[GRAPH] Node {node_id} is virtual (not a product)")
        return {
            "id": node_id,
            "type": "virtual",
            "label": node_id.replace('_', ' ').upper()
        }
