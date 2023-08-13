from bollinger import BollingerBandsBacktest
from nlp import StockSentimentAnalyzer
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import pandas as pd


class TradeEvaluator(BollingerBandsBacktest, StockSentimentAnalyzer):
    def __init__(self, ticker, start_date, end_date, window=20, num_std=2):
        BollingerBandsBacktest.__init__(
            self, ticker, start_date, end_date, window, num_std)
        StockSentimentAnalyzer.__init__(self, ticker)

        self.fetch_news_data()
        self.analyze_sentiment()

    def backtest(self):
        self.get_stock_data()
        self.calculate_bollinger_bands()

        signals = self.trading_strategy()
        self.evaluate_strategy(signals)

        self.stock_data['Daily_Return'] = self.stock_data['Adj Close'].pct_change(
        ) * self.stock_data['Position'].shift()

        # Simulate trading with realistic buying and selling
        self.simulate_trading()

        self.stock_data['Cumulative_Return'] = (
            1 + self.stock_data['Daily_Return']).cumprod()
        self.stock_data['Portfolio_Return'] = self.stock_data['Portfolio_Value'] / \
            self.stock_data['Portfolio_Value'].iloc[0]

        final_return = self.stock_data['Portfolio_Value'].iloc[-1] / \
            self.stock_data['Portfolio_Value'].iloc[0]
        print(f"Final Cumulative Return: {final_return}")

    def plot_graph(self):
        plt.figure(figsize=(12, 10))

        # Plot stock price and Bollinger Bands
        plt.subplot(3, 1, 1)
        plt.plot(self.stock_data['Adj Close'], label='Stock Price', color='b')
        plt.plot(self.stock_data['EMA'], label='EMA', color='orange')
        plt.plot(self.stock_data['Upper_Band'],
                 label='Upper Bollinger Band', color='gray', linestyle='dashed')
        plt.plot(self.stock_data['Lower_Band'],
                 label='Lower Bollinger Band', color='gray', linestyle='dashed')
        plt.fill_between(self.stock_data.index,
                         self.stock_data['Upper_Band'], self.stock_data['Lower_Band'], alpha=0.2, color='gray')
        plt.plot(self.stock_data[self.stock_data['Signal'] == 1].index,
                 self.stock_data['Adj Close'][self.stock_data['Signal'] == 1],
                 '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(self.stock_data[self.stock_data['Signal'] == -1].index,
                 self.stock_data['Adj Close'][self.stock_data['Signal'] == -1],
                 'v', markersize=10, color='r', label='Sell Signal')
        plt.title(f"{self.ticker} Bollinger Bands Trading Strategy")
        plt.xlabel("Date")
        plt.ylabel("Stock Price")
        plt.legend()

        # Plot cumulative returns and portfolio value with a second y-axis
        plt.subplot(3, 1, 2)
        plt.plot(self.stock_data.index,
                 self.stock_data['Cumulative_Return'], label='Cumulative Returns', color='b')
        plt.ylabel("Cumulative Returns", color='b')
        plt.tick_params(axis='y', labelcolor='b')
        plt.legend(loc='upper left')

        ax2 = plt.twinx()
        ax2.plot(self.stock_data.index,
                 self.stock_data['Portfolio_Return'], label='Portfolio Value', color='g')
        ax2.set_ylabel("Portfolio Value (Thousands)", color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.legend(loc='upper right')

        plt.xlabel("Date")

        # Plot sentiment scores
        plt.subplot(3, 1, 3)

        plt.scatter(self.overall_sentiment['date'], self.overall_sentiment['compound'],
                    s=self.overall_sentiment['compound'].abs() * 500,  # Adjust the size of the dots based on sentiment intensity
                    c=self.overall_sentiment['compound'], cmap='RdYlGn', alpha=1)  # Set vmin and vmax for color scale  
        plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)  # Horizontal line at sentiment score 0
        plt.colorbar(label='Sentiment Intensity')

        # plt.ylim(-0.5, 0.5)
        plt.ylabel("Sentiment", color='black')
        plt.tick_params(axis='y', labelcolor='black')
        plt.xlabel("Date")

                # Get buy/sell signals for the available dates and overlay them on the graph at y=0
        signals = self.trading_strategy()
        # print(signals.tail(10))
        available_dates = self.overall_sentiment['date'].values
        buy_signals = signals[signals.index.isin(available_dates) & (signals['Signal'] == 1)]
        sell_signals = signals[signals.index.isin(available_dates) & (signals['Signal'] == -1)]

        plt.scatter(buy_signals.index, [0] * len(buy_signals), marker='^', color='g', label='Buy Signal', s=100)
        plt.scatter(sell_signals.index, [0] * len(sell_signals), marker='v', color='r', label='Sell Signal', s=100)

        plt.legend(loc='upper right')

        plt.tight_layout()
        plt.show()

        return plt

    def analyze_specific_date(self, current_date = datetime.now()):
        self.get_stock_data()
        self.calculate_bollinger_bands()

        signals = self.trading_strategy()
        self.evaluate_strategy(signals)

        current_date = current_date.strftime('%Y-%m-%d')
        
        stock_date = None
        while stock_date is None:
            try:
                stock_date = self.stock_data.loc[current_date]['Adj Close']
            except KeyError:
                current_date = (datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')

        row = self.stock_data.loc[current_date]

        result = {
            "Date": current_date,
            "Bollinger Bands Signal": row['Position'],
            "Stock Price": f"${row['Adj Close']:.2f}",
            "Expected EMA Price": f"${row['EMA']:.2f}"
        }

        news_articles = self.get_news_articles(current_date)
        result["News Articles"] = news_articles

        return result


    def get_news_articles(self, date):
        self.news_df['date'] = pd.to_datetime(self.news_df['date'], format='%Y-%m-%d')
        news_articles = self.news_df[self.news_df['date'] == date]
        if not news_articles.empty:
            return news_articles.to_dict('records')
        return None

if __name__ == '__main__':
    ticker = 'META'
    start_date = '2020-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    window = 20
    num_std = 2

    trade_evaluator = TradeEvaluator(ticker, start_date, end_date, window, num_std)
    trade_evaluator.analyze_current_date()
    
    # trade_evaluator.backtest()
    # trade_evaluator.plot_graph()
