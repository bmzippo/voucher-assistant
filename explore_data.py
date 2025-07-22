import pandas as pd
import json

# Đọc file Excel để hiểu cấu trúc dữ liệu voucher
file_path = "data/imporyvoucher.xlsx"

try:
    # Đọc tất cả sheets trong file Excel
    xls = pd.ExcelFile(file_path)
    print("Sheets trong file Excel:")
    for sheet_name in xls.sheet_names:
        print(f"- {sheet_name}")
    
    # Đọc sheet đầu tiên để xem cấu trúc dữ liệu
    df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0])
    
    print(f"\nCấu trúc dữ liệu sheet '{xls.sheet_names[0]}':")
    print(f"Số hàng: {len(df)}")
    print(f"Số cột: {len(df.columns)}")
    print(f"Các cột: {list(df.columns)}")
    
    print("\nDữ liệu mẫu (5 hàng đầu):")
    print(df.head().to_string())
    
    print("\nThông tin chi tiết về các cột:")
    print(df.info())
    
    # Lưu sample data để phân tích
    sample_data = df.head(3).to_dict('records')
    with open('sample_voucher_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("\nĐã lưu dữ liệu mẫu vào file 'sample_voucher_data.json'")
    
except Exception as e:
    print(f"Lỗi khi đọc file: {e}")
