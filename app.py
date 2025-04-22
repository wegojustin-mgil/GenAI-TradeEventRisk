import streamlit as st
import pandas as pd
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

API_KEY = os.getenv("PERPLEXITY_API_KEY")

if not API_KEY:
    st.error("No API key found. Please set 'API_KEY' in your environment or .env file.")
    st.stop()
# Initialize OpenAI client
client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai/")
# Page config
st.set_page_config(
    page_title="FX Trade Event Risk Warning",
    page_icon="📈",
    layout="wide",
)
# CSS styling enhancement
st.markdown("""
    <style>
      /* Color palette */
      :root {
        --primary-color: #3b82f6;       /* blue-500 */
        --secondary-color: #10b981;     /* green-500 */
        --text-color: #111827;          /* gray-900 */
        --bg-light: #f9fafb;            /* gray-50 */
        --bg-container: #ffffff;        /* white */
        --border-radius: 12px;
        --transition: 0.2s ease;
      }

      /* Base font */
      html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: var(--bg-light);
        color: var(--text-color);
      }

      /* App background and main container */
      .stApp {
        background-color: var(--bg-light) !important;
      }
      .block-container {
        background-color: var(--bg-container);
        border-radius: var(--border-radius);
        padding: 2.5rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        color: var(--text-color);
      }

      /* Top banner */
      .top-banner {
        background-color: var(--primary-color);
        color: white;
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }

      /* Sidebar styling */
      .stSidebar {
        background-color: var(--bg-container);
        padding: 1.5rem 1rem;
        border-radius: var(--border-radius);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      }
      .stSidebar h2 {
        color: var(--primary-color);
        font-size: 1.5rem;
        margin-bottom: 1rem;
      }

      /* Headings */
      h1, h2, h3 {
        color: var(--primary-color);
        margin-top: 1.5rem;
      }

  /* Buttons */
  div.stButton > button {
  background-color: var(--primary-color) !important;
  color: #ffffff !important;
  border-radius: var(--border-radius) !important;
  padding: 0.75rem 1.5rem !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  border: none !important;
  transition: transform var(--transition), box-shadow var(--transition);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

div.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
}

      /* Inputs */
      input, textarea, select {
        background-color: var(--bg-container) !important;
        color: var(--text-color) !important;
        border-radius: 8px;
        border: 1px solid #e5e7eb !important;
        padding: 0.75rem !important;
      }
    </style>

    <div class="top-banner">
      FX Event Risk Analysis
    </div>
""", unsafe_allow_html=True)



gpt_model = "gpt-4.1"

def get_summary_and_sentiment(content: str, currency: str) -> (str, int):
    try:
        messages = [
    {
        "role": "system",
        "content": (
            f"You are a highly analytical financial expert specializing in currency market analysis. "
            f"Your primary role is to provide concise yet insightful summaries of risk assessments for currency pairs. "
            f"Additionally, you must assign an accurate and nuanced sentiment score (1-5) to the {currency} currency pair based on the provided risk assessment.\n\n"
            f"Sentiment Score Scale:\n"
            f"1 - Very Bearish (strong negative outlook)\n"
            f"2 - Bearish (negative outlook)\n"
            f"3 - Neutral (balanced outlook, no clear direction)\n"
            f"4 - Bullish (positive outlook)\n"
            f"5 - Very Bullish (strong positive outlook)\n\n"
            f"Consider economic indicators, geopolitical events, market sentiment, technical analysis, and recent news developments in your summary. "
            f"Clearly explain the rationale behind your sentiment score."
        )
    },
    {
        "role": "user",
        "content": (
            f"Please analyze and summarize the following detailed risk assessment report, then assign and justify a sentiment score (1-5) for {currency}:\n\n"
            f"{content}"
        )
    }
]
        response = client.chat.completions.create(model="gpt-4.1", messages=messages)
        summary = response.choices[0].message.content.strip()
        sentiment_match = re.search(r"(\d)", summary)
        sentiment_score = int(sentiment_match.group(1)) if sentiment_match else 3
        return summary, sentiment_score
    except Exception as e:
        st.error(f"Error generating summary and sentiment: {e}")
        return "Error generating summary.", 3

@st.cache_data(show_spinner=False)
def fetch_and_categorize_event_risks(currency_pair, direction, tenor):
    guidelines = """
    1. Central Bank Risk: Monetary policy announcements, Interest rate decisions, Speeches, Quantitative easing/tightening
    2. Economic Risk: Employment, GDP, CPI, PPI, Fiscal policy, Trade balance, Debt levels, Market volatility
    3. Geopolitical Risk: Conflicts, Political instability, Trade tensions, Diplomatic disputes, International agreements
    4. Liquidity Risk: Market depth, Bid-ask spreads, Participant exits, Liquidity crises
    5. Regulatory Risk: Capital controls, Regulatory interventions, Financial reforms
    6. Sentiment and Market Positioning Risk: Extreme positioning, Sentiment shifts, Herd behavior
    7. Credit Risk: Sovereign default, Banking sector vulnerability, Credit ratings
    The most important guidelines is that if no specific information is available, assign N/A in Risk Sentiment.
    """
    extraction_prompt = f"""
    For the currency pair {currency_pair}, extract current event risks from the internet. Categorize risks according to:
    {guidelines}

    Provide a detailed explanation (explanation per category, summarizing major events), assign a risk sentiment for {currency_pair}:
    - High: Highly unpredictable and significant uncertainities around {currency_pair}
    - Alerted: Elevated uncertainties with potential volatility requiring close monitoring for {currency_pair}
    - Medium: somewhat unpredictable and medium uncertainities for {currency_pair}
    - Low: relatively predictable and low uncertainties for {currency_pair}
    - If no specific information is available for a particular category, assign "N/A" in Risk Sentiment. 

    Return results in a structured table:

    | Risk Dimension | Brief Summary | Risk Sentiment |
    |----------------|---------------|----------------|
    """
    messages = [
        {"role": "system", "content": 
            "You are an expert financial analyst AI specialized in extracting structured, accurate, and detailed event risk data "
            "from current and highly credible internet sources. Your analysis should emphasize accuracy, clarity, and actionable insights. "
            "Ensure all extracted information is verifiable and derived exclusively from reputable financial sources such as "
            "Bloomberg, Reuters, Financial Times, CNBC, central banks, government reports, or recognized financial institutions."
            },
        {"role": "user", "content": extraction_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=messages,
            temperature=0.2
        )

        extracted_content = response.choices[0].message.content.strip()
        # Convert extracted markdown table to DataFrame
        rows = extracted_content.split('\n')
        # Filter out separator rows containing only dashes or header rows
        table_data = [row.split('|')[1:-1] for row in rows 
              if '|' in row and '---' not in row and 'Risk Dimension' not in row]

        df = pd.DataFrame(table_data, columns=["Risk Dimension", "Brief Summary", "Risk Sentiment"]).applymap(lambda x: x.strip())

        return df

    except Exception as e:
        print(f"Error fetching or categorizing event risks: {e}")
        return pd.DataFrame()
# Main app
st.title("FX Trade Event Risk Warning")
# Tab 1 content
currency_pair = st.text_input("Currency Pair (e.g., EURUSD):", "USDCHF")
direction = st.selectbox("Trade Direction:", ["BUY", "SELL"])
tenor = st.number_input("Tenor (Days):", min_value=1, max_value=90, value=10)
trade_pnl = st.number_input("Current Trade P&L (%):", -100.0, 100.0, 0.0, 0.1)

if st.button("Analyze Event Risks"):
    event_risks = fetch_and_categorize_event_risks(currency_pair, direction, tenor)
    st.session_state['event_risks'] = event_risks
    if not event_risks.empty:
        st.table(event_risks)
    else:
        st.warning("No event risks found.")
    
    if not event_risks.empty:
        st.subheader("🎯 Filtered Risk Dimensions (with Sentiment)")
        # Filter out rows with 'N/A' sentiment
        filtered_df = event_risks[event_risks['Risk Sentiment'] != 'N/A'][["Risk Dimension", "Risk Sentiment"]].reset_index(drop=True)

        # Define color mapping based on sentiment
        def sentiment_color(sentiment):
                colors = {'High': '🔴 Red', 'Alerted': '🟠 Orange', 'Medium': '🔵 Blue', 'Low': '🟢 Green'}
                return colors.get(sentiment, '⚪️ Grey')
        # Apply color mapping
        filtered_df['Risk Sentiment Color'] = filtered_df['Risk Sentiment'].apply(sentiment_color)
        # Display as a neat table
        st.table(filtered_df[['Risk Dimension', 'Risk Sentiment Color']])
    else:
        st.warning("No event risks found.")

st.subheader("🛡️ Trade Risk Analysis")

if 'event_risks' in st.session_state and not st.session_state['event_risks'].empty:
    event_risks = st.session_state['event_risks']
    risk_summary = event_risks[['Risk Dimension', 'Risk Sentiment']].to_dict(orient='records')
    # Prepare LLM prompt
    system_prompt = (
        """You are an FX trade risk advisor. Your role is to concisely analyze trade P&L and event-driven risk sentiments to provide intuitive risk management guidance:

        - For small P&L moves, closely highlight relevant risk factors.
        - For significantly positive P&L combined with elevated event risks, suggesting considering profit-taking or partial position adjustments.
        - For significantly negative P&L combined with elevated event risks, suggesting considering prompt risk reduction or loss-cutting actions.
        - Only providing 'Potential options for managing your risk' when P&L is above 1.5% or below -1.5%
        - Don't explicitly using the word 'advisory', using suggestions instead
        - Don't suggest any option related hedging strategies or hedging using correlated assets or any other exotic hedging strategies

        Ensure your guidance is clearly suggestions in nature, focusing on providing options, highlighting that these options are not our recommendations, we are happy to discus more if needed.
"""
    )

    user_prompt = (
        f"The current trade has a P&L of {trade_pnl:.2f}%.\n"
        f"Here are the event risks:\n" +
        "\n".join([f"- {r['Risk Dimension']}: {r['Risk Sentiment']}" for r in risk_summary]) +
        "\n\nPlease provide a concise and intuitive risk management recommendation."
    )

    response = openai.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    st.info(response.choices[0].message.content)

else:

    st.warning("🕵️‍♂️ No event risks to analyze. Please run 'Analyze Event Risks' first.")

# Sidebar info
st.sidebar.title("🛠 About This App")
st.sidebar.markdown("""
This app analyzes event risks for currency pairs using AI. It categorizes risks into different dimensions and assigns sentiment levels.

### How to use:
1. Enter your currency pair
2. Select trade direction
3. Set tenor length
4. Enter current P&L
5. Click "Analyze Event Risks"

### Risk Levels:
- 🔴 High: Highly unpredictable risks
- 🟠 Alerted: Elevated uncertainties
- 🔵 Medium: Moderate uncertainties
- 🟢 Low: Relatively predictable
- ⚪️ N/A: No specific information
""") 

