# 🎨 Frontend Guide

> **  AI Voucher Assistant - Frontend Development Guide**

## 📋 Table of Contents
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Development Setup](#development-setup)
- [UI/UX Design Patterns](#uiux-design-patterns)
- [State Management](#state-management)
- [Performance Optimization](#performance-optimization)

## 📁 Project Structure

```
voucher_assistant/frontend/
├── public/
│   ├── index.html                # Main HTML template
│   ├── favicon.ico               # App icon
│   └── manifest.json             # PWA manifest
│
├── src/
│   ├── components/               # Reusable UI components
│   │   ├── AdvancedVoucherSearch.tsx    # Main search component
│   │   ├── SearchResults.tsx            # Results display component
│   │   ├── VoucherCard.tsx              # Individual voucher card
│   │   ├── FilterPanel.tsx              # Search filters
│   │   ├── LoadingSpinner.tsx           # Loading indicator
│   │   └── ErrorBoundary.tsx            # Error handling
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useSearch.ts          # Search functionality hook
│   │   ├── useDebounce.ts        # Input debouncing
│   │   ├── useLocalStorage.ts    # Local storage management
│   │   └── useGeolocation.ts     # Location services
│   │
│   ├── services/                 # API and external services
│   │   ├── api.ts                # API client configuration
│   │   ├── searchService.ts      # Search API calls
│   │   ├── locationService.ts    # Location utilities
│   │   └── analytics.ts          # Analytics tracking
│   │
│   ├── types/                    # TypeScript type definitions
│   │   ├── search.ts             # Search-related types
│   │   ├── voucher.ts            # Voucher data types
│   │   └── api.ts                # API response types
│   │
│   ├── utils/                    # Utility functions
│   │   ├── formatters.ts         # Data formatting utilities
│   │   ├── validators.ts         # Input validation
│   │   ├── constants.ts          # App constants
│   │   └── helpers.ts            # General helpers
│   │
│   ├── styles/                   # Styling
│   │   ├── globals.css           # Global styles
│   │   ├── components.css        # Component styles
│   │   ├── themes.css            # Theme definitions
│   │   └── animations.css        # Animation definitions
│   │
│   ├── App.tsx                   # Main application component
│   ├── index.tsx                 # Application entry point
│   └── setupTests.ts             # Test configuration
│
├── package.json                  # Dependencies and scripts
├── tsconfig.json                 # TypeScript configuration
├── tailwind.config.js            # Tailwind CSS configuration
└── vite.config.ts                # Vite build configuration
```

## 🔧 Core Components

### 1. Advanced Voucher Search Component
```tsx
// src/components/AdvancedVoucherSearch.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { useSearch } from '../hooks/useSearch';
import { SearchRequest, SearchResponse, VoucherResult } from '../types/search';
import SearchResults from './SearchResults';
import FilterPanel from './FilterPanel';
import LoadingSpinner from './LoadingSpinner';

interface AdvancedVoucherSearchProps {
  onVoucherSelect?: (voucher: VoucherResult) => void;
  defaultQuery?: string;
  maxResults?: number;
}

const AdvancedVoucherSearch: React.FC<AdvancedVoucherSearchProps> = ({
  onVoucherSelect,
  defaultQuery = '',
  maxResults = 20
}) => {
  // State management
  const [query, setQuery] = useState(defaultQuery);
  const [filters, setFilters] = useState({
    location: '',
    serviceType: '',
    priceRange: '',
    targetAudience: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  
  // Custom hooks
  const debouncedQuery = useDebounce(query, 300);
  const { 
    results, 
    loading, 
    error, 
    metadata, 
    searchVouchers, 
    clearResults 
  } = useSearch();

  // Search effect
  useEffect(() => {
    if (debouncedQuery.trim().length > 0) {
      handleSearch();
    } else {
      clearResults();
    }
  }, [debouncedQuery, filters]);

  // Search handler
  const handleSearch = useCallback(async () => {
    const searchRequest: SearchRequest = {
      query: debouncedQuery,
      top_k: maxResults,
      location_filter: filters.location || undefined,
      service_filter: filters.serviceType || undefined,
      price_filter: filters.priceRange || undefined,
      target_audience_filter: filters.targetAudience || undefined
    };

    await searchVouchers(searchRequest);
  }, [debouncedQuery, filters, maxResults, searchVouchers]);

  // Filter change handler
  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      location: '',
      serviceType: '',
      priceRange: '',
      targetAudience: ''
    });
  };

  return (
    <div className="advanced-voucher-search">
      {/* Search Header */}
      <div className="search-header bg-white shadow-lg rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Tìm kiếm voucher, nhà hàng, khách sạn... (VD: buffet Hà Nội, Bellissimo)"
                className="w-full px-4 py-3 pl-12 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-3 rounded-lg border transition-colors ${
              showFilters 
                ? 'bg-blue-500 text-white border-blue-500' 
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
            </svg>
          </button>
        </div>

        {/* Quick Stats */}
        {metadata && (
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <div>
              Tìm thấy <span className="font-semibold text-blue-600">{metadata.total_results}</span> kết quả
              {metadata.processing_time_ms && (
                <span className="ml-2">
                  trong <span className="font-semibold">{metadata.processing_time_ms}ms</span>
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                {metadata.search_method === 'advanced_multi_field_with_intelligence' ? 'AI Search' : 'Standard'}
              </span>
              {filters.location && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  📍 {filters.location}
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <FilterPanel
          filters={filters}
          onFilterChange={handleFilterChange}
          onClearFilters={clearFilters}
          className="mb-6"
        />
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="large" message="Đang tìm kiếm voucher tốt nhất cho bạn..." />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
          <div className="flex items-center">
            <svg className="h-6 w-6 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-red-800 font-semibold">Có lỗi xảy ra</h3>
              <p className="text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {!loading && !error && (
        <SearchResults
          results={results}
          query={query}
          onVoucherSelect={onVoucherSelect}
          metadata={metadata}
        />
      )}

      {/* Empty State */}
      {!loading && !error && results.length === 0 && query.trim().length > 0 && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <svg className="h-16 w-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.54-.94-6.127-2.627C7.746 10.501 9.77 9 12 9s4.254 1.501 6.127 3.373A7.963 7.963 0 0112 15z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Không tìm thấy voucher phù hợp
            </h3>
            <p className="text-gray-500 mb-4">
              Thử tìm kiếm với từ khóa khác hoặc điều chỉnh bộ lọc
            </p>
            <button
              onClick={clearFilters}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Xóa bộ lọc và thử lại
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedVoucherSearch;
```

### 2. Search Results Component
```tsx
// src/components/SearchResults.tsx
import React from 'react';
import { VoucherResult, SearchMetadata } from '../types/search';
import VoucherCard from './VoucherCard';

interface SearchResultsProps {
  results: VoucherResult[];
  query: string;
  onVoucherSelect?: (voucher: VoucherResult) => void;
  metadata?: SearchMetadata;
}

const SearchResults: React.FC<SearchResultsProps> = ({ 
  results, 
  query, 
  onVoucherSelect,
  metadata 
}) => {
  if (results.length === 0) {
    return null;
  }

  return (
    <div className="search-results">
      {/* Results Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">
          Kết quả tìm kiếm
          {query && (
            <span className="text-gray-500 font-normal ml-2">
              cho "{query}"
            </span>
          )}
        </h2>
        
        {/* Sort Options */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Sắp xếp:</span>
          <select className="text-sm border border-gray-300 rounded px-2 py-1">
            <option value="relevance">Phù hợp nhất</option>
            <option value="price_low">Giá thấp đến cao</option>
            <option value="price_high">Giá cao đến thấp</option>
            <option value="distance">Khoảng cách</option>
          </select>
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {results.map((voucher, index) => (
          <VoucherCard
            key={voucher.voucher_id || index}
            voucher={voucher}
            rank={index + 1}
            onSelect={onVoucherSelect}
            highlightQuery={query}
          />
        ))}
      </div>

      {/* Load More Button */}
      {results.length >= 20 && (
        <div className="text-center mt-8">
          <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
            Xem thêm kết quả
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
```

### 3. Voucher Card Component
```tsx
// src/components/VoucherCard.tsx
import React from 'react';
import { VoucherResult } from '../types/search';
import { formatCurrency, highlightText } from '../utils/formatters';

interface VoucherCardProps {
  voucher: VoucherResult;
  rank: number;
  onSelect?: (voucher: VoucherResult) => void;
  highlightQuery?: string;
}

const VoucherCard: React.FC<VoucherCardProps> = ({ 
  voucher, 
  rank, 
  onSelect,
  highlightQuery 
}) => {
  const handleClick = () => {
    onSelect?.(voucher);
  };

  const similarityPercentage = Math.round((voucher.similarity_score || 0) * 100);
  const geographicScore = voucher.geographic_score || 0;

  return (
    <div 
      className="voucher-card bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
      onClick={handleClick}
    >
      {/* Card Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg text-gray-800 mb-1">
              {highlightQuery ? (
                <span dangerouslySetInnerHTML={{
                  __html: highlightText(voucher.voucher_name || 'Unknown Voucher', highlightQuery)
                }} />
              ) : (
                voucher.voucher_name || 'Unknown Voucher'
              )}
            </h3>
            
            {/* Location */}
            {voucher.location?.name && (
              <div className="flex items-center text-sm text-gray-600 mb-2">
                <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {voucher.location.name}
                {voucher.location.district && `, ${voucher.location.district}`}
              </div>
            )}
          </div>
          
          {/* Rank Badge */}
          <div className="flex flex-col items-end">
            <div className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded-full mb-2">
              #{rank}
            </div>
            {similarityPercentage > 0 && (
              <div className="text-xs text-gray-500">
                {similarityPercentage}% match
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Card Content */}
      <div className="p-4">
        {/* Service Information */}
        {voucher.service_info && (
          <div className="mb-3">
            <div className="flex items-center text-sm text-gray-600 mb-1">
              <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              {voucher.service_info.category || 'Dịch vụ'}
            </div>
            {voucher.service_info.cuisine_type && (
              <div className="text-xs text-gray-500">
                {voucher.service_info.cuisine_type}
              </div>
            )}
          </div>
        )}

        {/* Price Information */}
        {voucher.price_info && (
          <div className="mb-3">
            <div className="flex items-center justify-between">
              <div>
                {voucher.price_info.original_price && (
                  <div className="text-lg font-bold text-green-600">
                    {formatCurrency(voucher.price_info.original_price)}
                  </div>
                )}
                {voucher.price_info.discounted_price && (
                  <div className="text-sm text-gray-500 line-through">
                    {formatCurrency(voucher.price_info.discounted_price)}
                  </div>
                )}
              </div>
              
              {voucher.price_info.discount_percentage && (
                <div className="bg-red-100 text-red-800 text-xs font-semibold px-2 py-1 rounded">
                  -{voucher.price_info.discount_percentage}%
                </div>
              )}
            </div>
          </div>
        )}

        {/* Content Preview */}
        {voucher.content && (
          <div className="text-sm text-gray-600 mb-3">
            <p className="line-clamp-2">
              {highlightQuery ? (
                <span dangerouslySetInnerHTML={{
                  __html: highlightText(voucher.content.substring(0, 120) + '...', highlightQuery)
                }} />
              ) : (
                voucher.content.substring(0, 120) + '...'
              )}
            </p>
          </div>
        )}

        {/* Tags */}
        <div className="flex flex-wrap gap-1">
          {voucher.target_audience && (
            <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
              {voucher.target_audience}
            </span>
          )}
          
          {geographicScore > 0.8 && (
            <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
              📍 Gần bạn
            </span>
          )}
          
          {voucher.price_info?.price_range && (
            <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
              {voucher.price_info.price_range}
            </span>
          )}
        </div>
      </div>

      {/* Card Footer */}
      <div className="px-4 pb-4">
        <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg font-medium transition-colors">
          Xem chi tiết
        </button>
      </div>
    </div>
  );
};

export default VoucherCard;
```

## 🎯 Custom Hooks

### 1. Search Hook
```tsx
// src/hooks/useSearch.ts
import { useState, useCallback } from 'react';
import { searchVouchers as apiSearchVouchers } from '../services/searchService';
import { SearchRequest, SearchResponse, VoucherResult, SearchMetadata } from '../types/search';

interface UseSearchReturn {
  results: VoucherResult[];
  loading: boolean;
  error: string | null;
  metadata: SearchMetadata | null;
  searchVouchers: (request: SearchRequest) => Promise<void>;
  clearResults: () => void;
  retryLastSearch: () => Promise<void>;
}

export const useSearch = (): UseSearchReturn => {
  const [results, setResults] = useState<VoucherResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<SearchMetadata | null>(null);
  const [lastRequest, setLastRequest] = useState<SearchRequest | null>(null);

  const searchVouchers = useCallback(async (request: SearchRequest) => {
    try {
      setLoading(true);
      setError(null);
      setLastRequest(request);

      const response = await apiSearchVouchers(request);
      
      setResults(response.results || []);
      setMetadata(response.metadata || null);
      
      // Analytics tracking
      if (window.gtag) {
        window.gtag('event', 'search', {
          search_term: request.query,
          results_count: response.results?.length || 0
        });
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Có lỗi xảy ra khi tìm kiếm';
      setError(errorMessage);
      setResults([]);
      setMetadata(null);
      
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
    setMetadata(null);
    setLastRequest(null);
  }, []);

  const retryLastSearch = useCallback(async () => {
    if (lastRequest) {
      await searchVouchers(lastRequest);
    }
  }, [lastRequest, searchVouchers]);

  return {
    results,
    loading,
    error,
    metadata,
    searchVouchers,
    clearResults,
    retryLastSearch
  };
};
```

### 2. Debounce Hook
```tsx
// src/hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};
```

## 🎨 UI/UX Design Patterns

### 1. Design System
```css
/* src/styles/themes.css */
:root {
  /*   Brand Colors */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  
  /* Semantic Colors */
  --success-50: #ecfdf5;
  --success-500: #10b981;
  --error-50: #fef2f2;
  --error-500: #ef4444;
  --warning-50: #fffbeb;
  --warning-500: #f59e0b;
  
  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Spacing Scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 3rem;
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* Dark theme support */
[data-theme='dark'] {
  --primary-500: #60a5fa;
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
}
```

### 2. Responsive Grid System
```css
/* src/styles/components.css */
.search-grid {
  display: grid;
  gap: var(--spacing-lg);
  
  /* Mobile First */
  grid-template-columns: 1fr;
  
  /* Tablet */
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  /* Desktop */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
  
  /* Large Desktop */
  @media (min-width: 1280px) {
    grid-template-columns: repeat(4, 1fr);
  }
}

.voucher-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
}
```

### 3. Animation System
```css
/* src/styles/animations.css */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

/* Utility classes */
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}

/* Stagger animation for lists */
.stagger-children > * {
  animation: fadeIn 0.3s ease-out;
}

.stagger-children > *:nth-child(1) { animation-delay: 0.1s; }
.stagger-children > *:nth-child(2) { animation-delay: 0.2s; }
.stagger-children > *:nth-child(3) { animation-delay: 0.3s; }
```

## 📱 Responsive Design

### 1. Mobile-First Approach
```tsx
// src/components/MobileSearch.tsx
import React, { useState } from 'react';
import { useMediaQuery } from '../hooks/useMediaQuery';

const MobileSearch: React.FC = () => {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  if (!isMobile) {
    return <AdvancedVoucherSearch />;
  }

  return (
    <div className="mobile-search">
      {/* Mobile Search Header */}
      <div className="sticky top-0 bg-white z-10 p-4 border-b">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Tìm voucher..."
            className="flex-1 px-3 py-2 border rounded-lg"
          />
          <button
            onClick={() => setShowMobileFilters(true)}
            className="p-2 border rounded-lg"
          >
            <FilterIcon />
          </button>
        </div>
      </div>

      {/* Mobile Filter Modal */}
      {showMobileFilters && (
        <div className="fixed inset-0 z-50 bg-white">
          <div className="p-4 border-b flex items-center justify-between">
            <h3 className="text-lg font-semibold">Bộ lọc</h3>
            <button onClick={() => setShowMobileFilters(false)}>
              <CloseIcon />
            </button>
          </div>
          
          <div className="p-4">
            {/* Mobile-optimized filters */}
            <FilterPanel mobile />
          </div>
          
          <div className="p-4 border-t">
            <button 
              className="w-full bg-blue-500 text-white py-3 rounded-lg"
              onClick={() => setShowMobileFilters(false)}
            >
              Áp dụng bộ lọc
            </button>
          </div>
        </div>
      )}
      
      {/* Mobile Results */}
      <div className="p-4">
        <SearchResults mobile />
      </div>
    </div>
  );
};
```

### 2. Progressive Web App (PWA)
```json
// public/manifest.json
{
  "name": "  Voucher Assistant",
  "short_name": "  Vouchers",
  "description": "AI-powered voucher search for   ecosystem",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ],
  "categories": ["food", "shopping", "travel"],
  "lang": "vi-VN"
}
```

## ⚡ Performance Optimization

### 1. Code Splitting
```tsx
// src/App.tsx
import React, { Suspense, lazy } from 'react';
import LoadingSpinner from './components/LoadingSpinner';

// Lazy load heavy components
const AdvancedVoucherSearch = lazy(() => import('./components/AdvancedVoucherSearch'));
const VoucherDetails = lazy(() => import('./components/VoucherDetails'));
const UserProfile = lazy(() => import('./components/UserProfile'));

const App: React.FC = () => {
  return (
    <div className="app">
      <Suspense fallback={<LoadingSpinner />}>
        <AdvancedVoucherSearch />
      </Suspense>
    </div>
  );
};

export default App;
```

### 2. Image Optimization
```tsx
// src/components/LazyImage.tsx
import React, { useState, useRef, useEffect } from 'react';

interface LazyImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
}

const LazyImage: React.FC<LazyImageProps> = ({ 
  src, 
  alt, 
  className, 
  placeholder = '/images/placeholder.jpg' 
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div className={`relative ${className}`}>
      <img
        ref={imgRef}
        src={isInView ? src : placeholder}
        alt={alt}
        className={`transition-opacity duration-300 ${
          isLoaded ? 'opacity-100' : 'opacity-50'
        }`}
        onLoad={() => setIsLoaded(true)}
        loading="lazy"
      />
      
      {!isLoaded && isInView && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
    </div>
  );
};

export default LazyImage;
```

### 3. Virtual Scrolling
```tsx
// src/components/VirtualizedResults.tsx
import React from 'react';
import { FixedSizeList as List } from 'react-window';
import { VoucherResult } from '../types/search';
import VoucherCard from './VoucherCard';

interface VirtualizedResultsProps {
  results: VoucherResult[];
  height: number;
  itemHeight: number;
}

const VirtualizedResults: React.FC<VirtualizedResultsProps> = ({
  results,
  height,
  itemHeight
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style} className="p-2">
      <VoucherCard voucher={results[index]} rank={index + 1} />
    </div>
  );

  return (
    <List
      height={height}
      itemCount={results.length}
      itemSize={itemHeight}
      className="scrollbar-thin scrollbar-thumb-gray-300"
    >
      {Row}
    </List>
  );
};

export default VirtualizedResults;
```

## 🧪 Testing

### 1. Component Testing
```tsx
// src/components/__tests__/AdvancedVoucherSearch.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import AdvancedVoucherSearch from '../AdvancedVoucherSearch';
import * as searchService from '../../services/searchService';

// Mock the search service
vi.mock('../../services/searchService');

describe('AdvancedVoucherSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders search input', () => {
    render(<AdvancedVoucherSearch />);
    
    const searchInput = screen.getByPlaceholderText(/tìm kiếm voucher/i);
    expect(searchInput).toBeInTheDocument();
  });

  test('performs search when typing', async () => {
    const mockSearchResponse = {
      results: [
        {
          voucher_id: '1',
          voucher_name: 'Test Voucher',
          content: 'Test content',
          similarity_score: 0.9
        }
      ],
      metadata: {
        total_results: 1,
        processing_time_ms: 100
      }
    };

    vi.mocked(searchService.searchVouchers).mockResolvedValue(mockSearchResponse);

    render(<AdvancedVoucherSearch />);
    
    const searchInput = screen.getByPlaceholderText(/tìm kiếm voucher/i);
    fireEvent.change(searchInput, { target: { value: 'buffet' } });

    await waitFor(() => {
      expect(searchService.searchVouchers).toHaveBeenCalledWith({
        query: 'buffet',
        top_k: 20
      });
    });

    expect(screen.getByText('Test Voucher')).toBeInTheDocument();
  });

  test('displays error state', async () => {
    vi.mocked(searchService.searchVouchers).mockRejectedValue(
      new Error('Search failed')
    );

    render(<AdvancedVoucherSearch />);
    
    const searchInput = screen.getByPlaceholderText(/tìm kiếm voucher/i);
    fireEvent.change(searchInput, { target: { value: 'error' } });

    await waitFor(() => {
      expect(screen.getByText(/có lỗi xảy ra/i)).toBeInTheDocument();
    });
  });
});
```

### 2. Integration Testing
```tsx
// src/__tests__/SearchFlow.integration.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import App from '../App';

const server = setupServer(
  rest.post('/api/advanced-search', (req, res, ctx) => {
    return res(
      ctx.json({
        results: [
          {
            voucher_id: '1',
            voucher_name: 'Bellissimo Restaurant',
            content: 'Luxury buffet experience',
            similarity_score: 0.95
          }
        ],
        metadata: {
          total_results: 1,
          processing_time_ms: 150
        }
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Search Flow Integration', () => {
  test('complete search flow', async () => {
    render(<App />);

    // Type in search box
    const searchInput = screen.getByPlaceholderText(/tìm kiếm voucher/i);
    fireEvent.change(searchInput, { target: { value: 'Bellissimo' } });

    // Wait for search results
    await waitFor(() => {
      expect(screen.getByText('Bellissimo Restaurant')).toBeInTheDocument();
    });

    // Check metadata display
    expect(screen.getByText(/tìm thấy.*1.*kết quả/i)).toBeInTheDocument();
    expect(screen.getByText(/150ms/)).toBeInTheDocument();

    // Click on voucher card
    const voucherCard = screen.getByText('Bellissimo Restaurant').closest('.voucher-card');
    fireEvent.click(voucherCard!);

    // Should navigate or show details
    // Assert based on your navigation logic
  });
});
```

---

**Next**: [📊 Data Processing Guide](./DATA_PROCESSING.md)
