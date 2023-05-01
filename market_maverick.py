# Import relevant libraries
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import ta
from datetime import datetime, timedelta

from plotly.subplots import make_subplots
import plotly.graph_objects as go

import requests
from bs4 import BeautifulSoup


# Make an HTTP request to the Wikipedia page
response = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the table that contains the component stocks tickers
table = soup.find("table", {"id": "constituents"})

# Find all the rows in the table except the header row
rows = table.find_all("tr")[1:]

# Extract the tickers from the rows and store them in a list
tickers = []
for row in rows:
    ticker = row.find_all("td")[0].text.strip()
    tickers.append(ticker)

# Sort the tickers alphabetically and store it in a new variable
tickers.sort()

# Set up the page layout
st.set_page_config(
    page_title='The Market Maverick',
    page_icon=':money_with_wings:',
    initial_sidebar_state="auto",
    )


# Set the Header and Sub Header for the Dashboard
st.title('The Market Maverick')
st.subheader('Your Ultimate Stock Dashboard')

# Store ticker, start data and end date and put those in the sidebar
ticker = st.sidebar.selectbox("Select a ticker", [""] + tickers)
default_start_date = datetime.today() - timedelta(days=365)
start_date = st.sidebar.date_input("Start Date", default_start_date)
end_date = st.sidebar.date_input("End Date")

# Add text to the sidebar with relevant contacts
st.sidebar.markdown('**Discover the Market Maverick.**')
st.sidebar.write('[Let\'s connect](https://www.linkedin.com/in/luca-maffeis-/) and get insight on its full potential',
                 unsafe_allow_html=True)


# Define an if condition such as, if the ticker field is empy,
# the dashboard displays a brief description of the Market Maverick


if ticker == '':

    # If the user entered a stock ticker symbol, display the stock price chart
    st.write("""
    **Select your stock and let us handle the rest.**
    
    Introducing our cutting-edge dashboard that brings real-time financial data to your fingertips like never before.
    With its sleek design and intuitive interface, this dashboard is the perfect tool for anyone looking to stay ahead
    of the curve in the world of finance.

    With just a few clicks, you can access up-to-date information on stocks, allowing you to make informed investment
    decisions with confidence. And if you're not sure where to start, our dashboard provides helpful tips and insights
    to guide you along the way.

    But it's not just about the data – our dashboard also provides stunning visualizations that make it easy to 
    understand complex financial information at a glance. Whether you're a seasoned investor or just getting started, 
    this dashboard is the perfect tool to help you stay on top of your finances.

    And with its compatibility across all devices, you can access your financial data anytime, anywhere. Whether you're
    on your desktop, laptop, or mobile device, our dashboard makes it easy to stay connected to the financial world.

    So why wait? Experience the power of real-time financial data like never before – get started today!
    """, style={"text-align": "justify"})

# Else statement to populate the field and store the data in the variable
else:
    # Populate the data field and store it in the data variable
    data = yf.download(ticker, start=start_date, end=end_date)
    # get the company name from the ticker and put in upper case
    company_name_ticker = yf.Ticker(ticker)
    long_company_name = company_name_ticker.info['longName'].upper()
    # Plot the time series on the Adjusted Close price
    fig = px.line(data, x=data.index, y=['Adj Close'], title=long_company_name)
    # Remove the label for x and y axes in the graph
    fig.update_yaxes(title_text=None)
    fig.update_xaxes(title_text=None)
    st.plotly_chart(fig)

    # Create container for financial metrics
    fin_metrics_container = st.container()
    with fin_metrics_container:
        # Fetch financial metrics using yfinance
        info = yf.Ticker(ticker).info
        market_cap = info.get('marketCap', 'N/A')
        # Format the market cap field to have commas for decimals
        if market_cap != 'N/A':
            market_cap_str = "{:,}".format(market_cap)
        metrics = {
            'Market Cap': market_cap_str,
            'PE Ratio': info.get('trailingPE', 'N/A'),
            'Forward PE Ratio': info.get('forwardPE', 'N/A'),
            'Price to Sales Ratio (TTM)': info.get('priceToSalesTrailing12Months', 'N/A'),
            'Price to Book Ratio': info.get('priceToBook', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A')
        }

        # Display metrics in a table
        st.header('Financial Metrics')
        fin_metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
        st.table(fin_metrics_df)

    # Create container for the dataset
    data_container = st.container()
    with data_container:
        st.header('Dataset')
        st.write(data)

    # Create container for SMA indicator
    sma_container = st.container()
    with sma_container:
        # Calculate simple moving average
        st.header('SMA')
        period = st.slider("Select SMA period", min_value=2, max_value=50, value=20, step=1)
        sma = ta.trend.SMAIndicator(data['Close'], period).sma_indicator()
        # Plot the SMA
        fig = px.line(data, x=data.index, y=['Close', sma], title=f"{ticker} Close price and {period}"
                                                                  f"-day Simple Moving Average")
        # Rename the variables in the legend
        new_SMA_names = {'Close': 'Close', 'wide_variable_1': 'SMA'}
        fig.for_each_trace(lambda t: t.update(name=new_SMA_names[t.name],
                                              legendgroup=new_SMA_names[t.name],
                                              hovertemplate=t.hovertemplate.replace(t.name, new_SMA_names[t.name])
                                              )
                           )
        # Remove the label for x and y axes in the graph
        fig.update_yaxes(title_text=None)
        fig.update_xaxes(title_text=None)
        st.plotly_chart(fig)

    # Create container for Bollinger Bands indicator
    bb_container = st.container()
    with bb_container:
        # Calculate Bollinger Bands
        st.header('Bollinger Bands')
        period = st.slider("Select Bollinger Bands period", min_value=10, max_value=50, value=20, step=1)
        std_dev = st.slider("Select Standard Deviation", min_value=1, max_value=5, value=2, step=1)
        bb = ta.volatility.BollingerBands(data['Close'], window=period, window_dev=std_dev)
        upper_band = bb.bollinger_hband()
        lower_band = bb.bollinger_lband()
        fig = px.line(data, x=data.index, y=['Close', upper_band, lower_band], title=f"{ticker} Close price and Bollinger Bands ({period}, {std_dev})")
        new_BB_names = {'Close': 'Close', 'wide_variable_1': 'Upper BB', 'wide_variable_2': 'Lower BB'}
        # Rename the variables in the legend
        fig.for_each_trace(lambda t: t.update(name=new_BB_names[t.name],
                                              legendgroup=new_BB_names[t.name],
                                              hovertemplate=t.hovertemplate.replace(t.name, new_BB_names[t.name])
                                              )
                           )
        fig.update_yaxes(title_text=None)
        fig.update_xaxes(title_text=None)
        st.plotly_chart(fig)

        # Relative Strength Index (RSI)
        st.header('Relative Strength Index')
        rsi = ta.momentum.RSIIndicator(data['Adj Close'])
        data['RSI'] = rsi.rsi()
        fig_rsi = px.line(data, x=data.index, y='RSI', title='Relative Strength Index (RSI)')
        # Remove the label for x and y axes in the graph
        fig_rsi.update_yaxes(title_text=None)
        fig_rsi.update_xaxes(title_text=None)
        st.plotly_chart(fig_rsi)

    # Create container for MACD indicator
    macd_container = st.container()
    with macd_container:
        # Calculate MACD
        st.header('MACD')
        macd_fast_period = st.slider("Select MACD Fast Period", min_value=2, max_value=50, value=12, step=1)
        macd_slow_period = st.slider("Select MACD Slow Period", min_value=2, max_value=50, value=26, step=1)
        macd_signal_period = st.slider("Select MACD Signal Period", min_value=2, max_value=50, value=9, step=1)
        macd = ta.trend.MACD(data['Close'], window_fast=macd_fast_period, window_slow=macd_slow_period,
                             window_sign=macd_signal_period)
        macd_line = macd.macd()
        signal_line = macd.macd_signal()
        # Calculate MACD histogram
        macd_hist = macd_line - signal_line
        # Create plot
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=macd_line, name='MACD Line'), row=2, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=signal_line, name='Signal Line'), row=2, col=1)
        fig.add_trace(go.Bar(x=data.index, y=macd_hist, name='MACD Histogram'), row=2, col=1)
        fig.update_layout(title=f"{ticker} Close price and MACD",
                          xaxis_rangeslider_visible=False,
                          xaxis=dict(title=None),
                          yaxis=dict(title=None),
                          height=600)

        st.plotly_chart(fig)
