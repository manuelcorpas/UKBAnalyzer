
import requests
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import csv
import io

class UKBPublicationsParser:
    """Parser for UK Biobank Schema 19 (Publications)"""
    
    def __init__(self):
        self.base_url = "https://biobank.ndph.ox.ac.uk/ukb/scdown.cgi"
        self.session = requests.Session()
        self.publications = []

    def fetch_publications(self, format_type: str = 'txt') -> List[Dict]:
        """Fetch publications from UK Biobank Schema 19
        
        Args:
            format_type (str): Either 'txt' (tab-separated) or 'xml' (Pseudo-XML)
        """
        logging.info(f"Fetching UK Biobank publications in {format_type} format")
        
        params = {
            'fmt': format_type,
            'id': '19'  # Schema 19 for publications
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            if format_type == 'txt':
                self.publications = self._parse_tab_separated(response.text)
            else:
                self.publications = self._parse_xml(response.text)
            
            return self.publications

        except requests.RequestException as e:
            logging.error(f"Error fetching publications: {str(e)}")
            return []

    def _parse_tab_separated(self, content: str) -> List[Dict]:
        """Parse tab-separated publication data"""
        publications = []
        
        # Create a file-like object from the string content
        f = io.StringIO(content)
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            pub = {
                'publication_id': row.get('publication id (UKB internal)'),
                'title': row.get('title'),
                'keywords': row.get('keywords', '').split(';'),
                'authors': row.get('author(s)', '').split(';'),
                'journal': row.get('journal'),
                'year': row.get('year of publication'),
                'publication_date': row.get('publication date'),
                'abstract': row.get('abstract'),
                'pubmed_id': row.get('PubMed ID'),
                'doi': row.get('DOI'),
                'url': row.get('URL'),
                'total_citations': row.get('Total citations'),
                'recent_citations': row.get('Recent citations (last 2 years)'),
                'citation_update': row.get('When citation counts last updated')
            }
            publications.append(pub)
        
        return publications

    def _parse_xml(self, content: str) -> List[Dict]:
        """Parse Pseudo-XML publication data"""
        publications = []
        root = ET.fromstring(content)
        
        for pub_elem in root.findall('.//publication'):
            pub = {
                'publication_id': pub_elem.findtext('ukb_id'),
                'title': pub_elem.findtext('title'),
                'keywords': [k.strip() for k in pub_elem.findtext('keywords', '').split(';')],
                'authors': [a.strip() for a in pub_elem.findtext('authors', '').split(';')],
                'journal': pub_elem.findtext('journal'),
                'year': pub_elem.findtext('year'),
                'publication_date': pub_elem.findtext('pub_date'),
                'abstract': pub_elem.findtext('abstract'),
                'pubmed_id': pub_elem.findtext('pubmed_id'),
                'doi': pub_elem.findtext('doi'),
                'url': pub_elem.findtext('url'),
                'total_citations': pub_elem.findtext('citations_total'),
                'recent_citations': pub_elem.findtext('citations_recent'),
                'citation_update': pub_elem.findtext('citations_updated')
            }
            publications.append(pub)
        
        return publications

    def save_to_json(self, filename: str = 'ukb_publications.json'):
        """Save publications to JSON file"""
        output_path = Path('data') / filename
        output_path.parent.mkdir(exist_ok=True)
        
        pd.DataFrame(self.publications).to_json(output_path, orient='records', indent=2)
        logging.info(f"Saved {len(self.publications)} publications to {output_path}")

    def save_to_csv(self, filename: str = 'ukb_publications.csv'):
        """Save publications to CSV file"""
        output_path = Path('data') / filename
        
        df = pd.DataFrame(self.publications)
        df.to_csv(output_path, index=False)
        logging.info(f"Saved {len(self.publications)} publications to {output_path}")

    def get_publication_stats(self) -> Dict:
        """Get basic statistics about the publications"""
        df = pd.DataFrame(self.publications)
        
        return {
            'total_publications': len(df),
            'publications_by_year': df['year'].value_counts().to_dict(),
            'top_journals': df['journal'].value_counts().head(10).to_dict(),
            'total_citations': df['total_citations'].sum(),
            'mean_citations': df['total_citations'].mean(),
            'median_citations': df['total_citations'].median()
        }

def main():
    logging.basicConfig(level=logging.INFO)
    parser = UKBPublicationsParser()
    
    # Fetch publications in both formats
    txt_pubs = parser.fetch_publications(format_type='txt')
    parser.save_to_json('ukb_publications_txt.json')
    parser.save_to_csv('ukb_publications_txt.csv')
    
    xml_pubs = parser.fetch_publications(format_type='xml')
    parser.save_to_json('ukb_publications_xml.json')
    
    # Get and print statistics
    stats = parser.get_publication_stats()
    logging.info(f"Publication Statistics: {stats}")

if __name__ == "__main__":
    main()
