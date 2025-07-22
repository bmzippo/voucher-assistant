# 📊 Data Processing Guide

> **  AI Voucher Assistant - Data Pipeline & Processing Guide**

## 📋 Table of Contents
- [📊 Data Processing Guide](#-data-processing-guide)
  - [📋 Table of Contents](#-table-of-contents)
  - [📁 Project Structure](#-project-structure)
  - [🔄 Data Pipeline Overview](#-data-pipeline-overview)
    - [1. Main Indexer Orchestrator](#1-main-indexer-orchestrator)
    - [2. Data Loader](#2-data-loader)
    - [3. Data Cleaner](#3-data-cleaner)
    - [4. Embedding Processor](#4-embedding-processor)
  - [🚀 Running the Data Pipeline](#-running-the-data-pipeline)
    - [Command Line Usage](#command-line-usage)
    - [Programmatic Usage](#programmatic-usage)
    - [Monitoring and Logging](#monitoring-and-logging)

## 📁 Project Structure

```
voucher_assistant/backend/data_processing/
├── main_indexer.py               # Main indexing orchestrator
├── data_loader.py                # Excel/CSV data loading
├── data_cleaner.py               # Data validation & cleaning
├── modular_indexer.py            # Modular indexing system
├── embedding_processor.py        # AI embedding generation
├── location_processor.py         # Geographic data processing
├── price_processor.py            # Price & discount calculations
├── requirements.txt              # Processing dependencies
│
├── pipelines/                    # Data processing pipelines
│   ├── extraction_pipeline.py   # Data extraction from sources
│   ├── transformation_pipeline.py # Data transformation logic
│   ├── loading_pipeline.py      # Data loading to Elasticsearch
│   └── validation_pipeline.py   # Data quality validation
│
├── processors/                   # Specialized processors
│   ├── text_processor.py        # Vietnamese text processing
│   ├── image_processor.py       # Image metadata extraction
│   ├── geo_processor.py         # Geographic coordinate processing
│   └── time_processor.py        # Date/time standardization
│
├── validators/                   # Data validation modules
│   ├── schema_validator.py      # JSON schema validation
│   ├── business_validator.py    # Business logic validation
│   ├── quality_validator.py     # Data quality checks
│   └── completeness_validator.py # Completeness validation
│
├── utils/                        # Processing utilities
│   ├── file_handlers.py         # File I/O operations
│   ├── batch_processor.py       # Batch processing utilities
│   ├── error_handler.py         # Error handling & recovery
│   └── performance_monitor.py   # Performance monitoring
│
├── config/                       # Configuration files
│   ├── processing_config.yaml   # Processing configuration
│   ├── schema_definitions.json  # Data schemas
│   └── validation_rules.yaml    # Business validation rules
│
└── tests/                        # Data processing tests
    ├── test_data_loader.py       # Loader tests
    ├── test_data_cleaner.py      # Cleaner tests
    ├── test_pipelines.py         # Pipeline tests
    └── fixtures/                 # Test data fixtures
        ├── sample_vouchers.xlsx
        ├── sample_locations.json
        └── sample_embeddings.npy
```

## 🔄 Data Pipeline Overview

### 1. Main Indexer Orchestrator
```python
# data_processing/main_indexer.py
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd
from tqdm import tqdm

from .data_loader import DataLoader
from .data_cleaner import DataCleaner
from .modular_indexer import ModularIndexer
from .embedding_processor import EmbeddingProcessor
from .location_processor import LocationProcessor
from .validators.quality_validator import QualityValidator

@dataclass
class ProcessingConfig:
    """Configuration for data processing pipeline"""
    batch_size: int = 100
    max_workers: int = 4
    enable_validation: bool = True
    skip_existing: bool = True
    embedding_model: str = "dangvantuan/vietnamese-embedding"
    index_name: str = "vouchers_advanced"

class DataProcessingPipeline:
    """
    Main data processing pipeline for   voucher system
    Orchestrates: Loading → Cleaning → Validation → Embedding → Indexing
    """
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize components
        self.data_loader = DataLoader()
        self.data_cleaner = DataCleaner()
        self.embedding_processor = EmbeddingProcessor(config.embedding_model)
        self.location_processor = LocationProcessor()
        self.quality_validator = QualityValidator()
        self.modular_indexer = ModularIndexer(config.index_name)
        
        self.logger.info("🚀 Data Processing Pipeline initialized")
    
    async def process_voucher_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Main processing method - handles multiple Excel files
        """
        results = {
            "processed_files": [],
            "total_vouchers": 0,
            "successful_vouchers": 0,
            "failed_vouchers": 0,
            "processing_time": 0,
            "errors": []
        }
        
        start_time = time.time()
        self.logger.info(f"📁 Processing {len(file_paths)} voucher files...")
        
        try:
            # Phase 1: Load and validate all files
            all_vouchers = []
            for file_path in file_paths:
                self.logger.info(f"📖 Loading file: {file_path}")
                
                # Load raw data
                raw_data = await self.data_loader.load_excel_file(file_path)
                if raw_data.empty:
                    self.logger.warning(f"⚠️ Empty file: {file_path}")
                    continue
                
                # Clean and validate data
                cleaned_data = await self.data_cleaner.clean_voucher_data(raw_data)
                
                if self.config.enable_validation:
                    validation_results = self.quality_validator.validate_batch(cleaned_data)
                    if validation_results["error_count"] > 0:
                        self.logger.warning(f"⚠️ Validation issues in {file_path}: {validation_results['error_count']} errors")
                
                all_vouchers.extend(cleaned_data.to_dict('records'))
                results["processed_files"].append({
                    "file": file_path,
                    "voucher_count": len(cleaned_data),
                    "status": "loaded"
                })
            
            results["total_vouchers"] = len(all_vouchers)
            self.logger.info(f"📊 Total vouchers loaded: {results['total_vouchers']}")
            
            # Phase 2: Process in batches for performance
            successful_count = 0
            failed_count = 0
            
            for i in tqdm(range(0, len(all_vouchers), self.config.batch_size), 
                         desc="Processing batches"):
                batch = all_vouchers[i:i + self.config.batch_size]
                
                try:
                    # Process batch
                    processed_batch = await self._process_voucher_batch(batch)
                    
                    # Index to Elasticsearch
                    indexing_result = await self.modular_indexer.index_voucher_batch(processed_batch)
                    
                    successful_count += indexing_result["successful"]
                    failed_count += indexing_result["failed"]
                    
                except Exception as e:
                    self.logger.error(f"❌ Batch processing error: {e}")
                    failed_count += len(batch)
                    results["errors"].append(f"Batch {i//self.config.batch_size + 1}: {str(e)}")
            
            # Final results
            results["successful_vouchers"] = successful_count
            results["failed_vouchers"] = failed_count
            results["processing_time"] = time.time() - start_time
            
            self.logger.info(f"✅ Processing completed:")
            self.logger.info(f"   📈 Successful: {successful_count}")
            self.logger.info(f"   ❌ Failed: {failed_count}")
            self.logger.info(f"   ⏱️ Time: {results['processing_time']:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline error: {e}")
            results["errors"].append(f"Pipeline error: {str(e)}")
            return results
    
    async def _process_voucher_batch(self, vouchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of vouchers with all transformations"""
        processed_vouchers = []
        
        for voucher in vouchers:
            try:
                # 1. Geographic processing
                if voucher.get('location'):
                    voucher = await self.location_processor.process_location(voucher)
                
                # 2. Text processing and embedding generation
                voucher = await self.embedding_processor.generate_voucher_embeddings(voucher)
                
                # 3. Price calculations
                voucher = self._calculate_price_metrics(voucher)
                
                # 4. Final validation
                if self._validate_processed_voucher(voucher):
                    processed_vouchers.append(voucher)
                
            except Exception as e:
                self.logger.error(f"❌ Voucher processing error: {e}")
                continue
        
        return processed_vouchers

# CLI interface for manual processing
async def main():
    """Command-line interface for data processing"""
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description="  Voucher Data Processing Pipeline")
    parser.add_argument("--files", nargs="+", help="Excel files to process")
    parser.add_argument("--directory", help="Directory containing Excel files")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker processes")
    parser.add_argument("--index", default="vouchers_advanced", help="Elasticsearch index name")
    
    args = parser.parse_args()
    
    # Determine files to process
    files_to_process = []
    if args.files:
        files_to_process.extend(args.files)
    if args.directory:
        files_to_process.extend(glob.glob(f"{args.directory}/*.xlsx"))
    
    if not files_to_process:
        print("❌ No files specified for processing")
        return
    
    # Configure pipeline
    config = ProcessingConfig(
        batch_size=args.batch_size,
        max_workers=args.workers,
        index_name=args.index
    )
    
    # Run pipeline
    pipeline = DataProcessingPipeline(config)
    results = await pipeline.process_voucher_files(files_to_process)
    
    # Print results
    print("\n" + "="*50)
    print("📊 PROCESSING RESULTS")
    print("="*50)
    print(f"Files processed: {len(results['processed_files'])}")
    print(f"Total vouchers: {results['total_vouchers']}")
    print(f"Successful: {results['successful_vouchers']}")
    print(f"Failed: {results['failed_vouchers']}")
    print(f"Processing time: {results['processing_time']:.2f}s")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Data Loader
```python
# data_processing/data_loader.py
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import asyncio
import aiofiles
import logging
from dataclasses import dataclass

@dataclass
class LoaderConfig:
    """Configuration for data loading"""
    encoding: str = 'utf-8'
    sheet_name: Optional[str] = None  # None means all sheets
    header_row: int = 0
    skip_rows: Optional[List[int]] = None
    max_rows: Optional[int] = None
    chunk_size: int = 1000

class DataLoader:
    """
    Advanced data loader for   voucher system
    Supports: Excel, CSV, JSON with async processing
    """
    
    def __init__(self, config: LoaderConfig = None):
        self.config = config or LoaderConfig()
        self.logger = logging.getLogger(__name__)
        
        # Column mapping for different file formats
        self.column_mappings = {
            'standard': {
                'voucher_id': ['voucher_id', 'id', 'ID', 'Voucher ID'],
                'voucher_name': ['voucher_name', 'name', 'Name', 'Voucher Name', 'Title'],
                'content': ['content', 'description', 'Description', 'Details'],
                'location': ['location', 'Location', 'Address', 'Địa chỉ'],
                'service_category': ['category', 'Category', 'Service Type', 'Loại dịch vụ'],
                'price': ['price', 'Price', 'Giá', 'Original Price'],
                'discount_price': ['discount_price', 'Discounted Price', 'Giá khuyến mãi']
            }
        }
    
    async def load_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Load Excel file with intelligent column detection
        """
        try:
            self.logger.info(f"📖 Loading Excel file: {file_path}")
            
            # Check file existence
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load with error handling
            df = pd.read_excel(
                file_path,
                sheet_name=self.config.sheet_name,
                header=self.config.header_row,
                skiprows=self.config.skip_rows,
                nrows=self.config.max_rows,
                engine='openpyxl'
            )
            
            # Handle multiple sheets
            if isinstance(df, dict):
                # Combine all sheets
                combined_df = pd.DataFrame()
                for sheet_name, sheet_df in df.items():
                    sheet_df['source_sheet'] = sheet_name
                    combined_df = pd.concat([combined_df, sheet_df], ignore_index=True)
                df = combined_df
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Basic data type inference
            df = self._infer_data_types(df)
            
            self.logger.info(f"✅ Loaded {len(df)} rows from {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    async def load_multiple_files(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Load multiple files concurrently and combine
        """
        self.logger.info(f"📚 Loading {len(file_paths)} files concurrently...")
        
        # Load files concurrently
        tasks = [self.load_excel_file(file_path) for file_path in file_paths]
        dataframes = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine successful loads
        combined_df = pd.DataFrame()
        successful_loads = 0
        
        for i, df in enumerate(dataframes):
            if isinstance(df, pd.DataFrame) and not df.empty:
                df['source_file'] = file_paths[i]
                combined_df = pd.concat([combined_df, df], ignore_index=True)
                successful_loads += 1
            elif isinstance(df, Exception):
                self.logger.error(f"❌ Failed to load {file_paths[i]}: {df}")
        
        self.logger.info(f"📊 Combined {successful_loads}/{len(file_paths)} files: {len(combined_df)} total rows")
        return combined_df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names using intelligent mapping
        """
        standardized_df = df.copy()
        column_map = {}
        
        for standard_name, possible_names in self.column_mappings['standard'].items():
            for col in df.columns:
                if col.strip() in possible_names:
                    column_map[col] = standard_name
                    break
        
        if column_map:
            standardized_df = standardized_df.rename(columns=column_map)
            self.logger.info(f"🔧 Standardized columns: {column_map}")
        
        return standardized_df
    
    def _infer_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Intelligent data type inference for Vietnamese content
        """
        typed_df = df.copy()
        
        for col in typed_df.columns:
            # Price columns
            if 'price' in col.lower() or 'giá' in col.lower():
                typed_df[col] = pd.to_numeric(typed_df[col], errors='coerce')
            
            # Location columns
            elif 'location' in col.lower() or 'địa chỉ' in col.lower():
                typed_df[col] = typed_df[col].astype(str).str.strip()
            
            # Text content columns
            elif col in ['content', 'voucher_name', 'description']:
                typed_df[col] = typed_df[col].astype(str).str.strip()
            
            # ID columns
            elif 'id' in col.lower():
                # Try to keep as string to preserve leading zeros
                typed_df[col] = typed_df[col].astype(str).str.strip()
        
        return typed_df
```

### 3. Data Cleaner
```python
# data_processing/data_cleaner.py
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass

@dataclass
class CleaningStats:
    """Statistics from data cleaning process"""
    total_rows: int = 0
    cleaned_rows: int = 0
    removed_rows: int = 0
    modified_fields: Dict[str, int] = None
    errors: List[str] = None

class DataCleaner:
    """
    Advanced data cleaning for   voucher system
    Handles: Vietnamese text, pricing, locations, duplicates
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Vietnamese text normalization patterns
        self.text_patterns = {
            'extra_whitespace': re.compile(r'\s+'),
            'special_chars': re.compile(r'[^\w\s\-\.,\(\)\[\]\/]'),
            'price_extraction': re.compile(r'[\d,\.]+'),
            'vietnamese_normalize': self._build_vietnamese_patterns()
        }
        
        # Location standardization
        self.location_standards = {
            'Hà Nội': ['Ha Noi', 'Hanoi', 'HN', 'Hà Nội'],
            'TP.HCM': ['Ho Chi Minh', 'Saigon', 'HCM', 'TPHCM', 'Sài Gòn'],
            'Đà Nẵng': ['Da Nang', 'Danang', 'DN']
        }
    
    async def clean_voucher_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main cleaning method for voucher data
        """
        stats = CleaningStats(
            total_rows=len(df),
            modified_fields={},
            errors=[]
        )
        
        self.logger.info(f"🧹 Cleaning {stats.total_rows} voucher records...")
        
        try:
            cleaned_df = df.copy()
            
            # 1. Remove completely empty rows
            cleaned_df = self._remove_empty_rows(cleaned_df, stats)
            
            # 2. Clean text fields
            cleaned_df = self._clean_text_fields(cleaned_df, stats)
            
            # 3. Standardize locations
            cleaned_df = self._standardize_locations(cleaned_df, stats)
            
            # 4. Clean and normalize prices
            cleaned_df = self._clean_price_fields(cleaned_df, stats)
            
            # 5. Remove duplicates
            cleaned_df = self._remove_duplicates(cleaned_df, stats)
            
            # 6. Validate required fields
            cleaned_df = self._validate_required_fields(cleaned_df, stats)
            
            # 7. Add derived fields
            cleaned_df = self._add_derived_fields(cleaned_df, stats)
            
            stats.cleaned_rows = len(cleaned_df)
            stats.removed_rows = stats.total_rows - stats.cleaned_rows
            
            self.logger.info(f"✅ Cleaning completed:")
            self.logger.info(f"   📊 Original: {stats.total_rows} rows")
            self.logger.info(f"   ✨ Cleaned: {stats.cleaned_rows} rows")
            self.logger.info(f"   🗑️ Removed: {stats.removed_rows} rows")
            
            return cleaned_df
            
        except Exception as e:
            self.logger.error(f"❌ Cleaning error: {e}")
            stats.errors.append(str(e))
            return df
    
    def _clean_text_fields(self, df: pd.DataFrame, stats: CleaningStats) -> pd.DataFrame:
        """Clean Vietnamese text fields"""
        text_columns = ['voucher_name', 'content', 'description']
        
        for col in text_columns:
            if col in df.columns:
                original_nulls = df[col].isnull().sum()
                
                # Clean text
                df[col] = df[col].astype(str)
                df[col] = df[col].str.strip()
                
                # Remove extra whitespace
                df[col] = df[col].apply(lambda x: re.sub(r'\s+', ' ', x) if pd.notna(x) else x)
                
                # Remove special characters but keep Vietnamese
                df[col] = df[col].apply(self._clean_vietnamese_text)
                
                # Replace empty strings with NaN
                df[col] = df[col].replace('', np.nan)
                df[col] = df[col].replace('nan', np.nan)
                
                cleaned_nulls = df[col].isnull().sum()
                stats.modified_fields[f'{col}_cleaned'] = cleaned_nulls - original_nulls
        
        return df
    
    def _clean_vietnamese_text(self, text: str) -> str:
        """Specialized Vietnamese text cleaning"""
        if pd.isna(text) or text == 'nan':
            return np.nan
        
        # Convert to string
        text = str(text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Clean special characters but preserve Vietnamese diacritics
        text = re.sub(r'[^\w\s\-\.,\(\)\[\]\/àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text if text else np.nan
    
    def _standardize_locations(self, df: pd.DataFrame, stats: CleaningStats) -> pd.DataFrame:
        """Standardize location names"""
        if 'location' not in df.columns:
            return df
        
        def standardize_location(location):
            if pd.isna(location):
                return np.nan
            
            location = str(location).strip()
            
            # Check against standard locations
            for standard, variants in self.location_standards.items():
                for variant in variants:
                    if variant.lower() in location.lower():
                        return standard
            
            return location
        
        original_locations = df['location'].value_counts()
        df['location'] = df['location'].apply(standardize_location)
        standardized_locations = df['location'].value_counts()
        
        stats.modified_fields['locations_standardized'] = len(original_locations) - len(standardized_locations)
        
        return df
    
    def _clean_price_fields(self, df: pd.DataFrame, stats: CleaningStats) -> pd.DataFrame:
        """Clean and normalize price fields"""
        price_columns = ['price', 'discount_price', 'original_price', 'discounted_price']
        
        for col in price_columns:
            if col in df.columns:
                # Extract numeric values from price strings
                df[col] = df[col].astype(str)
                
                # Remove currency symbols and text
                df[col] = df[col].str.replace(r'[^\d,\.]', '', regex=True)
                
                # Handle Vietnamese number formatting (1.000.000 or 1,000,000)
                df[col] = df[col].str.replace(',', '')  # Remove commas
                
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Remove unrealistic prices (too high or too low)
                if col in ['price', 'original_price']:
                    df.loc[df[col] < 1000, col] = np.nan  # Too low
                    df.loc[df[col] > 50000000, col] = np.nan  # Too high (50M VND)
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame, stats: CleaningStats) -> pd.DataFrame:
        """Remove duplicate vouchers intelligently"""
        initial_count = len(df)
        
        # Define duplicate criteria
        duplicate_columns = ['voucher_name', 'location']
        available_columns = [col for col in duplicate_columns if col in df.columns]
        
        if available_columns:
            # Keep first occurrence of duplicates
            df = df.drop_duplicates(subset=available_columns, keep='first')
            
            removed = initial_count - len(df)
            stats.modified_fields['duplicates_removed'] = removed
            
            if removed > 0:
                self.logger.info(f"🗑️ Removed {removed} duplicate vouchers")
        
        return df
    
    def _validate_required_fields(self, df: pd.DataFrame, stats: CleaningStats) -> pd.DataFrame:
        """Ensure required fields are present and valid"""
        required_fields = ['voucher_name']
        
        for field in required_fields:
            if field in df.columns:
                initial_count = len(df)
                df = df[df[field].notna()]
                df = df[df[field] != '']
                
                removed = initial_count - len(df)
                if removed > 0:
                    stats.modified_fields[f'missing_{field}_removed'] = removed
        
        return df
    
    def _add_derived_fields(self, df: pd.DataFrame, stats: CleaningStats) -> pd.DataFrame:
        """Add computed/derived fields"""
        
        # Add price range categorization
        if 'price' in df.columns:
            df['price_range'] = pd.cut(df['price'], 
                                     bins=[0, 100000, 500000, 1000000, float('inf')],
                                     labels=['budget', 'mid-range', 'premium', 'luxury'])
        
        # Add content length
        if 'content' in df.columns:
            df['content_length'] = df['content'].str.len()
        
        # Add location type
        if 'location' in df.columns:
            df['location_type'] = df['location'].apply(self._categorize_location)
        
        # Add data quality score
        df['data_quality_score'] = self._calculate_quality_score(df)
        
        return df
    
    def _categorize_location(self, location: str) -> str:
        """Categorize location type"""
        if pd.isna(location):
            return 'unknown'
        
        location = str(location).lower()
        
        if any(city in location for city in ['hà nội', 'hanoi']):
            return 'hanoi'
        elif any(city in location for city in ['hcm', 'sài gòn', 'saigon']):
            return 'hcm'
        elif any(city in location for city in ['đà nẵng', 'da nang']):
            return 'danang'
        else:
            return 'other'
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate data quality score for each record"""
        score = pd.Series(0.0, index=df.index)
        
        # Points for having required fields
        if 'voucher_name' in df.columns:
            score += df['voucher_name'].notna() * 0.3
        
        if 'content' in df.columns:
            score += df['content'].notna() * 0.2
        
        if 'location' in df.columns:
            score += df['location'].notna() * 0.2
        
        if 'price' in df.columns:
            score += df['price'].notna() * 0.2
        
        # Points for content quality
        if 'content_length' in df.columns:
            score += (df['content_length'] > 50) * 0.1
        
        return score
```

### 4. Embedding Processor
```python
# data_processing/embedding_processor.py
import numpy as np
import asyncio
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation"""
    model_name: str = "dangvantuan/vietnamese-embedding"
    batch_size: int = 32
    max_length: int = 512
    dimension: int = 768
    normalize: bool = True

class EmbeddingProcessor:
    """
    Advanced embedding processor for Vietnamese voucher content
    Optimized for   ecosystem with multi-field embedding strategy
    """
    
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize model
        self.model = SentenceTransformer(self.config.model_name)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Field weights for combined embeddings
        self.field_weights = {
            'content': 0.4,
            'voucher_name': 0.25,
            'location': 0.15,
            'service_category': 0.1,
            'target_audience': 0.1
        }
        
        self.logger.info(f"🤖 Embedding processor initialized with {self.config.model_name}")
    
    async def generate_voucher_embeddings(self, voucher: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate multiple embeddings for a single voucher
        """
        try:
            # Extract text fields
            texts = self._extract_embedding_texts(voucher)
            
            # Generate individual embeddings
            embeddings = {}
            for field, text in texts.items():
                if text and text.strip():
                    embedding = await self._generate_single_embedding(text)
                    embeddings[f'{field}_embedding'] = embedding.tolist()
            
            # Generate combined embedding
            if embeddings:
                combined_embedding = self._create_combined_embedding(embeddings, texts)
                embeddings['combined_embedding'] = combined_embedding.tolist()
            
            # Add embeddings to voucher
            voucher.update(embeddings)
            
            # Add embedding metadata
            voucher['embedding_model'] = self.config.model_name
            voucher['embedding_dimension'] = self.config.dimension
            voucher['embedding_fields'] = list(texts.keys())
            
            return voucher
            
        except Exception as e:
            self.logger.error(f"❌ Embedding generation error: {e}")
            return voucher
    
    async def generate_batch_embeddings(self, vouchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a batch of vouchers efficiently
        """
        self.logger.info(f"🔄 Generating embeddings for {len(vouchers)} vouchers...")
        
        # Process in parallel batches
        tasks = []
        for i in range(0, len(vouchers), self.config.batch_size):
            batch = vouchers[i:i + self.config.batch_size]
            task = self._process_voucher_batch(batch)
            tasks.append(task)
        
        # Execute all batches
        processed_batches = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        processed_vouchers = []
        for batch_result in processed_batches:
            if isinstance(batch_result, list):
                processed_vouchers.extend(batch_result)
            else:
                self.logger.error(f"❌ Batch processing error: {batch_result}")
        
        self.logger.info(f"✅ Generated embeddings for {len(processed_vouchers)} vouchers")
        return processed_vouchers
    
    async def _process_voucher_batch(self, vouchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of vouchers for embedding generation"""
        processed = []
        
        # Collect all texts for batch processing
        all_texts = []
        text_mapping = []  # Maps text index to (voucher_index, field_name)
        
        for voucher_idx, voucher in enumerate(vouchers):
            texts = self._extract_embedding_texts(voucher)
            for field, text in texts.items():
                if text and text.strip():
                    all_texts.append(text[:self.config.max_length])
                    text_mapping.append((voucher_idx, field))
        
        # Generate all embeddings at once
        if all_texts:
            all_embeddings = await self._generate_batch_embeddings_sync(all_texts)
            
            # Distribute embeddings back to vouchers
            for i, (voucher_idx, field) in enumerate(text_mapping):
                if voucher_idx < len(vouchers):
                    voucher = vouchers[voucher_idx]
                    if f'{field}_embedding' not in voucher:
                        voucher[f'{field}_embedding'] = all_embeddings[i].tolist()
        
        # Generate combined embeddings
        for voucher in vouchers:
            embeddings = {k: np.array(v) for k, v in voucher.items() if k.endswith('_embedding')}
            if embeddings:
                texts = self._extract_embedding_texts(voucher)
                combined = self._create_combined_embedding(embeddings, texts)
                voucher['combined_embedding'] = combined.tolist()
                voucher['embedding_model'] = self.config.model_name
                voucher['embedding_dimension'] = self.config.dimension
            
            processed.append(voucher)
        
        return processed
    
    def _extract_embedding_texts(self, voucher: Dict[str, Any]) -> Dict[str, str]:
        """Extract and prepare text fields for embedding"""
        texts = {}
        
        # Main content fields
        if voucher.get('content'):
            texts['content'] = str(voucher['content']).strip()
        
        if voucher.get('voucher_name'):
            texts['voucher_name'] = str(voucher['voucher_name']).strip()
        
        # Location information
        location_parts = []
        if voucher.get('location'):
            location_parts.append(str(voucher['location']))
        if voucher.get('district'):
            location_parts.append(str(voucher['district']))
        if voucher.get('city'):
            location_parts.append(str(voucher['city']))
        
        if location_parts:
            texts['location'] = ' '.join(location_parts).strip()
        
        # Service information
        service_parts = []
        if voucher.get('service_category'):
            service_parts.append(str(voucher['service_category']))
        if voucher.get('cuisine_type'):
            service_parts.append(str(voucher['cuisine_type']))
        if voucher.get('service_type'):
            service_parts.append(str(voucher['service_type']))
        
        if service_parts:
            texts['service_info'] = ' '.join(service_parts).strip()
        
        # Target audience
        if voucher.get('target_audience'):
            texts['target_audience'] = str(voucher['target_audience']).strip()
        
        return texts
    
    async def _generate_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            self.executor,
            self.model.encode,
            text[:self.config.max_length]
        )
        
        if self.config.normalize:
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    async def _generate_batch_embeddings_sync(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for batch of texts synchronously"""
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            self.executor,
            self.model.encode,
            texts
        )
        
        if self.config.normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings
    
    def _create_combined_embedding(self, embeddings: Dict[str, np.ndarray], 
                                 texts: Dict[str, str]) -> np.ndarray:
        """Create weighted combined embedding from multiple field embeddings"""
        
        weighted_embeddings = []
        total_weight = 0.0
        
        for field, weight in self.field_weights.items():
            embedding_key = f'{field}_embedding'
            if embedding_key in embeddings and field in texts:
                embedding = embeddings[embedding_key]
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                
                weighted_embeddings.append(embedding * weight)
                total_weight += weight
        
        if not weighted_embeddings:
            # Fallback to first available embedding
            first_embedding = next(iter(embeddings.values()))
            if isinstance(first_embedding, list):
                first_embedding = np.array(first_embedding)
            return first_embedding
        
        # Combine weighted embeddings
        combined = np.sum(weighted_embeddings, axis=0)
        
        # Normalize if requested
        if self.config.normalize and total_weight > 0:
            combined = combined / np.linalg.norm(combined)
        
        return combined
```

## 🚀 Running the Data Pipeline

### Command Line Usage
```bash
# Process single file
python data_processing/main_indexer.py --files data/temp_voucher.xlsx

# Process multiple files
python data_processing/main_indexer.py --files data/voucher1.xlsx data/voucher2.xlsx

# Process entire directory
python data_processing/main_indexer.py --directory data/ --batch-size 50

# Custom index name
python data_processing/main_indexer.py --files data/vouchers.xlsx --index vouchers_production
```

### Programmatic Usage
```python
from data_processing.main_indexer import DataProcessingPipeline, ProcessingConfig

# Configure pipeline
config = ProcessingConfig(
    batch_size=100,
    max_workers=4,
    enable_validation=True,
    embedding_model="dangvantuan/vietnamese-embedding"
)

# Create and run pipeline
pipeline = DataProcessingPipeline(config)
results = await pipeline.process_voucher_files([
    "data/temp_voucher.xlsx",
    "data/importvoucher.xlsx"
])

print(f"Processed {results['successful_vouchers']} vouchers successfully")
```

### Monitoring and Logging
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Custom log configuration
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'data_processing.log',
            'formatter': 'detailed',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'data_processing': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

**Next**: [📚 Complete Project Documentation](../README.md)
