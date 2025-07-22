import requests
import json

# Test request đơn giản
test_voucher = {
    "name": "Test Voucher",
    "description": "Test description",
    "usage_instructions": "Test usage",
    "terms_of_use": "Test terms",
    "tags": "test",
    "location": "Test location",
    "price": 100000,
    "unit": 1,
    "merchant": "Test Merchant"
}

try:
    print("🧪 Testing simple voucher API...")
    response = requests.post(
        "http://localhost:8000/api/admin/add_voucher",
        json=test_voucher,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
