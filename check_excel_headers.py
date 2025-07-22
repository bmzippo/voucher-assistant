#!/usr/bin/env python3
"""
Script để kiểm tra headers của các file Excel
"""

import pandas as pd
import os

def check_excel_headers():
    """Kiểm tra headers của các file Excel"""
    
    excel_files = [
        "data/temp voucher.xlsx",
        "data/importvoucher.xlsx", 
        "data/importvoucher2.xlsx"
    ]
    
    print("🔍 Kiểm tra headers của các file Excel:")
    print("=" * 60)
    
    for file_path in excel_files:
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                print(f"\n📁 File: {file_path}")
                print(f"📊 Số dòng: {len(df)}")
                print(f"📋 Headers:")
                for i, col in enumerate(df.columns, 1):
                    print(f"   {i:2d}. {col}")
                
                # Hiển thị vài dòng đầu
                print(f"\n📄 Dữ liệu mẫu (5 dòng đầu):")
                print(df.head().to_string())
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ Lỗi đọc file {file_path}: {e}")
        else:
            print(f"❌ File không tồn tại: {file_path}")

if __name__ == "__main__":
    check_excel_headers()
