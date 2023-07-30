import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

class BollingerBandsBacktest:
    def __init__(self, ticker, start_date, end_date, window=20, num_std=2):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.window = window
        self.num_std = num_std
        self.stock_data = None

    def get_stock_data(self):
        self.stock_data = yf.download(self.ticker, start=self.start_date, end=self.end_date)

    def calculate_bollinger_bands(self):
        self.stock_data['SMA'] = self.stock_data['Adj Close'].rolling(window=self.window).mean()
        self.stock_data['Std'] = self.stock_data['Adj Close'].rolling(window=self.window).std()
        self.stock_data['Upper_Band'] = self.stock_data['SMA'] + self.num_std * self.stock_data['Std']
        self.stock_data['Lower_Band'] = self.stock_data['SMA'] - self.num_std * self.stock_data['Std']

    def trading_strategy(self):
        signals = pd.DataFrame(index=self.stock_data.index)
        signals['Signal'] = 0
        signals.loc[self.stock_data['Adj Close'] > self.stock_data['Upper_Band'], 'Signal'] = -1
        signals.loc[self.stock_data['Adj Close'] < self.stock_data['Lower_Band'], 'Signal'] = 1
        return signals

    def evaluate_strategy(self, signals):
        self.stock_data['Signal'] = signals['Signal']
        self.stock_data['Position'] = self.stock_data['Signal'].diff()

    def simulate_trading(self):
        initial_cash = 100000  # Initial cash balance
        num_stocks = 0  # Number of stocks in the portfolio
        portfolio_value = []  # To keep track of the portfolio value at each trading point
        cash_balance = initial_cash

        for index, row in self.stock_data.iterrows():
            print(cash_balance)
            if row['Position'] == 1:  # Buy signal
                num_stocks = cash_balance // row['Adj Close']  # Buy as many stocks as possible
                cash_balance -= num_stocks * row['Adj Close']

            elif row['Position'] == -1 and num_stocks > 0:  # Sell signal and we have stocks to sell
                cash_balance += num_stocks * row['Adj Close']
                num_stocks = 0

            portfolio_value.append(cash_balance + num_stocks * row['Adj Close'])

        self.stock_data['Portfolio_Value'] = portfolio_value

    def backtest(self):
        self.get_stock_data()
        self.calculate_bollinger_bands()

        signals = self.trading_strategy()
        self.evaluate_strategy(signals)

        self.stock_data['Daily_Return'] = self.stock_data['Adj Close'].pct_change() * self.stock_data['Position'].shift()

        # Simulate trading with realistic buying and selling
        self.simulate_trading()

        self.stock_data['Cumulative_Return'] = (1 + self.stock_data['Daily_Return']).cumprod()
        self.stock_data['Portfolio_Return'] = self.stock_data['Portfolio_Value'] / self.stock_data['Portfolio_Value'].iloc[0]

        final_return = self.stock_data['Portfolio_Value'].iloc[-1] / self.stock_data['Portfolio_Value'].iloc[0]
        print(f"Final Cumulative Return: {final_return}")

    def plot_graph(self):
        plt.figure(figsize=(12, 10))

        # Plot stock price and Bollinger Bands
        plt.subplot(2, 1, 1)
        plt.plot(self.stock_data['Adj Close'], label='Stock Price', color='b')
        plt.plot(self.stock_data['SMA'], label='SMA', color='orange')
        plt.plot(self.stock_data['Upper_Band'], label='Upper Bollinger Band', color='gray', linestyle='dashed')
        plt.plot(self.stock_data['Lower_Band'], label='Lower Bollinger Band', color='gray', linestyle='dashed')
        plt.fill_between(self.stock_data.index, self.stock_data['Upper_Band'], self.stock_data['Lower_Band'], alpha=0.2, color='gray')
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
        plt.subplot(2, 1, 2)
        plt.plot(self.stock_data.index, self.stock_data['Cumulative_Return'], label='Cumulative Returns', color='b')
        plt.ylabel("Cumulative Returns", color='b')
        plt.tick_params(axis='y', labelcolor='b')
        plt.legend(loc='upper left')

        ax2 = plt.twinx()
        ax2.plot(self.stock_data.index, self.stock_data['Portfolio_Return'], label='Portfolio Value', color='g')
        ax2.set_ylabel("Portfolio Value", color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.legend(loc='upper right')

        plt.xlabel("Date")

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Replace these with your desired stock ticker and date range
    ticker = 'PG'
    start_date = '2020-01-01'
    end_date = '2023-07-30'
    window = 20  # Bollinger Bands window
    num_std = 2  # Number of standard deviations for Bollinger Bands

    backtester = BollingerBandsBacktest(ticker, start_date, end_date, window, num_std)
    backtester.backtest()
    backtester.plot_graph()