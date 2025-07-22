#!/usr/bin/env python3
"""
Vector hóa dữ liệu voucher từ file Excel mới
Processing importvoucher.xlsx và importvoucher2.xlsx
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
import asyncio
import logging

# Add backend directory to path
sys.path.append('/Users/1-tiennv-m/1MG/Projects/LLM/voucher_assistant/backend')

from vector_store import VectorStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoucherDataProcessor:
    """Xử lý và vector hóa dữ liệu voucher từ Excel files"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.processed_count = 0
        self.error_count = 0
        
    def clean_text(self, text):
        """Clean và chuẩn hóa text"""
        if pd.isna(text):
            return ""
        return str(text).strip()
    
    def read_excel_file(self, file_path):
        """Đọc file Excel và trả về DataFrame"""
        try:
            logger.info(f"📖 Đọc file: {file_path}")
            
            # Try different sheet names and indexes
            try:
                df = pd.read_excel(file_path, sheet_name=0)
            except Exception as e:
                logger.warning(f"Không đọc được sheet đầu tiên: {e}")
                # Try reading all sheets
                excel_file = pd.ExcelFile(file_path)
                logger.info(f"Available sheets: {excel_file.sheet_names}")
                df = pd.read_excel(file_path, sheet_name=excel_file.sheet_names[0])
            
            logger.info(f"✅ Đã đọc {len(df)} dòng từ file")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Lỗi đọc file {file_path}: {e}")
            return None
    
    def extract_voucher_info(self, row, row_index, source_file):
        """Extract thông tin voucher từ mỗi row"""
        try:
            # Try to map common column names
            voucher_data = {}
            
            # Common mappings
            column_mappings = {
                'name': ['Name', 'name', 'Tên', 'Voucher Name', 'VoucherName', 'title', 'Title'],
                'description': ['Desc', 'Description', 'Mô tả', 'desc', 'description'],
                'usage': ['Usage', 'usage', 'Sử dụng', 'Cách sử dụng'],
                'terms': ['TermOfUse', 'Terms', 'Điều khoản', 'terms', 'term_of_use'],
                'price': ['Price', 'price', 'Giá', 'Giá trị'],
                'unit': ['Unit', 'unit', 'Đơn vị'],
                'merchant': ['Merchant', 'merchant', 'Đối tác', 'Merrchant']
            }
            
            # Extract data based on available columns
            for key, possible_cols in column_mappings.items():
                value = ""
                for col in possible_cols:
                    if col in row.index and pd.notna(row[col]):
                        value = str(row[col]).strip()
                        break
                voucher_data[key] = value
            
            # If no specific mapping found, use all columns
            if not any(voucher_data.values()):
                all_text = []
                for col, val in row.items():
                    if pd.notna(val):
                        all_text.append(f"{col}: {val}")
                voucher_data['content'] = " | ".join(all_text)
            else:
                # Combine all fields into content
                content_parts = []
                for key, value in voucher_data.items():
                    if value and value.strip():
                        content_parts.append(f"{key.capitalize()}: {value}")
                voucher_data['content'] = " | ".join(content_parts)
            
            # Generate voucher ID
            name = voucher_data.get('name', f'voucher_{row_index}')
            voucher_data['voucher_id'] = f"voucher_{hash(name)}_{row_index}"
            voucher_data['voucher_name'] = name or f"Voucher {row_index}"
            voucher_data['source'] = source_file
            voucher_data['row_index'] = row_index
            
            return voucher_data
            
        except Exception as e:
            logger.error(f"❌ Lỗi extract voucher từ row {row_index}: {e}")
            return None
    
    async def process_excel_file(self, file_path):
        """Xử lý một file Excel"""
        try:
            # Read Excel file
            df = self.read_excel_file(file_path)
            if df is None:
                return False
            
            source_file = os.path.basename(file_path)
            logger.info(f"🔄 Bắt đầu xử lý {len(df)} vouchers từ {source_file}")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract voucher info
                    voucher_data = self.extract_voucher_info(row, index, source_file)
                    if not voucher_data:
                        continue
                    
                    # Vector hóa và lưu vào Elasticsearch
                    await self.store_voucher_vector(voucher_data)
                    self.processed_count += 1
                    
                    if self.processed_count % 5 == 0:
                        logger.info(f"✅ Đã xử lý {self.processed_count} vouchers...")
                        
                except Exception as e:
                    logger.error(f"❌ Lỗi xử lý row {index}: {e}")
                    self.error_count += 1
            
            logger.info(f"✅ Hoàn thành xử lý file {source_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý file {file_path}: {e}")
            return False
    
    async def store_voucher_vector(self, voucher_data):
        """Vector hóa và lưu voucher vào Elasticsearch"""
        try:
            content = voucher_data.get('content', '')
            if not content:
                logger.warning(f"⚠️ Voucher {voucher_data['voucher_id']} không có content")
                return
            
            # Tạo embedding vector
            embedding = self.vector_store.create_embedding(content)
            
            # Prepare document for Elasticsearch
            doc = {
                'voucher_id': voucher_data['voucher_id'],
                'voucher_name': voucher_data['voucher_name'],
                'content': content,
                'embedding': embedding,
                'metadata': {
                    'source': voucher_data['source'],
                    'row_index': voucher_data['row_index'],
                    'merchant': voucher_data.get('merchant', ''),
                    'price': voucher_data.get('price', ''),
                    'total_columns': len(voucher_data)
                },
                'created_at': datetime.now().isoformat()
            }
            
            # Store in Elasticsearch
            if self.vector_store.es:
                try:
                    result = self.vector_store.es.index(
                        index=self.vector_store.index_name,
                        id=voucher_data['voucher_id'],
                        body=doc
                    )
                    logger.debug(f"💾 Stored voucher {voucher_data['voucher_id']}: {result['result']}")
                except Exception as e:
                    logger.error(f"❌ Lỗi lưu Elasticsearch: {e}")
            else:
                logger.warning("⚠️ Elasticsearch không available")
                
        except Exception as e:
            logger.error(f"❌ Lỗi store voucher vector: {e}")
    
    async def process_all_files(self):
        """Xử lý tất cả file Excel"""
        data_dir = "/Users/1-tiennv-m/1MG/Projects/LLM/data"
        excel_files = [
            "importvoucher.xlsx",
            "importvoucher2.xlsx"
        ]
        
        logger.info("🚀 Bắt đầu vector hóa dữ liệu voucher")
        logger.info("=" * 50)
        
        # Ensure vector store is ready
        if not self.vector_store.is_ready:
            logger.error("❌ Vector Store chưa sẵn sàng")
            return
        
        # Process each file
        for excel_file in excel_files:
            file_path = os.path.join(data_dir, excel_file)
            
            if os.path.exists(file_path):
                logger.info(f"\n📁 Xử lý file: {excel_file}")
                await self.process_excel_file(file_path)
            else:
                logger.warning(f"⚠️ File không tồn tại: {file_path}")
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 KẾT QUẢ VECTOR HÓA")
        logger.info("=" * 50)
        logger.info(f"✅ Tổng số vouchers đã xử lý: {self.processed_count}")
        logger.info(f"❌ Số lỗi: {self.error_count}")
        
        # Check final status
        if self.vector_store.es:
            try:
                count_response = self.vector_store.es.count(index=self.vector_store.index_name)
                total_docs = count_response.get('count', 0)
                logger.info(f"📈 Tổng documents trong Elasticsearch: {total_docs}")
            except Exception as e:
                logger.error(f"❌ Lỗi kiểm tra số lượng docs: {e}")
        
        logger.info("🎉 Hoàn thành vector hóa dữ liệu!")

async def main():
    """Main function"""
    processor = VoucherDataProcessor()
    await processor.process_all_files()

if __name__ == "__main__":
    asyncio.run(main())
