# main.py

import logging
from pathlib import Path
import json
import pandas as pd
from ukb_analysis.ukb_publications_parser import UKBPublicationsParser
from ukb_analysis.showcase_scraper import UKBShowcaseScraper
from ukb_analysis.disease_contributions_analyzer import DiseaseContributionsAnalyzer
from ukb_analysis.integrated_analyzer import IntegratedAnalyzer

class UKBiobankAnalysisPipeline:
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ukb_analysis.log'),
                logging.StreamHandler()
            ]
        )

    def setup_directories(self):
        """Create necessary directories"""
        self.dirs = {
            'data': Path('data'),
            'outputs': Path('outputs'),
            'visualizations': Path('visualizations')
        }
        
        for directory in self.dirs.values():
            directory.mkdir(exist_ok=True)

    def fetch_publications(self):
        """Fetch and parse UK Biobank publications"""
        logging.info("Fetching UK Biobank publications...")
        pub_parser = UKBPublicationsParser()
        
        # Try to fetch publications in tab-separated format
        publications = pub_parser.fetch_publications(format_type='txt')
        
        if not publications:
            logging.warning("Failed to fetch tab-separated format, trying XML...")
            publications = pub_parser.fetch_publications(format_type='xml')
        
        if publications:
            # Save publications in multiple formats
            pub_parser.save_to_json()
            pub_parser.save_to_csv()
            
            # Get and log basic statistics
            stats = pub_parser.get_publication_stats()
            logging.info(f"Publication Statistics: {stats}")
            
            # Save statistics
            with open(self.dirs['outputs'] / 'publication_stats.json', 'w') as f:
                json.dump(stats, f, indent=2)
        
        return publications

    def fetch_showcase_data(self):
        """Fetch UK Biobank showcase data"""
        logging.info("Fetching UK Biobank showcase data...")
        scraper = UKBShowcaseScraper()
        showcase_data = scraper.fetch_categories()
        
        if showcase_data:
            scraper.save_categories()
            scraper.save_as_csv()
        
        return showcase_data

    def analyze_disease_contributions(self, publications):
        """Analyze disease-specific contributions"""
        logging.info("Analyzing disease contributions...")
        disease_analyzer = DiseaseContributionsAnalyzer(publications)
    
        # Generate comprehensive report
        report = disease_analyzer.generate_contribution_report()
        report_path = self.dirs['outputs'] / 'disease_contributions_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
    
        # Generate visualizations (fixed method name)
        visualizations = disease_analyzer.create_visualizations()
        for name, fig in visualizations.items():
            viz_path = self.dirs['visualizations'] / f'disease_{name}.html'
            fig.write_html(str(viz_path))
    
        logging.info("Disease contribution analysis completed")
    def perform_integrated_analysis(self, publications, showcase_data):
        """Perform integrated analysis of publications and showcase data"""
        logging.info("Performing integrated analysis...")
        analyzer = IntegratedAnalyzer(showcase_data, publications)
        
        # Generate reports
        reports = analyzer.generate_reports()
        for name, report in reports.items():
            report_path = self.dirs['outputs'] / f'{name}_report.md'
            with open(report_path, 'w') as f:
                f.write(report)
        
        # Generate visualizations
        visualizations = analyzer.create_visualizations()
        for name, fig in visualizations.items():
            viz_path = self.dirs['visualizations'] / f'{name}.html'
            fig.write_html(str(viz_path))

    def run_pipeline(self):
        """Run the complete analysis pipeline"""
        try:
            # Step 1: Fetch publications
            publications = self.fetch_publications()
            if not publications:
                raise ValueError("Failed to fetch publications")

            # Step 2: Fetch showcase data
            showcase_data = self.fetch_showcase_data()
            if not showcase_data:
                raise ValueError("Failed to fetch showcase data")

            # Step 3: Analyze disease contributions
            self.analyze_disease_contributions(publications)

            # Step 4: Perform integrated analysis
            self.perform_integrated_analysis(publications, showcase_data)

            logging.info("Analysis pipeline completed successfully!")
            logging.info(f"Outputs can be found in:")
            logging.info(f"- Reports: {self.dirs['outputs']}")
            logging.info(f"- Visualizations: {self.dirs['visualizations']}")

        except Exception as e:
            logging.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise

def main():
    pipeline = UKBiobankAnalysisPipeline()
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()
