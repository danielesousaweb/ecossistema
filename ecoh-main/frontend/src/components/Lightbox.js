import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

const Lightbox = ({ isOpen, onClose, title, children, icon }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);
  
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-xl"
            style={{ zIndex: 9998 }}
            onClick={onClose}
            data-testid="lightbox-backdrop"
          />
          
          {/* Lightbox Content */}
          <div className="fixed inset-0 flex items-center justify-center p-4 pointer-events-none"
               style={{ zIndex: 9999 }}>
            <motion.div
              initial={{ scale: 0.8, opacity: 0, y: 50 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 50 }}
              transition={{ 
                type: 'spring',
                damping: 25,
                stiffness: 300
              }}
              className="w-full max-w-5xl max-h-[85vh] pointer-events-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="backdrop-blur-2xl bg-gradient-to-br from-slate-900/95 via-indigo-950/95 to-slate-900/95 border-2 border-cyan-500/30 rounded-3xl shadow-2xl overflow-hidden"
                   style={{
                     boxShadow: '0 0 60px rgba(34, 211, 238, 0.3), inset 0 0 80px rgba(34, 211, 238, 0.05)'
                   }}>
                
                {/* Header */}
                <div className="relative px-8 py-6 border-b border-cyan-500/20 bg-gradient-to-r from-cyan-500/10 to-blue-500/10">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {icon && (
                        <div className="text-5xl animate-pulse">
                          {icon}
                        </div>
                      )}
                      <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-400"
                          data-testid="lightbox-title">
                        {title}
                      </h2>
                    </div>
                    
                    <Button
                      data-testid="lightbox-close-btn"
                      onClick={onClose}
                      variant="ghost"
                      className="text-cyan-300 hover:text-white hover:bg-cyan-500/20 rounded-full w-12 h-12 p-0"
                    >
                      <X className="w-6 h-6" />
                    </Button>
                  </div>
                </div>
                
                {/* Content */}
                <div className="overflow-y-auto max-h-[calc(85vh-120px)] p-8 custom-scrollbar">
                  {children}
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

export default Lightbox;