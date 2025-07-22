# AI Voucher Assistant for   - Phase 1: Responsive AI

Dự án xây dựng AI Trợ Lý Voucher thông minh cho ứng dụng  , giúp người dùng dễ dàng hiểu và áp dụng các điều khoản & điều kiện phức tạp của voucher.

## 🎯 Mục tiêu

- **Tóm tắt điểm chính**: AI tự động đọc và tóm tắt các điều kiện quan trọng nhất của voucher
- **Hỏi-đáp tự nhiên**: Giao diện chat cho phép người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên về voucher
- **Xử lý tiếng Việt**: Tối ưu cho ngôn ngữ tiếng Việt và thuật ngữ đặc thù của  

## 🏗️ Kiến trúc

```
voucher_assistant/
├── backend/           # FastAPI backend với RAG implementation
├── frontend/          # React frontend cho giao diện người dùng
├── data_processing/   # Scripts xử lý dữ liệu và embedding
├── config/           # Configuration files
└── docs/             # Documentation
```

## 🚀 Công nghệ sử dụng

- **Backend**: FastAPI (Python)
- **Vector Database**: Elasticsearch với Vector Search
- **LLM**: Vertex AI Endpoint (tối ưu cho tiếng Việt)
- **Embedding**: Sentence Transformers / Vertex AI Embeddings
- **Frontend**: React với TypeScript
- **RAG**: Retrieval Augmented Generation

## 📋 Các giai đoạn phát triển

### Giai đoạn 1.1: Chuẩn bị Dữ liệu và Xây dựng Knowledge Base ✅
- [x] Thu thập và chuẩn hóa dữ liệu voucher
- [x] Xây dựng pipeline embedding
- [x] Cấu hình Elasticsearch Vector Search

### Giai đoạn 1.2: Triển khai LLM Service và RAG Logic ✅
- [x] Deploy LLM trên Vertex AI (Mock implementation ready)
- [x] Phát triển API Gateway
- [x] Implement RAG logic

### Giai đoạn 1.3: Tích hợp Giao diện người dùng ✅
- [x] Thiết kế UI component cho PDP
- [x] Tích hợp chat interface
- [x] Kết nối frontend với backend

### Giai đoạn 1.4: Kiểm thử và Tối ưu hóa ✅
- [x] Test cases toàn diện
- [x] Performance monitoring system
- [x] User feedback collection
- [x] Production deployment scripts
- [x] Real Vertex AI integration
- [x] Health monitoring and metrics
- [x] Error handling and fallbacks

## ✨ Tính năng mới trong Phase 1.4

### 🔍 Performance Monitoring
- Real-time API performance tracking
- Search query analytics
- LLM response time monitoring
- Health indicators and alerts
- Metrics export functionality

### 💬 User Feedback System
- Quick feedback (thumbs up/down)
- Detailed rating system (1-5 stars)
- Categorized feedback types
- Improvement suggestions based on feedback
- Feedback analytics and trends

### 🧪 Comprehensive Testing
- API endpoint testing
- Vietnamese language processing tests
- Edge case handling
- Error scenarios testing
- LLM service testing

### 🚀 Production Ready
- Real Vertex AI integration
- Production deployment scripts
- Security configurations
- Automated backup system
- Monitoring and alerting

## 🔧 Cài đặt và Chạy

### Quick Start (Recommended)
```bash
cd voucher_assistant
./deploy.sh
```

### Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start

# Data Processing
cd data_processing
python setup_knowledge_base.py
```

### Testing
```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Production Deployment
```bash
./deploy.sh production
```

## 📊 Monitoring & Analytics

### Performance Metrics
- Access: http://localhost:8000/api/metrics
- Health: http://localhost:8000/health
- Export: POST /api/metrics/export

### User Feedback
- Submit: POST /api/feedback
- Analytics: GET /api/feedback/summary
- Trends: GET /api/feedback/trends

### Management Commands
```bash
# Monitor services
./monitoring.sh

# Create backup
./backup.sh

# View logs
docker-compose logs -f
```

## 📞 Liên hệ

- Hotline: 1900 558 865
- Email: support@abc.vn
