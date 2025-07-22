from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime
from typing import List

from models import (
    VoucherData, VoucherSummary, ChatMessage, ChatResponse, 
    SearchRequest, SearchResult, VectorSearchRequest, 
    VectorSearchResponse, VectorSearchResult, HybridSearchResponse
)
from feedback_models import UserFeedback, FeedbackSummary
from vector_store import VectorStore
from llm_service import VertexAIService
from config import settings
from performance_monitor import performance_monitor, monitor_api_request, monitor_search_query
from feedback_collector import feedback_collector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
vector_store = None
llm_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global vector_store, llm_service
    
    # Startup
    logger.info("Starting Voucher Assistant API...")
    
    # Initialize services
    vector_store = VectorStore()
    llm_service = VertexAIService()
    
    # Create Elasticsearch index
    await vector_store.create_index()
    
    logger.info("Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Voucher Assistant API...")

# Create FastAPI app
app = FastAPI(
    title="  Voucher Assistant API",
    description="AI Assistant for   Voucher Information",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record API request metrics
    performance_monitor.record_api_request(
        endpoint=request.url.path,
        method=request.method,
        duration=duration,
        status_code=response.status_code
    )
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(round(duration * 1000, 2))
    return response

# Dependency to get vector store
def get_vector_store() -> VectorStore:
    return vector_store

# Dependency to get LLM service
def get_llm_service() -> VertexAIService:
    return llm_service

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "  Voucher Assistant API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check with performance metrics"""
    # Get performance stats
    stats = performance_monitor.get_summary_stats(hours=1)
    
    # Determine overall health status
    health_indicators = stats.get("health_indicators", {})
    overall_status = "healthy"
    
    for indicator in health_indicators.values():
        if indicator.get("status") == "critical":
            overall_status = "critical"
            break
        elif indicator.get("status") == "warning" and overall_status == "healthy":
            overall_status = "warning"
    
    return {
        "status": overall_status,
        "services": {
            "elasticsearch": "connected",
            "llm_service": "available"
        },
        "performance_stats": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics endpoint"""
    return performance_monitor.get_summary_stats(hours=24)

@app.post("/api/metrics/export")
async def export_metrics():
    """Export metrics to file"""
    filename = performance_monitor.export_metrics()
    return {"message": "Metrics exported successfully", "filename": filename}

@app.post("/api/feedback")
async def submit_feedback(feedback: UserFeedback):
    """Submit user feedback"""
    try:
        feedback_id = feedback_collector.submit_feedback(feedback)
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/feedback/summary")
async def get_feedback_summary(days: int = 30) -> FeedbackSummary:
    """Get feedback summary"""
    return feedback_collector.get_feedback_summary(days)

@app.get("/api/feedback/voucher/{voucher_id}")
async def get_voucher_feedback(voucher_id: str):
    """Get feedback for specific voucher"""
    feedback = feedback_collector.get_voucher_feedback(voucher_id)
    return {"voucher_id": voucher_id, "feedback": feedback}

@app.get("/api/feedback/trends")
async def get_feedback_trends(days: int = 90):
    """Get feedback trends"""
    return feedback_collector.get_feedback_trends(days)

@app.post("/api/feedback/export")
async def export_feedback_report(days: int = 30):
    """Export feedback report"""
    filename = feedback_collector.export_feedback_report(days)
    return {"message": "Feedback report exported", "filename": filename}

@app.post("/api/vouchers/{voucher_id}/summary")
async def get_voucher_summary(
    voucher_id: str,
    vs: VectorStore = Depends(get_vector_store),
    llm: VertexAIService = Depends(get_llm_service)
) -> VoucherSummary:
    """Get AI-generated summary for a voucher"""
    try:
        # Get voucher context from vector store
        context = await vs.get_voucher_context(voucher_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Voucher not found")
        
        # Get voucher name from context or search
        search_results = await vs.search_similar("", voucher_id=voucher_id, top_k=1)
        voucher_name = search_results[0]["voucher_name"] if search_results else f"Voucher {voucher_id}"
        merchant = search_results[0]["merchant"] if search_results else "Unknown"
        
        # Generate summary using LLM
        summary_result = await llm.generate_summary(context, voucher_name)
        
        return VoucherSummary(
            voucher_id=voucher_id,
            name=voucher_name,
            key_points=summary_result["key_points"],
            discount_amount="Theo điều kiện voucher",
            usage_restrictions=["Xem điều khoản chi tiết"],
            merchant=merchant
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating voucher summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/vouchers/{voucher_id}/chat")
async def chat_with_voucher(
    voucher_id: str,
    message: ChatMessage,
    vs: VectorStore = Depends(get_vector_store),
    llm: VertexAIService = Depends(get_llm_service)
) -> ChatResponse:
    """Chat about a specific voucher"""
    try:
        # Search for relevant information
        search_results = await vs.search_similar(
            message.message, 
            voucher_id=voucher_id,
            top_k=settings.TOP_K_RESULTS
        )
        
        if not search_results:
            return ChatResponse(
                response="Xin lỗi, tôi không tìm thấy thông tin về voucher này. Vui lòng liên hệ hotline 1900 558 865 để được hỗ trợ.",
                confidence_score=0.0,
                sources=[],
                timestamp=datetime.now()
            )
        
        # Build context from search results
        context_parts = []
        sources = []
        
        for result in search_results:
            context_parts.append(result["content"])
            sources.append(f"{result['section']}_{result['voucher_id']}")
        
        context = "\n\n".join(context_parts)
        voucher_name = search_results[0]["voucher_name"]
        
        # Get answer from LLM
        answer_result = await llm.answer_question(
            message.message, 
            context, 
            voucher_name
        )
        
        return ChatResponse(
            response=answer_result["answer"],
            confidence_score=answer_result["confidence"],
            sources=sources,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/search")
async def search_vouchers(
    request: SearchRequest,
    vs: VectorStore = Depends(get_vector_store)
) -> List[SearchResult]:
    """Search across all vouchers"""
    try:
        results = await vs.search_similar(
            request.query,
            voucher_id=request.voucher_id,
            top_k=request.top_k
        )
        
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                content=result["content"],
                score=result["score"],
                metadata={
                    "voucher_id": result["voucher_id"],
                    "voucher_name": result["voucher_name"],
                    "merchant": result["merchant"],
                    "section": result["section"]
                }
            ))
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# NEW VECTOR SEARCH APIs
# =============================================================================

@app.post("/api/vector-search", response_model=VectorSearchResponse)
async def vector_search_vouchers(
    request: VectorSearchRequest,
    vs: VectorStore = Depends(get_vector_store)
):
    """
    Vector Search API - Tìm kiếm voucher bằng vector similarity
    1. Vector hoá search text 
    2. Sử dụng vector đó để tìm kiếm trong Elasticsearch
    3. Trả về kết quả với similarity scores
    """
    start_time = time.time()
    
    try:
        # Monitor search query
        monitor_search_query(request.query)
        
        # Thực hiện vector search
        results = await vs.vector_search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        # Convert kết quả sang VectorSearchResult models
        search_results = []
        for result in results:
            search_results.append(VectorSearchResult(
                voucher_id=result["voucher_id"],
                voucher_name=result["voucher_name"],
                content=result["content"],
                similarity_score=result["similarity_score"],
                raw_score=result["raw_score"],
                metadata=result["metadata"],
                created_at=result.get("created_at"),
                search_query=result["search_query"]
            ))
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Log search performance
        logger.info(f"Vector search completed in {search_time:.2f}ms for query: '{request.query}'")
        
        return VectorSearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time, 2),
            embedding_dimension=vs.embedding_dimension
        )
        
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")

@app.post("/api/hybrid-search", response_model=HybridSearchResponse)
async def hybrid_search_vouchers(
    request: VectorSearchRequest,
    vs: VectorStore = Depends(get_vector_store)
):
    """
    Hybrid Search API - Kết hợp vector search và text search
    Để có kết quả tốt nhất cho việc tìm kiếm voucher
    """
    start_time = time.time()
    
    try:
        # Monitor search query
        monitor_search_query(request.query)
        
        # Thực hiện hybrid search
        results = await vs.hybrid_search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        # Convert vector results
        vector_results = []
        for result in results["vector_results"]:
            vector_results.append(VectorSearchResult(
                voucher_id=result["voucher_id"],
                voucher_name=result["voucher_name"],
                content=result["content"],
                similarity_score=result["similarity_score"],
                raw_score=result["raw_score"],
                metadata=result["metadata"],
                created_at=result.get("created_at"),
                search_query=result["search_query"]
            ))
        
        search_time = (time.time() - start_time) * 1000
        
        return HybridSearchResponse(
            query=request.query,
            vector_results=vector_results,
            text_results=results["text_results"],
            total_vector_results=results["total_vector_results"],
            total_text_results=results["total_text_results"],
            search_time_ms=round(search_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")

@app.get("/api/vector-search/health")
async def vector_search_health_check(vs: VectorStore = Depends(get_vector_store)):
    """Kiểm tra trạng thái của Vector Search system"""
    try:
        health_status = await vs.health_check()
        
        return {
            "status": "healthy" if health_status["vector_store_ready"] else "unhealthy",
            "details": health_status,
            "embedding_model": vs.embedding_model_name,
            "embedding_dimension": vs.embedding_dimension,
            "elasticsearch_index": vs.index_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vector search health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# =============================================================================
# END NEW VECTOR SEARCH APIs
# =============================================================================

@app.post("/api/admin/add_voucher")
async def add_voucher_to_knowledge_base(
    voucher: VoucherData,
    vs: VectorStore = Depends(get_vector_store)
):
    """Add a new voucher to the knowledge base (admin endpoint)"""
    try:
        voucher_id = f"voucher_{hash(voucher.name)}_{voucher.merchant}"
        
        # Add different sections of the voucher
        await vs.add_document(
            content=voucher.description,
            voucher_id=voucher_id,
            voucher_name=voucher.name,
            merchant=voucher.merchant,
            section="description",
            metadata={"price": voucher.price, "unit": voucher.unit}
        )
        
        await vs.add_document(
            content=voucher.usage_instructions,
            voucher_id=voucher_id,
            voucher_name=voucher.name,
            merchant=voucher.merchant,
            section="usage",
            metadata={"price": voucher.price, "unit": voucher.unit}
        )
        
        await vs.add_document(
            content=voucher.terms_of_use,
            voucher_id=voucher_id,
            voucher_name=voucher.name,
            merchant=voucher.merchant,
            section="terms",
            metadata={"price": voucher.price, "unit": voucher.unit}
        )
        
        return {
            "message": "Voucher added successfully",
            "voucher_id": voucher_id
        }
        
    except Exception as e:
        logger.error(f"Error adding voucher: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
