import pytest
import asyncio
from httpx import AsyncClient
from backend.main import app
from backend.vector_store import VectorStore
from backend.models import VoucherData

@pytest.fixture
async def async_client():
    """Create async client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_vector_store():
    """Create test vector store"""
    vs = VectorStore()
    vs.index_name = "test_voucher_knowledge_base"
    await vs.create_index()
    return vs

@pytest.fixture
def sample_voucher():
    """Sample voucher data for testing"""
    return VoucherData(
        name="Test Voucher - RuNam",
        description="Đây là voucher test cho cafe RuNam với ưu đãi đặc biệt.",
        usage_instructions="Xuất trình voucher tại quầy thanh toán để sử dụng ưu đãi.",
        terms_of_use="Voucher có hiệu lực đến 31/12/2024. Áp dụng tối đa 1 voucher/hóa đơn.",
        tags="test, runam, cafe",
        price=100000,
        unit=1,
        merchant="RuNam"
    )

class TestVoucherAPI:
    """Test cases for Voucher API endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """Test root endpoint"""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "OneU Voucher Assistant API" in data["message"]
        assert data["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_add_voucher_to_knowledge_base(self, async_client, sample_voucher):
        """Test adding voucher to knowledge base"""
        response = await async_client.post(
            "/api/admin/add_voucher",
            json=sample_voucher.dict()
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "voucher_id" in data
    
    @pytest.mark.asyncio
    async def test_search_vouchers(self, async_client):
        """Test voucher search functionality"""
        search_request = {
            "query": "café runam",
            "top_k": 5
        }
        response = await async_client.post("/api/search", json=search_request)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestVectorStore:
    """Test cases for Vector Store functionality"""
    
    @pytest.mark.asyncio
    async def test_create_index(self, test_vector_store):
        """Test index creation"""
        # Index should be created in fixture
        assert test_vector_store.index_name == "test_voucher_knowledge_base"
    
    @pytest.mark.asyncio
    async def test_encode_text(self, test_vector_store):
        """Test text encoding"""
        text = "Đây là văn bản tiếng Việt để test"
        embedding = test_vector_store.encode_text(text)
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_add_and_search_document(self, test_vector_store):
        """Test adding and searching documents"""
        # Add test document
        await test_vector_store.add_document(
            content="Voucher giảm giá cho quán café RuNam",
            voucher_id="test_voucher_001",
            voucher_name="Test Voucher RuNam",
            merchant="RuNam",
            section="description",
            metadata={"price": 50000}
        )
        
        # Search for similar content
        results = await test_vector_store.search_similar(
            query="café runam giảm giá",
            top_k=3
        )
        
        assert len(results) > 0
        assert results[0]["voucher_id"] == "test_voucher_001"
        assert results[0]["score"] > 0.5

class TestVietnameseLanguageProcessing:
    """Test cases specifically for Vietnamese language processing"""
    
    @pytest.mark.asyncio
    async def test_vietnamese_text_embedding(self, test_vector_store):
        """Test Vietnamese text embedding"""
        vietnamese_texts = [
            "Voucher giảm giá cho quán cà phê",
            "Ưu đãi đặc biệt cho khách hàng thân thiết",
            "Áp dụng tại tất cả các cửa hàng trong hệ thống",
            "Không áp dụng cho ngày lễ tết"
        ]
        
        for text in vietnamese_texts:
            embedding = test_vector_store.encode_text(text)
            assert len(embedding) > 0
            assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_vietnamese_search_similarity(self, test_vector_store):
        """Test search with Vietnamese queries"""
        # Add Vietnamese content
        await test_vector_store.add_document(
            content="Voucher này áp dụng cho tất cả các món ăn và đồ uống tại RuNam",
            voucher_id="vn_test_001",
            voucher_name="Voucher tiếng Việt",
            merchant="RuNam",
            section="terms",
            metadata={}
        )
        
        # Test with various Vietnamese queries
        queries = [
            "món ăn đồ uống",
            "áp dụng cho tất cả",
            "RuNam voucher"
        ]
        
        for query in queries:
            results = await test_vector_store.search_similar(query, top_k=1)
            assert len(results) > 0
            assert results[0]["score"] > 0.3

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_empty_query_search(self, async_client):
        """Test search with empty query"""
        response = await async_client.post("/api/search", json={"query": "", "top_k": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_nonexistent_voucher_summary(self, async_client):
        """Test getting summary for non-existent voucher"""
        response = await async_client.post("/api/vouchers/nonexistent_voucher/summary")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_voucher_data(self, async_client):
        """Test adding invalid voucher data"""
        invalid_data = {
            "name": "",  # Empty name
            "description": "Test",
            "usage_instructions": "Test",
            "terms_of_use": "Test",
            "merchant": "Test"
            # Missing required fields
        }
        response = await async_client.post("/api/admin/add_voucher", json=invalid_data)
        assert response.status_code == 422  # Validation error
