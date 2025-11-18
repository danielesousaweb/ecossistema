import React, { useRef, useEffect, useState, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Node component for 3D visualization
function Node({ node, isSelected, onSelect, onHover }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);
  
  useFrame((state) => {
    if (meshRef.current) {
      // Gentle floating animation
      meshRef.current.position.y += Math.sin(state.clock.elapsedTime + node.x) * 0.001;
      
      // Rotation animation
      meshRef.current.rotation.y += 0.005;
      
      // Scale animation on hover or select
      const targetScale = (hovered || isSelected) ? node.size * 1.5 : node.size;
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
      );
    }
  });
  
  return (
    <mesh
      ref={meshRef}
      position={[node.x, node.y, node.z]}
      onClick={() => onSelect(node)}
      onPointerOver={() => {
        setHovered(true);
        onHover(node);
      }}
      onPointerOut={() => {
        setHovered(false);
        onHover(null);
      }}
    >
      <sphereGeometry args={[node.size, 32, 32]} />
      <meshStandardMaterial
        color={node.color}
        emissive={node.color}
        emissiveIntensity={hovered || isSelected ? 0.6 : 0.2}
        metalness={0.8}
        roughness={0.2}
      />
      
      {/* Glow effect */}
      <mesh scale={1.2}>
        <sphereGeometry args={[node.size, 16, 16]} />
        <meshBasicMaterial
          color={node.color}
          transparent
          opacity={hovered || isSelected ? 0.3 : 0.1}
        />
      </mesh>
    </mesh>
  );
}

// Edge/Connection component
function Edge({ edge, nodes }) {
  const lineRef = useRef();
  
  const sourceNode = nodes.find(n => n.id === edge.source);
  const targetNode = nodes.find(n => n.id === edge.target);
  
  if (!sourceNode || !targetNode) return null;
  
  const points = [
    new THREE.Vector3(sourceNode.x, sourceNode.y, sourceNode.z),
    new THREE.Vector3(targetNode.x, targetNode.y, targetNode.z)
  ];
  
  useFrame(() => {
    if (lineRef.current) {
      // Pulse animation
      const mat = lineRef.current.material;
      mat.opacity = 0.15 + Math.sin(Date.now() * 0.001) * 0.05;
    }
  });
  
  return (
    <line ref={lineRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={points.length}
          array={new Float32Array(points.flatMap(p => [p.x, p.y, p.z]))}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color="#4ecdc4"
        transparent
        opacity={0.2}
        linewidth={2}
      />
    </line>
  );
}

// Camera controller
function CameraController({ selectedNode }) {
  const { camera } = useThree();
  
  useEffect(() => {
    if (selectedNode) {
      // Smoothly move camera to node
      const targetPos = new THREE.Vector3(
        selectedNode.x + 10,
        selectedNode.y + 5,
        selectedNode.z + 10
      );
      
      // Animate camera
      const currentPos = camera.position.clone();
      const steps = 30;
      let step = 0;
      
      const animate = () => {
        if (step < steps) {
          step++;
          camera.position.lerpVectors(currentPos, targetPos, step / steps);
          camera.lookAt(selectedNode.x, selectedNode.y, selectedNode.z);
          requestAnimationFrame(animate);
        }
      };
      animate();
    }
  }, [selectedNode, camera]);
  
  return null;
}

// Main Scene component
function Scene({ graphData, selectedNode, onNodeSelect, onNodeHover }) {
  const { nodes = [], edges = [] } = graphData || {};
  
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#ffffff" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4ecdc4" />
      <pointLight position={[0, 20, 0]} intensity={0.8} color="#00ff88" />
      
      {/* Nodes */}
      {nodes.map(node => (
        <Node
          key={node.id}
          node={node}
          isSelected={selectedNode?.id === node.id}
          onSelect={onNodeSelect}
          onHover={onNodeHover}
        />
      ))}
      
      {/* Edges */}
      {edges.map((edge, idx) => (
        <Edge key={idx} edge={edge} nodes={nodes} />
      ))}
      
      {/* Camera controller */}
      <CameraController selectedNode={selectedNode} />
      
      {/* Particle field background */}
      <Stars />
    </>
  );
}

// Starfield background
function Stars() {
  const count = 1000;
  const positions = new Float32Array(count * 3);
  
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 100;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 100;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
  }
  
  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.1}
        color="#ffffff"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
}

// Main EcosystemGraph component
export default function EcosystemGraph() {
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    loadGraphData();
  }, []);
  
  const loadGraphData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/graph/complete`);
      if (response.data.success) {
        setGraphData(response.data.data);
      }
    } catch (err) {
      console.error('Error loading graph:', err);
      setError('Failed to load ecosystem data');
    } finally {
      setLoading(false);
    }
  };
  
  const handleNodeSelect = (node) => {
    setSelectedNode(node);
  };
  
  const handleNodeHover = (node) => {
    setHoveredNode(node);
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400 mx-auto"></div>
          <p className="text-cyan-400 text-lg font-light">Loading CAS Ecosystem...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900">
        <div className="text-center space-y-4">
          <p className="text-red-400 text-lg">{error}</p>
          <button
            data-testid="retry-load-btn"
            onClick={loadGraphData}
            className="px-6 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [30, 20, 30], fov: 60 }}
        style={{ width: '100%', height: '100%' }}
      >
        <Suspense fallback={null}>
          <Scene
            graphData={graphData}
            selectedNode={selectedNode}
            onNodeSelect={handleNodeSelect}
            onNodeHover={handleNodeHover}
          />
        </Suspense>
      </Canvas>
      
      {/* HUD Overlay */}
      <div className="absolute top-0 left-0 w-full p-6 pointer-events-none">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-start justify-between">
            {/* Title */}
            <div className="backdrop-blur-xl bg-slate-900/40 border border-cyan-500/30 rounded-2xl p-6 shadow-2xl">
              <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500"
                  data-testid="ecosystem-title">
                CAS Tecnologia Ecosystem
              </h1>
              <p className="text-cyan-300/70 text-sm mt-2">Interactive Product Network</p>
            </div>
            
            {/* Stats */}
            {graphData && (
              <div className="backdrop-blur-xl bg-slate-900/40 border border-cyan-500/30 rounded-2xl p-4 shadow-2xl">
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
                    <span className="text-cyan-100">{graphData.stats.total_nodes} Nodes</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
                    <span className="text-cyan-100">{graphData.stats.total_edges} Connections</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></div>
                    <span className="text-cyan-100">{graphData.stats.total_clusters} Clusters</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Hovered Node Info */}
      {hoveredNode && (
        <div className="absolute bottom-6 left-6 backdrop-blur-xl bg-slate-900/60 border border-cyan-500/30 rounded-xl p-4 shadow-2xl max-w-md pointer-events-none"
             data-testid="hovered-node-info">
          <div className="flex items-center gap-3">
            <div
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: hoveredNode.color }}
            ></div>
            <div>
              <h3 className="text-cyan-100 font-semibold">{hoveredNode.label}</h3>
              <p className="text-cyan-300/60 text-sm capitalize">{hoveredNode.type}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Selected Node Details */}
      {selectedNode && (
        <div className="absolute top-6 right-6 w-96 backdrop-blur-xl bg-slate-900/60 border border-cyan-500/30 rounded-2xl shadow-2xl pointer-events-auto"
             data-testid="selected-node-details">
          <div className="p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-6 h-6 rounded-full animate-pulse"
                  style={{ backgroundColor: selectedNode.color }}
                ></div>
                <div>
                  <h2 className="text-xl font-bold text-cyan-100">{selectedNode.label}</h2>
                  <p className="text-cyan-300/60 text-sm capitalize">{selectedNode.type}</p>
                </div>
              </div>
              <button
                data-testid="close-node-details-btn"
                onClick={() => setSelectedNode(null)}
                className="text-cyan-300 hover:text-cyan-100 transition-colors"
              >
                ✕
              </button>
            </div>
            
            {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-cyan-300">Attributes</h3>
                <div className="space-y-1 max-h-64 overflow-y-auto">
                  {Object.entries(selectedNode.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-cyan-300/70">{key}:</span>
                      <span className="text-cyan-100 font-mono text-xs">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Controls hint */}
      <div className="absolute bottom-6 right-6 backdrop-blur-xl bg-slate-900/40 border border-cyan-500/30 rounded-xl p-4 shadow-2xl pointer-events-none">
        <div className="space-y-2 text-xs text-cyan-300/70">
          <p>🖱️ Drag to rotate</p>
          <p>🔍 Scroll to zoom</p>
          <p>👆 Click nodes to explore</p>
        </div>
      </div>
    </div>
  );
}