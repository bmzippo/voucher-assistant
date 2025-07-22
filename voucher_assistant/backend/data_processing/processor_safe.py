"""
Advanced Data Processor for Voucher System (Safe Version)
Handles complete pipeline: loading, cleaning, and indexing
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from .voucher_loader import VoucherDataLoader
from .data_cleaner import VoucherDataCleaner
from advanced_vector_store_safe import AdvancedVectorStoreSafe

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoucherDataProcessorSafe:
    """
    Complete data processing pipeline for voucher data (Safe Version)
    """
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.loader = VoucherDataLoader()
        self.cleaner = VoucherDataCleaner()
        self.vector_store = AdvancedVectorStoreSafe(es_url=elasticsearch_url)
        
    async def process_all_files(self, data_dir: str) -> Dict[str, Any]:
        """
        Process all voucher files in the given directory
        """
        results = {
            'total_processed': 0,
            'successful_indexed': 0,
            'errors': [],
            'file_results': {}
        }
        
        data_path = Path(data_dir)
        excel_files = list(data_path.glob("*.xlsx"))
        
        if not excel_files:
            logger.warning(f"No Excel files found in {data_dir}")
            return results
        
        logger.info(f"Found {len(excel_files)} Excel files to process")
        
        for excel_file in excel_files:
            try:
                file_result = await self.process_single_file(excel_file)
                results['file_results'][excel_file.name] = file_result
                results['total_processed'] += file_result.get('total_vouchers', 0)
                results['successful_indexed'] += file_result.get('successful_indexed', 0)
                
            except Exception as e:
                error_msg = f"Error processing {excel_file.name}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['file_results'][excel_file.name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    async def process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single voucher file
        """
        logger.info(f"🔄 Processing file: {file_path.name}")
        
        # Step 1: Load data
        raw_data = await self.loader.load_excel_file(file_path)
        if not raw_data:
            return {
                'status': 'error',
                'error': 'Failed to load data from file'
            }
        
        logger.info(f"📊 Loaded {len(raw_data)} vouchers from {file_path.name}")
        
        # Step 2: Clean data
        cleaned_data = await self.cleaner.clean_voucher_batch(raw_data)
        valid_vouchers = [v for v in cleaned_data if v.get('is_valid', False)]
        
        logger.info(f"✅ Cleaned data: {len(valid_vouchers)}/{len(raw_data)} vouchers are valid")
        
        # Step 3: Index to vector store
        successful_indexed = 0
        errors = []
        
        for voucher in valid_vouchers:
            try:
                success = self.vector_store.add_voucher(voucher)
                if success:
                    successful_indexed += 1
                else:
                    errors.append(f"Failed to index voucher: {voucher.get('name', 'Unknown')}")
                    
            except Exception as e:
                error_msg = f"Error indexing voucher {voucher.get('name', 'Unknown')}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        result = {
            'status': 'success',
            'total_vouchers': len(raw_data),
            'valid_vouchers': len(valid_vouchers),
            'successful_indexed': successful_indexed,
            'errors': errors
        }
        
        logger.info(f"📈 File processing complete: {successful_indexed}/{len(valid_vouchers)} vouchers indexed")
        
        return result
    
    async def search_vouchers(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """
        Search vouchers using the vector store
        """
        return self.vector_store.search_vouchers(query, size)

# Async function for external use
async def process_voucher_data_safe(data_dir: str) -> Dict[str, Any]:
    """
    Process voucher data from the given directory (Safe Version)
    """
    processor = VoucherDataProcessorSafe()
    return await processor.process_all_files(data_dir)
