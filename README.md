# FX Event Risk Analysis

A Streamlit web application that analyzes event risks for currency pairs using AI. This app categorizes risks into different dimensions like Central Bank risk, Economic risk, Geopolitical risk, etc., and assigns sentiment levels to help traders make informed decisions.

## Features

- Analyze event risks for any currency pair
- Categorize risks into 8 different dimensions
- Provide sentiment analysis (High, Medium, Low)
- Color-coded risk assessment
- Light and Dark theme modes

## Setup Instructions

1. Clone this repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API key:
```
API_KEY=your_perplexity_api_key_here
```

4. Run the Streamlit app:
```
streamlit run FX_Event_Risk_Tab.py
```

## How to Use

1. Enter your currency pair (e.g., USDCHF, EURUSD)
2. Select the trade direction (BUY or SELL)
3. Set the tenor length in days
4. Enter your current trade P&L percentage
5. Click "Analyze Event Risks"

The app will display:
- A comprehensive table of all risk dimensions with summaries
- A filtered view showing only dimensions with non-N/A sentiment
- Color-coded risk indicators (🔴 High, 🔵 Medium, 🟢 Low)

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- OpenAI Python client
- python-dotenv

## Notes

This app uses the Perplexity AI API (via OpenAI client) to analyze currency risks. You'll need a valid API key from Perplexity to use this application. 