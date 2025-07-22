import axios from 'axios';
import { VoucherSummary, ChatMessage, ChatResponse, SearchResult } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const voucherApi = {
  // Get voucher summary
  getVoucherSummary: async (voucherId: string): Promise<VoucherSummary> => {
    const response = await api.post(`/api/vouchers/${voucherId}/summary`);
    return response.data;
  },

  // Chat with voucher
  chatWithVoucher: async (voucherId: string, message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post(`/api/vouchers/${voucherId}/chat`, message);
    return response.data;
  },

  // Search vouchers
  searchVouchers: async (query: string, voucherId?: string, topK: number = 5): Promise<SearchResult[]> => {
    const response = await api.post('/api/search', {
      query,
      voucher_id: voucherId,
      top_k: topK
    });
    return response.data;
  },

  // Vector search
  vectorSearch: async (query: string, topK: number = 5, minScore: number = 0.7): Promise<any> => {
    const response = await api.post('/api/vector-search', {
      query,
      top_k: topK,
      min_score: minScore
    });
    return response.data;
  },

  // Hybrid search
  hybridSearch: async (query: string, topK: number = 5, minScore: number = 0.7): Promise<any> => {
    const response = await api.post('/api/hybrid-search', {
      query,
      top_k: topK,
      min_score: minScore
    });
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health');
    return response.data;
  },

  // Raw axios instance for direct calls
  post: api.post.bind(api),
  get: api.get.bind(api),
  put: api.put.bind(api),
  delete: api.delete.bind(api)
};

export default api;
