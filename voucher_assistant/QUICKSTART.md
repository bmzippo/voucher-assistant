# OneU AI Voucher Assistant

## Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and setup
cd voucher_assistant
chmod +x setup.sh
./setup.sh
```

### Option 2: Development Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend  
```bash
cd frontend
npm install
npm start
```

#### Data Processing
```bash
cd data_processing
python setup_knowledge_base.py
```

## Testing the Application

1. **Open frontend**: http://localhost:3000
2. **Select a voucher** from the dropdown
3. **View AI summary** in the left panel
4. **Chat with the AI** in the right panel

### Sample Questions to Try:
- "Voucher này có thời hạn sử dụng đến khi nào?"
- "Tôi có thể sử dụng bao nhiều voucher cùng lúc?"
- "Điều kiện áp dụng là gì?"
- "Làm sao để sử dụng voucher này?"

## Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **Elasticsearch**: http://localhost:9200

## Troubleshooting

### Common Issues:
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Elasticsearch fails**: Increase Docker memory to 4GB+
3. **Backend errors**: Check .env configuration

### Logs:
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend  
docker-compose logs -f elasticsearch
```

### Restart Services:
```bash
docker-compose restart
```

### Stop Services:
```bash
docker-compose down
```
