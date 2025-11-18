import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SearchBar = ({ onSelectResult }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);
  const debounceTimer = useRef(null);
  
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowResults(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  useEffect(() => {
    if (query.length < 2) {
      setResults(null);
      setShowResults(false);
      return;
    }
    
    // Debounce search
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    
    debounceTimer.current = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API}/topicos/busca-global`, {
          params: { q: query, per_page: 10 }
        });
        
        if (response.data.success) {
          setResults(response.data.data);
          setShowResults(true);
        }
      } catch (error) {
        console.error('Erro na busca:', error);
      } finally {
        setLoading(false);
      }
    }, 300);
    
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [query]);
  
  const handleSelectResult = (item, tipo) => {
    onSelectResult(item, tipo);
    setQuery('');
    setShowResults(false);
  };
  
  // Detectar se há espaço suficiente abaixo
  const [dropdownPosition, setDropdownPosition] = React.useState('below');
  
  React.useEffect(() => {
    if (searchRef.current && showResults) {
      const rect = searchRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;
      
      // Se não há espaço abaixo (menos de 400px), mostrar acima
      if (spaceBelow < 400 && spaceAbove > spaceBelow) {
        setDropdownPosition('above');
      } else {
        setDropdownPosition('below');
      }
      
      // Scroll suave para manter dropdown visível
      setTimeout(() => {
        if (searchRef.current) {
          searchRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest',
            inline: 'nearest'
          });
        }
      }, 150);
    }
  }, [showResults, dropdownPosition]);
  
  return (
    <div ref={searchRef} className="relative w-full max-w-3xl mx-auto">
      {/* Search Input */}
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="relative"
      >
        <div className="relative backdrop-blur-2xl bg-gradient-to-r from-slate-900/80 via-indigo-900/60 to-slate-900/80 border-2 border-cyan-500/40 rounded-2xl overflow-hidden"
             style={{
               boxShadow: '0 0 40px rgba(34, 211, 238, 0.3), inset 0 0 60px rgba(34, 211, 238, 0.05)'
             }}>
          
          <div className="flex items-center px-6 py-4">
            <Search className="w-7 h-7 text-cyan-400 mr-4 animate-pulse" />
            
            <input
              data-testid="search-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar produtos, protocolos, características..."
              className="flex-1 bg-transparent text-cyan-100 text-lg placeholder:text-cyan-300/50 outline-none"
              autoComplete="off"
            />
            
            {query && (
              <button
                onClick={() => {
                  setQuery('');
                  setShowResults(false);
                }}
                className="text-cyan-300 hover:text-cyan-100 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            )}
          </div>
          
          {loading && (
            <div className="absolute inset-0 bg-cyan-500/10 backdrop-blur-sm flex items-center justify-center">
              <div className="w-8 h-8 border-3 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </div>
      </motion.div>
      
      {/* Results Dropdown */}
      <AnimatePresence>
        {showResults && results && (results.produtos?.length > 0 || results.topicos?.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: dropdownPosition === 'below' ? -10 : 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: dropdownPosition === 'below' ? -10 : 10 }}
            transition={{ duration: 0.2 }}
            className={`absolute ${dropdownPosition === 'below' ? 'top-full mt-4' : 'bottom-full mb-4'} w-full backdrop-blur-2xl bg-slate-900/95 border-2 border-cyan-500/30 rounded-2xl shadow-2xl overflow-hidden z-50`}
            style={{
              boxShadow: '0 0 40px rgba(34, 211, 238, 0.3)',
              maxHeight: '70vh'
            }}
          >
            <div className="max-h-96 overflow-y-auto custom-scrollbar">
              {/* Tópicos */}
              {results.topicos && results.topicos.length > 0 && (
                <div className="p-4 border-b border-cyan-500/20">
                  <h3 className="text-sm font-semibold text-cyan-300 mb-3">TÓPICOS</h3>
                  <div className="space-y-2">
                    {results.topicos.map((topico, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSelectResult(topico, 'topico')}
                        className="w-full text-left px-4 py-3 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20 transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{topico.icone}</span>
                          <div>
                            <p className="text-cyan-100 font-medium group-hover:text-cyan-300">
                              {topico.nome}
                            </p>
                            {topico.valor_encontrado && (
                              <p className="text-xs text-cyan-300/60">
                                Valor: {topico.valor_encontrado}
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Produtos */}
              {results.produtos && results.produtos.length > 0 && (
                <div className="p-4">
                  <h3 className="text-sm font-semibold text-cyan-300 mb-3">PRODUTOS</h3>
                  <div className="space-y-2">
                    {results.produtos.map((produto) => (
                      <button
                        key={produto.sku}
                        onClick={() => handleSelectResult(produto, 'produto')}
                        className="w-full text-left px-4 py-3 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 transition-all group"
                      >
                        <p className="text-cyan-100 font-medium group-hover:text-cyan-300">
                          {produto.sku}
                        </p>
                        <p className="text-sm text-cyan-300/60">{produto.title}</p>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SearchBar;