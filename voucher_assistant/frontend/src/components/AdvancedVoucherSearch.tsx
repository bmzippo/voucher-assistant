import React, { useState } from 'react';
import styled from 'styled-components';

// Type definitions for API responses
interface ParsedQuery {
  intent: string;
  location?: string;
  service_requirements: string[];
  confidence: number;
}

interface QueryAnalysis {
  parsing_results: ParsedQuery;
}

interface SearchMetadata {
  total_results: number;
  processing_time_ms: number;
  search_method: string;
}

interface LocationInfo {
  name: string;
}

interface ServiceInfo {
  category?: string;
  has_kids_area?: boolean;
}

interface PriceInfo {
  price_range?: string;
}

interface SearchResult {
  voucher_id?: string;
  voucher_name: string;
  similarity_score: number;
  location?: LocationInfo;
  ranking_factor?: string;
  content?: string;
  service_info?: ServiceInfo;
  price_info?: PriceInfo;
}

interface SearchExplanations {
  geographic_ranking?: string;
}

interface SearchResponse {
  metadata: SearchMetadata;
  results: SearchResult[];
  explanations?: SearchExplanations;
}

// Advanced UI Components
const AdvancedSearchContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const SearchHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  margin-bottom: 30px;
  text-align: center;
`;

const SearchTitle = styled.h1`
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
`;

const SearchSubtitle = styled.p`
  margin: 10px 0 0 0;
  font-size: 1.1rem;
  opacity: 0.9;
`;

const SearchForm = styled.div`
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  margin-bottom: 30px;
`;

const SearchInputContainer = styled.div`
  position: relative;
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 15px 20px;
  font-size: 1.1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  outline: none;
  transition: all 0.3s ease;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const AdvancedOptions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const FilterSelect = styled.select`
  padding: 10px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  
  &:focus {
    border-color: #667eea;
  }
`;

const SearchButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ResultsContainer = styled.div`
  display: grid;
  gap: 20px;
`;

const QueryAnalysisCard = styled.div`
  background: #f8f9ff;
  border: 2px solid #e6e9ff;
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
`;

const AnalysisTitle = styled.h3`
  color: #4a5568;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const AnalysisGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
`;

const AnalysisItem = styled.div`
  background: white;
  padding: 15px;
  border-radius: 10px;
  border-left: 4px solid #667eea;
`;

const ResultCard = styled.div`
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  }
`;

const ResultHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
`;

const ResultTitle = styled.h3`
  color: #2d3748;
  margin: 0;
  font-size: 1.3rem;
  flex: 1;
`;

const ScoreBadge = styled.span<{ score: number }>`
  background: ${props => props.score > 0.7 ? '#48bb78' : props.score > 0.5 ? '#ed8936' : '#e53e3e'};
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
`;

const LocationBadge = styled.span`
  background: #667eea;
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  margin-left: 10px;
`;

const RankingFactorBadge = styled.span<{ factor: string }>`
  background: ${props => {
    switch(props.factor) {
      case 'exact_location_match': return '#48bb78';
      case 'nearby_location_match': return '#ed8936';
      case 'regional_match': return '#3182ce';
      case 'semantic_match': return '#805ad5';
      default: return '#718096';
    }
  }};
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  margin-left: 5px;
`;

const ResultContent = styled.div`
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 15px;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e0e0e0;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: #fed7d7;
  border: 1px solid #f56565;
  color: #c53030;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
`;

const AdvancedVoucherSearch = () => {
  const [query, setQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [serviceFilter, setServiceFilter] = useState('');
  const [priceFilter, setPriceFilter] = useState('');
  const [strictLocation, setStrictLocation] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [queryAnalysis, setQueryAnalysis] = useState<QueryAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8001/api/advanced-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          top_k: 10,
          location_filter: locationFilter || null,
          service_filter: serviceFilter || null,
          price_filter: priceFilter || null,
          strict_location: strictLocation
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data);
      
      // Also get query analysis
      const analysisResponse = await fetch(`http://localhost:8001/api/analyze-query?query=${encodeURIComponent(query)}`);
      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        setQueryAnalysis(analysisData);
      }
      
    } catch (err) {
      let message = 'Lỗi không xác định';
      if (err instanceof Error) {
        message = err.message;
      } else if (typeof err === 'string') {
        message = err;
      }
      setError(`Lỗi tìm kiếm: ${message}`);
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getIntentIcon = (intent: string): string => {
    const icons: { [key: string]: string } = {
      'find_restaurant': '🍽️',
      'find_hotel': '🏨',
      'find_entertainment': '🎮',
      'find_shopping': '🛍️',
      'find_beauty': '💅',
      'find_kids': '👶',
      'general_search': '🔍'
    };
    return icons[intent] || '🔍';
  };

  const getRankingFactorText = (factor: string) => {
    const texts: { [key: string]: string } = {
      'exact_location_match': 'Khớp chính xác địa điểm',
      'nearby_location_match': 'Địa điểm gần đó',
      'regional_match': 'Cùng vùng',
      'semantic_match': 'Khớp ngữ nghĩa'
    };
    return texts[factor] || factor;
  };

  return (
    <AdvancedSearchContainer>
      <SearchHeader>
        <SearchTitle>🎯   AI Voucher Assistant</SearchTitle>
        <SearchSubtitle>Advanced Intelligence • Multi-field Embedding • Location Awareness</SearchSubtitle>
      </SearchHeader>

      <SearchForm>
        <SearchInputContainer>
          <SearchInput
            type="text"
            placeholder="Nhập tìm kiếm của bạn... VD: 'quán ăn tại hải phòng có chỗ cho trẻ em chơi'"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
          />
        </SearchInputContainer>

        <AdvancedOptions>
          <FilterSelect 
            value={locationFilter} 
            onChange={(e) => setLocationFilter(e.target.value)}
          >
            <option value="">🌍 Tất cả địa điểm</option>
            <option value="Hải Phòng">Hải Phòng</option>
            <option value="Hà Nội">Hà Nội</option>
            <option value="Hồ Chí Minh">Hồ Chí Minh</option>
            <option value="Đà Nẵng">Đà Nẵng</option>
            <option value="Cần Thơ">Cần Thơ</option>
          </FilterSelect>

          <FilterSelect 
            value={serviceFilter} 
            onChange={(e) => setServiceFilter(e.target.value)}
          >
            <option value="">🏪 Tất cả dịch vụ</option>
            <option value="Restaurant">Nhà hàng</option>
            <option value="Hotel">Khách sạn</option>
            <option value="Entertainment">Giải trí</option>
            <option value="Shopping">Mua sắm</option>
            <option value="Beauty">Làm đẹp</option>
            <option value="Kids">Trẻ em</option>
          </FilterSelect>

          <FilterSelect 
            value={priceFilter} 
            onChange={(e) => setPriceFilter(e.target.value)}
          >
            <option value="">💰 Tất cả mức giá</option>
            <option value="Budget">Tiết kiệm</option>
            <option value="Mid-range">Trung bình</option>
            <option value="Premium">Cao cấp</option>
            <option value="Luxury">Sang trọng</option>
          </FilterSelect>

          <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <input
              type="checkbox"
              checked={strictLocation}
              onChange={(e) => setStrictLocation(e.target.checked)}
            />
            🎯 Chỉ địa điểm chính xác
          </label>
        </AdvancedOptions>

        <SearchButton onClick={handleSearch} disabled={loading || !query.trim()}>
          {loading ? '🔍 Đang tìm kiếm...' : '🚀 Tìm kiếm thông minh'}
        </SearchButton>
      </SearchForm>

      {loading && (
        <LoadingSpinner>
          <div className="spinner"></div>
        </LoadingSpinner>
      )}

      {error && (
        <ErrorMessage>
          ❌ {error}
        </ErrorMessage>
      )}

      {queryAnalysis && (
        <QueryAnalysisCard>
          <AnalysisTitle>
            🧠 Phân tích truy vấn thông minh
          </AnalysisTitle>
          <AnalysisGrid>
            <AnalysisItem>
              <strong>Ý định:</strong><br/>
              {getIntentIcon(queryAnalysis.parsing_results.intent)} {queryAnalysis.parsing_results.intent}
            </AnalysisItem>
            {queryAnalysis.parsing_results.location && (
              <AnalysisItem>
                <strong>Địa điểm:</strong><br/>
                📍 {queryAnalysis.parsing_results.location}
              </AnalysisItem>
            )}
            {queryAnalysis.parsing_results.service_requirements.length > 0 && (
              <AnalysisItem>
                <strong>Yêu cầu dịch vụ:</strong><br/>
                🏪 {queryAnalysis.parsing_results.service_requirements.join(', ')}
              </AnalysisItem>
            )}
            <AnalysisItem>
              <strong>Độ tin cậy:</strong><br/>
              📊 {Math.round(queryAnalysis.parsing_results.confidence * 100)}%
            </AnalysisItem>
          </AnalysisGrid>
        </QueryAnalysisCard>
      )}

      {results && (
        <ResultsContainer>
          <div style={{ 
            background: '#e6fffa', 
            padding: '15px', 
            borderRadius: '10px',
            marginBottom: '20px',
            border: '2px solid #38b2ac'
          }}>
            <strong>📊 Kết quả tìm kiếm:</strong> {results.metadata.total_results} voucher 
            • ⏱️ {results.metadata.processing_time_ms}ms 
            • 🧠 {results.metadata.search_method}
          </div>

          {results.results.map((result, index) => (
            <ResultCard key={result.voucher_id || index}>
              <ResultHeader>
                <ResultTitle>{result.voucher_name}</ResultTitle>
                <div>
                  <ScoreBadge score={result.similarity_score}>
                    {Math.round(result.similarity_score * 100)}%
                  </ScoreBadge>
                  {result.location?.name && (
                    <LocationBadge>📍 {result.location.name}</LocationBadge>
                  )}
                  {result.ranking_factor && (
                    <RankingFactorBadge factor={result.ranking_factor}>
                      {getRankingFactorText(result.ranking_factor)}
                    </RankingFactorBadge>
                  )}
                </div>
              </ResultHeader>
              
              <ResultContent>
                {result.content?.substring(0, 200)}...
              </ResultContent>
              
              {result.service_info && (
                <div style={{ 
                  display: 'flex', 
                  gap: '10px', 
                  flexWrap: 'wrap',
                  marginTop: '10px' 
                }}>
                  {result.service_info.category && (
                    <span style={{ 
                      background: '#f0f4f8', 
                      padding: '3px 8px', 
                      borderRadius: '12px',
                      fontSize: '0.8rem' 
                    }}>
                      🏪 {result.service_info.category}
                    </span>
                  )}
                  {result.service_info.has_kids_area && (
                    <span style={{ 
                      background: '#fed7fe', 
                      padding: '3px 8px', 
                      borderRadius: '12px',
                      fontSize: '0.8rem' 
                    }}>
                      👶 Kid-friendly
                    </span>
                  )}
                  {result.price_info?.price_range && (
                    <span style={{ 
                      background: '#fef5e7', 
                      padding: '3px 8px', 
                      borderRadius: '12px',
                      fontSize: '0.8rem' 
                    }}>
                      💰 {result.price_info.price_range}
                    </span>
                  )}
                </div>
              )}
            </ResultCard>
          ))}

          {results.explanations?.geographic_ranking && (
            <QueryAnalysisCard>
              <AnalysisTitle>🗺️ Giải thích xếp hạng địa lý</AnalysisTitle>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                fontSize: '0.9rem',
                background: 'white',
                padding: '15px',
                borderRadius: '8px'
              }}>
                {results.explanations.geographic_ranking}
              </pre>
            </QueryAnalysisCard>
          )}
        </ResultsContainer>
      )}
    </AdvancedSearchContainer>
  );
};

export default AdvancedVoucherSearch;
