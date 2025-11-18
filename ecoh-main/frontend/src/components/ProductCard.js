import React from 'react';
import { motion } from 'framer-motion';
import { Badge } from './ui/badge';
import { ExternalLink } from 'lucide-react';
import { formatValue, formatFieldName } from '../utils/formatters';

const ProductCard = ({ product, onClick, onBadgeClick }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'inactive': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      case 'discontinued': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    }
  };
  
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick(product)}
      className="backdrop-blur-xl bg-gradient-to-br from-slate-900/60 via-indigo-950/40 to-slate-900/60 border-2 border-cyan-500/20 hover:border-cyan-400/50 rounded-2xl p-6 cursor-pointer transition-all group"
      style={{
        boxShadow: '0 0 30px rgba(34, 211, 238, 0.1), inset 0 0 40px rgba(34, 211, 238, 0.03)'
      }}
      data-testid={`product-card-${product.sku}`}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-cyan-100 group-hover:text-cyan-300 transition-colors flex items-center gap-2">
              {product.sku}
              <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
            </h3>
            <p className="text-sm text-cyan-300/70 mt-1">{product.title}</p>
          </div>
          
          <Badge className={`${getStatusColor(product.status)} border`}>
            {product.status === 'active' ? 'Ativo' : 
             product.status === 'inactive' ? 'Inativo' : 'Descontinuado'}
          </Badge>
        </div>
        
        {/* Categories */}
        {product.categories && product.categories.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {product.categories.map(cat => (
              <Badge
                key={cat}
                variant="outline"
                className="bg-blue-500/10 text-blue-300 border-blue-500/30 text-xs"
              >
                {cat}
              </Badge>
            ))}
          </div>
        )}
        
        {/* Attributes Preview */}
        {product.attributes && Object.keys(product.attributes).length > 0 && (
          <div className="space-y-1">
            {Object.entries(product.attributes).slice(0, 3).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2 text-xs">
                <span className="text-cyan-300/50" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  {formatFieldName(key)}:
                </span>
                <span className="text-cyan-100" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  {formatValue(value)}
                </span>
              </div>
            ))}
          </div>
        )}
        
        {/* Relationships as clickable badges */}
        {product.relationships && Object.keys(product.relationships).length > 0 && (
          <div className="space-y-2 pt-2 border-t border-cyan-500/10">
            <div className="flex items-center gap-2 text-xs text-cyan-300/70">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <span style={{ fontFamily: 'Roboto, sans-serif' }}>Conexões</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {Object.entries(product.relationships).slice(0, 2).map(([relType, targets]) => 
                targets.slice(0, 3).map(target => (
                  <Badge
                    key={`${relType}-${target}`}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      console.log('Badge clicked in ProductCard:', target, relType);
                      if (onBadgeClick) {
                        onBadgeClick(target, relType);
                      }
                    }}
                    className="bg-blue-500/20 text-blue-300 border-blue-500/30 hover:bg-blue-500/30 cursor-pointer transition-all text-xs"
                    style={{ fontFamily: 'Roboto Condensed, sans-serif' }}
                    data-testid={`badge-${target}`}
                  >
                    {formatValue(target)}
                  </Badge>
                ))
              )}
            </div>
          </div>
        )}
        
        {/* Completeness Score */}
        {product.completeness_score && (
          <div className="space-y-1 pt-2">
            <div className="flex justify-between text-xs text-cyan-300/70">
              <span>Completude</span>
              <span>{product.completeness_score}%</span>
            </div>
            <div className="w-full bg-slate-800/50 rounded-full h-1.5 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${product.completeness_score}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full"
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ProductCard;