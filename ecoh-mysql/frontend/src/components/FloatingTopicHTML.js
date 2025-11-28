import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

/**
 * Tópico flutuante usando HTML overlay (mais confiável que Three.js Text)
 * Posicionado com base em coordenadas 3D convertidas para 2D
 */
const FloatingTopicHTML = ({ topico, position3D, camera, onSelect, isHovered, onHover }) => {
  const [position2D, setPosition2D] = useState({ x: 0, y: 0, visible: false });
  
  // Capitalizar primeira letra
  const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  };
  
  // Converter 3D para 2D
  useEffect(() => {
    const convert3Dto2D = () => {
      if (!position3D || !camera) return;
      
      // Criar vetor 3D
      const vector = {
        x: position3D[0],
        y: position3D[1],
        z: position3D[2]
      };
      
      // Projetar para coordenadas de tela
      const widthHalf = window.innerWidth / 2;
      const heightHalf = window.innerHeight / 2;
      
      // Calcular distância da câmera
      const dx = vector.x - camera.position.x;
      const dy = vector.y - camera.position.y;
      const dz = vector.z - camera.position.z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
      
      // Verificar se está na frente da câmera
      const isInFront = dz < camera.position.z;
      
      // Projeção simples com escala mais controlada
      const scale = 300 / distance;  // Reduzido de 500 para 300
      const x = widthHalf + (vector.x - camera.position.x) * scale;
      const y = heightHalf - (vector.y - camera.position.y) * scale;
      
      setPosition2D({
        x,
        y,
        visible: isInFront && x > -200 && x < window.innerWidth + 200 && y > -200 && y < window.innerHeight + 200,
        scale: 1  // Fixo em 1 para evitar zoom excessivo
      });
    };
    
    convert3Dto2D();
    const interval = setInterval(convert3Dto2D, 50);
    return () => clearInterval(interval);
  }, [position3D, camera]);
  
  if (!position2D.visible) return null;
  
  // Cores do tema CAS
  const getColor = (topicoId) => {
    const colorMap = {
      'medidores': '#004c96',
      'protocolos': '#00ae4f',
      'caracteristicas': '#0066cc',
      'mdcs': '#004c96',
      'tipo_integracao': '#00ae4f',
      'hemera': '#0099ff',
      'comunicacao': '#00cc66',
      'mobii': '#004c96'
    };
    return colorMap[topicoId] || '#004c96';
  };
  
  const color = getColor(topico.id);
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ 
        opacity: position2D.visible ? 1 : 0,
        scale: position2D.visible ? 0.6 : 0.5  // REDUZIDO de 1.5 para 0.6 (60% menor)
      }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'fixed',
        left: position2D.x,
        top: position2D.y,
        transform: 'translate(-50%, -50%)',
        zIndex: 30,
        pointerEvents: 'auto'
      }}
      onMouseEnter={() => onHover(topico)}
      onMouseLeave={() => onHover(null)}
      onClick={() => onSelect(topico)}
      role="button"
      aria-label={`Tópico ${topico.nome}`}
      data-testid={`floating-topic-${topico.id}`}
    >
      <motion.div
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className="cursor-pointer backdrop-blur-xl rounded-xl px-4 py-2 shadow-2xl border-2"
        style={{
          background: `linear-gradient(135deg, ${color}15, ${color}08)`,
          borderColor: isHovered ? `${color}80` : `${color}30`,
          boxShadow: isHovered 
            ? `0 0 40px ${color}60, inset 0 0 20px ${color}20`
            : `0 0 20px ${color}30, inset 0 0 10px ${color}10`
        }}
      >
        <div className="flex items-center gap-4">
          {/* Ícone */}
          {topico.icone && (
            <span className="text-2xl" style={{ filter: 'drop-shadow(0 0 8px rgba(0,0,0,0.5))' }}>
              {topico.icone}
            </span>
          )}
          
          {/* Texto */}
          <div>
            <h3 
              className="font-bold text-base leading-tight"
              style={{
                fontFamily: 'Roboto Condensed, sans-serif',
                color: isHovered ? '#ffffff' : color,
                textShadow: `0 0 10px ${color}80, 0 2px 4px rgba(0,0,0,0.5)`,
                filter: 'brightness(1.8)'
              }}
            >
              {capitalize(topico.nome)}
            </h3>
            
            {/* Count badge */}
            {topico.count > 0 && (
              <span 
                className="text-xs font-medium opacity-80"
                style={{
                  fontFamily: 'Roboto, sans-serif',
                  color: '#ffffff'
                }}
              >
                {topico.count} itens
              </span>
            )}
          </div>
        </div>
        
        {/* Glow indicator */}
        {isHovered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 rounded-2xl"
            style={{
              background: `radial-gradient(circle at center, ${color}20, transparent 70%)`,
              pointerEvents: 'none'
            }}
          />
        )}
      </motion.div>
    </motion.div>
  );
};

export default FloatingTopicHTML;
