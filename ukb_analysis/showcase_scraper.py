# ukb_analysis/showcase_scraper.py

import requests
import pandas as pd
import json
from pathlib import Path
import logging
import io
from typing import Dict, List, Optional
from collections import defaultdict

class UKBShowcaseScraper:
    """Handler for UK Biobank Showcase data"""
    
    def __init__(self):
        self.base_url = "https://biobank.ndph.ox.ac.uk/showcase/scdown.cgi"
        self.session = requests.Session()
        self.categories = {}
        
        # Define schema URLs
        self.schema_urls = {
            'fields': {'fmt': 'txt', 'id': '1'},  # Data fields
            'categories': {'fmt': 'txt', 'id': '2'},  # Category hierarchy
            'codings': {'fmt': 'txt', 'id': '3'}  # Data codings
        }

    def fetch_categories(self) -> Dict:
        """Fetch category information from schema files"""
        logging.info("Fetching UK Biobank category information")
        
        try:
            # Fetch schema files
            fields_df = self._fetch_schema('fields')
            categories_df = self._fetch_schema('categories')
            
            # Check if DataFrames are empty
            if fields_df is None or categories_df is None or fields_df.empty or categories_df.empty:
                raise ValueError("Failed to fetch valid schema files")
            
            # Process category hierarchy
            categories = self._process_categories(categories_df, fields_df)
            self.categories = categories
            return categories
            
        except Exception as e:
            logging.error(f"Error processing showcase data: {str(e)}")
            return {}

    def _fetch_schema(self, schema_type: str) -> Optional[pd.DataFrame]:
        """Fetch a specific schema file"""
        params = self.schema_urls[schema_type]
        
        try:
            logging.info(f"Fetching {schema_type} schema...")
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Check if response is valid
            if not response.text:
                logging.error(f"Empty response for {schema_type} schema")
                return None
            
            # Read tab-separated data
            df = pd.read_csv(io.StringIO(response.text), sep='\t', low_memory=False)
            
            # Log the structure of received data
            logging.info(f"Received {schema_type} schema with columns: {df.columns.tolist()}")
            logging.info(f"Number of rows in {schema_type} schema: {len(df)}")
            
            return df
            
        except Exception as e:
            logging.error(f"Error fetching {schema_type} schema: {str(e)}")
            return None

    def _process_categories(self, categories_df: pd.DataFrame, fields_df: pd.DataFrame) -> Dict:
        """Process category hierarchy and field information"""
        logging.info("Processing category hierarchy...")
        
        categories = defaultdict(lambda: {
            'name': '',
            'subcategories': defaultdict(lambda: {
                'name': '',
                'fields': []
            })
        })
        
        # Process category hierarchy
        for _, row in categories_df.iterrows():
            cat_id = str(row.get('cat_id', ''))
            if not cat_id:
                continue
                
            cat_name = row.get('title', row.get('cat_name', ''))  # Try both possible column names
            parent_id = str(row.get('parent_id', ''))
            
            if parent_id and parent_id != 'nan':
                # This is a subcategory
                categories[parent_id]['subcategories'][cat_id]['name'] = cat_name
            else:
                # This is a main category
                categories[cat_id]['name'] = cat_name
        
        # Process fields
        logging.info("Processing fields...")
        for _, field in fields_df.iterrows():
            field_id = str(field.get('field_id', ''))
            if not field_id:
                continue
                
            cat_id = str(field.get('category', field.get('cat_id', '')))  # Try both possible column names
            
            field_info = {
                'field_id': field_id,
                'name': field.get('title', field.get('field_name', '')),  # Try both possible column names
                'type': field.get('type', ''),
                'description': field.get('description', '')
            }
            
            # Find the appropriate category
            found_category = False
            for main_cat in categories.values():
                for subcat in main_cat['subcategories'].values():
                    if cat_id in subcat['name'] or cat_id == subcat['name']:
                        subcat['fields'].append(field_info)
                        found_category = True
                        break
                if found_category:
                    break
            
            # If no category found, add to default
            if not found_category:
                categories['uncategorized']['subcategories']['default']['fields'].append(field_info)
        
        logging.info(f"Processed {len(categories)} categories")
        return dict(categories)

    def save_categories(self, filename: str = 'ukb_categories.json'):
        """Save category information to JSON"""
        output_path = Path('data') / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.categories, f, indent=2)
            
        logging.info(f"Saved category information to {output_path}")

    def save_as_csv(self, filename: str = 'ukb_fields.csv'):
        """Save fields in a flat CSV format"""
        rows = []
        
        for cat_id, cat_data in self.categories.items():
            for subcat_id, subcat_data in cat_data['subcategories'].items():
                for field in subcat_data['fields']:
                    row = {
                        'category_id': cat_id,
                        'category_name': cat_data['name'],
                        'subcategory_id': subcat_id,
                        'subcategory_name': subcat_data['name'],
                        'field_id': field['field_id'],
                        'field_name': field['name'],
                        'field_type': field.get('type', ''),
                        'description': field.get('description', '')
                    }
                    rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            output_path = Path('data') / filename
            df.to_csv(output_path, index=False)
            logging.info(f"Saved field information to {output_path}")
        else:
            logging.warning("No fields to save to CSV")
