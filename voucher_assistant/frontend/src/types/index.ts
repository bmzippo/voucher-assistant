export interface VoucherSummary {
  voucher_id: string;
  name: string;
  key_points: string[];
  discount_amount: string;
  validity_period?: string;
  usage_restrictions: string[];
  merchant: string;
}

export interface ChatMessage {
  message: string;
  timestamp?: string;
}

export interface ChatResponse {
  response: string;
  confidence_score: number;
  sources: string[];
  timestamp: string;
}

export interface SearchResult {
  content: string;
  score: number;
  metadata: {
    voucher_id: string;
    voucher_name: string;
    merchant: string;
    section: string;
  };
}

export interface VoucherData {
  name: string;
  description: string;
  usage_instructions: string;
  terms_of_use: string;
  tags?: string;
  location?: string;
  price: number;
  unit: number;
  merchant: string;
}
