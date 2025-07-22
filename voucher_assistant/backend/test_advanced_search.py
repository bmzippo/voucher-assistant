#!/usr/bin/env python3
"""
Quick test of advanced search with the newly loaded data
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append('/Users/1-tiennv-m/1MG/Projects/LLM/voucher_assistant/backend')

from advanced_vector_store import AdvancedVectorStore

async def test_search():
    """Test advanced search with newly loaded data"""
    
    print("Testing Advanced Search with newly loaded data")
    print("=" * 50)
    
    # Initialize vector store
    vector_store = AdvancedVectorStore()
    
    # Test 1: Basic search for buffet
    print("Test 1: Searching for 'buffet'...")
    try:
        results = await vector_store.advanced_vector_search(
            query="buffet",
            top_k=5
        )
        
        print(f"Found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result.get('voucher_name', 'Unknown')}")
            print(f"     Score: {result.get('_score', 0):.2f}")
            
    except Exception as e:
        print(f"Error in basic search: {e}")
    
    # Test 2: Advanced search with filters
    print("\nTest 2: Searching for 'nhà hàng' in Hà Nội...")
    try:
        results = await vector_store.advanced_vector_search(
            query="nhà hàng",
            location_filter="Hà Nội",
            top_k=5
        )
        
        print(f"Found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result.get('voucher_name', 'Unknown')}")
            print(f"     Location: {result.get('location', 'Unknown')}")
            print(f"     Score: {result.get('_score', 0):.2f}")
            
    except Exception as e:
        print(f"Error in advanced search: {e}")
    
    # Test 3: Service search
    print("\nTest 3: Searching for service type...")
    try:
        results = await vector_store.advanced_vector_search(
            query="ăn uống",
            service_filter="Restaurant",
            top_k=5
        )
        
        print(f"Found {len(results)} results")
        for i, result in enumerate(results[:3]):
            print(f"  {i+1}. {result.get('voucher_name', 'Unknown')}")
            print(f"     Business Type: {result.get('business_type', 'Unknown')}")
            print(f"     Score: {result.get('_score', 0):.2f}")
            
    except Exception as e:
        print(f"Error in service search: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Advanced search testing completed!")

if __name__ == "__main__":
    asyncio.run(test_search())
