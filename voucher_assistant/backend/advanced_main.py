"""
Advanced Main API cho   AI Voucher Assistant
Tích hợp tất cả các giải pháp dài hạn: Multi-field embedding, Smart query parsing, Location-aware indexing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import asyncio
import time
from datetime import datetime
import os

# Import advanced modules
from advanced_vector_store import AdvancedVectorStore, EmbeddingWeights
from smart_query_parser import SmartQueryParser, QueryComponents
from location_aware_indexer import LocationAwareIndexer, GeographicContext

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="  AI Voucher Assistant - Advanced API",
    description="Advanced AI-powered voucher search với multi-field embedding, smart query parsing và location intelligence",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class AdvancedSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    location_filter: Optional[str] = None
    service_filter: Optional[str] = None
    price_filter: Optional[str] = None
    strict_location: Optional[bool] = False
    embedding_weights: Optional[Dict[str, float]] = None

class VoucherIndexRequest(BaseModel):
    voucher_data: Dict[str, Any]

class AnalyticsRequest(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    user_action: Optional[str] = None

# Global instances
advanced_vector_store = None
query_parser = None
location_indexer = None

@app.on_event("startup")
async def startup_event():
    """Initialize advanced components"""
    global advanced_vector_store, query_parser, location_indexer
    
    logger.info("🚀 Initializing   Advanced AI Voucher Assistant...")
    
    try:
        # Initialize advanced vector store
        advanced_vector_store = AdvancedVectorStore(
            es_url="http://localhost:9200",
            embedding_model= os.getenv("EMBEDDING_MODEL","keepitreal/vietnamese-sbert"),
            index_name=os.getenv("ELASTICSEARCH_INDEX","vouchers_advanced")
        )
        
        # Initialize query parser
        query_parser = SmartQueryParser()
        
        # Initialize location indexer
        location_indexer = LocationAwareIndexer()
        
        logger.info("✅ All advanced components initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise

@app.get("/")
async def root():
    return {
        "message": "  AI Voucher Assistant - Advanced API v2.0",
        "features": [
            "Multi-field Embedding Strategy",
            "Smart Query Parsing",
            "Location-Aware Indexing", 
            "Geographic Intelligence",
            "Advanced Vietnamese NLP",
            "Contextual Ranking"
        ],
        "status": "🚀 Ready for advanced AI search!"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        # Check vector store
        if advanced_vector_store and advanced_vector_store.is_ready:
            health_status["components"]["vector_store"] = "✅ Ready"
        else:
            health_status["components"]["vector_store"] = "❌ Not Ready"
        
        # Check query parser
        if query_parser:
            health_status["components"]["query_parser"] = "✅ Ready"
        else:
            health_status["components"]["query_parser"] = "❌ Not Ready"
        
        # Check location indexer
        if location_indexer:
            health_status["components"]["location_indexer"] = "✅ Ready"
        else:
            health_status["components"]["location_indexer"] = "❌ Not Ready"
        
        # Overall status
        all_ready = all("✅" in status for status in health_status["components"].values())
        health_status["overall"] = "✅ All Systems Operational" if all_ready else "⚠️ Some Issues Detected"
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status

@app.post("/api/advanced-search")
async def advanced_search(request: AdvancedSearchRequest):
    """
    Advanced search với full intelligence pipeline
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Advanced search: '{request.query}'")
        
        # Step 1: Parse query with smart parser
        parsed_components = query_parser.parse_query(request.query)
        
        # Step 2: Generate search strategy
        search_strategy = query_parser.generate_search_strategy(parsed_components)
        
        # Step 3: Update embedding weights if provided
        if request.embedding_weights:
            custom_weights = EmbeddingWeights(**request.embedding_weights)
            advanced_vector_store.weights = custom_weights
        
        # Step 4: Execute advanced search
        results = await advanced_vector_store.advanced_vector_search(
            query=request.query,
            top_k=request.top_k,
            location_filter=request.location_filter or parsed_components.location,
            service_filter=request.service_filter,
            price_filter=request.price_filter
        )
        
        # Step 5: Apply location-aware re-ranking if location detected
        if parsed_components.location:
            results = await _apply_location_aware_reranking(results, parsed_components)
        
        # Step 6: Generate explanations
        search_explanation = query_parser.explain_parsing(parsed_components)
        
        geographic_explanation = ""
        if parsed_components.location:
            geographic_explanation = location_indexer.explain_geographic_ranking(
                results, parsed_components.location
            )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "query": request.query,
            "parsed_components": {
                "intent": parsed_components.intent.value,
                "location": parsed_components.location,
                "location_type": parsed_components.location_type.value if parsed_components.location_type else None,
                "service_requirements": parsed_components.service_requirements,
                "target_audience": parsed_components.target_audience,
                "confidence": parsed_components.confidence
            },
            "search_strategy": search_strategy,
            "results": results,
            "explanations": {
                "query_parsing": search_explanation,
                "geographic_ranking": geographic_explanation
            },
            "metadata": {
                "total_results": len(results),
                "processing_time_ms": round(processing_time, 2),
                "search_method": "advanced_multi_field_with_intelligence",
                "embedding_dimensions": advanced_vector_store.embedding_dimension
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

async def _apply_location_aware_reranking(results: List[Dict[str, Any]], 
                                        parsed_components: QueryComponents) -> List[Dict[str, Any]]:
    """Apply additional location-aware re-ranking"""
    if not parsed_components.location:
        return results
    
    # Get geographic context
    geo_context = location_indexer.build_geographic_context(parsed_components.location)
    if not geo_context:
        return results
    
    # Re-score results based on geographic relevance
    for result in results:
        result_location = result.get('location', {}).get('name', '')
        
        # Apply location-based score adjustments
        if result_location == parsed_components.location:
            result['similarity_score'] *= 1.8  # Exact match boost
            result['ranking_factor'] = 'exact_location_match'
        elif result_location in [loc.name for loc in geo_context.nearby_locations]:
            # Nearby location boost
            relevance = geo_context.distance_relevance.get(result_location, 0)
            result['similarity_score'] *= (1.0 + relevance * 0.5)
            result['ranking_factor'] = 'nearby_location_match'
        elif result.get('location', {}).get('region') == geo_context.primary_location.region:
            result['similarity_score'] *= 1.3  # Same region boost
            result['ranking_factor'] = 'regional_match'
        else:
            result['ranking_factor'] = 'semantic_match'
    
    # Re-sort by adjusted scores
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return results

@app.post("/api/index-voucher-advanced")
async def index_voucher_advanced(request: VoucherIndexRequest):
    """
    Index voucher với advanced multi-field strategy
    """
    try:
        # Enhance voucher data với location intelligence
        enhanced_data = location_indexer.enhance_voucher_with_location_data(
            request.voucher_data
        )
        
        # Index với advanced vector store
        success = await advanced_vector_store.index_voucher_advanced(enhanced_data)
        
        if success:
            return {
                "status": "success",
                "message": "Voucher indexed successfully with advanced features",
                "voucher_id": enhanced_data.get('voucher_id'),
                "enhancements": {
                    "location_data": bool(enhanced_data.get('location')),
                    "nearby_locations": len(enhanced_data.get('nearby_locations', [])),
                    "cultural_context": len(enhanced_data.get('location', {}).get('cultural_context', [])),
                    "boost_factors": bool(enhanced_data.get('location_boost'))
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to index voucher")
            
    except Exception as e:
        logger.error(f"❌ Indexing error: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")

@app.post("/api/analyze-query")
async def analyze_query(query: str):
    """
    Analyze query and return detailed parsing results
    """
    try:
        parsed_components = query_parser.parse_query(query)
        search_strategy = query_parser.generate_search_strategy(parsed_components)
        
        geographic_info = None
        if parsed_components.location:
            geo_context = location_indexer.build_geographic_context(parsed_components.location)
            if geo_context:
                geographic_info = {
                    "primary_location": {
                        "name": geo_context.primary_location.name,
                        "coordinates": geo_context.primary_location.coordinates,
                        "region": geo_context.primary_location.region,
                        "cultural_context": geo_context.cultural_context
                    },
                    "nearby_locations": [
                        {
                            "name": loc.name,
                            "distance_km": location_indexer.calculate_distance(
                                geo_context.primary_location.coordinates,
                                loc.coordinates
                            )
                        }
                        for loc in geo_context.nearby_locations
                    ]
                }
        
        return {
            "query": query,
            "parsing_results": {
                "intent": parsed_components.intent.value,
                "location": parsed_components.location,
                "location_type": parsed_components.location_type.value if parsed_components.location_type else None,
                "service_requirements": parsed_components.service_requirements,
                "target_audience": parsed_components.target_audience,
                "time_requirements": parsed_components.time_requirements,
                "keywords": parsed_components.keywords,
                "confidence": parsed_components.confidence
            },
            "search_strategy": search_strategy,
            "geographic_info": geographic_info,
            "explanation": query_parser.explain_parsing(parsed_components)
        }
        
    except Exception as e:
        logger.error(f"❌ Query analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/api/location-info/{location}")
async def get_location_info(location: str):
    """
    Get detailed location information
    """
    try:
        geo_context = location_indexer.build_geographic_context(location)
        
        if not geo_context:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return {
            "location": location,
            "geographic_context": {
                "primary_location": {
                    "name": geo_context.primary_location.name,
                    "normalized_name": geo_context.primary_location.normalized_name,
                    "coordinates": geo_context.primary_location.coordinates,
                    "region": geo_context.primary_location.region,
                    "province": geo_context.primary_location.province,
                    "districts": geo_context.primary_location.districts,
                    "landmarks": geo_context.primary_location.landmarks,
                    "population_category": geo_context.primary_location.population_category
                },
                "nearby_locations": [
                    {
                        "name": loc.name,
                        "distance_km": round(location_indexer.calculate_distance(
                            geo_context.primary_location.coordinates,
                            loc.coordinates
                        ), 1),
                        "relevance": geo_context.distance_relevance.get(loc.name, 0)
                    }
                    for loc in geo_context.nearby_locations
                ],
                "cultural_context": geo_context.cultural_context,
                "economic_level": geo_context.economic_level
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Location info error: {e}")
        raise HTTPException(status_code=500, detail=f"Location info error: {str(e)}")

@app.post("/api/analytics")
async def record_analytics(request: AnalyticsRequest):
    """
    Record search analytics for learning and improvement
    """
    try:
        # Parse the original query
        parsed_components = query_parser.parse_query(request.query)
        
        # Analyze results quality
        quality_metrics = _analyze_results_quality(request.results, parsed_components)
        
        # Record analytics (in real implementation, save to database)
        analytics_data = {
            "timestamp": datetime.now().isoformat(),
            "query": request.query,
            "parsed_components": {
                "intent": parsed_components.intent.value,
                "location": parsed_components.location,
                "confidence": parsed_components.confidence
            },
            "results_count": len(request.results),
            "quality_metrics": quality_metrics,
            "user_action": request.user_action
        }
        
        logger.info(f"📊 Analytics recorded for query: '{request.query}'")
        
        return {
            "status": "success",
            "analytics_id": f"analytics_{int(time.time())}",
            "quality_score": quality_metrics.get('overall_quality', 0),
            "recommendations": _generate_improvement_recommendations(quality_metrics)
        }
        
    except Exception as e:
        logger.error(f"❌ Analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

def _analyze_results_quality(results: List[Dict[str, Any]], 
                           parsed_components: QueryComponents) -> Dict[str, Any]:
    """Analyze quality of search results"""
    if not results:
        return {"overall_quality": 0, "issues": ["no_results"]}
    
    quality_metrics = {
        "location_accuracy": 0,
        "intent_relevance": 0,
        "score_distribution": [],
        "issues": []
    }
    
    # Check location accuracy
    if parsed_components.location:
        location_matches = sum(1 for r in results if r.get('location', {}).get('name') == parsed_components.location)
        quality_metrics["location_accuracy"] = location_matches / len(results)
        
        if quality_metrics["location_accuracy"] < 0.5:
            quality_metrics["issues"].append("poor_location_accuracy")
    
    # Check score distribution
    scores = [r.get('similarity_score', 0) for r in results]
    quality_metrics["score_distribution"] = {
        "min": min(scores),
        "max": max(scores),
        "avg": sum(scores) / len(scores)
    }
    
    if quality_metrics["score_distribution"]["max"] < 0.5:
        quality_metrics["issues"].append("low_similarity_scores")
    
    # Calculate overall quality
    quality_metrics["overall_quality"] = (
        quality_metrics["location_accuracy"] * 0.6 +
        min(quality_metrics["score_distribution"]["avg"], 1.0) * 0.4
    )
    
    return quality_metrics

def _generate_improvement_recommendations(quality_metrics: Dict[str, Any]) -> List[str]:
    """Generate recommendations for improving search quality"""
    recommendations = []
    
    if "poor_location_accuracy" in quality_metrics.get("issues", []):
        recommendations.append("Increase location boosting factors")
        recommendations.append("Improve location extraction from content")
    
    if "low_similarity_scores" in quality_metrics.get("issues", []):
        recommendations.append("Retrain embedding model with domain-specific data")
        recommendations.append("Adjust embedding weights for better semantic matching")
    
    if quality_metrics.get("overall_quality", 0) < 0.7:
        recommendations.append("Consider implementing user feedback learning")
        recommendations.append("Fine-tune multi-field embedding strategy")
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
