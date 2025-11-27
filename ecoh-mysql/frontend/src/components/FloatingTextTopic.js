import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';

const FloatingTextTopic = ({ topico, position, onSelect, isHovered, onHover }) => {
  const groupRef = useRef();
  const glowRef = useRef();
  
  // Capitalizar primeira letra
  const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  };
  
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
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.elapsedTime;
      
      // Movimento flutuante suave
      groupRef.current.position.y = position[1] + Math.sin(time + position[0]) * 0.4;
      groupRef.current.position.x = position[0] + Math.cos(time * 0.5 + position[2]) * 0.3;
      
      // Rotação sutil no hover
      if (isHovered) {
        groupRef.current.rotation.y += 0.01;
      }
      
      // Escala no hover
      const targetScale = isHovered ? 1.2 : 1.0;
      groupRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
      );
    }
    
    if (glowRef.current) {
      // Pulsação do glow
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.3 + 0.7;
      glowRef.current.material.opacity = isHovered ? 0.4 * pulse : 0.15 * pulse;
    }
  });
  
  return (
    <group 
      ref={groupRef}
      position={position}
      onClick={() => onSelect(topico)}
      onPointerOver={() => onHover(topico)}
      onPointerOut={() => onHover(null)}
    >
      {/* Background glassmorphism */}
      <mesh>
        <planeGeometry args={[8, 2]} />
        <meshPhysicalMaterial
          color={color}
          transparent
          opacity={0.15}
          metalness={0.3}
          roughness={0.4}
          clearcoat={0.8}
          clearcoatRoughness={0.2}
          transmission={0.2}
        />
      </mesh>
      
      {/* Glow externo */}
      <mesh ref={glowRef} position={[0, 0, -0.1]}>
        <planeGeometry args={[9, 2.5]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.15}
          side={THREE.DoubleSide}
        />
      </mesh>
      
      {/* Texto principal */}
      <Text
        position={[0, 0, 0.1]}
        fontSize={0.6}
        color={isHovered ? '#ffffff' : color}
        anchorX="center"
        anchorY="middle"
        font="https://fonts.gstatic.com/s/robotocondensed/v27/ieVl2ZhZI2eCN5jzbjEETS9weq8-_d6T_POl0fRJeyWyo6mSDQ.woff"
        fontWeight="bold"
        outlineWidth={0.02}
        outlineColor="#000000"
      >
        {capitalize(topico.nome)}
      </Text>
      
      {/* Ícone emoji */}
      {topico.icone && (
        <Text
          position={[-3.5, 0, 0.1]}
          fontSize={0.8}
          anchorX="center"
          anchorY="middle"
        >
          {topico.icone}
        </Text>
      )}
      
      {/* Borda decorativa */}
      <mesh position={[0, 0, 0]}>
        <planeGeometry args={[8.1, 2.1]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={isHovered ? 0.4 : 0.2}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
};

export default FloatingTextTopic;
