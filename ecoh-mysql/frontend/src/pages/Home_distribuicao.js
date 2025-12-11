// TRECHO DO HOME.JS PARA SUBSTITUIR A DISTRIBUIÇÃO DOS TÓPICOS
// Substitua a função loadTopicos a partir da linha 137

const loadTopicos = async () => {
  try {
    setLoading(true);
    const response = await axios.get(`${API}/topicos`);
    if (response.data.success) {
      setTopicos(response.data.data);
      
      // Calcular posições 3D - DISTRIBUIÇÃO MELHORADA
      const topicosList = Object.values(response.data.data);
      const positions = topicosList.map((_, index) => {
        // Distribuição em espiral de Fibonacci para melhor espaçamento
        const goldenAngle = Math.PI * (3 - Math.sqrt(5));
        const theta = index * goldenAngle;
        const phi = Math.acos(1 - 2 * (index + 0.5) / topicosList.length);
        const radius = 35; // Raio balanceado
        
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