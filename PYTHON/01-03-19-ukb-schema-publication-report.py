import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class UKBPublicationAnalyzer:
    def __init__(self, schema_dir='ukb_schemas'):
        self.schema_dir = schema_dir
        self.publications_df = None

    def parse_publications_schema(self):
        """Parse schema 19 (publications) file."""
        try:
            file_path = os.path.join(self.schema_dir, 'schema_19.txt')
            if not os.path.exists(file_path):
                print("Publications schema file not found")
                return None
            
            # Read tab-separated file
            self.publications_df = pd.read_csv(file_path, sep='\t', on_bad_lines='skip')
            
            return self.publications_df
        except Exception as e:
            print(f"Error parsing publications schema: {e}")
            return None

    def analyze_keywords(self):
        """Analyze and visualize keyword statistics."""
        if 'keywords' in self.publications_df.columns:
            # Split keywords into individual terms
            keywords_series = self.publications_df['keywords'].dropna().str.split('|').explode()
            top_keywords = keywords_series.value_counts().head(20)
            
            print("\nTop Keywords:")
            print(top_keywords)
            
            # Visualize top keywords
            plt.figure(figsize=(10, 6))
            top_keywords.sort_values().plot(kind='barh', color='skyblue')
            plt.title("Top 20 Keywords in Publications")
            plt.xlabel("Count")
            plt.ylabel("Keywords")
            plt.tight_layout()
            plt.savefig("top_keywords.png")
            plt.show()
        else:
            print("No 'keywords' column in the dataset.")

    def analyze_authors(self):
        """Analyze and visualize author statistics."""
        if 'authors' in self.publications_df.columns:
            # Split authors into individual names
            authors_series = self.publications_df['authors'].dropna().str.split('|').explode()
            top_authors = authors_series.value_counts().head(20)
            
            print("\nTop Authors:")
            print(top_authors)
            
            # Visualize top authors
            plt.figure(figsize=(10, 6))
            top_authors.sort_values().plot(kind='barh', color='lightgreen')
            plt.title("Top 20 Authors by Number of Publications")
            plt.xlabel("Count")
            plt.ylabel("Authors")
            plt.tight_layout()
            plt.savefig("top_authors.png")
            plt.show()
        else:
            print("No 'authors' column in the dataset.")

    def visualize_year_pub(self):
        """Visualize the number of publications per year."""
        if 'year_pub' in self.publications_df.columns:
            year_counts = self.publications_df['year_pub'].value_counts().sort_index()
            
            print("\nPublications by Year:")
            print(year_counts)
            
            # Visualize publications by year
            plt.figure(figsize=(10, 6))
            year_counts.plot(kind='bar', color='coral')
            plt.title("Number of Publications by Year")
            plt.xlabel("Year")
            plt.ylabel("Number of Publications")
            plt.tight_layout()
            plt.savefig("publications_by_year.png")
            plt.show()
        else:
            print("No 'year_pub' column in the dataset.")

    def visualize_most_cited_articles(self):
        """Visualize the most cited articles with truncated titles and journal names displayed underneath."""
        if {'cite_total', 'title', 'journal'}.issubset(self.publications_df.columns):
            # Extract the top 10 most cited articles
            most_cited = self.publications_df.nlargest(10, 'cite_total')[['pub_id', 'title', 'journal', 'cite_total']]
            
            # Truncate titles to 60 characters
            most_cited['short_title'] = most_cited['title'].apply(lambda x: x[:60] + '...' if len(x) > 60 else x)
            
            # Add journal underneath the truncated titles
            most_cited['title_with_journal'] = most_cited['short_title'] + "\n(" + most_cited['journal'] + ")"
            
            print("\nMost Cited Articles:")
            print(most_cited[['pub_id', 'title_with_journal', 'cite_total']])
            
            # Visualize most cited articles with titles and journals as y-axis
            plt.figure(figsize=(12, 8))
            sns.barplot(data=most_cited, x='cite_total', y='title_with_journal', palette='viridis')
            plt.title("Top 10 Most Cited Articles with Journals")
            plt.xlabel("Total Citations")
            plt.ylabel("Article Title\n(with Journal)")
            plt.tight_layout()
            plt.savefig("most_cited_articles_with_journals_underneath.png")
            plt.show()
        else:
            print("Required columns ('cite_total', 'title', 'journal') are missing in the dataset.")


    def generate_report(self):
        """Generate a comprehensive report."""
        self.parse_publications_schema()
        
        print("\nAnalyzing Keywords...")
        self.analyze_keywords()
        
        print("\nAnalyzing Authors...")
        self.analyze_authors()
        
        print("\nVisualizing Publications by Year...")
        self.visualize_year_pub()
        
        print("\nVisualizing Most Cited Articles...")
        self.visualize_most_cited_articles()

def main():
    analyzer = UKBPublicationAnalyzer(schema_dir='ukb_schemas')
    analyzer.generate_report()

if __name__ == "__main__":
    main()

