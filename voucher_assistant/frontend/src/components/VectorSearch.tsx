import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSearch, FiLoader, FiZap, FiFilter, FiCpu } from 'react-icons/fi';
import { voucherApi } from '../services/api';

// Types for Vector Search
interface VectorSearchResult {
  voucher_id: string;
  voucher_name: string;
  content: string;
  similarity_score: number;
  raw_score: number;
  metadata: Record<string, any>;
  created_at?: string;
  search_query: string;
}

interface HybridVectorSearchResult extends VectorSearchResult {
  text_score?: number;
}

interface VectorSearchResponse {
  query: string;
  results: VectorSearchResult[];
  total_results: number;
  search_time_ms: number;
  embedding_dimension: number;

  // Hybrid search fields (optional, only present in hybrid mode)
  total_vector_results?: number;
  total_text_results?: number;
  vector_results?: VectorSearchResult[];
  text_results?: HybridVectorSearchResult[];
}

// Styled Components
const SearchContainer = styled.div`
  background: white;
  border-radius: 16px;
  border: 1px solid #e0e0e0;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const SearchHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
`;

const SearchTitle = styled.h2`
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
`;

const SearchIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
`;

const SearchInputContainer = styled.div`
  position: relative;
  margin-bottom: 16px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 16px 52px 16px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  background: #fafafa;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #999;
  }
`;

const SearchButton = styled.button`
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-50%) scale(1.05);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: translateY(-50%);
  }
`;

const SearchOptions = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
`;

const OptionGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const OptionLabel = styled.label`
  font-size: 14px;
  color: #666;
  font-weight: 500;
`;

const OptionInput = styled.input`
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  width: 80px;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const SearchModeToggle = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const ModeButton = styled.button<{ active: boolean }>`
  padding: 8px 16px;
  border: 2px solid ${props => props.active ? '#667eea' : '#e0e0e0'};
  background: ${props => props.active ? '#667eea' : 'white'};
  color: ${props => props.active ? 'white' : '#666'};
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    background: ${props => props.active ? '#667eea' : '#f8f9ff'};
  }
`;

const ResultsContainer = styled.div`
  margin-top: 24px;
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
`;

const ResultsInfo = styled.div`
  color: #666;
  font-size: 14px;
`;

const ResultCard = styled.div`
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  }
`;

const ResultHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const VoucherName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  flex: 1;
`;

const ScoreContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
`;

const SimilarityScore = styled.div<{ score: number }>`
  background: ${props => {
    if (props.score >= 0.8) return 'linear-gradient(135deg, #4CAF50, #45a049)';
    if (props.score >= 0.6) return 'linear-gradient(135deg, #FF9800, #f57c00)';
    return 'linear-gradient(135deg, #757575, #616161)';
  }};
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
`;

const RawScore = styled.div`
  font-size: 10px;
  color: #999;
`;

const VoucherContent = styled.div`
  color: #555;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
  max-height: 100px;
  overflow: hidden;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 20px;
    background: linear-gradient(transparent, #fafafa);
  }
`;

const MetadataContainer = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 12px;
`;

const MetadataTag = styled.span`
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
`;

const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
  gap: 12px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
`;

// Main Component
const VectorSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'vector' | 'hybrid'>('vector');
  const [topK, setTopK] = useState(5);
  const [minScore, setMinScore] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<VectorSearchResponse | null>(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const searchParams = {
        query: query.trim(),
        top_k: topK,
        min_score: minScore
      };

      let response;
      if (searchMode === 'vector') {
        response = await voucherApi.post('/api/vector-search', searchParams);
      } else {
        response = await voucherApi.post('/api/hybrid-search', searchParams);
      }

      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Có lỗi xảy ra khi tìm kiếm');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <SearchContainer>
      <SearchHeader>
        <SearchIcon>
          <FiCpu />
        </SearchIcon>
        <SearchTitle>Vector Search - Tìm kiếm thông minh</SearchTitle>
      </SearchHeader>

      <SearchModeToggle>
        <ModeButton 
          active={searchMode === 'vector'} 
          onClick={() => setSearchMode('vector')}
        >
          <FiZap />
          Vector Search
        </ModeButton>
        <ModeButton 
          active={searchMode === 'hybrid'} 
          onClick={() => setSearchMode('hybrid')}
        >
          <FiFilter />
          Hybrid Search
        </ModeButton>
      </SearchModeToggle>

      <SearchInputContainer>
        <SearchInput
          type="text"
          placeholder="Nhập từ khóa tìm kiếm voucher (VD: 'voucher giảm giá RuNam', 'spa massage'...)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <SearchButton 
          onClick={handleSearch} 
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? <FiLoader className="animate-spin" /> : <FiSearch />}
        </SearchButton>
      </SearchInputContainer>

      <SearchOptions>
        <OptionGroup>
          <OptionLabel>Số kết quả:</OptionLabel>
          <OptionInput
            type="number"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value) || 5)}
          />
        </OptionGroup>
        <OptionGroup>
          <OptionLabel>Độ tương đồng tối thiểu:</OptionLabel>
          <OptionInput
            type="number"
            min="0.1"
            max="1.0"
            step="0.1"
            value={minScore}
            onChange={(e) => setMinScore(parseFloat(e.target.value) || 0.7)}
          />
        </OptionGroup>
      </SearchOptions>

      {error && (
        <div style={{ 
          color: '#f44336', 
          background: '#ffebee', 
          padding: '12px', 
          borderRadius: '8px',
          marginBottom: '16px'
        }}>
          {error}
        </div>
      )}

      {isLoading && (
        <LoadingContainer>
          <FiLoader className="animate-spin" />
          Đang tìm kiếm...
        </LoadingContainer>
      )}

      {results && !isLoading && (
        <ResultsContainer>
          <ResultsHeader>
            <ResultsInfo>
              {searchMode === 'vector' ? (
                <>
                  Tìm thấy <strong>{results.total_results}</strong> kết quả trong{' '}
                  <strong>{results.search_time_ms}ms</strong> 
                  (Embedding dimension: {results.embedding_dimension})
                </>
              ) : (
                <>
                  Tìm thấy <strong>{results.total_vector_results}</strong> kết quả vector + <strong>{results.total_text_results}</strong> kết quả text trong{' '}
                  <strong>{results.search_time_ms}ms</strong>
                </>
              )}
            </ResultsInfo>
          </ResultsHeader>

          {searchMode === 'vector' ? (
            // Vector Search Results
            results.results && results.results.length === 0 ? (
              <EmptyState>
                Không tìm thấy voucher nào phù hợp với từ khóa "{query}"
              </EmptyState>
            ) : (
              results.results && results.results.map((result, index) => (
                <ResultCard key={`${result.voucher_id}-${index}`}>
                  <ResultHeader>
                    <VoucherName>{result.voucher_name}</VoucherName>
                    <ScoreContainer>
                      <SimilarityScore score={result.similarity_score}>
                        {(result.similarity_score * 100).toFixed(1)}% phù hợp
                      </SimilarityScore>
                      <RawScore>Raw: {result.raw_score.toFixed(3)}</RawScore>
                    </ScoreContainer>
                  </ResultHeader>

                  <VoucherContent>
                    {result.content}
                  </VoucherContent>

                  <MetadataContainer>
                    <MetadataTag>ID: {result.voucher_id}</MetadataTag>
                    {result.metadata.source && (
                      <MetadataTag>Nguồn: {result.metadata.source}</MetadataTag>
                    )}
                    {result.created_at && (
                      <MetadataTag>
                        Ngày tạo: {new Date(result.created_at).toLocaleDateString('vi-VN')}
                      </MetadataTag>
                    )}
                  </MetadataContainer>
                </ResultCard>
              ))
            )
          ) : (
            // Hybrid Search Results
            <>
              {/* Vector Results Section */}
              {results.vector_results && results.vector_results.length > 0 && (
                <>
                  <div style={{ 
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                    color: 'white', 
                    padding: '12px 16px', 
                    borderRadius: '8px', 
                    marginBottom: '16px',
                    fontWeight: 'bold'
                  }}>
                    🔍 Kết quả Vector Search (Ngữ nghĩa) - {results.total_vector_results} voucher
                  </div>
                  {results.vector_results.map((result, index) => (
                    <ResultCard key={`vector-${result.voucher_id}-${index}`}>
                      <ResultHeader>
                        <VoucherName>{result.voucher_name}</VoucherName>
                        <ScoreContainer>
                          <SimilarityScore score={result.similarity_score}>
                            {(result.similarity_score * 100).toFixed(1)}% phù hợp
                          </SimilarityScore>
                          <RawScore>Raw: {result.raw_score.toFixed(3)}</RawScore>
                        </ScoreContainer>
                      </ResultHeader>

                      <VoucherContent>
                        {result.content}
                      </VoucherContent>

                      <MetadataContainer>
                        <MetadataTag>ID: {result.voucher_id}</MetadataTag>
                        {result.metadata.location && (
                          <MetadataTag>📍 {result.metadata.location}</MetadataTag>
                        )}
                        {result.created_at && (
                          <MetadataTag>
                            Ngày tạo: {new Date(result.created_at).toLocaleDateString('vi-VN')}
                          </MetadataTag>
                        )}
                      </MetadataContainer>
                    </ResultCard>
                  ))}
                </>
              )}

              {/* Text Results Section */}
              {results.text_results && results.text_results.length > 0 && (
                <>
                  <div style={{ 
                    background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)', 
                    color: 'white', 
                    padding: '12px 16px', 
                    borderRadius: '8px', 
                    marginBottom: '16px',
                    fontWeight: 'bold'
                  }}>
                    📝 Kết quả Text Search (Từ khóa) - {results.total_text_results} voucher
                  </div>
                  {results.text_results.map((result, index) => (
                    <ResultCard key={`text-${result.voucher_id}-${index}`}>
                      <ResultHeader>
                        <VoucherName>{result.voucher_name}</VoucherName>
                        <ScoreContainer>
                          <SimilarityScore score={(result.text_score ?? 0) / 20}>
                            Text Score: {(result.text_score ?? 0).toFixed(2)}
                          </SimilarityScore>
                        </ScoreContainer>
                      </ResultHeader>

                      <VoucherContent>
                        {result.content}
                      </VoucherContent>

                      <MetadataContainer>
                        <MetadataTag>ID: {result.voucher_id}</MetadataTag>
                        {result.metadata.location && (
                          <MetadataTag>📍 {result.metadata.location}</MetadataTag>
                        )}
                      </MetadataContainer>
                    </ResultCard>
                  ))}
                </>
              )}

              {(!results.vector_results || results.vector_results.length === 0) && 
               (!results.text_results || results.text_results.length === 0) && (
                <EmptyState>
                  Không tìm thấy voucher nào phù hợp với từ khóa "{query}"
                </EmptyState>
              )}
            </>
          )}
        </ResultsContainer>
      )}
    </SearchContainer>
  );
};

export default VectorSearch;
