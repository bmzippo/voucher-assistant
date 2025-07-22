"""
Voucher Data Loader Module
Handles loading data from multiple Excel files with different formats
"""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class VoucherDataLoader:
    """
    Advanced loader for voucher data from multiple Excel sources
    """
    
    def __init__(self):
        self.loaded_files = []
        self.total_vouchers = 0
        
    def load_temp_voucher_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load temp voucher.xlsx file (original format)
        Columns: ['Name', 'Desc', 'Usage', 'TermOfUse', 'Tags', 'Location', 'Price', 'Unit', 'Merrchant']
        """
        logger.info(f"📊 Loading temp voucher file: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            logger.info(f"✅ Loaded {len(df)} vouchers from temp voucher file")
            
            vouchers = []
            for idx, row in df.iterrows():
                voucher_data = {
                    'voucher_id': f"temp_voucher_{idx + 1}",
                    'voucher_name': str(row.get('Name', '')).strip(),
                    'location': str(row.get('Location', 'Hà Nội')).strip(),
                    'description': str(row.get('Desc', '')).strip(),
                    'terms_conditions': str(row.get('TermOfUse', '')).strip(),
                    'usage': str(row.get('Usage', '')).strip(),
                    'price': str(row.get('Price', '')).strip(),
                    'tags': str(row.get('Tags', '')).strip(),
                    'merchant': str(row.get('Merrchant', '')).strip(),
                    'unit': str(row.get('Unit', '')).strip(),
                    'source_file': 'temp_voucher.xlsx',
                    'content': str(row.get('Desc', '')).strip() + ". " + str(row.get('TermOfUse', '')).strip() + ". " + str(row.get('Usage', '')).strip()
                }
                
                # Skip empty vouchers
                if voucher_data['voucher_name'] and voucher_data['voucher_name'] != 'nan':
                    vouchers.append(voucher_data)
            
            self.loaded_files.append(file_path)
            logger.info(f"✅ Processed {len(vouchers)} valid vouchers from temp file")
            return vouchers
            
        except Exception as e:
            logger.error(f"❌ Error loading temp voucher file {file_path}: {e}")
            raise
    
    def load_import_voucher_file(self, file_path: str, has_header: bool = True) -> List[Dict[str, Any]]:
        """
        Load importvoucher.xlsx or importvoucher2.xlsx files
        Expected columns: ['Name', 'Description', 'Terms', 'Location', 'Price', 'Category', 'Merchant']
        """
        logger.info(f"📊 Loading import voucher file: {file_path} (has_header: {has_header})")
        
        try:
            if has_header:
                df = pd.read_excel(file_path)
            else:
                # Load without header and assign column names from importvoucher.xlsx format
                df = pd.read_excel(file_path, header=None)
                # Assume same structure as importvoucher.xlsx
                expected_columns = ['Name', 'Description', 'Terms', 'Location', 'Price', 'Category', 'Merchant']
                if len(df.columns) >= len(expected_columns):
                    df.columns = expected_columns + [f'Extra_{i}' for i in range(len(df.columns) - len(expected_columns))]
                else:
                    # Pad missing columns
                    for i in range(len(df.columns), len(expected_columns)):
                        df[expected_columns[i]] = ''
                    df.columns = expected_columns[:len(df.columns)]
            
            logger.info(f"✅ Loaded {len(df)} vouchers from import file")
            logger.info(f"📋 Columns detected: {df.columns.tolist()}")
            
            vouchers = []
            file_name = Path(file_path).name
            
            for idx, row in df.iterrows():
                voucher_data = {
                    'voucher_id': f"import_{file_name.replace('.xlsx', '')}_{idx + 1}",
                    'voucher_name': str(row.get('Name', '')).strip(),
                    'location': str(row.get('Location', 'Hà Nội')).strip(),
                    'description': str(row.get('Description', '')).strip(),                    
                    'terms_conditions': str(row.get('Terms', '')).strip(),
                    'usage': '',  # Not available in import files
                    'price': str(row.get('Price', '')).strip(),
                    'tags': '',  # Not available in import files
                    'merchant': str(row.get('Merchant', '')).strip(),
                    'category': str(row.get('Category', '')).strip(),
                    'unit': '',  # Not available in import files
                    'source_file': file_name,
                    'content': str(row.get('Description', '')).strip() + ". " + str(row.get('Terms', '')).strip() + ". " + str(row.get('Usage', '')).strip()
                }

                
                # Skip empty vouchers
                if voucher_data['voucher_name'] and voucher_data['voucher_name'] != 'nan':
                    vouchers.append(voucher_data)
            
            self.loaded_files.append(file_path)
            logger.info(f"✅ Processed {len(vouchers)} valid vouchers from import file")
            return vouchers
            
        except Exception as e:
            logger.error(f"❌ Error loading import voucher file {file_path}: {e}")
            raise
    
    def load_all_voucher_files(self, data_dir: str) -> List[Dict[str, Any]]:
        """
        Load all voucher files from data directory
        """
        data_path = Path(data_dir)
        all_vouchers = []
        
        logger.info(f"🔍 Scanning for voucher files in: {data_path}")
        
        # Load temp voucher.xlsx
        temp_file = data_path / "temp voucher.xlsx"
        if temp_file.exists():
            vouchers = self.load_temp_voucher_file(str(temp_file))
            all_vouchers.extend(vouchers)
            logger.info(f"📂 Added {len(vouchers)} vouchers from temp voucher.xlsx")
        
        # Load importvoucher.xlsx (with header)
        import1_file = data_path / "importvoucher.xlsx"
        if import1_file.exists():
            vouchers = self.load_import_voucher_file(str(import1_file), has_header=True)
            all_vouchers.extend(vouchers)
            logger.info(f"📂 Added {len(vouchers)} vouchers from importvoucher.xlsx")
        
        # Load importvoucher2.xlsx (no header)
        import2_file = data_path / "importvoucher2.xlsx"
        if import2_file.exists():
            vouchers = self.load_import_voucher_file(str(import2_file), has_header=False)
            all_vouchers.extend(vouchers)
            logger.info(f"📂 Added {len(vouchers)} vouchers from importvoucher2.xlsx")
        
        self.total_vouchers = len(all_vouchers)
        logger.info(f"🎉 Total vouchers loaded: {self.total_vouchers} from {len(self.loaded_files)} files")
        
        return all_vouchers
    
    def get_loading_summary(self) -> Dict[str, Any]:
        """
        Get summary of loading process
        """
        return {
            'total_vouchers': self.total_vouchers,
            'files_loaded': len(self.loaded_files),
            'file_paths': self.loaded_files
        }
