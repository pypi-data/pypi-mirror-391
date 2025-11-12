# FinSense Analyzer: Financial Sentiment Tool

**FinSense** is a lightweight Python package specialized for analyzing sentiment in financial text. It uses a custom, finance-tuned lexicon to overcome the limitations of general-purpose sentiment tools when dealing with market jargon and financial concepts.

## Installation

```bash
pip install finsense-analyzer
from finsense import FinSenseAnalyzer

# 1. Initialize the analyzer
analyzer = FinSenseAnalyzer()

# 2. Define test sentences
text_positive = "The stock rallied strongly today on excellent profits."
text_negative = "Q4 earnings missed estimates, causing large losses."
text_negation = "The team did not see major losses this quarter."

# 3. Analyze and print results
print("--- Analysis Results ---")
print(f"Positive Score: {analyzer.analyze_sentiment(text_positive)['polarity']:.4f}")
print(f"Negative Score: {analyzer.analyze_sentiment(text_negative)['polarity']:.4f}")
print(f"Negation Score: {analyzer.analyze_sentiment(text_negation)['polarity']:.4f}")