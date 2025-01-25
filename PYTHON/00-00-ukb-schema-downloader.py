import requests
import os
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UKBiobankSchemaDownloader:
    def __init__(self, base_url: str = "https://biobank.ndph.ox.ac.uk/ukb"):
        self.base_url = base_url
        self.session = requests.Session()
        self.schema_ids = [
            27, 3, 13, 18, 1, 14, 16, 2, 15, 9, 24, 26, 25, 19, 17, 
            21, 23, 22, 4, 999, 11, 12, 10, 8, 5, 7, 6, 20
        ]

    def download_schema(self, schema_id: int, fmt: str, output_dir: str):
        url = f"{self.base_url}/scdown.cgi?fmt={fmt}&id={schema_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        extension = 'txt' if fmt == 'txt' else 'xml'
        filename = f"schema_{schema_id}.{extension}"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info(f"Downloaded schema {schema_id} in {fmt} format")

    def download_all(self, output_dir: str = "ukb_schemas"):
        os.makedirs(output_dir, exist_ok=True)
        
        for schema_id in self.schema_ids:
            try:
                self.download_schema(schema_id, 'txt', output_dir)
                self.download_schema(schema_id, 'xml', output_dir)
            except Exception as e:
                logger.error(f"Failed to download schema {schema_id}: {e}")

if __name__ == "__main__":
    downloader = UKBiobankSchemaDownloader()
    downloader.download_all()
