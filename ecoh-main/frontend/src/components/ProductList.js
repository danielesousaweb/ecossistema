import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Button } from './ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  useEffect(() => {
    loadProducts();
    loadCategories();
  }, []);
  
  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/products`);
      if (response.data.success) {
        setProducts(response.data.data);
      }
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API}/products/categories/list`);
      if (response.data.success) {
        setCategories(response.data.data);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };
  
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' ||
                           product.categories.includes(selectedCategory);
    return matchesSearch && matchesCategory;
  });
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'inactive': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      case 'discontinued': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500"
              data-testid="product-list-title">
            Product Catalog
          </h1>
          <p className="text-cyan-300/70 text-lg">Unopim Synchronized Products</p>
        </div>
        
        {/* Filters */}
        <div className="flex gap-4 backdrop-blur-xl bg-slate-900/40 border border-cyan-500/30 rounded-2xl p-6">
          <Input
            data-testid="search-input"
            placeholder="Search by SKU or title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 bg-slate-800/50 border-cyan-500/30 text-cyan-100 placeholder:text-cyan-300/50"
          />
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-64 bg-slate-800/50 border-cyan-500/30 text-cyan-100"
                          data-testid="category-filter">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-cyan-500/30">
              <SelectItem value="all">All Categories</SelectItem>
              {categories.map(cat => (
                <SelectItem key={cat.slug} value={cat.slug}>
                  {cat.name} ({cat.count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        {/* Product Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-400"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map(product => (
              <Card
                key={product.sku}
                data-testid={`product-card-${product.sku}`}
                className="backdrop-blur-xl bg-slate-900/60 border-cyan-500/30 hover:border-cyan-400/50 transition-all cursor-pointer group"
                onClick={() => setSelectedProduct(product)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-cyan-100 group-hover:text-cyan-400 transition-colors">
                        {product.sku}
                      </CardTitle>
                      <p className="text-sm text-cyan-300/60 mt-1">{product.title}</p>
                    </div>
                    <Badge className={`${getStatusColor(product.status)} border`}>
                      {product.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Categories */}
                  <div className="flex flex-wrap gap-2">
                    {product.categories.map(cat => (
                      <Badge
                        key={cat}
                        variant="outline"
                        className="bg-blue-500/10 text-blue-400 border-blue-500/30"
                      >
                        {cat}
                      </Badge>
                    ))}
                  </div>
                  
                  {/* Relationships count */}
                  {product.relationships && Object.keys(product.relationships).length > 0 && (
                    <div className="flex items-center gap-2 text-sm text-cyan-300/70">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      <span>
                        {Object.values(product.relationships).reduce((sum, arr) => sum + arr.length, 0)} connections
                      </span>
                    </div>
                  )}
                  
                  {/* Completeness score */}
                  {product.completeness_score && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-cyan-300/70">
                        <span>Completeness</span>
                        <span>{product.completeness_score}%</span>
                      </div>
                      <div className="w-full bg-slate-800/50 rounded-full h-1.5">
                        <div
                          className="bg-gradient-to-r from-cyan-500 to-blue-500 h-1.5 rounded-full transition-all"
                          style={{ width: `${product.completeness_score}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        
        {filteredProducts.length === 0 && !loading && (
          <div className="text-center py-16">
            <p className="text-cyan-300/60 text-lg">No products found</p>
          </div>
        )}
      </div>
      
      {/* Product Detail Modal */}
      {selectedProduct && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedProduct(null)}
          data-testid="product-modal"
        >
          <div
            className="backdrop-blur-xl bg-slate-900/90 border border-cyan-500/30 rounded-2xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-cyan-100">{selectedProduct.sku}</h2>
                  <p className="text-cyan-300/70 mt-1">{selectedProduct.title}</p>
                </div>
                <button
                  data-testid="close-modal-btn"
                  onClick={() => setSelectedProduct(null)}
                  className="text-cyan-300 hover:text-cyan-100 transition-colors text-2xl"
                >
                  ✕
                </button>
              </div>
              
              <div className="flex gap-2">
                <Badge className={`${getStatusColor(selectedProduct.status)} border`}>
                  {selectedProduct.status}
                </Badge>
                {selectedProduct.categories.map(cat => (
                  <Badge key={cat} variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
                    {cat}
                  </Badge>
                ))}
              </div>
              
              {/* Attributes */}
              {selectedProduct.attributes && Object.keys(selectedProduct.attributes).length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-cyan-300">Attributes</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(selectedProduct.attributes).map(([key, value]) => (
                      <div key={key} className="bg-slate-800/50 rounded-lg p-3">
                        <p className="text-xs text-cyan-300/70">{key}</p>
                        <p className="text-sm text-cyan-100 font-mono">{String(value)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Relationships */}
              {selectedProduct.relationships && Object.keys(selectedProduct.relationships).length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-cyan-300">Relationships</h3>
                  {Object.entries(selectedProduct.relationships).map(([relType, targets]) => (
                    <div key={relType} className="space-y-2">
                      <p className="text-sm text-cyan-300/70 capitalize">{relType}</p>
                      <div className="flex flex-wrap gap-2">
                        {targets.map(target => (
                          <Badge key={target} variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/30">
                            {target}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}