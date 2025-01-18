from setuptools import setup, find_packages

setup(
    name="ukb_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        'scholarly>=1.7.0',
        'spacy>=3.5.0',
        'scikit-learn>=1.0.0',
        'plotly>=5.13.0',
        'networkx>=2.8.0',
        'python-dotenv>=0.21.0'
    ],
    python_requires='>=3.8',
)
