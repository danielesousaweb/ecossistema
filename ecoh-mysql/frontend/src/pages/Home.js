import React, { useState, useEffect, Suspense, useRef } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { motion } from 'framer-motion';
import axios from 'axios';
import * as THREE from 'three';

import SearchBar from '../components/SearchBar';
import Lightbox from '../components/Lightbox';
import ProductCard from '../components/ProductCard';
import FloatingTopicHTML from '../components/FloatingTopicHTML';
import StarfieldBackground from '../components/StarfieldBackground';
import { Badge } from '../components/ui/badge';
import { formatValue, formatFieldName } from '../utils/formatters';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Particle background
function ParticleField() {
  const points = useRef();
  const particleCount = 2000;
  
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 200;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 200;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 200;
    
    // Cores ciano/azul
    colors[i * 3] = Math.random() * 0.3;
    colors[i * 3 + 1] = Math.random() * 0.5 + 0.5;
    colors[i * 3 + 2] = Math.random() * 0.3 + 0.7;
  }
  
  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y += 0.0002;
      points.current.rotation.x += 0.0001;
    }
  });
  
  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
}

// Camera controller with mouse tracking
function CameraController({ mousePosition }) {
  const { camera } = useThree();
  
  useFrame(() => {
    // Parallax baseado no mouse - REDUZIDO para menos sensibilidade
    const targetX = mousePosition.x * 1.5;  // Reduzido de 5 para 1.5
    const targetY = -mousePosition.y * 1.5; // Reduzido de 5 para 1.5
    
    camera.position.x += (targetX - camera.position.x) * 0.03;  // Reduzido de 0.05 para 0.03
    camera.position.y += (targetY - camera.position.y) * 0.03;
    
    camera.lookAt(0, 0, 0);
  });
  
  return null;
}

// 3D Scene with floating topics
function FloatingScene({ topicos, onSelectTopic, hoveredTopic, onHoverTopic, camera, positions }) {
  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#00ae4f" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#004c96" />
      
      <ParticleField />
    </>
  );
}

const Home = () => {
  const [topicos, setTopicos] = useState({});
  const [loading, setLoading] = useState(true);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [hoveredTopic, setHoveredTopic] = useState(null);
  const [cameraRef, setCameraRef] = useState(null);
  const [topicoPositions, setTopicoPositions] = useState([]);
  
  // Lightbox states
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxContent, setLightboxContent] = useState(null);
  const [lightboxType, setLightboxType] = useState(null);
  const [produtos, setProdutos] = useState([]);
  const [loadingProdutos, setLoadingProdutos] = useState(false);
  
  // Product detail lightbox
  const [detailLightboxOpen, setDetailLightboxOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  useEffect(() => {
    loadTopicos();
  }, []);
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 2 - 1,
        y: (e.clientY / window.innerHeight) * 2 - 1
      });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
  
  const loadTopicos = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/topicos`);
      if (response.data.success) {
        setTopicos(response.data.data);
        
        // Calcular posições 3D para os tópicos
        const topicosList = Object.values(response.data.data);
        const positions = topicosList.map((_, index) => {
          const phi = Math.acos(-1 + (2 * index) / topicosList.length);
          const theta = Math.sqrt(topicosList.length * Math.PI) * phi;
          const radius = 25;
          
          return [
            radius * Math.cos(theta) * Math.sin(phi),
            radius * Math.sin(theta) * Math.sin(phi),
            radius * Math.cos(phi)
          ];
        });
        setTopicoPositions(positions);
      }
    } catch (error) {
      console.error('Erro ao carregar tópicos:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSelectTopic = async (topico) => {
    setLightboxContent(topico);
    setLightboxType('topico');
    setLightboxOpen(true);
    
    // Se o tópico tem valores, carregar produtos
    if (topico.valores && topico.valores.length > 0) {
      setLoadingProdutos(true);
      setProdutos([]);
      
      try {
        const response = await axios.get(`${API}/topicos/produtos-por-topico`, {
          params: {
            campo: topico.id,
            valor: topico.id,
            per_page: 50
          }
        });
        
        if (response.data.success) {
          setProdutos(response.data.data);
        }
      } catch (error) {
        console.error('Erro ao carregar produtos:', error);
      } finally {
        setLoadingProdutos(false);
      }
    }
  };
  
  const handleSelectSubtopic = async (topico, valor) => {
    setLoadingProdutos(true);
    setProdutos([]);
    
    try {
      const response = await axios.get(`${API}/topicos/produtos-por-topico`, {
        params: {
          nome: valor,
          categoria: topico.id,
          per_page: 50
        }
      });
      
      if (response.data.success) {
        setProdutos(response.data.data);
      }
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    } finally {
      setLoadingProdutos(false);
    }
  };
  
  const handleSelectProduct = (product) => {
    setSelectedProduct(product);
    setDetailLightboxOpen(true);
  };
  
  const handleBadgeClick = async (badgeValue, category) => {
    console.log('Badge clicada:', badgeValue, category);
    
    // Fechar lightbox de produto atual
    setDetailLightboxOpen(false);
    
    // Preparar novo lightbox
    setLoadingProdutos(true);
    setProdutos([]);
    
    const topicoInfo = {
      id: category,
      nome: formatFieldName(category) + ': ' + formatValue(badgeValue),
      icone: '🔗',
      valores: [badgeValue]
    };
    
    setLightboxContent(topicoInfo);
    setLightboxType('topico');
    
    // Abrir lightbox ANTES de carregar (para feedback visual)
    setTimeout(() => {
      setLightboxOpen(true);
    }, 100);
    
    try {
      const response = await axios.get(`${API}/topicos/produtos-por-topico`, {
        params: {
          nome: badgeValue,
          categoria: category,
          per_page: 50
        }
      });
      
      console.log('Resposta da API:', response.data);
      
      if (response.data.success) {
        setProdutos(response.data.data);
        console.log('Produtos carregados:', response.data.data.length);
      }
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    } finally {
      setLoadingProdutos(false);
    }
  };
  
  const handleSearchResult = (item, tipo) => {
    if (tipo === 'topico') {
      handleSelectTopic(item);
    } else if (tipo === 'produto') {
      handleSelectProduct(item);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-20 h-20 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-cyan-400 text-xl">Carregando Ecossistema...</p>
        </div>
      </div>
    );
  }
  
  const topicosList = Object.values(topicos);
  
  return (
    <div className="relative w-full h-screen overflow-hidden"
         style={{
           background: `
             radial-gradient(ellipse 50% 80% at 50% 0%, rgba(0, 174, 79, 0.15), transparent 60%),
             radial-gradient(circle at ${(mousePosition.x + 1) * 50}% ${(mousePosition.y + 1) * 50}%, rgba(0, 76, 150, 0.1), transparent 50%),
             linear-gradient(180deg, #001021 0%, #000a14 50%, #02182f 100%)`
         }}>
      
      {/* Camada de Estrelas (z-index: 1) */}
      <StarfieldBackground mousePosition={mousePosition} />
      
      {/* 3D Canvas - Partículas de fundo (z-index: 2) */}
      <Canvas
        camera={{ position: [0, 0, 50], fov: 60 }}
        style={{ position: 'absolute', inset: 0, zIndex: 2 }}
        onCreated={({ camera }) => setCameraRef(camera)}
      >
        <Suspense fallback={null}>
          <FloatingScene
            topicos={topicos}
            onSelectTopic={handleSelectTopic}
            hoveredTopic={hoveredTopic}
            onHoverTopic={setHoveredTopic}
            camera={cameraRef}
            positions={topicoPositions}
          />
          <CameraController mousePosition={mousePosition} />
        </Suspense>
      </Canvas>
      
      {/* Tópicos Flutuantes HTML Overlay (z-index: 30) */}
      {!loading && topicosList.length > 0 && topicosList.map((topico, index) => (
        <FloatingTopicHTML
          key={topico.id}
          topico={topico}
          position3D={topicoPositions[index]}
          camera={cameraRef}
          onSelect={handleSelectTopic}
          isHovered={hoveredTopic?.id === topico.id}
          onHover={setHoveredTopic}
        />
      ))}
      
      {/* UI Overlay (z-index: 40) */}
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 40 }}>
        <div className="container mx-auto h-full flex flex-col items-center justify-center px-4">
          
          {/* Logo & Title */}
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12 pointer-events-auto"
          >
            <h1 className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-green-400 to-white mb-4"
                data-testid="home-title"
                style={{
                  fontFamily: 'Roboto Condensed, sans-serif',
                  textShadow: '0 0 80px rgba(0, 174, 79, 0.5)'
                }}>
              Tech Mesh Sync
            </h1>
            <p className="text-white/90 text-xl" style={{ fontFamily: 'Roboto, sans-serif' }}>
              Ecossistema Interativo de Produtos CAS Tecnologia
            </p>
          </motion.div>
          
          {/* Search Bar */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="w-full max-w-3xl mb-8 pointer-events-auto"
          >
            <SearchBar onSelectResult={handleSearchResult} />
          </motion.div>
          
          {/* Instructions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="text-center space-y-2 text-cyan-300/50 text-sm pointer-events-auto"
          >
            <p>🖱️ Mova o mouse para navegar • 🔍 Clique nas bolhas para explorar</p>
          </motion.div>
          
          {/* Hovered Topic Info */}
          {hoveredTopic && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="absolute bottom-8 left-8 backdrop-blur-xl bg-slate-900/60 border-2 border-cyan-500/30 rounded-xl p-4 shadow-2xl pointer-events-none"
              style={{
                boxShadow: '0 0 40px rgba(34, 211, 238, 0.3)'
              }}
            >
              <div className="flex items-center gap-3">
                <span className="text-4xl">{hoveredTopic.icone}</span>
                <div>
                  <h3 className="text-cyan-100 font-bold text-lg">{hoveredTopic.nome}</h3>
                  {hoveredTopic.count > 0 && (
                    <p className="text-cyan-300/60 text-sm">{hoveredTopic.count} itens</p>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
      
      {/* Lightbox - Tópico */}
      <Lightbox
        isOpen={lightboxOpen && lightboxType === 'topico'}
        onClose={() => {
          setLightboxOpen(false);
          setProdutos([]);
        }}
        title={lightboxContent?.nome || ''}
        icon={lightboxContent?.icone}
      >
        {lightboxContent && (
          <div className="space-y-6">
            {/* Descrição do tópico */}
            <div className="text-cyan-100">
              <p className="text-lg">
                Explore {lightboxContent.nome.toLowerCase()} e suas conexões no ecossistema.
              </p>
            </div>
            
            {/* Valores/Subtópicos */}
            {lightboxContent.valores && lightboxContent.valores.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-cyan-300">Valores Disponíveis</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {lightboxContent.valores.map((valor) => (
                    <motion.button
                      key={valor}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleSelectSubtopic(lightboxContent, valor)}
                      className="backdrop-blur-xl bg-cyan-500/10 hover:bg-cyan-500/20 border-2 border-cyan-500/30 rounded-xl p-4 text-center transition-all"
                      data-testid={`subtopic-${valor}`}
                    >
                      <p className="text-cyan-100 font-medium uppercase text-sm">
                        {valor.replace(/_/g, ' ')}
                      </p>
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Subtópicos (para medidores) */}
            {lightboxContent.subtopicos && lightboxContent.subtopicos.length > 0 && (
              <div className="space-y-4">
                {lightboxContent.subtopicos.map((sub) => (
                  <div key={sub.id} className="space-y-2">
                    <h3 className="text-lg font-semibold text-cyan-300">{sub.nome}</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {sub.valores.map((valor) => (
                        <Badge
                          key={valor}
                          variant="outline"
                          className="bg-blue-500/10 text-blue-300 border-blue-500/30 justify-center py-2"
                        >
                          {valor}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Loading produtos */}
            {loadingProdutos && (
              <div className="flex items-center justify-center py-12">
                <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
            
            {/* Lista de produtos */}
            {produtos.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-cyan-300" style={{ fontFamily: 'Roboto Condensed, sans-serif' }}>
                  Produtos Relacionados ({produtos.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {produtos.map((produto) => (
                    <ProductCard
                      key={produto.sku}
                      product={produto}
                      onClick={handleSelectProduct}
                      onBadgeClick={handleBadgeClick}
                    />
                  ))}
                </div>
              </div>
            )}
            
            {!loadingProdutos && produtos.length === 0 && lightboxContent.valores && lightboxContent.valores.length > 1 && (
              <div className="text-center py-8 text-cyan-300/60" style={{ fontFamily: 'Roboto, sans-serif' }}>
                Selecione um valor acima para ver os produtos relacionados
              </div>
            )}
            
            {!loadingProdutos && produtos.length === 0 && (!lightboxContent.valores || lightboxContent.valores.length <= 1) && (
              <div className="text-center py-8 text-cyan-300/60" style={{ fontFamily: 'Roboto, sans-serif' }}>
                Nenhum produto encontrado para este filtro.
              </div>
            )}
          </div>
        )}
      </Lightbox>
      
      {/* Lightbox - Detalhes do Produto */}
      <Lightbox
        isOpen={detailLightboxOpen}
        onClose={() => setDetailLightboxOpen(false)}
        title={selectedProduct?.sku || ''}
        icon="📦"
      >
        {selectedProduct && (
          <div className="space-y-6">
            {/* Informações básicas */}
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-cyan-100">{selectedProduct.title}</h2>
              <div className="flex gap-2">
                {selectedProduct.categories?.map(cat => (
                  <Badge key={cat} variant="outline" className="bg-blue-500/10 text-blue-300 border-blue-500/30">
                    {cat}
                  </Badge>
                ))}
              </div>
            </div>
            
            {/* Atributos */}
            {selectedProduct.attributes && Object.keys(selectedProduct.attributes).length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-cyan-300" style={{ fontFamily: 'Roboto Condensed, sans-serif' }}>
                  Atributos
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(selectedProduct.attributes).map(([key, value]) => (
                    <div key={key} className="backdrop-blur-xl bg-cyan-500/5 border border-cyan-500/20 rounded-lg p-3">
                      <p className="text-xs text-cyan-300/70 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                        {formatFieldName(key)}
                      </p>
                      <p className="text-cyan-100" style={{ fontFamily: 'Roboto, sans-serif' }}>
                        {formatValue(value)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Relacionamentos */}
            {selectedProduct.relationships && Object.keys(selectedProduct.relationships).length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-cyan-300" style={{ fontFamily: 'Roboto Condensed, sans-serif' }}>
                  Conexões
                </h3>
                {Object.entries(selectedProduct.relationships).map(([relType, targets]) => (
                  <div key={relType} className="space-y-2">
                    <p className="text-sm text-cyan-300/70" style={{ fontFamily: 'Roboto, sans-serif' }}>
                      {formatFieldName(relType)}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {targets.map(target => (
                        <Badge 
                          key={target} 
                          onClick={() => handleBadgeClick(target, relType)}
                          className="bg-purple-500/20 text-purple-300 border-purple-500/30 hover:bg-purple-500/30 cursor-pointer transition-all"
                          style={{ fontFamily: 'Roboto Condensed, sans-serif' }}
                          data-testid={`connection-badge-${target}`}
                        >
                          {formatValue(target)}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Completeness */}
            {selectedProduct.completeness_score && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-cyan-300">Completude dos Dados</span>
                  <span className="text-cyan-100 font-bold">{selectedProduct.completeness_score}%</span>
                </div>
                <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${selectedProduct.completeness_score}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    className="bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 h-full rounded-full"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </Lightbox>
    </div>
  );
};

export default Home;
