# ukb_analysis/disease_contributions_analyzer.py

import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Any
import logging
import spacy
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go

class DiseaseContributionsAnalyzer:
    def __init__(self, publications: List[Dict]):
        self.publications = publications
        self.nlp = spacy.load("en_core_web_sm")
        
        # Major disease categories and their keywords
        self.disease_categories = {
            'cardiovascular': [
                'cardiovascular disease', 'heart disease', 'stroke', 
                'hypertension', 'atherosclerosis', 'arrhythmia',
                'coronary artery disease', 'heart failure'
            ],
            'cancer': [
                'cancer', 'tumour', 'carcinoma', 'neoplasm', 'lymphoma',
                'leukemia', 'melanoma', 'oncology', 'metastasis'
            ],
            'neurodegenerative': [
                'alzheimer', 'parkinson', 'dementia', 'neurodegeneration',
                'cognitive decline', 'brain aging', 'neurological'
            ],
            'metabolic': [
                'diabetes', 'obesity', 'metabolic syndrome', 
                'thyroid disease', 'insulin resistance'
            ],
            'psychiatric': [
                'depression', 'anxiety', 'mental health', 'schizophrenia',
                'bipolar disorder', 'psychiatric illness'
            ],
            'respiratory': [
                'asthma', 'copd', 'lung disease', 'respiratory disease',
                'pulmonary disease', 'covid-19', 'pneumonia'
            ]
        }

    def analyze_disease_contributions(self) -> Dict[str, List[Dict]]:
        """Analyze contributions to each disease area"""
        contributions = defaultdict(list)
        
        for pub in self.publications:
            text = f"{pub.get('title', '')} {pub.get('abstract', '')}"
            
            # Safely handle citations
            try:
                citations = int(float(pub.get('total_citations', 0)))
            except (TypeError, ValueError):
                citations = 0
            
            # Check each disease category
            for category, keywords in self.disease_categories.items():
                if self._text_contains_keywords(text.lower(), keywords):
                    findings = self._extract_key_findings(text)
                    if findings:
                        contribution = {
                            'title': pub.get('title', ''),
                            'year': pub.get('year', 'Unknown'),
                            'journal': pub.get('journal', ''),
                            'citations': citations,
                            'findings': findings,
                            'doi': pub.get('doi', ''),
                            'pubmed_id': pub.get('pubmed_id', ''),
                            'impact_score': self._calculate_impact_score(text, citations)
                        }
                        contributions[category].append(contribution)
        
        # Sort contributions by impact score
        for category in contributions:
            contributions[category].sort(key=lambda x: x['impact_score'], reverse=True)
        
        return dict(contributions)

    def _text_contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords"""
        return any(keyword.lower() in text for keyword in keywords)

    def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from text using NLP"""
        findings = []
        doc = self.nlp(text)
        
        # Look for sentences containing specific findings patterns
        finding_patterns = [
            r"we (found|identified|discovered|observed|showed)",
            r"results (showed|demonstrated|indicated|revealed)",
            r"significant(ly)? associated",
            r"strong(ly)? correlated",
            r"key finding",
            r"novel (finding|discovery|association)"
        ]
        
        for sent in doc.sents:
            if any(re.search(pattern, sent.text, re.IGNORECASE) for pattern in finding_patterns):
                findings.append(sent.text.strip())
        
        return findings

    def _calculate_impact_score(self, text: str, citations: int) -> float:
        """Calculate impact score based on findings and citations"""
        try:
            # Base score from citations (handle potential errors)
            citation_score = np.log1p(float(citations)) / 10 if citations is not None else 0
            
            # Impact phrase score
            impact_phrases = [
                'first', 'novel', 'breakthrough', 'significant', 'important',
                'major advance', 'key finding', 'innovative'
            ]
            impact_count = sum(1 for phrase in impact_phrases 
                             if phrase in text.lower())
            impact_score = impact_count / len(impact_phrases)
            
            return float(citation_score + impact_score)
        except:
            return 0.0

    def generate_contribution_report(self) -> str:
        """Generate a detailed report of disease contributions"""
        contributions = self.analyze_disease_contributions()
        
        report = ["# UK Biobank Major Disease Contributions\n"]
        
        for category, papers in contributions.items():
            if not papers:  # Skip empty categories
                continue
                
            report.append(f"\n## {category.title()} Disease\n")
            
            # Key statistics
            total_papers = len(papers)
            total_citations = sum(paper['citations'] for paper in papers)
            avg_impact = np.mean([paper['impact_score'] for paper in papers])
            
            report.append(f"### Overview")
            report.append(f"- Total Publications: {total_papers}")
            report.append(f"- Total Citations: {total_citations}")
            report.append(f"- Average Impact Score: {avg_impact:.2f}\n")
            
            # Top contributions
            report.append(f"### Key Contributions")
            for i, paper in enumerate(papers[:5], 1):  # Top 5 papers by impact score
                report.append(f"\n#### {i}. {paper['title']}")
                report.append(f"- Year: {paper['year']}")
                report.append(f"- Journal: {paper['journal']}")
                report.append(f"- Citations: {paper['citations']}")
                report.append("\nKey Findings:")
                for finding in paper['findings']:
                    report.append(f"- {finding}")
                if paper['doi']:
                    report.append(f"\nDOI: {paper['doi']}")
                report.append("")
        
        return '\n'.join(report)

    def create_visualizations(self):
        """Create visualizations of disease contributions"""
        contributions = self.analyze_disease_contributions()
        
        # 1. Disease category distribution
        category_stats = {
            cat: len(papers) for cat, papers in contributions.items()
        }
        
        fig_dist = px.bar(
            x=list(category_stats.keys()),
            y=list(category_stats.values()),
            title='Publications by Disease Category',
            labels={'x': 'Disease Category', 'y': 'Number of Publications'}
        )
        
        # 2. Impact scores over time
        time_data = []
        for category, papers in contributions.items():
            for paper in papers:
                time_data.append({
                    'category': category,
                    'year': paper['year'],
                    'impact_score': paper['impact_score']
                })
        
        df_time = pd.DataFrame(time_data)
        fig_impact = px.line(
            df_time,
            x='year',
            y='impact_score',
            color='category',
            title='Research Impact Over Time by Disease Category'
        )
        
        return {
            'category_distribution': fig_dist,
            'impact_trends': fig_impact
        }
