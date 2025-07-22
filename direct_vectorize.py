#!/usr/bin/env python3
"""
Script vectorization trực tiếp vào Elasticsearch
Bỏ qua API backend, thêm trực tiếp vào Elasticsearch
"""

import pandas as pd
import sys
import os
import json
import time
from typing import Dict, List, Optional
import hashlib
from datetime import datetime

# Add backend path to import modules
sys.path.append('/Users/1-tiennv-m/1MG/Projects/LLM/voucher_assistant/backend')

try:
    from vector_store import VectorStore
    print("✅ Successfully imported VectorStore")
except ImportError as e:
    print(f"❌ Failed to import VectorStore: {e}")
    sys.exit(1)

class DirectVectorizer:
    def __init__(self):
        self.vector_store = VectorStore()
        
    async def initialize(self):
        """Initialize vector store"""
        await self.vector_store.create_index()
        print("✅ Vector store initialized")
        
    def normalize_voucher_data(self, file_path: str, df: pd.DataFrame, limit: int = None) -> List[Dict]:
        """
        Chuẩn hóa dữ liệu voucher từ các file Excel khác nhau về format thống nhất
        """
        vouchers = []
        
        if "importvoucher2.xlsx" in file_path:
            # File importvoucher2.xlsx có cấu trúc khác
            print(f"🔄 Xử lý file đặc biệt: {file_path}")
            
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
            # File temp voucher.xlsx và importvoucher.xlsx có cấu trúc chuẩn
            print(f"🔄 Xử lý file chuẩn: {file_path}")
            
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
    
    async def add_voucher_to_vector_store(self, voucher: Dict) -> bool:
        """
        Thêm voucher vào vector store
        """
        try:
            # Tạo voucher ID duy nhất
            voucher_name = voucher['name']
            voucher_merchant = voucher['merchant']
            voucher_id = f"voucher_{hashlib.md5(f'{voucher_name}_{voucher_merchant}'.encode()).hexdigest()[:8]}"
            
            # Thêm các phần khác nhau của voucher
            # 1. Description
            if voucher.get('description'):
                await self.vector_store.add_document(
                    content=voucher['description'],
                    voucher_id=voucher_id,
                    voucher_name=voucher['name'],
                    merchant=voucher['merchant'],
                    section="description",
                    metadata={"price": voucher['price'], "unit": voucher['unit'], **voucher.get('metadata', {})}
                )
            
            # 2. Usage Instructions
            if voucher.get('usage_instructions'):
                await self.vector_store.add_document(
                    content=voucher['usage_instructions'],
                    voucher_id=voucher_id,
                    voucher_name=voucher['name'],
                    merchant=voucher['merchant'],
                    section="usage",
                    metadata={"price": voucher['price'], "unit": voucher['unit'], **voucher.get('metadata', {})}
                )
            
            # 3. Terms of Use
            if voucher.get('terms_of_use'):
                await self.vector_store.add_document(
                    content=voucher['terms_of_use'],
                    voucher_id=voucher_id,
                    voucher_name=voucher['name'],
                    merchant=voucher['merchant'],
                    section="terms",
                    metadata={"price": voucher['price'], "unit": voucher['unit'], **voucher.get('metadata', {})}
                )
            
            # 4. Combined content
            combined_content = f"{voucher['name']} | {voucher['description']} | {voucher['usage_instructions']} | {voucher['terms_of_use']}"
            if voucher.get('tags'):
                combined_content += f" | Tags: {voucher['tags']}"
            if voucher.get('location'):
                combined_content += f" | Location: {voucher['location']}"
                
            await self.vector_store.add_document(
                content=combined_content,
                voucher_id=voucher_id,
                voucher_name=voucher['name'],
                merchant=voucher['merchant'],
                section="combined",
                metadata={"price": voucher['price'], "unit": voucher['unit'], **voucher.get('metadata', {})}
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding voucher to vector store: {e}")
            return False
    
    async def process_file(self, file_path: str, limit: int = None) -> int:
        """
        Xử lý một file Excel
        """
        try:
            print(f"\n📖 Đọc file: {file_path}")
            df = pd.read_excel(file_path)
            
            if limit:
                print(f"📊 Tìm thấy {len(df)} dòng dữ liệu (sẽ xử lý {limit} vouchers đầu)")
            else:
                print(f"📊 Tìm thấy {len(df)} dòng dữ liệu")
            
            # Chuẩn hóa dữ liệu
            vouchers = self.normalize_voucher_data(file_path, df, limit)
            print(f"🔄 Đã chuẩn hóa {len(vouchers)} vouchers")
            
            # Thêm từng voucher vào vector store
            success_count = 0
            for i, voucher in enumerate(vouchers):
                print(f"📤 Đang xử lý voucher {i+1}/{len(vouchers)}: {voucher['name'][:50]}...")
                
                if await self.add_voucher_to_vector_store(voucher):
                    success_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"✅ Đã xử lý {i+1}/{len(vouchers)} vouchers")
                else:
                    print(f"❌ Lỗi xử lý voucher {i+1}: {voucher['name']}")
                
                # Delay nhỏ để tránh overwhelm Elasticsearch
                await asyncio.sleep(0.1)
            
            print(f"✅ Hoàn thành file {file_path}: {success_count}/{len(vouchers)} vouchers")
            return success_count
            
        except Exception as e:
            print(f"❌ Lỗi xử lý file {file_path}: {e}")
            return 0

async def main():
    """
    Main function
    """
    import asyncio
    
    print("🚀 Bắt đầu vectorization trực tiếp vào Elasticsearch")
    print("=" * 60)
    
    # Initialize vectorizer
    vectorizer = DirectVectorizer()
    await vectorizer.initialize()
    
    # Danh sách các file cần xử lý
    files = [
        ("data/temp voucher.xlsx", 19),      # Tất cả vouchers
        ("data/importvoucher.xlsx", 169),    # Tất cả vouchers  
        ("data/importvoucher2.xlsx", 100)    # Chỉ 100 vouchers đầu để test
    ]
    
    total_processed = 0
    
    # Xử lý từng file
    for file_path, limit in files:
        try:
            success_count = await vectorizer.process_file(file_path, limit)
            total_processed += success_count
        except Exception as e:
            print(f"❌ Lỗi nghiêm trọng với file {file_path}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"🎉 HOÀN THÀNH! Đã vectorize và lưu {total_processed} vouchers")
    
    # Kiểm tra kết quả cuối cùng
    print("\n🔍 Kiểm tra kết quả cuối cùng...")
    try:
        # Check index stats
        stats = await vectorizer.vector_store.get_index_stats()
        print(f"📊 Index stats: {stats}")
    except Exception as e:
        print(f"❌ Lỗi kiểm tra cuối: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
