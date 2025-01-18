# ukb_analysis/ukb_paper_parser.py

import pandas as pd
from scholarly import scholarly
import json
from datetime import datetime
import re
from collections import defaultdict
import spacy
import time
import random
from pathlib import Path
import logging

class UKBiobankPaperParser:
    def __init__(self, use_cache=True, cache_file='data/ukb_papers_cache.json'):
        """Initialise the parser with caching capabilities"""
        self.papers_data = []
        self.search_terms = [
            "UK Biobank",
            "UKBiobank",
            "U.K. Biobank",
            "United Kingdom Biobank"
        ]
        self.use_cache = use_cache
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def search_papers(self, max_results=100):
        """Search for papers with caching and error handling"""
        if self.use_cache and self.cache_file.exists():
            logging.info("Loading papers from cache...")
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        
        papers = []
        for term in self.search_terms:
            try:
                search_query = scholarly.search_pubs(term)
                for _ in range(max_results // len(self.search_terms)):
                    try:
                        # Add delays to avoid rate limiting
                        time.sleep(random.uniform(1, 3))
                        paper = next(search_query)
                        papers.append(paper)
                    except StopIteration:
                        break
                    except Exception as e:
                        logging.warning(f"Error fetching paper: {str(e)}")
                        continue
            except Exception as e:
                logging.error(f"Error in search term '{term}': {str(e)}")
                continue
        
        # Save to cache if we got any papers
        if papers and self.use_cache:
            with open(self.cache_file, 'w') as f:
                json.dump(papers, f)
        
        # If we couldn't get papers from API or cache, use sample data
        if not papers:
            logging.warning("Using sample data as fallback...")
            papers = self._get_sample_data()
        
        return papers

    def _get_sample_data(self):
        """Return sample paper data for development and testing"""
        return [
            {
                'title': 'Genetic associations with risk of COVID-19 severity in UK Biobank',
                'author': ['A Smith', 'B Jones'],
                'year': 2023,
                'journal': 'Nature Genetics',
                'abstract': 'We investigated genetic variants associated with COVID-19 severity using UK Biobank data. The study included 500,000 participants with genome-wide association analysis revealing significant loci.',
                'citations': 150
            },
            {
                'title': 'Brain imaging and cognitive decline in UK Biobank',
                'author': ['C Wilson', 'D Brown'],
                'year': 2024,
                'journal': 'NeuroImage',
                'abstract': 'Using MRI data from 10,000 UK Biobank participants, we examined associations between brain volume and cognitive decline. Results showed significant correlations.',
                'citations': 75
            }
        ]

    def extract_paper_info(self, paper):
        """Extract relevant information from a paper"""
        return {
            'title': paper.get('title'),
            'authors': paper.get('author'),
            'year': paper.get('year'),
            'journal': paper.get('journal'),
            'citations': paper.get('num_citations'),
            'abstract': paper.get('abstract'),
            'url': paper.get('url'),
            'keywords': self._extract_keywords(paper.get('abstract', '')),
            'ukb_sample_size': self._extract_sample_size(paper.get('abstract', '')),
            'analysis_methods': self._extract_methods(paper.get('abstract', '')),
            'research_questions': self._extract_research_questions(paper.get('abstract', '')),
            'findings': self._extract_key_findings(paper.get('abstract', ''))
        }

    def _extract_keywords(self, text):
        """Extract key biomedical terms from text"""
        if not text:
            return []
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 3]

    def _extract_sample_size(self, text):
        """Extract UK Biobank sample size mentions"""
        if not text:
            return None
        sample_patterns = [
            r'n\s*=\s*(\d{3,6})',
            r'(\d{3,6})\s*participants',
            r'(\d{3,6})\s*individuals'
        ]
        
        for pattern in sample_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return max([int(m) for m in matches])
        return None

    def _extract_methods(self, text):
        """Extract analysis methods used"""
        if not text:
            return []
        method_keywords = [
            'GWAS', 'regression', 'machine learning',
            'deep learning', 'Cox model', 'survival analysis'
        ]
        
        found_methods = []
        for method in method_keywords:
            if method.lower() in text.lower():
                found_methods.append(method)
        return found_methods

    def _extract_research_questions(self, text):
        """Extract research questions using rule-based patterns"""
        if not text:
            return []
        patterns = [
            r"we (investigated|examined|studied|assessed|analyzed|aimed to|sought to).*?(?=\.|$)",
            r"this study (investigated|examined|studied|assessed|analyzed|aimed to|sought to).*?(?=\.|$)",
            r"our (aim|objective|goal) was to.*?(?=\.|$)"
        ]
        
        questions = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            questions.extend([m.group(0) for m in matches])
        return questions

    def _extract_key_findings(self, text):
        """Extract key findings using rule-based patterns"""
        if not text:
            return []
        patterns = [
            r"we found that.*?(?=\.|$)",
            r"results showed.*?(?=\.|$)",
            r"our findings.*?(?=\.|$)",
            r"(significantly|strong(ly)?|robust(ly)?) associated with.*?(?=\.|$)"
        ]
        
        findings = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            findings.extend([m.group(0) for m in matches])
        return findings

    def save_to_json(self, filename):
        """Save parsed papers to JSON file"""
        output_file = Path(filename)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'date_created': datetime.now().isoformat(),
                    'number_of_papers': len(self.papers_data)
                },
                'papers': self.papers_data
            }, f, indent=2)

    def generate_summary_report(self):
        """Generate summary statistics of parsed papers"""
        if not self.papers_data:
            return "No papers analysed yet"
            
        df = pd.DataFrame(self.papers_data)
        
        summary = {
            'total_papers': len(df),
            'papers_by_year': df['year'].value_counts().to_dict() if 'year' in df else {},
            'total_citations': df['citations'].sum() if 'citations' in df else 0,
            'top_journals': df['journal'].value_counts().head(10).to_dict() if 'journal' in df else {},
            'common_methods': self._aggregate_methods(df) if 'analysis_methods' in df else {},
            'median_sample_size': df['ukb_sample_size'].median() if 'ukb_sample_size' in df else None
        }
        
        return summary

    def _aggregate_methods(self, df):
        """Aggregate analysis methods across papers"""
        if 'analysis_methods' not in df:
            return {}
        methods_list = df['analysis_methods'].explode()
        return methods_list.value_counts().to_dict() if not methods_list.empty else {}
