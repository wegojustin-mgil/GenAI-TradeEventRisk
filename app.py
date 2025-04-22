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
      /* Color palette - extended with light/dark mode support */
      :root {
        /* Primary colors */
        --primary-color: #3b82f6;     /* blue-500 */
        --primary-light: #60a5fa;     /* blue-400 */  
        --primary-dark: #2563eb;      /* blue-600 */
        
        /* Secondary colors */
        --secondary-color: #10b981;   /* green-500 */
        --secondary-light: #34d399;   /* green-400 */
        --secondary-dark: #059669;    /* green-600 */
        
        /* Neutral colors */
        --text-color: #111827;        /* gray-900 */
        --text-secondary: #4b5563;    /* gray-600 */
        --text-muted: #9ca3af;        /* gray-400 */
        
        /* Background colors */
        --bg-light: #f9fafb;          /* gray-50 */
        --bg-container: #ffffff;      /* white */
        --bg-card: #ffffff;           /* white */
        --bg-muted: #f3f4f6;          /* gray-100 */
        --sidebar-bg: #f1f5f9;        /* light gray (slate-100) */
        
        /* Border colors */
        --border-light: #e5e7eb;      /* gray-200 */
        --border-medium: #d1d5db;     /* gray-300 */
        
        /* Accent colors for financial data */
        --accent-positive: #10b981;   /* green-500 */
        --accent-negative: #ef4444;   /* red-500 */
        --accent-neutral: #f59e0b;    /* amber-500 */
        
        /* UI properties */
        --border-radius-sm: 8px;
        --border-radius: 12px;
        --border-radius-lg: 16px;
        --transition-fast: 0.15s ease;
        --transition: 0.25s ease;
        --box-shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
        --box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        --box-shadow-lg: 0 12px 24px rgba(0,0,0,0.12);
      }

      /* Typography system */
      html, body, [class*="css"] {
        font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        background-color: var(--bg-light);
        color: var(--text-color);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }

      /* Text styles */
      h1 {
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 1.5rem;
        color: var(--primary-dark);
      }

      h2 {
        font-size: 1.75rem;
        font-weight: 600;
        line-height: 1.3;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: var(--primary-color);
      }

      h3 {
        font-size: 1.35rem;
        font-weight: 600;
        line-height: 1.4;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        color: var(--text-color);
      }

      p {
        margin-bottom: 1rem;
        color: var(--text-secondary);
      }

      /* App background and main container */
      .stApp {
        background-color: var(--bg-light) !important;
      }

      .block-container {
        background-color: var(--bg-container);
        border-radius: var(--border-radius-lg);
        padding: 2.5rem;
        box-shadow: var(--box-shadow);
        color: var(--text-color);
        transition: var(--transition);
      }

      /* Top banner with gradient */
      .top-banner {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        border-radius: var(--border-radius);
        padding: 1.75rem;
        margin-bottom: 2.5rem;
        box-shadow: var(--box-shadow);
        position: relative;
        overflow: hidden;
      }

      .top-banner::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
      }

      /* Sidebar styling with light gray background */
      .stSidebar {
        background-color: var(--sidebar-bg) !important;
      }
      
      .stSidebar [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
      }
      
      .stSidebar [data-testid="stSidebarNav"] {
        background-color: var(--sidebar-bg) !important;
      }
      
      .stSidebar .sidebar-content {
        background-color: var(--sidebar-bg) !important;
      }
      
      /* Elements within sidebar */
      .stSidebar h2 {
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border-light);
      }

      /* Card containers for content sections */
      .data-card {
        background-color: var(--bg-card);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-light);
        box-shadow: var(--box-shadow-sm);
        transition: var(--transition-fast);
      }

      .data-card:hover {
        box-shadow: var(--box-shadow);
        transform: translateY(-2px);
      }

      /* Buttons with improved styling */
      button[kind="primary"] {
        background: linear-gradient(to bottom, var(--primary-light), var(--primary-color)) !important;
        color: #ffffff !important;
        border-radius: var(--border-radius-sm);
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 500;
        transition: transform var(--transition-fast), box-shadow var(--transition-fast);
        border: none !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
      }

      button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
      }

      button[kind="primary"]:active {
        transform: translateY(0px);
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
      }

      button[kind="secondary"] {
        background-color: var(--bg-muted) !important;
        color: var(--text-secondary) !important;
        border-radius: var(--border-radius-sm);
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 500;
        transition: var(--transition-fast);
        border: 1px solid var(--border-light) !important;
      }

      button[kind="secondary"]:hover {
        background-color: var(--border-light) !important;
        box-shadow: var(--box-shadow-sm);
      }

      /* Form elements */
      input, textarea, select {
        background-color: var(--bg-container) !important;
        color: var(--text-color) !important;
        border-radius: var(--border-radius-sm);
        border: 1px solid var(--border-light) !important;
        padding: 0.85rem 1rem !important;
        font-size: 1rem;
        transition: var(--transition-fast);
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
      }

      input:focus, textarea:focus, select:focus {
        border-color: var(--primary-light) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        outline: none;
      }

      /* Tables with light header */
      table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 1.5rem 0;
        border-radius: var(--border-radius-sm);
        overflow: hidden;
        box-shadow: var(--box-shadow-sm);
      }

      thead tr {
        background-color: #f8fafc;    /* Very light bluish gray */
        color: var(--text-color);
        border-bottom: 2px solid var(--border-medium);
      }

      th {
        text-align: left;
        padding: 1rem;
        font-weight: 600;
      }

      td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-light);
      }

      tbody tr:nth-child(even) {
        background-color: var(--bg-muted);
      }

      tbody tr:hover {
        background-color: rgba(59, 130, 246, 0.05);
      }

      /* Financial data styling */
      .value-positive {
        color: var(--accent-positive);
        font-weight: 500;
      }

      .value-negative {
        color: var(--accent-negative);
        font-weight: 500;
      }

      /* Responsive adjustments */
      @media screen and (max-width: 768px) {
        .block-container {
          padding: 1.5rem;
        }
        
        .top-banner {
          font-size: 1.75rem;
          padding: 1.25rem;
        }
        
        h1 {
          font-size: 1.85rem;
        }
        
        h2 {
          font-size: 1.5rem;
        }
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

