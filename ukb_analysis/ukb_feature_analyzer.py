# ukb_analysis/ukb_feature_analyzer.py

import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import re
from typing import List, Dict, Any

class UKBiobankFeatureAnalyzer:
    def __init__(self, papers_data: List[Dict]):
        self.papers_data = papers_data
        self.feature_categories = {
            'genetic': [
                r'(SNP|variant|allele|gene|locus|genomic|genetic)',
                r'(GWAS|polygenic|heritability|QTL)'
            ],
            'imaging': [
                r'(MRI|imaging|brain volume|white matter|grey matter)',
                r'(cardiac|liver|scanning|radiological|image)'
            ],
            'lifestyle': [
                r'(diet|exercise|smoking|alcohol|physical activity)',
                r'(sleep|nutrition|BMI|obesity|lifestyle)'
            ],
            'biomarkers': [
                r'(cholesterol|triglycerides|blood pressure|glucose)',
                r'(biomarker|protein|metabolite|hormone)'
            ],
            'environmental': [
                r'(pollution|air quality|socioeconomic|education)',
                r'(income|occupation|environmental|exposure)'
            ],
            'clinical': [
                r'(medication|treatment|diagnosis|symptoms)',
                r'(comorbidity|disease history|clinical)'
            ]
        }

    def create_feature_disease_visualizations(self):
        """Create visualizations of feature-disease relationships"""
        relationships = self._extract_feature_disease_relationships()
        
        # Create network graph
        G = nx.Graph()
        edge_weights = defaultdict(int)
        
        # Add nodes and edges
        for disease in relationships:
            G.add_node(disease, node_type='disease')
            for category in relationships[disease]:
                for rel in relationships[disease][category]:
                    feature = rel['feature']
                    G.add_node(feature, node_type='feature')
                    edge_weights[(disease, feature)] += 1
        
        # Add edges with weights
        for (disease, feature), weight in edge_weights.items():
            G.add_edge(disease, feature, weight=weight)
        
        # Create network visualization
        pos = nx.spring_layout(G)
        
        edge_trace = go.Scatter(
            x=[], y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        node_trace = go.Scatter(
            x=[], y=[],
            mode='markers+text',
            hoverinfo='text',
            text=[],
            marker=dict(
                color=[],
                size=10,
                line_width=2))
        
        # Add edge positions
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)
        
        # Add node positions
        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            node_trace['text'] += (node,)
            node_trace['marker']['color'] += ('red' if G.nodes[node]['node_type'] == 'disease' else 'blue',)
        
        # Create figure
        network_fig = go.Figure(data=[edge_trace, node_trace],
                              layout=go.Layout(
                                  title='Disease-Feature Network',
                                  showlegend=False,
                                  hovermode='closest',
                                  margin=dict(b=20,l=5,r=5,t=40),
                                  xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                  yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                              )
        
        # Create heatmap
        heatmap_data = defaultdict(lambda: defaultdict(int))
        for disease in relationships:
            for category in relationships[disease]:
                heatmap_data[disease][category] = len(relationships[disease][category])
        
        df_heatmap = pd.DataFrame(heatmap_data).fillna(0)
        
        heatmap_fig = px.imshow(df_heatmap,
                               title='Feature Categories vs Diseases Heatmap',
                               labels=dict(x='Disease', y='Feature Category'),
                               color_continuous_scale='Viridis')
        
        return {
            'network': network_fig,
            'heatmap': heatmap_fig
        }

    def _extract_feature_disease_relationships(self) -> Dict[str, Any]:
        """Extract relationships between features and diseases from papers"""
        relationships = defaultdict(lambda: defaultdict(list))
        
        for paper in self.papers_data:
            abstract = paper.get('abstract', '').lower()
            findings = ' '.join(paper.get('findings', [])).lower()
            text = abstract + ' ' + findings
            
            diseases = self._extract_diseases(text)
            
            for disease in diseases:
                for category, patterns in self.feature_categories.items():
                    features = self._extract_features(text, patterns)
                    
                    for feature in features:
                        sentences = self._split_into_sentences(text)
                        for sentence in sentences:
                            if disease in sentence and feature in sentence:
                                relationship = {
                                    'feature': feature,
                                    'category': category,
                                    'sentence': sentence,
                                    'paper_title': paper.get('title'),
                                    'year': paper.get('year')
                                }
                                relationships[disease][category].append(relationship)
        
        return relationships

    def _extract_diseases(self, text: str) -> List[str]:
        """Extract disease mentions from text"""
        disease_patterns = [
            r'(cancer|carcinoma|tumor|neoplasm)',
            r'(diabetes|metabolic syndrome)',
            r'(cardiovascular|heart disease|stroke)',
            r'(alzheimer|dementia|parkinson)',
            r'(depression|anxiety|psychiatric)',
            r'(obesity|hypertension|arthritis)'
        ]
        
        diseases = []
        for pattern in disease_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            diseases.extend([m.group(0).lower() for m in matches])
        
        return list(set(diseases))

    def _extract_features(self, text: str, patterns: List[str]) -> List[str]:
        """Extract features based on category patterns"""
        features = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            features.extend([m.group(0).lower() for m in matches])
        
        return list(set(features))

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
