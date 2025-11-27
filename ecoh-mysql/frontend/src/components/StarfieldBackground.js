import React, { useEffect, useRef } from 'react';

/**
 * Camada de estrelas (pontos) animados no fundo
 * Canvas 2D para performance
 */
const StarfieldBackground = ({ mousePosition }) => {
  const canvasRef = useRef(null);
  const starsRef = useRef([]);
  const animationRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Configurar canvas
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Criar estrelas
    const createStars = () => {
      const stars = [];
      const starCount = 200; // Quantidade moderada para não competir com tópicos
      
      for (let i = 0; i < starCount; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          radius: Math.random() * 1.5 + 0.5,
          opacity: Math.random() * 0.5 + 0.2,
          twinkleSpeed: Math.random() * 0.02 + 0.005,
          twinklePhase: Math.random() * Math.PI * 2
        });
      }
      
      return stars;
    };
    
    starsRef.current = createStars();
    
    // Animar
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      starsRef.current.forEach(star => {
        // Efeito twinkle
        star.twinklePhase += star.twinkleSpeed;
        const currentOpacity = star.opacity * (0.5 + Math.sin(star.twinklePhase) * 0.5);
        
        // Parallax sutil com mouse - REDUZIDO
        const parallaxX = mousePosition.x * 3;  // Reduzido de 10 para 3
        const parallaxY = mousePosition.y * 3;  // Reduzido de 10 para 3
        
        // Desenhar estrela
        ctx.beginPath();
        ctx.arc(
          star.x + parallaxX * star.radius,
          star.y + parallaxY * star.radius,
          star.radius,
          0,
          Math.PI * 2
        );
        ctx.fillStyle = `rgba(255, 255, 255, ${currentOpacity})`;
        ctx.shadowBlur = 3;
        ctx.shadowColor = 'rgba(255, 255, 255, 0.5)';
        ctx.fill();
        ctx.shadowBlur = 0;
      });
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [mousePosition]);
  
  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 1 }}
      aria-hidden="true"
    />
  );
};

export default StarfieldBackground;
