{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import pandas as pd\
import numpy as np\
import yfinance as yf\
from sklearn.ensemble import RandomForestRegressor\
from sklearn.model_selection import train_test_split\
from sklearn.metrics import mean_squared_error\
from textblob import TextBlob\
\
# Step 1: Fetch Stock Data\
def fetch_stock_data(ticker, start_date="2010-01-01"):\
    data = yf.download(ticker, start=start_date, prepost=True)\
    data['Date'] = data.index\
    data.reset_index(drop=True, inplace=True)\
    return data\
\
# Step 2: Fetch Consensus Target Price\
def fetch_consensus_target_price(ticker):\
    stock = yf.Ticker(ticker)\
    try:\
        target_price = stock.info.get('targetMeanPrice', np.nan)\
    except:\
        target_price = np.nan  # If unavailable, use NaN\
    return target_price\
\
# Step 3: Calculate Pre-Market Indicators\
def calculate_pre_market_indicators(stock_data):\
    stock_data['PreMarket_Change'] = (stock_data['Open'] - stock_data['Close'].shift(1)) / stock_data['Close'].shift(1)\
    stock_data['PreMarket_Volume_Ratio'] = stock_data['Volume'] / stock_data['Volume'].rolling(window=10).mean()\
    return stock_data\
\
# Step 4: Fetch and Analyse News Sentiment\
def fetch_news_sentiment(ticker):\
    # Simulated News Data - Replace this with an API (e.g., Alpha Vantage News or NewsAPI)\
    news_data = [\
        \{"headline": f"\{ticker\} reports strong earnings growth", "date": "2023-12-01"\},\
        \{"headline": f"\{ticker\} faces regulatory scrutiny over new product", "date": "2023-12-02"\},\
    ]\
    sentiments = []\
    for news in news_data:\
        sentiment = TextBlob(news["headline"]).sentiment.polarity\
        sentiments.append(sentiment)\
    return np.mean(sentiments) if sentiments else 0\
\
# Step 5: Merge Features\
def merge_features(stock_data, consensus_target_price, sentiment_score):\
    stock_data['Consensus_Target_Price'] = consensus_target_price\
    stock_data['Sentiment_Score'] = sentiment_score\
    stock_data['Target_Price_Variance'] = (stock_data['Consensus_Target_Price'] - stock_data['Close']) / stock_data['Close']\
    stock_data.dropna(inplace=True)\
    return stock_data\
\
# Step 6: Add Technical Indicators\
def add_technical_indicators(data):\
    data['Price_Change'] = data['Close'].pct_change()\
    data['SMA_10'] = data['Close'].rolling(window=10).mean()\
    data['SMA_50'] = data['Close'].rolling(window=50).mean()\
    data['RSI'] = (100 - (100 / (1 + data['Price_Change'].rolling(14).mean())))\
    data['Target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)  # 1=Buy, 0=Sell\
    data.dropna(inplace=True)\
    return data\
\
# Step 7: Train the Model\
def train_model(data):\
    features = ['Close', 'SMA_10', 'SMA_50', 'RSI', 'PreMarket_Change', 'PreMarket_Volume_Ratio', \
                'Consensus_Target_Price', 'Sentiment_Score', 'Target_Price_Variance']\
    X = data[features]\
    y = data['Close'].shift(-1)  # Predict next day's close price\
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\
    model = RandomForestRegressor(random_state=42)\
    model.fit(X_train, y_train)\
    predictions = model.predict(X_test)\
    print("Model Performance - RMSE:", np.sqrt(mean_squared_error(y_test, predictions)))\
    return model\
\
# Step 8: Predict Next Move\
def predict_next_move(model, data):\
    recent_data = data.iloc[-1:]\
    features = ['Close', 'SMA_10', 'SMA_50', 'RSI', 'PreMarket_Change', 'PreMarket_Volume_Ratio', \
                'Consensus_Target_Price', 'Sentiment_Score', 'Target_Price_Variance']\
    prediction = model.predict(recent_data[features])\
    return prediction[0]\
\
# Main Execution\
if __name__ == "__main__":\
    ticker = "AAPL"\
\
    # Fetch stock data and consensus target price\
    stock_data = fetch_stock_data(ticker)\
    consensus_target_price = fetch_consensus_target_price(ticker)\
\
    # Calculate pre-market indicators and news sentiment\
    stock_data = calculate_pre_market_indicators(stock_data)\
    sentiment_score = fetch_news_sentiment(ticker)\
\
    # Merge features and train model\
    combined_data = merge_features(stock_data, consensus_target_price, sentiment_score)\
    combined_data = add_technical_indicators(combined_data)\
    model = train_model(combined_data)\
\
    # Predict the next move\
    next_price = predict_next_move(model, combined_data)\
    print(f"Predicted Next Day Close Price for \{ticker\}: $\{next_price:.2f\}")\
}