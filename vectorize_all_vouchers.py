#!/usr/bin/env python3
"""
Script vectorization toàn bộ voucher data từ 3 file Excel
Xử lý và gửi data lên backend API để vectorize và lưu vào Elasticsearch
"""

import pandas as pd
import requests
import json
import sys
import time
from typing import Dict, List, Optional

# Backend API configuration  
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = f"{BACKEND_URL}/api/admin/add_voucher"

def normalize_voucher_data(file_path: str, df: pd.DataFrame) -> List[Dict]:
    """
    Chuẩn hóa dữ liệu voucher từ các file Excel khác nhau về format thống nhất
    """
    vouchers = []
    
    if "importvoucher2.xlsx" in file_path:
        # File importvoucher2.xlsx có cấu trúc khác - lấy row đầu làm header
        print(f"🔄 Xử lý file đặc biệt: {file_path}")
        
        # Row đầu tiên chứa data thật, không phải header
        if len(df) > 0:
            first_row = df.iloc[0]
            
            # Mapping columns từ importvoucher2.xlsx về format chuẩn
            voucher = {
                "name": str(first_row.iloc[0]) if pd.notna(first_row.iloc[0]) else "Voucher không tên",
                "description": str(first_row.iloc[1]) if pd.notna(first_row.iloc[1]) else "",
                "usage_instructions": str(first_row.iloc[2]) if pd.notna(first_row.iloc[2]) else "",
                "terms_of_use": str(first_row.iloc[3]) if pd.notna(first_row.iloc[3]) else "",
                "tags": str(first_row.iloc[4]) if pd.notna(first_row.iloc[4]) else "",
                "location": str(first_row.iloc[5]) if pd.notna(first_row.iloc[5]) else "",
                "price": int(float(first_row.iloc[6])) if pd.notna(first_row.iloc[6]) and str(first_row.iloc[6]).replace('.','').isdigit() else 0,
                "unit": int(first_row.iloc[7]) if pd.notna(first_row.iloc[7]) and str(first_row.iloc[7]).isdigit() else 1,
                "merchant": str(first_row.iloc[8]) if pd.notna(first_row.iloc[8]) else "",
                "metadata": {
                    "source_file": file_path,
                    "row_index": 0,
                    "original_columns": df.columns.tolist()
                }
            }
            vouchers.append(voucher)
        
        # Xử lý các row còn lại (từ row 1 trở đi)
        for idx in range(1, len(df)):
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
                    "original_columns": df.columns.tolist()
                }
            }
            vouchers.append(voucher)
            
    else:
        # File temp voucher.xlsx và importvoucher.xlsx có cấu trúc chuẩn
        print(f"🔄 Xử lý file chuẩn: {file_path}")
        
        for idx, row in df.iterrows():
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
                    "original_columns": df.columns.tolist()
                }
            }
            vouchers.append(voucher)
    
    return vouchers

def send_voucher_to_backend(voucher_data: Dict) -> bool:
    """
    Gửi data voucher lên backend API để vectorize và lưu
    """
    try:
        response = requests.post(
            API_ENDPOINT,
            json=voucher_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return True
            else:
                print(f"❌ Backend error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_backend_health() -> bool:
    """
    Kiểm tra backend có sẵn sàng không
    """
    try:
        response = requests.get(f"{BACKEND_URL}/api/vector-search/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy: {health_data}")
            return True
        else:
            print(f"❌ Backend not healthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def process_excel_file(file_path: str) -> int:
    """
    Xử lý một file Excel và gửi tất cả vouchers lên backend
    """
    try:
        print(f"\n📖 Đọc file: {file_path}")
        df = pd.read_excel(file_path)
        print(f"📊 Tìm thấy {len(df)} dòng dữ liệu")
        
        # Chuẩn hóa dữ liệu
        vouchers = normalize_voucher_data(file_path, df)
        print(f"🔄 Đã chuẩn hóa {len(vouchers)} vouchers")
        
        # Gửi từng voucher lên backend
        success_count = 0
        for i, voucher in enumerate(vouchers):
            print(f"📤 Đang gửi voucher {i+1}/{len(vouchers)}: {voucher['name'][:50]}...")
            
            if send_voucher_to_backend(voucher):
                success_count += 1
                if (i + 1) % 10 == 0:
                    print(f"✅ Đã xử lý {i+1}/{len(vouchers)} vouchers")
            else:
                print(f"❌ Lỗi gửi voucher {i+1}: {voucher['name']}")
            
            # Delay nhỏ để tránh overwhelm backend
            time.sleep(0.1)
        
        print(f"✅ Hoàn thành file {file_path}: {success_count}/{len(vouchers)} vouchers")
        return success_count
        
    except Exception as e:
        print(f"❌ Lỗi xử lý file {file_path}: {e}")
        return 0

def main():
    """
    Main function - xử lý toàn bộ 3 file Excel
    """
    print("🚀 Bắt đầu vectorization voucher data từ 3 file Excel")
    print("=" * 60)
    
    # 1. Kiểm tra backend
    if not check_backend_health():
        print("❌ Backend không sẵn sàng. Vui lòng khởi động backend trước.")
        sys.exit(1)
    
    # 2. Danh sách các file cần xử lý
    excel_files = [
        "data/temp voucher.xlsx",      # 19 vouchers
        "data/importvoucher.xlsx",     # 169 vouchers  
        "data/importvoucher2.xlsx"     # 2100 vouchers
    ]
    
    total_processed = 0
    
    # 3. Xử lý từng file
    for file_path in excel_files:
        try:
            success_count = process_excel_file(file_path)
            total_processed += success_count
        except Exception as e:
            print(f"❌ Lỗi nghiêm trọng với file {file_path}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"🎉 HOÀN THÀNH! Đã vectorize và lưu {total_processed} vouchers")
    print("📋 Tóm tắt:")
    print(f"   • temp voucher.xlsx: ~19 vouchers")
    print(f"   • importvoucher.xlsx: ~169 vouchers")  
    print(f"   • importvoucher2.xlsx: ~2100 vouchers")
    print(f"   • Tổng cộng: {total_processed} vouchers thành công")
    
    # 4. Kiểm tra kết quả cuối cùng
    print("\n🔍 Kiểm tra kết quả cuối cùng...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/vector-search/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"📊 Document count trong Elasticsearch: {health_data.get('document_count', 'N/A')}")
        else:
            print("❌ Không thể kiểm tra document count")
    except Exception as e:
        print(f"❌ Lỗi kiểm tra cuối: {e}")

if __name__ == "__main__":
    main()
