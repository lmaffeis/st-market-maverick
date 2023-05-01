# Scrap Wikipedia to have the list of tickers from S&P 500 and store them alphabetically in a list
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
