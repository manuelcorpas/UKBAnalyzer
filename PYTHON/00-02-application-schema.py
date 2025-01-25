import os
import pandas as pd
import xml.etree.ElementTree as ET
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re

class UKBioschemaAnalyzer:
    def __init__(self, schema_dir='ukb_schemas'):
        self.schema_dir = schema_dir
        self.applications_df = None
        
    def parse_txt_schema(self, file_path):
        """Parse a tab-separated schema file"""
        try:
            # Read tab-separated file
            df = pd.read_csv(file_path, sep='\t')
            return df
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def parse_schemas(self):
        """Parse all schema files in the directory"""
        all_data = []
        
        # Parse each file in the schemas directory
        for filename in os.listdir(self.schema_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.schema_dir, filename)
                schema_num = re.search(r'schema_(\d+)', filename).group(1)
                
                df = self.parse_txt_schema(file_path)
                if df is not None:
                    df['schema_number'] = schema_num
                    all_data.append(df)
        
        # Combine all data
        if all_data:
            self.applications_df = pd.concat(all_data, ignore_index=True)
            return self.applications_df
        else:
            print("No data found in schema files")
            return None

    def analyze_applications(self):
        """Analyze application data (Schema 27)"""
        app_schema = None
        for filename in os.listdir(self.schema_dir):
            if filename == 'schema_27.txt':
                app_schema = self.parse_txt_schema(os.path.join(self.schema_dir, filename))
                break
        
        if app_schema is not None:
            print("\nApplication Analysis:")
            print(f"Total number of applications: {len(app_schema)}")
            
            # Analyze institutions
            print("\nTop 10 institutions by number of applications:")
            print(app_schema['institution'].value_counts().head(10))
            
            # Plot institutions
            plt.figure(figsize=(12, 6))
            app_schema['institution'].value_counts().head(10).plot(kind='bar')
            plt.title('Top 10 Institutions by Number of Applications')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('top_institutions.png')
            plt.close()
            
            # Save detailed application data
            app_schema.to_csv('application_analysis.csv', index=False)
            return app_schema
        else:
            print("Application schema (27) not found")
            return None

    def generate_report(self):
        """Generate a comprehensive report of the analysis"""
        if self.applications_df is None:
            self.parse_schemas()
        
        report = ["UK Biobank Schema Analysis Report", "=" * 30 + "\n"]
        
        # Analyze applications
        app_data = self.analyze_applications()
        if app_data is not None:
            report.append(f"Total Applications Analyzed: {len(app_data)}")
            
            # Institution summary
            inst_counts = app_data['institution'].value_counts()
            report.append("\nTop 10 Institutions:")
            report.append(inst_counts.head(10).to_string())
            
            # Save report
            with open('ukb_schema_analysis_report.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            print("Report generated: ukb_schema_analysis_report.txt")
            print("Detailed application data saved: application_analysis.csv")
            print("Institution visualization saved: top_institutions.png")

def main():
    analyzer = UKBioschemaAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
