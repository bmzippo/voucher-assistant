#!/usr/bin/env python3
"""
Simple script to vectorize voucher data from Excel files
Sử dụng API endpoint để thêm vouchers vào vector database
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime

def process_excel_file(file_path, api_url="http://localhost:8000"):
    """Process Excel file and send to API"""
    print(f"\n📁 Processing file: {file_path}")
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        print(f"✅ Read {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Determine column mapping based on file structure
        if 'Name' in df.columns:
            # Standard format (importvoucher.xlsx)
            column_map = {
                'name': 'Name',
                'description': 'Desc', 
                'usage': 'Usage',
                'terms': 'TermOfUse',
                'price': 'Price',
                'unit': 'Unit',
                'merchant': 'Merrchant'
            }
        else:
            # Non-standard format (importvoucher2.xlsx) - use first 4 columns as main fields
            columns = list(df.columns)
            column_map = {
                'name': columns[0] if len(columns) > 0 else None,
                'description': columns[1] if len(columns) > 1 else None,
                'usage': columns[2] if len(columns) > 2 else None,
                'terms': columns[3] if len(columns) > 3 else None,
                'price': columns[6] if len(columns) > 6 else None,
                'unit': columns[7] if len(columns) > 7 else None,
                'merchant': columns[8] if len(columns) > 8 else None
            }
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extract voucher data
                name = str(row[column_map['name']]) if column_map['name'] and pd.notna(row[column_map['name']]) else f"Voucher {index}"
                description = str(row[column_map['description']]) if column_map['description'] and pd.notna(row[column_map['description']]) else ""
                usage = str(row[column_map['usage']]) if column_map['usage'] and pd.notna(row[column_map['usage']]) else ""
                terms = str(row[column_map['terms']]) if column_map['terms'] and pd.notna(row[column_map['terms']]) else ""
                price = str(row[column_map['price']]) if column_map['price'] and pd.notna(row[column_map['price']]) else "0"
                unit = str(row[column_map['unit']]) if column_map['unit'] and pd.notna(row[column_map['unit']]) else "1"
                merchant = str(row[column_map['merchant']]) if column_map['merchant'] and pd.notna(row[column_map['merchant']]) else "Unknown"
                
                # Create voucher data object
                voucher_data = {
                    "name": name,
                    "description": description,
                    "usage_instructions": usage,
                    "terms_of_use": terms,
                    "price": price,
                    "unit": unit,
                    "merchant": merchant
                }
                
                # Send to API
                response = requests.post(
                    f"{api_url}/api/admin/add_voucher",
                    json=voucher_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"✅ Processed {success_count} vouchers...")
                else:
                    print(f"❌ Error adding voucher {index}: {response.status_code} - {response.text}")
                    error_count += 1
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error processing row {index}: {e}")
                error_count += 1
        
        print(f"\n📊 Results for {file_path}:")
        print(f"✅ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        
        return success_count, error_count
        
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return 0, 1

def main():
    """Main function"""
    print("🚀   Voucher Data Vectorization")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running")
        else:
            print("❌ Backend API not accessible")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend API: {e}")
        print("Please make sure the backend is running on http://localhost:8000")
        return
    
    # Process files
    files = [
        "/Users/1-tiennv-m/1MG/Projects/LLM/data/importvoucher.xlsx",
        "/Users/1-tiennv-m/1MG/Projects/LLM/data/importvoucher2.xlsx"
    ]
    
    total_success = 0
    total_errors = 0
    
    for file_path in files:
        success, errors = process_excel_file(file_path)
        total_success += success
        total_errors += errors
    
    print("\n" + "=" * 50)
    print("🎉 FINAL RESULTS")
    print("=" * 50)
    print(f"✅ Total vouchers processed: {total_success}")
    print(f"❌ Total errors: {total_errors}")
    
    # Check final database status
    try:
        response = requests.get("http://localhost:8000/api/vector-search/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"📈 Total documents in database: {health_data['details']['document_count']}")
        
    except Exception as e:
        print(f"❌ Error checking final status: {e}")

if __name__ == "__main__":
    main()
