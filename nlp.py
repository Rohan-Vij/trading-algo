import os
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

class StockSentimentAnalyzer:
    def __init__(self, ticker):
        self.web_url = 'https://finviz.com/quote.ashx?t=' + ticker
        self.news_tables = {}
        self.news_list = []  # Store news data as an instance variable
        self.news_df = None
        self.overall_sentiment = None

    def fetch_news_data(self):
        req = Request(url=self.web_url, headers={"User-Agent": "Chrome"})
        response = urlopen(req)
        html = BeautifulSoup(response, "html.parser")
        news_table = html.find(id='news-table')
        last_date = None  # Store the last valid date

        for i in news_table.find_all('tr'):
            date = last_date  # Use the last valid date value
            time = ""  # Initialize time with an empty string

            if i.a is not None:
                text = i.a.get_text()
            date_scrape = i.td.text.split()

            try:
                source = i.find('div', {'class': 'news-link-right'}).text.strip().replace('(', '').replace(')', '')

            except AttributeError:
                # Skip ads
                continue

            if len(date_scrape) == 1:
                time = date_scrape[0]
                
            else:
                date = date_scrape[0]
                time = date_scrape[1]
                last_date = date  # Update last_date with the new valid date value

            self.news_list.append([date, time, text, source])  # Append data to the instance variable

        self.news_df = pd.DataFrame(self.news_list, columns=["date", "time", "headline", "source"])

    def remove_source(self, source_name):
        # Remove articles with the specified source name from the news_df DataFrame
        self.news_df = self.news_df[self.news_df['source'] != source_name]

    def analyze_sentiment(self):
        # Remove articles from the "Motley Fool" source before performing sentiment analysis
        self.remove_source("Motley Fool")

        nltk.download('vader_lexicon')
        vader = SentimentIntensityAnalyzer()
        scores = self.news_df['headline'].apply(vader.polarity_scores).tolist()
        scores_df = pd.DataFrame(scores)
        self.news_df = self.news_df.join(scores_df, rsuffix='_right')
        self.news_df['date'] = pd.to_datetime(self.news_df.date).dt.date

        # Calculate overall sentiment for each day
        self.overall_sentiment = self.news_df.groupby('date')['compound'].mean().reset_index()
        self.overall_sentiment['sentiment'] = self.overall_sentiment['compound'].apply(lambda score: -1 if score < 0 else 1 if score > 0 else 0)

    def plot_sentiment(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.overall_sentiment['date'], self.overall_sentiment['compound'], marker='o', linestyle='-')
        plt.xlabel('Date')
        plt.ylabel('Overall Sentiment Score')
        plt.title('Overall Sentiment Score for Each Day')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    ticker = 'META'
    analyzer = StockSentimentAnalyzer(ticker)
    analyzer.fetch_news_data()
    analyzer.analyze_sentiment()
    print(analyzer.news_df.head(10))
    print(analyzer.overall_sentiment)
