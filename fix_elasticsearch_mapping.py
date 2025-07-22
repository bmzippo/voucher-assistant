#!/usr/bin/env python3
"""
Script to fix Elasticsearch mapping and rebuild index with correct dimensions
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "voucher_assistant" / "backend"
sys.path.insert(0, str(backend_dir))

from vector_store import vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_elasticsearch_mapping():
    """Fix ES mapping to match current model dimensions"""
    
    print("🔧 Fixing Elasticsearch Mapping Issues")
    print("=" * 60)
    
    # Check current health
    health = await vector_store.health_check()
    print(f"Current health: {health}")
    
    # Get current model dimension
    test_embedding = vector_store.create_embedding("test")
    actual_dimension = len(test_embedding)
    
    print(f"📏 Model actual dimension: {actual_dimension}")
    print(f"📏 Vector store expected dimension: {vector_store.embedding_dimension}")
    
    if actual_dimension != vector_store.embedding_dimension:
        print(f"⚠️  Dimension mismatch detected!")
        print(f"   Model produces: {actual_dimension}")
        print(f"   Index expects: {vector_store.embedding_dimension}")
        
        # Update vector store dimension
        vector_store.embedding_dimension = actual_dimension
        print(f"✅ Updated vector store dimension to {actual_dimension}")
    
    # Check if we need to recreate index
    if vector_store.es and vector_store.es.ping():
        try:
            # Check current mapping
            mapping = vector_store.es.indices.get_mapping(index=vector_store.index_name)
            current_dims = mapping[vector_store.index_name]['mappings']['properties']['content_embedding']['dims']
            
            print(f"📋 Current index mapping dimension: {current_dims}")
            
            if current_dims != actual_dimension:
                print(f"🔄 Need to recreate index with correct dimension...")
                
                # Backup current data first
                print("💾 Backing up current data...")
                search_body = {
                    "query": {"match_all": {}},
                    "size": 10000,
                    "_source": True
                }
                
                backup_data = []
                response = vector_store.es.search(index=vector_store.index_name, body=search_body)
                
                for hit in response.get('hits', {}).get('hits', []):
                    backup_data.append(hit['_source'])
                
                print(f"📦 Backed up {len(backup_data)} documents")
                
                # Delete old index
                print("🗑️  Deleting old index...")
                vector_store.es.indices.delete(index=vector_store.index_name, ignore=[400, 404])
                
                # Create new index with correct mapping
                print("🆕 Creating new index with correct mapping...")
                mapping = {
                    "mappings": {
                        "properties": {
                            "voucher_id": {"type": "keyword"},
                            "voucher_name": {
                                "type": "text", 
                                "analyzer": "vietnamese",
                                "fields": {
                                    "keyword": {"type": "keyword"}
                                }
                            },
                            "content": {
                                "type": "text", 
                                "analyzer": "vietnamese"
                            },
                            "content_embedding": {
                                "type": "dense_vector",
                                "dims": actual_dimension,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "location_embedding": {
                                "type": "dense_vector",
                                "dims": actual_dimension,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "service_embedding": {
                                "type": "dense_vector",
                                "dims": actual_dimension,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "target_embedding": {
                                "type": "dense_vector",
                                "dims": actual_dimension,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "combined_embedding": {
                                "type": "dense_vector",
                                "dims": actual_dimension,
                                "index": True,
                                "similarity": "cosine"
                            },
                            
                            # Structured data fields
                            "location": {
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "region": {"type": "keyword"},
                                    "district": {"type": "keyword"},
                                    "coordinates": {"type": "geo_point"}
                                }
                            },
                            "service_info": {
                                "properties": {
                                    "category": {"type": "keyword"},
                                    "subcategory": {"type": "keyword"},
                                    "restaurant_type": {"type": "keyword"},
                                    "tags": {"type": "keyword"},
                                    "has_kids_area": {"type": "boolean"}
                                }
                            },
                            "price_info": {
                                "properties": {
                                    "original_price": {"type": "long"},
                                    "discounted_price": {"type": "long"},
                                    "price_range": {"type": "keyword"},
                                    "currency": {"type": "keyword"}
                                }
                            },
                            "target_audience": {"type": "keyword"},
                            "keywords": {"type": "keyword"},
                            
                            # Additional fields for voucher details
                            "usage_instructions": {
                                "type": "text",
                                "analyzer": "vietnamese"
                            },
                            "terms_conditions": {
                                "type": "text", 
                                "analyzer": "vietnamese"
                            },
                            "merchant": {"type": "keyword"},
                            "validity_period": {"type": "keyword"},
                            
                            # Metadata
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"}
                        }
                    },
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "vietnamese": {
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "stop"]
                                }
                            }
                        },
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }
                
                vector_store.es.indices.create(index=vector_store.index_name, body=mapping)
                print(f"✅ Created new index with {actual_dimension} dimensions")
                
                # Restore data with corrected embeddings
                if backup_data:
                    print("🔄 Restoring data with corrected embeddings...")
                    restored_count = 0
                    
                    for doc in backup_data:
                        try:
                            # Fix embedding dimensions if needed
                            for emb_field in ['content_embedding', 'location_embedding', 'service_embedding', 'target_embedding', 'combined_embedding']:
                                if emb_field in doc and doc[emb_field]:
                                    embedding = doc[emb_field]
                                    if len(embedding) != actual_dimension:
                                        if len(embedding) < actual_dimension:
                                            # Pad with zeros
                                            embedding.extend([0.0] * (actual_dimension - len(embedding)))
                                        else:
                                            # Truncate
                                            embedding = embedding[:actual_dimension]
                                        doc[emb_field] = embedding
                            
                            # Re-index document
                            vector_store.es.index(
                                index=vector_store.index_name,
                                id=doc.get('voucher_id', f"restored_{restored_count}"),
                                body=doc
                            )
                            restored_count += 1
                            
                        except Exception as e:
                            print(f"❌ Error restoring document: {e}")
                    
                    print(f"✅ Restored {restored_count}/{len(backup_data)} documents")
                
                # Refresh index
                vector_store.es.indices.refresh(index=vector_store.index_name)
                
            else:
                print("✅ Index mapping dimension is already correct")
                
        except Exception as e:
            print(f"❌ Error checking/fixing mapping: {e}")
            return False
    
    # Final health check
    print("\n" + "=" * 60)
    print("🏥 Final Health Check")
    final_health = await vector_store.health_check()
    print(f"Vector store ready: {final_health['vector_store_ready']}")
    print(f"Elasticsearch connected: {final_health['elasticsearch_connected']}")
    print(f"Index exists: {final_health['index_exists']}")
    print(f"Document count: {final_health['document_count']}")
    print(f"Model loaded: {final_health['embedding_model_loaded']}")
    
    # Test search
    print("\n🔍 Testing search functionality...")
    try:
        test_results = await vector_store.vector_search("cafe", top_k=3)
        print(f"✅ Search test successful: {len(test_results)} results found")
        
        for i, result in enumerate(test_results, 1):
            print(f"   {i}. {result.get('voucher_name', 'N/A')} (score: {result.get('similarity_score', 0):.3f})")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    return True

if __name__ == "__main__":
    asyncio.run(fix_elasticsearch_mapping())
