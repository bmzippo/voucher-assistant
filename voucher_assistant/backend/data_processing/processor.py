"""
Advanced Data Processor for Voucher System
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
from advanced_vector_store import AdvancedVectorStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoucherDataProcessor:
    """
    Complete data processing pipeline for voucher data
    """
    
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.loader = VoucherDataLoader()
        self.cleaner = VoucherDataCleaner()
        self.vector_store = AdvancedVectorStore(es_url=elasticsearch_url)
        
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
        
        # Load all data files using the loader's directory method
        try:
            logger.info(f"Loading all voucher files from {data_dir}")
            all_vouchers = self.loader.load_all_voucher_files(data_dir)
            
            logger.info(f"Total vouchers loaded: {len(all_vouchers)}")
            results['total_processed'] = len(all_vouchers)
            
            # Get file-specific results from loader
            loader_summary = self.loader.get_loading_summary()
            results['file_results'] = loader_summary.get('file_results', {})
            
        except Exception as e:
            error_msg = f"Error loading voucher files: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        if not all_vouchers:
            logger.error("No vouchers loaded from any file")
            return results
        
        # Clean data
        logger.info("Starting data cleaning process...")
        cleaned_vouchers = []
        
        for voucher in all_vouchers:
            try:
                cleaned_voucher = self.cleaner.clean_voucher_data(voucher)
                cleaned_vouchers.append(cleaned_voucher)
            except Exception as e:
                error_msg = f"Error cleaning voucher {voucher.get('voucher_name', 'Unknown')}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        logger.info(f"Cleaned {len(cleaned_vouchers)} vouchers")
        
        # Get cleaning summary
        cleaning_summary = self.cleaner.get_cleaning_summary()
        results['cleaning_summary'] = cleaning_summary
        
        # Index to Elasticsearch
        if cleaned_vouchers:
            logger.info("Starting indexing to Elasticsearch...")
            try:
                indexed_count = 0
                for voucher in cleaned_vouchers:
                    success = await self.vector_store.index_voucher_advanced(voucher)
                    if success:
                        indexed_count += 1
                
                results['successful_indexed'] = indexed_count
                logger.info(f"Successfully indexed {indexed_count} vouchers")
            except Exception as e:
                error_msg = f"Error indexing to Elasticsearch: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def verify_indexing(self) -> Dict[str, Any]:
        """
        Verify that data was indexed correctly
        """
        try:
            # Test basic search
            basic_results = await self.vector_store.search("buffet", size=5)
            
            # Test advanced search
            advanced_results = await self.vector_store.advanced_search(
                query="nhà hàng",
                filters={
                    "location": "Hà Nội",
                    "business_type": "Restaurant"
                },
                size=5
            )
            
            return {
                'basic_search_count': len(basic_results.get('hits', [])),
                'advanced_search_count': len(advanced_results.get('hits', [])),
                'indexing_verified': True
            }
            
        except Exception as e:
            logger.error(f"Error verifying indexing: {str(e)}")
            return {
                'basic_search_count': 0,
                'advanced_search_count': 0,
                'indexing_verified': False,
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics
        """
        return {
            'loader_stats': self.loader.get_loading_summary(),
            'cleaner_stats': self.cleaner.get_cleaning_summary(),
        }

# Standalone processing function
async def process_voucher_data(
    data_dir: str = "/Users/1-tiennv-m/1MG/Projects/LLM/data",
    elasticsearch_url: str = "http://localhost:9200"
) -> Dict[str, Any]:
    """
    Process all voucher data in the specified directory
    """
    processor = VoucherDataProcessor(elasticsearch_url)
    
    logger.info("Starting voucher data processing...")
    results = await processor.process_all_files(data_dir)
    
    if results['successful_indexed'] > 0:
        logger.info("Verifying indexing...")
        verification = await processor.verify_indexing()
        results['verification'] = verification
    
    # Get final statistics
    stats = processor.get_statistics()
    results['final_stats'] = stats
    
    logger.info("Processing completed!")
    logger.info(f"Summary: {results['total_processed']} processed, {results['successful_indexed']} indexed")
    
    return results

if __name__ == "__main__":
    # Run the processor
    results = asyncio.run(process_voucher_data())
    
    print("\n" + "="*50)
    print("VOUCHER DATA PROCESSING RESULTS")
    print("="*50)
    print(f"Total processed: {results['total_processed']}")
    print(f"Successfully indexed: {results['successful_indexed']}")
    print(f"Errors: {len(results['errors'])}")
    
    if results.get('verification'):
        print(f"Basic search results: {results['verification']['basic_search_count']}")
        print(f"Advanced search results: {results['verification']['advanced_search_count']}")
    
    if results.get('final_stats'):
        print(f"Loading stats: {results['final_stats']['loader_stats']}")
        print(f"Cleaning stats: {results['final_stats']['cleaner_stats']}")
