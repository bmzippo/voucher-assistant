#!/usr/bin/env python3
"""
Script test vectorization với số lượng giới hạn
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

def normalize_voucher_data(file_path: str, df: pd.DataFrame, limit: int = 5) -> List[Dict]:
    """
    Chuẩn hóa dữ liệu voucher từ các file Excel khác nhau về format thống nhất (test với limit)
    """
    vouchers = []
    
    if "importvoucher2.xlsx" in file_path:
        # File importvoucher2.xlsx có cấu trúc khác - lấy row đầu làm header
        print(f"🔄 Xử lý file đặc biệt: {file_path} (giới hạn {limit} vouchers)")
        
        # Lấy tối đa limit vouchers 
        max_rows = min(limit, len(df))
        
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
            }
            vouchers.append(voucher)
            
    else:
        # File temp voucher.xlsx và importvoucher.xlsx có cấu trúc chuẩn
        print(f"🔄 Xử lý file chuẩn: {file_path} (giới hạn {limit} vouchers)")
        
        # Lấy tối đa limit vouchers
        max_rows = min(limit, len(df))
        
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

def main():
    """
    Test main function - chỉ xử lý 5 vouchers từ mỗi file
    """
    print("🧪 TEST VECTORIZATION - chỉ 5 vouchers từ mỗi file")
    print("=" * 60)
    
    # 1. Kiểm tra backend
    if not check_backend_health():
        print("❌ Backend không sẵn sàng. Vui lòng khởi động backend trước.")
        sys.exit(1)
    
    # 2. Danh sách các file cần xử lý
    test_files = [
        "data/temp voucher.xlsx",      # Test 5 vouchers
        "data/importvoucher.xlsx",     # Test 5 vouchers  
        "data/importvoucher2.xlsx"     # Test 5 vouchers
    ]
    
    total_processed = 0
    
    # 3. Xử lý từng file với limit
    for file_path in test_files:
        try:
            print(f"\n📖 Đọc file: {file_path}")
            df = pd.read_excel(file_path)
            print(f"📊 Tìm thấy {len(df)} dòng dữ liệu (sẽ test 5 vouchers đầu)")
            
            # Chuẩn hóa dữ liệu với limit = 5
            vouchers = normalize_voucher_data(file_path, df, limit=5)
            print(f"🔄 Đã chuẩn hóa {len(vouchers)} vouchers")
            
            # Gửi từng voucher lên backend
            success_count = 0
            for i, voucher in enumerate(vouchers):
                print(f"📤 Đang gửi voucher {i+1}/{len(vouchers)}: {voucher['name'][:50]}...")
                
                if send_voucher_to_backend(voucher):
                    success_count += 1
                    print(f"✅ Thành công!")
                else:
                    print(f"❌ Lỗi gửi voucher {i+1}: {voucher['name']}")
                
                # Delay nhỏ để tránh overwhelm backend
                time.sleep(0.5)
            
            total_processed += success_count
            print(f"✅ Hoàn thành file {file_path}: {success_count}/{len(vouchers)} vouchers")
            
        except Exception as e:
            print(f"❌ Lỗi xử lý file {file_path}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"🎉 TEST HOÀN THÀNH! Đã vectorize và lưu {total_processed} vouchers")
    
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
