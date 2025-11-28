import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const FloatingTopic = ({ topico, position, onSelect, isHovered, onHover }) => {
  const meshRef = useRef();
  const glowRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      // Movimento flutuante suave
      const time = state.clock.elapsedTime;
      meshRef.current.position.y = position[1] + Math.sin(time + position[0]) * 0.3;
      meshRef.current.position.x = position[0] + Math.cos(time * 0.5 + position[2]) * 0.2;
      
      // Rotação suave
      meshRef.current.rotation.y += 0.003;
      meshRef.current.rotation.x = Math.sin(time * 0.3) * 0.1;
      
      // Escala no hover
      const targetScale = isHovered ? 1.15 : 1.0;
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
      );
    }
    
    if (glowRef.current) {
      // Pulsação do glow
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.2 + 0.8;
      glowRef.current.material.opacity = isHovered ? 0.4 * pulse : 0.15 * pulse;
    }
  });
  
  return (
    <group position={position}>
      {/* Bolha principal - MUITO REDUZIDA */}
      <mesh
        ref={meshRef}
        onClick={() => onSelect(topico)}
        onPointerOver={() => onHover(topico)}
        onPointerOut={() => onHover(null)}
      >
        <sphereGeometry args={[0.4, 32, 32]} />
        <meshPhysicalMaterial
          color={topico.cor || '#00ff88'}
          transparent
          opacity={0.6}
          metalness={0.3}
          roughness={0.2}
          clearcoat={1.0}
          clearcoatRoughness={0.1}
          transmission={0.3}
        />
      </mesh>
      
      {/* Glow externo - AJUSTADO */}
      <mesh ref={glowRef} scale={1.15}>
        <sphereGeometry args={[0.4, 16, 16]} />
        <meshBasicMaterial
          color={topico.cor || '#00ff88'}
          transparent
          opacity={0.15}
          side={THREE.BackSide}
        />
      </mesh>
      
      {/* Anel orbital - AJUSTADO */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.5, 0.015, 16, 100]} />
        <meshBasicMaterial
          color={topico.cor || '#00ff88'}
          transparent
          opacity={isHovered ? 0.6 : 0.3}
        />
      </mesh>
    </group>
  );
};

export default FloatingTopic;