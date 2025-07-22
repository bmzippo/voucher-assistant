#!/usr/bin/env python3
"""
Simple direct Elasticsearch indexing script
Bypassing VectorStore and adding documents directly to Elasticsearch
"""

import pandas as pd
import sys
import os
import json
import time
from typing import Dict, List, Optional
import hashlib
from datetime import datetime
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

class SimpleElasticsearchIndexer:
    def __init__(self):
        self.es_url = "http://localhost:9200"
        self.index_name = "voucher_knowledge_base" 
        self.model_name = "dangvantuan/vietnamese-embedding"
        
        # Initialize components
        self.es = Elasticsearch([self.es_url], verify_certs=False, request_timeout=30)
        self.model = SentenceTransformer(self.model_name)
        
        print(f"✅ Connected to Elasticsearch: {self.es_url}")
        print(f"✅ Loaded embedding model: {self.model_name}")
        
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return [0.0] * 768  # Fallback
    
    def add_voucher_document(self, voucher: Dict) -> bool:
        """Add voucher document to Elasticsearch"""
        try:
            # Create voucher ID
            voucher_name = voucher.get('name', '')
            voucher_merchant = voucher.get('merchant', '')
            voucher_id = f"voucher_{hashlib.md5(f'{voucher_name}_{voucher_merchant}'.encode()).hexdigest()[:8]}"
            
            # Create combined content for embedding
            content_parts = []
            if voucher.get('name'):
                content_parts.append(f"Tên: {voucher['name']}")
            if voucher.get('description'):
                content_parts.append(f"Mô tả: {voucher['description']}")
            if voucher.get('usage_instructions'):
                content_parts.append(f"Cách sử dụng: {voucher['usage_instructions']}")
            if voucher.get('terms_of_use'):
                content_parts.append(f"Điều kiện: {voucher['terms_of_use']}")
            if voucher.get('tags'):
                content_parts.append(f"Tags: {voucher['tags']}")
            if voucher.get('location'):
                content_parts.append(f"Địa điểm: {voucher['location']}")
            
            combined_content = " | ".join(content_parts)
            
            # Create embedding
            embedding = self.create_embedding(combined_content)
            
            # Create document for Elasticsearch
            doc = {
                "voucher_id": voucher_id,
                "voucher_name": voucher['name'],
                "content": combined_content,
                "content_type": "voucher_combined",
                "embedding": embedding,
                "merchant": voucher.get('merchant', ''),
                "section": "combined",
                "metadata": {
                    "price": voucher.get('price', 0),
                    "unit": voucher.get('unit', 1),
                    "location": voucher.get('location', ''),
                    "tags": voucher.get('tags', ''),
                    "source_file": voucher.get('metadata', {}).get('source_file', ''),
                    "processed_at": datetime.now().isoformat()
                },
                "created_at": datetime.now().isoformat()
            }
            
            # Index document
            response = self.es.index(index=self.index_name, id=voucher_id, document=doc)
            
            if response.get('result') in ['created', 'updated']:
                return True
            else:
                print(f"❌ Unexpected response: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Error indexing document: {e}")
            return False
    
    def normalize_voucher_data(self, file_path: str, df: pd.DataFrame, limit: int = None) -> List[Dict]:
        """Normalize voucher data from Excel files"""
        vouchers = []
        
        if "importvoucher2.xlsx" in file_path:
            # Special handling for importvoucher2.xlsx
            print(f"🔄 Processing special file: {file_path}")
            
            max_rows = min(limit, len(df)) if limit else len(df)
            
            for idx in range(max_rows):
                row = df.iloc[idx]
                
                voucher = {
                    "name": str(row.iloc[0]) if pd.notna(row.iloc[0]) else f"Voucher {idx + 1}",
                    "description": str(row.iloc[1]) if pd.notna(row.iloc[1]) else "",
                    "usage_instructions": str(row.iloc[2]) if pd.notna(row.iloc[2]) else "",
                    "terms_of_use": str(row.iloc[3]) if pd.notna(row.iloc[3]) else "",
                    "tags": str(row.iloc[4]) if pd.notna(row.iloc[4]) else "",
                    "location": str(row.iloc[5]) if pd.notna(row.iloc[5]) else "",
                    "price": int(float(row.iloc[6])) if pd.notna(row.iloc[6]) and str(row.iloc[6]).replace('.','').isdigit() else 0,
                    "unit": int(row.iloc[7]) if pd.notna(row.iloc[7]) and str(row.iloc[7]).isdigit() else 1,
                    "merchant": str(row.iloc[8]) if pd.notna(row.iloc[8]) else "",
                    "metadata": {
                        "source_file": file_path,
                        "row_index": idx,
                        "processed_at": datetime.now().isoformat()
                    }
                }
                vouchers.append(voucher)
                
        else:
            # Standard handling for temp voucher.xlsx and importvoucher.xlsx
            print(f"🔄 Processing standard file: {file_path}")
            
            max_rows = min(limit, len(df)) if limit else len(df)
            
            for idx in range(max_rows):
                row = df.iloc[idx]
                voucher = {
                    "name": str(row.get('Name', f'Voucher {idx + 1}')) if pd.notna(row.get('Name')) else f'Voucher {idx + 1}',
                    "description": str(row.get('Desc', '')) if pd.notna(row.get('Desc')) else '',
                    "usage_instructions": str(row.get('Usage', '')) if pd.notna(row.get('Usage')) else '',
                    "terms_of_use": str(row.get('TermOfUse', '')) if pd.notna(row.get('TermOfUse')) else '',
                    "tags": str(row.get('Tags', '')) if pd.notna(row.get('Tags')) else '',
                    "location": str(row.get('Location', '')) if pd.notna(row.get('Location')) else '',
                    "price": int(float(row.get('Price', 0))) if pd.notna(row.get('Price')) and str(row.get('Price', '')).replace('.','').isdigit() else 0,
                    "unit": int(row.get('Unit', 1)) if pd.notna(row.get('Unit')) and str(row.get('Unit', '')).isdigit() else 1,
                    "merchant": str(row.get('Merrchant', '')) if pd.notna(row.get('Merrchant')) else '',  # Note: typo in original
                    "metadata": {
                        "source_file": file_path,
                        "row_index": idx,
                        "processed_at": datetime.now().isoformat()
                    }
                }
                vouchers.append(voucher)
        
        return vouchers
    
    def process_file(self, file_path: str, limit: int = None) -> int:
        """Process one Excel file"""
        try:
            print(f"\n📖 Reading file: {file_path}")
            df = pd.read_excel(file_path)
            
            if limit:
                print(f"📊 Found {len(df)} rows (will process first {limit} vouchers)")
            else:
                print(f"📊 Found {len(df)} rows")
            
            # Normalize data
            vouchers = self.normalize_voucher_data(file_path, df, limit)
            print(f"🔄 Normalized {len(vouchers)} vouchers")
            
            # Add each voucher to Elasticsearch
            success_count = 0
            for i, voucher in enumerate(vouchers):
                print(f"📤 Processing voucher {i+1}/{len(vouchers)}: {voucher['name'][:50]}...")
                
                if self.add_voucher_document(voucher):
                    success_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"✅ Processed {i+1}/{len(vouchers)} vouchers")
                else:
                    print(f"❌ Error processing voucher {i+1}: {voucher['name']}")
                
                # Small delay to avoid overwhelming Elasticsearch
                time.sleep(0.05)
            
            print(f"✅ Completed file {file_path}: {success_count}/{len(vouchers)} vouchers")
            return success_count
            
        except Exception as e:
            print(f"❌ Error processing file {file_path}: {e}")
            return 0

def main():
    """Main function"""
    print("🚀 Direct Elasticsearch vectorization script")
    print("=" * 60)
    
    # Initialize indexer
    try:
        indexer = SimpleElasticsearchIndexer()
    except Exception as e:
        print(f"❌ Failed to initialize indexer: {e}")
        sys.exit(1)
    
    # Files to process
    files = [
        ("data/temp voucher.xlsx", None),       # All vouchers (19)
        ("data/importvoucher.xlsx", None),      # All vouchers (169)  
        ("data/importvoucher2.xlsx", None)      # All vouchers (2100)
    ]
    
    total_processed = 0
    
    # Process each file
    for file_path, limit in files:
        try:
            success_count = indexer.process_file(file_path, limit)
            total_processed += success_count
        except Exception as e:
            print(f"❌ Critical error with file {file_path}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"🎉 COMPLETED! Vectorized and stored {total_processed} vouchers")
    
    # Final check
    print("\n🔍 Final check...")
    try:
        # Refresh index
        indexer.es.indices.refresh(index=indexer.index_name)
        
        # Count documents
        count_response = indexer.es.count(index=indexer.index_name)
        count = count_response.get('count', 0)
        print(f"📊 Total documents in Elasticsearch: {count}")
        
        # Sample search
        search_response = indexer.es.search(index=indexer.index_name, body={"query": {"match_all": {}}, "size": 1})
        if search_response['hits']['total']['value'] > 0:
            sample_doc = search_response['hits']['hits'][0]['_source']
            print(f"📄 Sample document: {sample_doc.get('voucher_name', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error in final check: {e}")

if __name__ == "__main__":
    main()
