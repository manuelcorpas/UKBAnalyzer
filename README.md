# UKBAnalyzer

## Overview
UKBAnalyzer is a comprehensive Python application for analyzing UK Biobank publications, research fields, and data usage patterns.

## Features
- Fetch and parse UK Biobank publications
- Analyze research field contributions
- Generate detailed reports
- Create interactive visualizations of research trends

## Prerequisites
- Python 3.8+
- pip
- spacy

## Installation

### Clone the Repository
```bash
git clone https://github.com/manuelcorpas1/UKBAnalyzer.git
cd UKBAnalyzer
```

### Create Virtual Environment
```bash
python3 -m venv ukb_env
source ukb_env/bin/activate  # On Windows use `ukb_env\Scripts\activate`
```

### Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage
```bash 
python main.py
```

## Project Structure
```
UKBAnalyzer/
│
├── main.py                     # Main pipeline script
├── requirements.txt            # Project dependencies
│
├── ukb_analysis/               # Core analysis modules
│   ├── __init__.py
│   ├── ukb_publications_parser.py
│   ├── showcase_scraper.py
│   ├── disease_contributions_analyzer.py
│   └── integrated_analyzer.py
│
├── data/                       # Data storage (gitignored)
├── outputs/                    # Analysis outputs (gitignored)
└── visualizations/             # Generated visualizations (gitignored)
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
[Manuel Corpas](https://manuelcorpas.com)

Project Link: [https://github.com/manuelcorpas1/UKBAnalyzer](https://github.com/manuelcorpas1/UKBAnalyzer)

