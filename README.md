# OneU AI Voucher Assistant 🎯

> **Hệ thống AI Trợ Lý Voucher thông minh cho OneU Ecosystem - Giai đoạn 1: Responsive AI**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.0+-orange.svg)](https://elastic.co)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)

## 🚀 Tổng Quan

OneU AI Voucher Assistant là một hệ thống AI thông minh được thiết kế để giúp người dùng dễ dàng tìm kiếm và hiểu các voucher phức tạp trong hệ sinh thái OneU. Hệ thống sử dụng công nghệ **Hybrid Search** kết hợp giữa **Semantic Search** và **Exact Text Search** để mang lại trải nghiệm tìm kiếm tối ưu.

## ✨ Tính Năng Chính

### 🎯 Core Features
- **Tóm tắt điểm chính**: Tự động phân tích và tóm tắt các điều kiện quan trọng của voucher
- **Hỏi-đáp tự nhiên**: Chat interface cho phép đặt câu hỏi bằng tiếng Việt tự nhiên
- **Hybrid Search**: Kết hợp exact text search và semantic search cho độ chính xác cao
- **Multi-field Embedding**: Tối ưu hóa search theo location, service type, target audience

### 🌐 Language & Location Support  
- **Tiếng Việt đầy đủ**: Hỗ trợ cả có dấu và không dấu
- **Location Intelligence**: Tự động detect và filter theo địa điểm
- **Brand Name Recognition**: Tìm kiếm thương hiệu/brand names chính xác
- **Intent Detection**: Hiểu ý định người dùng (restaurant, hotel, entertainment, etc.)

### 🔧 Technical Features
- **Real-time Search**: Tìm kiếm real-time với hiệu suất cao
- **Advanced Vector Store**: Multi-field embedding strategy
- **Smart Query Parser**: Phân tích và hiểu câu query phức tạp
- **Location-aware Indexing**: Indexing thông minh theo địa lý

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │────│  FastAPI Backend │────│   Elasticsearch │
│                 │    │                 │    │                 │
│ • Advanced UI   │    │ • Hybrid Search │    │ • Vector Store  │
│ • Chat Interface│    │ • Smart Parser  │    │ • Multi-field   │
│ • Real-time     │    │ • Location AI   │    │ • Vietnamese    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │  ML Components  │
                    │                 │
                    │ • Vietnamese    │
                    │   Embeddings    │
                    │ • Sentence      │
                    │   Transformers  │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Elasticsearch 8.0+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/bmzippo/voucher-assistant.git
cd voucher-assistant
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Elasticsearch (Docker)
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.0.0

# Run data indexing
python voucher_assistant/backend/data_processing/main_indexer.py

# Start backend server
python voucher_assistant/backend/advanced_main.py
```

### 3. Frontend Setup
```bash
cd voucher_assistant/frontend
npm install
npm start
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Elasticsearch**: http://localhost:9200

## 📚 Documentation

- [🏗️ Architecture Overview](./docs/ARCHITECTURE.md)
- [🔧 API Documentation](./docs/API.md)
- [⚙️ Backend Guide](./docs/BACKEND.md)
- [🎨 Frontend Guide](./docs/FRONTEND.md)
- [📊 Data Processing](./docs/DATA_PROCESSING.md)
- [🚀 Deployment Guide](./docs/DEPLOYMENT.md)

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Elasticsearch**: Search and analytics engine
- **Sentence Transformers**: Vietnamese embedding model
- **Pydantic**: Data validation and settings management

### Frontend  
- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API calls
- **CSS Modules**: Scoped styling

### AI/ML Components
- **dangvantuan/vietnamese-embedding**: Vietnamese language model
- **Vector Search**: Semantic similarity search
- **Intent Classification**: Smart query understanding
- **Location Intelligence**: Geographic context understanding

## 📊 Performance

- **Search Latency**: < 200ms average
- **Embedding Dimensions**: 768
- **Supported Languages**: Vietnamese (with/without diacritics), English
- **Index Size**: ~100MB for 10K+ vouchers
- **Concurrent Users**: 100+ supported

## 🔄 Development Workflow

### Data Pipeline
1. **Excel Data Import** → Clean & validate voucher data
2. **Multi-field Extraction** → Location, service type, target audience
3. **Embedding Generation** → Create semantic vectors
4. **Index Creation** → Store in Elasticsearch with hybrid search

### Search Pipeline  
1. **Query Parsing** → Intent detection & component extraction
2. **Hybrid Search** → Combine exact text + semantic search
3. **Result Ranking** → Score combination & geographic relevance
4. **Response Formatting** → Structured JSON with explanations

## 🧪 Testing

```bash
# Backend tests
python -m pytest voucher_assistant/tests/

# Frontend tests  
cd voucher_assistant/frontend
npm test

# API tests
curl -X POST "http://localhost:8001/api/advanced-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "buffet tre em tai ha noi", "top_k": 5}'
```

## 📈 Roadmap

### Phase 1: Responsive AI ✅
- [x] Hybrid search implementation
- [x] Vietnamese language support
- [x] Basic UI development
- [x] Core API endpoints

### Phase 2: Proactive AI (Planned)
- [ ] Personalized recommendations
- [ ] User behavior analytics
- [ ] Advanced chatbot features
- [ ] Multi-modal search (image + text)

### Phase 3: Predictive AI (Future)
- [ ] Demand forecasting
- [ ] Dynamic pricing suggestions
- [ ] Automated voucher optimization
- [ ] Advanced analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Tech Lead**: OneU Engineering Team
- **AI/ML**: Advanced Vector Search Implementation
- **Frontend**: React & TypeScript Development  
- **Backend**: FastAPI & Elasticsearch Integration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/bmzippo/voucher-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bmzippo/voucher-assistant/discussions)
- **Email**: support@oneu.com

---

**Built with ❤️ for OneU Ecosystem**
