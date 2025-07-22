#!/usr/bin/env python3
"""
OneU AI Voucher Assistant - Knowledge Base Setup
Thiết lập knowledge base từ dữ liệu voucher Excel
"""

import sys
import os

# Kiểm tra và cài đặt dependencies
def check_and_install_dependencies():
    """Kiểm tra và cài đặt các thư viện cần thiết"""
    required_packages = [
        'pandas',
        'numpy', 
        'elasticsearch>=8.0.0,<9.0.0',  # Fix version compatibility
        'sentence-transformers',
        'openpyxl',
        'python-dotenv',
        'requests'
    ]
    
    missing_packages = []
    
    # Kiểm tra từng package
    for package in required_packages:
        package_name = package.split('>=')[0].split('==')[0].replace('-', '_')
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Thiếu các thư viện: {', '.join(missing_packages)}")
        print("🔧 Đang cài đặt dependencies...")
        
        import subprocess
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing_packages
            ])
            print("✅ Cài đặt thành công!")
        except subprocess.CalledProcessError:
            print("❌ Lỗi cài đặt. Vui lòng chạy:")
            print(f"pip install {' '.join(missing_packages)}")
            sys.exit(1)

# Kiểm tra dependencies trước khi import
check_and_install_dependencies()

try:
    import pandas as pd
    import numpy as np
    from elasticsearch import Elasticsearch
    from sentence_transformers import SentenceTransformer
    import json
    import logging
    from dotenv import load_dotenv
    import time
    import requests
    import warnings
    
    # Suppress Elasticsearch warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("🔧 Vui lòng chạy: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class VoucherKnowledgeBaseSetup:
    def __init__(self):
        self.es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost:9200')
        self.es_index = os.getenv('ELASTICSEARCH_INDEX', 'voucher_knowledge_base')
        self.model_name = os.getenv('EMBEDDING_MODEL', 'dangvantuan/vietnamese-embedding')
        self.embedding_dimension = int(os.getenv('EMBEDDING_DIMENSION', '768'))  # Default to 768 for Vietnamese model
        
        # Initialize components
        self.es = None
        self.model = None
        self.actual_embedding_dimension = None
        
    def wait_for_elasticsearch(self, max_retries=30):
        """Đợi Elasticsearch khởi động"""
        logger.info("🔍 Đang kiểm tra Elasticsearch...")
        
        for i in range(max_retries):
            try:
                response = requests.get(f"http://{self.es_host}/_cluster/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Elasticsearch đã sẵn sàng!")
                    return True
            except requests.RequestException:
                pass
            
            logger.info(f"⏳ Đang đợi Elasticsearch... ({i+1}/{max_retries})")
            time.sleep(2)
        
        logger.error("❌ Không thể kết nối tới Elasticsearch")
        return False
    
    def setup_elasticsearch(self):
        """Thiết lập kết nối Elasticsearch với version compatibility"""
        if not self.wait_for_elasticsearch():
            logger.error("❌ Elasticsearch không khả dụng")
            return False
            
        try:
            # Tạo Elasticsearch client với cấu hình phù hợp
            self.es = Elasticsearch(
                [f"http://{self.es_host}"],
                verify_certs=False,
                request_timeout=30,
                retry_on_timeout=True,
                max_retries=3
            )
            
            # Test connection với error handling
            try:
                info = self.es.info()
                version = info.get('version', {}).get('number', 'unknown')
                logger.info(f"✅ Kết nối Elasticsearch thành công: v{version}")
                return True
            except Exception as version_error:
                logger.warning(f"⚠️ Version check failed: {version_error}")
                # Try basic ping instead
                if self.es.ping():
                    logger.info("✅ Kết nối Elasticsearch thành công (basic ping)")
                    return True
                else:
                    raise Exception("Ping failed")
            
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối Elasticsearch: {e}")
            logger.info("🔧 Thử sử dụng phiên bản Elasticsearch client tương thích...")
            
            # Try with legacy client configuration
            try:
                self.es = Elasticsearch(
                    [{'host': 'localhost', 'port': 9200}],
                    verify_certs=False,
                    timeout=30
                )
                
                if self.es.ping():
                    logger.info("✅ Kết nối Elasticsearch thành công (legacy mode)")
                    return True
                    
            except Exception as legacy_error:
                logger.error(f"❌ Legacy connection failed: {legacy_error}")
                
            return False
    
    def setup_embedding_model(self):
        """Thiết lập model embedding"""
        try:
            logger.info(f"🤖 Đang tải model embedding: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Test model để lấy actual dimension
            test_embedding = self.model.encode("test")
            self.actual_embedding_dimension = len(test_embedding)
            logger.info(f"✅ Model embedding đã sẵn sàng! Dimension: {self.actual_embedding_dimension}")
            
            # Update embedding dimension nếu khác với config
            if self.actual_embedding_dimension != self.embedding_dimension:
                logger.info(f"🔄 Cập nhật embedding dimension từ {self.embedding_dimension} thành {self.actual_embedding_dimension}")
                self.embedding_dimension = self.actual_embedding_dimension
            
            return True
        except Exception as e:
            logger.error(f"❌ Lỗi tải model: {e}")
            return False
    
    def create_index_mapping(self):
        """Tạo mapping cho Elasticsearch index với version compatibility"""
        mapping = {
            "mappings": {
                "properties": {
                    "voucher_id": {"type": "keyword"},
                    "voucher_name": {
                        "type": "text", 
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "content": {
                        "type": "text", 
                        "analyzer": "standard"
                    },
                    "content_type": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": self.embedding_dimension,  # Use actual dimension from model
                        "index": True,
                        "similarity": "cosine"
                    },
                    "metadata": {"type": "object"},
                    "created_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        try:
            # Xóa index cũ nếu tồn tại
            if self.es.indices.exists(index=self.es_index):
                self.es.indices.delete(index=self.es_index)
                logger.info(f"🗑️ Đã xóa index cũ: {self.es_index}")
            
            # Tạo index mới
            response = self.es.indices.create(index=self.es_index, body=mapping)
            logger.info(f"✅ Đã tạo index: {self.es_index} với dimension: {self.embedding_dimension}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo index: {e}")
            
            # Try with simpler mapping if advanced features fail
            try:
                simple_mapping = {
                    "mappings": {
                        "properties": {
                            "voucher_id": {"type": "keyword"},
                            "voucher_name": {"type": "text"},
                            "content": {"type": "text"},
                            "content_type": {"type": "keyword"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": self.embedding_dimension  # Use actual dimension
                            },
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
                
                response = self.es.indices.create(index=self.es_index, body=simple_mapping)
                logger.info(f"✅ Đã tạo index với simple mapping: {self.es_index} (dims: {self.embedding_dimension})")
                return True
                
            except Exception as simple_error:
                logger.error(f"❌ Lỗi tạo simple index: {simple_error}")
                return False
    
    def load_voucher_data(self):
        """Tải dữ liệu voucher từ Excel file"""
        # Tìm file Excel trong các đường dẫn có thể
        possible_paths = [
            "../data/temp voucher.xlsx",
            "./data/temp voucher.xlsx", 
            "../temp voucher.xlsx",
            "./temp voucher.xlsx",
            "temp voucher.xlsx"
        ]
        
        excel_file = None
        for path in possible_paths:
            if os.path.exists(path):
                excel_file = path
                break
        
        if not excel_file:
            logger.error(f"❌ Không tìm thấy file Excel trong các đường dẫn: {possible_paths}")
            logger.info("💡 Vui lòng đặt file 'temp voucher.xlsx' trong thư mục data/")
            return None
        
        try:
            df = pd.read_excel(excel_file)
            logger.info(f"✅ Đã tải {len(df)} vouchers từ {excel_file}")
            
            # In thông tin cột để debug
            logger.info(f"📋 Các cột trong Excel: {list(df.columns)}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Lỗi đọc Excel: {e}")
            return None
    
    def process_and_index_vouchers(self, df):
        """Xử lý và index vouchers vào Elasticsearch"""
        logger.info("🔄 Bắt đầu xử lý và index vouchers...")
        
        total_docs = 0
        
        for idx, row in df.iterrows():
            try:
                voucher_id = f"voucher_{idx}"
                
                # Lấy tên voucher từ các cột có thể
                voucher_name = None
                for col_name in ['Tên voucher', 'Voucher Name', 'Name', 'Title']:
                    if col_name in df.columns and pd.notna(row.get(col_name)):
                        voucher_name = str(row[col_name])
                        break
                
                if not voucher_name:
                    voucher_name = f'Voucher {idx + 1}'
                
                # Tạo nội dung từ các cột
                content_parts = []
                for col in df.columns:
                    if pd.notna(row[col]) and str(row[col]).strip():
                        content_parts.append(f"{col}: {str(row[col]).strip()}")
                
                content = " | ".join(content_parts)
                
                # Đảm bảo content không rỗng
                if not content.strip():
                    logger.warning(f"⚠️ Voucher {idx} có nội dung rỗng, bỏ qua")
                    continue
                
                # Tạo embedding
                try:
                    embedding = self.model.encode(content).tolist()
                except Exception as embed_error:
                    logger.error(f"❌ Lỗi tạo embedding cho voucher {idx}: {embed_error}")
                    continue
                
                # Tạo document
                doc = {
                    "voucher_id": voucher_id,
                    "voucher_name": voucher_name,
                    "content": content,
                    "content_type": "voucher_details",
                    "embedding": embedding,
                    "metadata": {
                        "source": "temp_voucher.xlsx",
                        "row_index": idx,
                        "total_columns": len(df.columns)
                    },
                    "created_at": pd.Timestamp.now().isoformat()
                }
                
                # Index document
                self.es.index(index=self.es_index, id=voucher_id, document=doc)
                total_docs += 1
                
                if (idx + 1) % 5 == 0 or idx + 1 == len(df):
                    logger.info(f"📝 Đã xử lý {idx + 1}/{len(df)} vouchers")
                    
            except Exception as e:
                logger.error(f"❌ Lỗi xử lý voucher {idx}: {e}")
                continue
        
        logger.info(f"✅ Hoàn thành! Đã index {total_docs} documents")
        return total_docs
    
    def verify_setup(self):
        """Kiểm tra setup"""
        try:
            # Refresh index
            self.es.indices.refresh(index=self.es_index)
            
            # Đếm documents
            count_response = self.es.count(index=self.es_index)
            count = count_response['count']
            logger.info(f"📊 Tổng số documents trong index: {count}")
            
            if count == 0:
                logger.warning("⚠️ Không có documents nào trong index")
                return False
            
            # Test search
            test_query = {
                "query": {
                    "match_all": {}
                },
                "size": 1
            }
            
            result = self.es.search(index=self.es_index, body=test_query)
            if result['hits']['total']['value'] > 0:
                logger.info("✅ Test search thành công!")
                
                # In thông tin sample document
                sample_doc = result['hits']['hits'][0]['_source']
                logger.info(f"📄 Sample document: {sample_doc['voucher_name']}")
                return True
            else:
                logger.warning("⚠️ Không tìm thấy kết quả test search")
                return False
                
        except Exception as e:
            logger.error(f"❌ Lỗi verification: {e}")
            return False
    
    def run_setup(self):
        """Chạy toàn bộ setup process"""
        logger.info("🚀 Bắt đầu setup Knowledge Base cho OneU AI Voucher Assistant")
        
        # 1. Setup Elasticsearch
        if not self.setup_elasticsearch():
            return False
        
        # 2. Setup embedding model
        if not self.setup_embedding_model():
            return False
        
        # 3. Tạo index mapping
        if not self.create_index_mapping():
            return False
        
        # 4. Load voucher data
        df = self.load_voucher_data()
        if df is None:
            return False
        
        # 5. Process và index vouchers
        docs_count = self.process_and_index_vouchers(df)
        if docs_count == 0:
            return False
        
        # 6. Verify setup
        if not self.verify_setup():
            return False
        
        logger.info("🎉 Setup Knowledge Base hoàn thành thành công!")
        return True

def main():
    """Main function"""
    setup = VoucherKnowledgeBaseSetup()
    
    if setup.run_setup():
        print("\n🎉 OneU AI Voucher Assistant Knowledge Base đã sẵn sàng!")
        print(f"📊 Index: {setup.es_index}")
        print(f"🔍 Elasticsearch: http://{setup.es_host}")
        print("\n🚀 Bây giờ bạn có thể chạy backend API!")
        print("\n📝 Để test knowledge base:")
        print("   curl http://localhost:8000/api/search?q=voucher")
    else:
        print("\n❌ Setup thất bại. Vui lòng kiểm tra logs và thử lại.")
        sys.exit(1)

if __name__ == "__main__":
    main()