#!/usr/bin/env python3
"""
Load voucher data into Advanced Vector Store
"""

import pandas as pd
import asyncio
import logging
from pathlib import Path
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_vector_store import AdvancedVectorStore, EmbeddingWeights
from location_aware_indexer import LocationAwareIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_voucher_data():
    """Load voucher data from Excel into Advanced Vector Store"""
    
    # Initialize components
    logger.info("🚀 Initializing Advanced Vector Store...")
    advanced_store = AdvancedVectorStore(
        es_url="http://localhost:9200",
        embedding_model= os.getenv("EMBEDDING_MODEL","keepitreal/vietnamese-sbert"),
        index_name=os.getenv('ELASTICSEARCH_INDEX', 'voucher_knowledge')
    )
    
    location_indexer = LocationAwareIndexer()
    
    # Load data from Excel
    data_file = "/Users/1-tiennv-m/1MG/Projects/LLM/data/temp voucher.xlsx"
    logger.info(f"📊 Loading data from: {data_file}")
    
    try:
        df = pd.read_excel(data_file)
        logger.info(f"✅ Loaded {len(df)} vouchers from Excel")
        
        # Process and index each voucher
        success_count = 0
        for idx, row in df.iterrows():
            try:
                # Convert row to dictionary and clean
                voucher_data = {
                    'voucher_id': f"voucher_{idx + 1}",
                    'voucher_name': str(row.get('Name', '')).strip(),
                    'location': str(row.get('Location', 'Hà Nội')).strip(),  # Default to Hà Nội if nan
                    'description': str(row.get('Desc', '')).strip(),
                    'terms_conditions': str(row.get('TermOfUse', '')).strip(),
                    'usage': str(row.get('Usage', '')).strip(),
                    'price': str(row.get('Price', '')).strip(),
                    'tags': str(row.get('Tags', '')).strip(),
                    'merchant': str(row.get('Merrchant', '')).strip()  # Note: typo in original Excel
                }
                
                # Skip empty vouchers
                if not voucher_data['voucher_name'] or voucher_data['voucher_name'] == 'nan':
                    continue
                
                # Handle NaN location
                if voucher_data['location'] == 'nan' or not voucher_data['location']:
                    # Try to extract location from description or default to Hà Nội
                    voucher_data['location'] = extract_location_from_text(voucher_data['description']) or 'Hà Nội'
                
                # Enhance with location data
                enhanced_data = location_indexer.enhance_voucher_with_location_data(voucher_data)
                
                # Add business type detection
                enhanced_data['business_type'] = detect_business_type(voucher_data['voucher_name'], voucher_data['description'])
                
                # Add service info for kids-friendly detection
                enhanced_data['service_info'] = analyze_service_info(voucher_data['description'], voucher_data['terms_conditions'])
                
                # Index the voucher
                success = await advanced_store.index_voucher_advanced(enhanced_data)
                
                if success:
                    success_count += 1
                    if success_count % 10 == 0:
                        logger.info(f"✅ Indexed {success_count} vouchers...")
                else:
                    logger.warning(f"❌ Failed to index voucher: {voucher_data['voucher_name']}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing voucher {idx}: {e}")
                continue
        
        logger.info(f"🎉 Successfully indexed {success_count} vouchers!")
        
        # Verify data was loaded
        await verify_data_loaded(advanced_store)
        
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        raise

def detect_business_type(name: str, description: str) -> str:
    """Detect business type from voucher name and description"""
    text = f"{name} {description}".lower()
    
    if any(keyword in text for keyword in ['buffet', 'nhà hàng', 'quán ăn', 'restaurant', 'food', 'cafe', 'bistro']):
        return 'Restaurant'
    elif any(keyword in text for keyword in ['khách sạn', 'hotel', 'resort', 'homestay']):
        return 'Hotel'
    elif any(keyword in text for keyword in ['spa', 'massage', 'làm đẹp', 'beauty']):
        return 'Beauty'
    elif any(keyword in text for keyword in ['mua sắm', 'shopping', 'mall', 'siêu thị']):
        return 'Shopping'
    elif any(keyword in text for keyword in ['giải trí', 'vui chơi', 'entertainment', 'game']):
        return 'Entertainment'
    else:
        return 'Other'

def extract_location_from_text(text: str) -> str:
    """Try to extract location from text description"""
    if not text or text == 'nan':
        return None
    
    # Common Vietnamese cities and areas
    locations = ['hà nội', 'hồ chí minh', 'đà nẵng', 'hải phòng', 'cần thơ', 'nha trang', 'huế', 'đà lạt', 'vũng tàu']
    text_lower = text.lower()
    
    for location in locations:
        if location in text_lower:
            return location.title()
    
    return None

def analyze_service_info(description: str, terms: str) -> dict:
    """Analyze service information"""
    text = f"{description} {terms}".lower()
    
    service_info = {
        'has_kids_area': any(keyword in text for keyword in ['trẻ em', 'children', 'kids', 'khu vui chơi', 'playground']),
        'is_family_friendly': any(keyword in text for keyword in ['gia đình', 'family', 'trẻ nhỏ']),
        'has_parking': any(keyword in text for keyword in ['đỗ xe', 'parking', 'bãi xe']),
        'has_wifi': any(keyword in text for keyword in ['wifi', 'internet', 'mạng']),
        'outdoor_seating': any(keyword in text for keyword in ['ngoài trời', 'outdoor', 'sân vườn']),
        'air_conditioned': any(keyword in text for keyword in ['máy lạnh', 'điều hòa', 'air conditioning'])
    }
    
    return service_info

async def verify_data_loaded(advanced_store):
    """Verify that data was successfully loaded"""
    try:
        # Check document count
        es_client = advanced_store.es
        response = es_client.count(index=advanced_store.index_name)
        doc_count = response['count']
        
        logger.info(f"📊 Total documents in index: {doc_count}")
        
        if doc_count > 0:
            # Get sample document
            sample_response = es_client.search(
                index=advanced_store.index_name,
                body={"size": 1}
            )
            
            if sample_response['hits']['hits']:
                sample_doc = sample_response['hits']['hits'][0]['_source']
                logger.info(f"📄 Sample document keys: {list(sample_doc.keys())}")
                logger.info(f"📄 Sample voucher: {sample_doc.get('voucher_name', 'N/A')}")
            
            logger.info("✅ Data verification successful!")
        else:
            logger.warning("⚠️ No documents found in index!")
            
    except Exception as e:
        logger.error(f"❌ Error verifying data: {e}")

if __name__ == "__main__":
    asyncio.run(load_voucher_data())
