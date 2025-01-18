# ukb_analysis/integrated_analyzer.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import re
from typing import Dict, List, Any
import logging
import spacy
from pathlib import Path

class IntegratedAnalyzer:
    def __init__(self, showcase_data: Dict, publications: List[Dict]):
        self.showcase_data = showcase_data
        self.publications = publications
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("SpaCy English model not found. NLP features will be limited.")
            self.nlp = None
        
        # Create field mappings from showcase data
        self.field_mappings = self._create_field_mappings()
        
        # Track field usage
        self.field_usage = self._analyze_field_usage()
    
    def _create_field_mappings(self) -> Dict:
        """Create mappings of field IDs to their metadata"""
        mappings = {}
        for cat_id, cat_data in self.showcase_data.items():
            for subcat_id, subcat_data in cat_data['subcategories'].items():
                for field in subcat_data['fields']:
                    mappings[field['field_id']] = {
                        'name': field['name'],
                        'type': field['type'],
                        'category': cat_data['name'],
                        'subcategory': subcat_data['name']
                    }
        return mappings

    def _analyze_field_usage(self) -> Dict:
        """Analyze how UK Biobank fields are used in publications"""
        field_usage = defaultdict(lambda: {
            'mentions': 0,
            'papers': set(),
            'contexts': [],
            'years': set()
        })
        
        # Regular expression for field IDs (e.g., "1234-0.0")
        field_pattern = r'\b\d+-\d+\.\d+\b'
        
        for pub in self.publications:
            text = f"{pub.get('title', '')} {pub.get('abstract', '')}"
            year = pub.get('year')
            
            # Find all field IDs mentioned in the text
            found_fields = re.findall(field_pattern, text)
            
            # Update usage statistics for each field
            for field_id in found_fields:
                if field_id in self.field_mappings:
                    field_usage[field_id]['mentions'] += 1
                    field_usage[field_id]['papers'].add(pub.get('title'))
                    field_usage[field_id]['years'].add(year)
                    
                    # Store context if NLP is available
                    if self.nlp:
                        sentences = self._get_field_context(text, field_id)
                        field_usage[field_id]['contexts'].extend(sentences)
        
        return field_usage

    def _get_field_context(self, text: str, field_id: str) -> List[str]:
        """Extract sentences containing field references"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        relevant_sentences = []
        
        for sent in doc.sents:
            if field_id in sent.text:
                relevant_sentences.append(sent.text.strip())
        
        return relevant_sentences

    def generate_reports(self) -> Dict[str, str]:
        """Generate detailed reports about data usage"""
        reports = {}
        
        # Generate category usage report
        category_coverage = self.analyze_category_coverage()
        category_report = ["# UK Biobank Data Category Usage Report\n"]
        
        for category, stats in category_coverage.items():
            category_report.append(f"\n## {category}")
            category_report.append(f"- Total Fields: {stats['total_fields']}")
            category_report.append(f"- Fields Used in Research: {stats['used_fields']}")
            category_report.append(f"- Total Mentions: {stats['total_mentions']}")
            category_report.append(f"- Number of Papers: {len(stats['papers'])}")
            
            # Add most used fields in this category
            category_fields = [
                (field_id, self.field_usage[field_id])
                for field_id, metadata in self.field_mappings.items()
                if metadata['category'] == category and field_id in self.field_usage
            ]
            
            if category_fields:
                category_report.append("\n### Most Used Fields:")
                sorted_fields = sorted(category_fields, 
                                    key=lambda x: x[1]['mentions'],
                                    reverse=True)[:5]
                
                for field_id, usage in sorted_fields:
                    metadata = self.field_mappings[field_id]
                    category_report.append(f"\n#### {metadata['name']} (Field {field_id})")
                    category_report.append(f"- Mentions: {usage['mentions']}")
                    category_report.append(f"- Papers: {len(usage['papers'])}")
                    if usage['contexts']:
                        category_report.append("\nExample Usage Context:")
                        category_report.append(f"  {usage['contexts'][0]}")
        
        reports['category_usage'] = '\n'.join(category_report)
        
        return reports

    def create_visualizations(self):
        """Create visualizations of data usage patterns"""
        visualizations = {}
        
        # 1. Category Coverage Heatmap
        category_coverage = self.analyze_category_coverage()
        coverage_data = pd.DataFrame([{
            'category': cat,
            'total_fields': data['total_fields'],
            'used_fields': data['used_fields'],
            'usage_percentage': (data['used_fields'] / data['total_fields'] * 100) if data['total_fields'] > 0 else 0
        } for cat, data in category_coverage.items()])
        
        visualizations['category_coverage'] = px.imshow(
            coverage_data.pivot(columns='category', values='usage_percentage'),
            title='UK Biobank Data Category Usage',
            labels={'value': 'Usage Percentage (%)'}
        )
        
        # 2. Publication Trends Over Time
        # Extract years from publications
        years = [pub.get('year') for pub in self.publications if pub.get('year') is not None]
        publications_by_year = pd.DataFrame({'year': years}).groupby('year').size().reset_index(name='publication_count')
        
        visualizations['usage_over_time'] = px.line(
            publications_by_year,
            x='year', 
            y='publication_count',
            title='UK Biobank Publications Over Time',
            labels={'publication_count': 'Number of Publications', 'year': 'Year'}
        )
        
        # 3. Top Journals Visualization
        journal_counts = {}
        for pub in self.publications:
            journal = pub.get('journal', 'Unknown')
            journal_counts[journal] = journal_counts.get(journal, 0) + 1
        
        journal_df = pd.DataFrame.from_dict(journal_counts, orient='index', columns=['publication_count']).reset_index()
        journal_df.columns = ['journal', 'publication_count']
        journal_df = journal_df.sort_values('publication_count', ascending=False).head(10)
        
        visualizations['top_journals'] = px.bar(
            journal_df, 
            x='journal', 
            y='publication_count',
            title='Top 10 Journals Publishing UK Biobank Research',
            labels={'publication_count': 'Number of Publications', 'journal': 'Journal'}
        )
        
        return visualizations

    def analyze_category_coverage(self) -> Dict:
        """Analyze which categories of UK Biobank data are most studied"""
        category_coverage = defaultdict(lambda: {
            'total_fields': 0,
            'used_fields': 0,
            'total_mentions': 0,
            'papers': set()
        })
        
        # Count total fields per category
        for field_id, metadata in self.field_mappings.items():
            category = metadata['category']
            category_coverage[category]['total_fields'] += 1
            
            # Add usage statistics if the field is used
            if field_id in self.field_usage:
                usage = self.field_usage[field_id]
                category_coverage[category]['used_fields'] += 1
                category_coverage[category]['total_mentions'] += usage['mentions']
                category_coverage[category]['papers'].update(usage['papers'])
        
        return category_coverage
