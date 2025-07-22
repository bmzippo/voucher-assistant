import time
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring for OneU Voucher Assistant"""
    
    def __init__(self, max_records=1000):
        self.max_records = max_records
        self.metrics = {
            "api_requests": deque(maxlen=max_records),
            "search_queries": deque(maxlen=max_records),
            "llm_calls": deque(maxlen=max_records),
            "embedding_operations": deque(maxlen=max_records)
        }
        self.counters = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_api_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record API request metrics"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "duration_ms": round(duration * 1000, 2),
            "status_code": status_code
        }
        self.metrics["api_requests"].append(record)
        self.counters[f"api_{endpoint}_{method}"] += 1
        
        if status_code >= 400:
            self.counters["api_errors"] += 1
    
    def record_search_query(self, query: str, results_count: int, duration: float, voucher_id: str = None):
        """Record search query metrics"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "query_length": len(query),
            "results_count": results_count,
            "duration_ms": round(duration * 1000, 2),
            "voucher_id": voucher_id,
            "has_results": results_count > 0
        }
        self.metrics["search_queries"].append(record)
        self.counters["search_queries"] += 1
        
        if results_count == 0:
            self.counters["search_no_results"] += 1
    
    def record_llm_call(self, operation: str, input_length: int, output_length: int, duration: float, confidence: float = None):
        """Record LLM operation metrics"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,  # "summary" or "qa"
            "input_length": input_length,
            "output_length": output_length,
            "duration_ms": round(duration * 1000, 2),
            "confidence": confidence
        }
        self.metrics["llm_calls"].append(record)
        self.counters[f"llm_{operation}"] += 1
    
    def record_embedding_operation(self, text_length: int, duration: float):
        """Record embedding operation metrics"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "text_length": text_length,
            "duration_ms": round(duration * 1000, 2)
        }
        self.metrics["embedding_operations"].append(record)
        self.counters["embedding_operations"] += 1
    
    def get_summary_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        stats = {
            "period": f"Last {hours} hours",
            "generated_at": datetime.now().isoformat(),
            "uptime_hours": round((datetime.now() - self.start_time).total_seconds() / 3600, 2)
        }
        
        # API Request Stats
        recent_api_requests = [
            r for r in self.metrics["api_requests"] 
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]
        
        if recent_api_requests:
            durations = [r["duration_ms"] for r in recent_api_requests]
            status_codes = [r["status_code"] for r in recent_api_requests]
            
            stats["api_requests"] = {
                "total": len(recent_api_requests),
                "avg_duration_ms": round(sum(durations) / len(durations), 2),
                "max_duration_ms": max(durations),
                "min_duration_ms": min(durations),
                "success_rate": round(len([s for s in status_codes if s < 400]) / len(status_codes) * 100, 2),
                "endpoints": self._get_endpoint_stats(recent_api_requests)
            }
        else:
            stats["api_requests"] = {"total": 0}
        
        # Search Query Stats
        recent_searches = [
            r for r in self.metrics["search_queries"]
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]
        
        if recent_searches:
            search_durations = [r["duration_ms"] for r in recent_searches]
            results_counts = [r["results_count"] for r in recent_searches]
            
            stats["search_queries"] = {
                "total": len(recent_searches),
                "avg_duration_ms": round(sum(search_durations) / len(search_durations), 2),
                "avg_results": round(sum(results_counts) / len(results_counts), 2),
                "success_rate": round(len([s for s in recent_searches if s["has_results"]]) / len(recent_searches) * 100, 2)
            }
        else:
            stats["search_queries"] = {"total": 0}
        
        # LLM Call Stats
        recent_llm_calls = [
            r for r in self.metrics["llm_calls"]
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]
        
        if recent_llm_calls:
            llm_durations = [r["duration_ms"] for r in recent_llm_calls]
            confidences = [r["confidence"] for r in recent_llm_calls if r["confidence"] is not None]
            
            stats["llm_calls"] = {
                "total": len(recent_llm_calls),
                "avg_duration_ms": round(sum(llm_durations) / len(llm_durations), 2),
                "avg_confidence": round(sum(confidences) / len(confidences), 3) if confidences else None,
                "operations": self._get_operation_stats(recent_llm_calls)
            }
        else:
            stats["llm_calls"] = {"total": 0}
        
        # System Health Indicators
        stats["health_indicators"] = self._get_health_indicators(recent_api_requests, recent_searches, recent_llm_calls)
        
        return stats
    
    def _get_endpoint_stats(self, api_requests: List[Dict]) -> Dict[str, int]:
        """Get statistics by endpoint"""
        endpoint_counts = defaultdict(int)
        for req in api_requests:
            endpoint_counts[req["endpoint"]] += 1
        return dict(endpoint_counts)
    
    def _get_operation_stats(self, llm_calls: List[Dict]) -> Dict[str, int]:
        """Get statistics by LLM operation"""
        operation_counts = defaultdict(int)
        for call in llm_calls:
            operation_counts[call["operation"]] += 1
        return dict(operation_counts)
    
    def _get_health_indicators(self, api_requests: List, searches: List, llm_calls: List) -> Dict[str, Any]:
        """Calculate system health indicators"""
        indicators = {}
        
        # API Health
        if api_requests:
            error_rate = len([r for r in api_requests if r["status_code"] >= 400]) / len(api_requests)
            avg_response_time = sum(r["duration_ms"] for r in api_requests) / len(api_requests)
            
            indicators["api_health"] = {
                "status": "healthy" if error_rate < 0.05 and avg_response_time < 2000 else "warning" if error_rate < 0.1 else "critical",
                "error_rate": round(error_rate * 100, 2),
                "avg_response_time_ms": round(avg_response_time, 2)
            }
        
        # Search Health
        if searches:
            no_results_rate = len([s for s in searches if not s["has_results"]]) / len(searches)
            avg_search_time = sum(s["duration_ms"] for s in searches) / len(searches)
            
            indicators["search_health"] = {
                "status": "healthy" if no_results_rate < 0.2 and avg_search_time < 1000 else "warning",
                "no_results_rate": round(no_results_rate * 100, 2),
                "avg_search_time_ms": round(avg_search_time, 2)
            }
        
        # LLM Health
        if llm_calls:
            confidences = [c["confidence"] for c in llm_calls if c["confidence"] is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            avg_llm_time = sum(c["duration_ms"] for c in llm_calls) / len(llm_calls)
            
            indicators["llm_health"] = {
                "status": "healthy" if avg_confidence > 0.7 and avg_llm_time < 3000 else "warning",
                "avg_confidence": round(avg_confidence, 3),
                "avg_response_time_ms": round(avg_llm_time, 2)
            }
        
        return indicators
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to JSON file"""
        if filename is None:
            filename = f"voucher_assistant_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "uptime_hours": round((datetime.now() - self.start_time).total_seconds() / 3600, 2),
            "summary_stats": self.get_summary_stats(),
            "counters": dict(self.counters),
            "recent_metrics": {
                "api_requests": list(self.metrics["api_requests"])[-100:],  # Last 100 requests
                "search_queries": list(self.metrics["search_queries"])[-100:],
                "llm_calls": list(self.metrics["llm_calls"])[-100:],
                "embedding_operations": list(self.metrics["embedding_operations"])[-100:]
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filename

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Decorators for automatic monitoring
def monitor_api_request(func):
    """Decorator to monitor API request performance"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        endpoint = func.__name__
        status_code = 200
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            performance_monitor.record_api_request(endpoint, "POST", duration, status_code)
    
    return wrapper

def monitor_search_query(func):
    """Decorator to monitor search query performance"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        result = await func(*args, **kwargs)
        
        duration = time.time() - start_time
        results_count = len(result) if isinstance(result, list) else 0
        query = kwargs.get('query', '') or (args[0] if args else '')
        
        performance_monitor.record_search_query(query, results_count, duration)
        
        return result
    
    return wrapper

def monitor_llm_call(operation: str):
    """Decorator to monitor LLM call performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            result = await func(*args, **kwargs)
            
            duration = time.time() - start_time
            input_length = len(str(args)) + len(str(kwargs))
            output_length = len(str(result))
            confidence = result.get("confidence") if isinstance(result, dict) else None
            
            performance_monitor.record_llm_call(operation, input_length, output_length, duration, confidence)
            
            return result
        
        return wrapper
    return decorator
