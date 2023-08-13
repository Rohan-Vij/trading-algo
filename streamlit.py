import streamlit as st
from datetime import datetime
from combine import TradeEvaluator

st.set_option('deprecation.showPyplotGlobalUse', False)  # Disable warning


def analyze_trade(ticker, evaluation_date, window, num_std, generate_graph):
    trade_evaluator = TradeEvaluator(ticker, "2020-01-01", evaluation_date)

    if evaluation_date != datetime.now().date():
        trade_evaluator.analyze_specific_date(evaluation_date)

    current_date_info = trade_evaluator.analyze_specific_date()

    if generate_graph:
        trade_evaluator.backtest()
        st.subheader("Bollinger Bands Strategy Backtesting Results")
        trade_evaluator.plot_graph()

    st.subheader("Trading Analysis")
    if current_date_info:
        st.write("Date:", current_date_info["Date"])
        
        # Interpret the Bollinger Bands Signal
        signal_interpretation = {
            0: "Hold",
            1: "Buy",
            -1: "Sell"
        }
        bollinger_signal = current_date_info["Bollinger Bands Signal"]
        st.write("Bollinger Bands Signal:", signal_interpretation.get(bollinger_signal, "Unknown"))
        
        # Format the Stock Price and Expected EMA Price only if they are numeric
        if current_date_info["Stock Price"].replace(".", "", 1).isdigit():
            st.write("Stock Price:", f"${float(current_date_info['Stock Price']):.2f}")
        else:
            st.write("Stock Price:", current_date_info["Stock Price"])
            
        if current_date_info["Expected EMA Price"].replace(".", "", 1).isdigit():
            st.write("Expected EMA Price:", f"${float(current_date_info['Expected EMA Price']):.2f}")
        else:
            st.write("Expected EMA Price:", current_date_info["Expected EMA Price"])
        
        st.write("News Articles:")
        if current_date_info["News Articles"]:
            for i, article in enumerate(current_date_info["News Articles"]):
                st.write(f"{i + 1}. {article['headline']} (Sentiment: {article['compound']:.2f}, Source: {article['source']})")
        else:
            st.write("No news articles available for this date.")
    else:
        st.write("No analysis available for the selected date.")

    if generate_graph:
        trade_evaluator.backtest()
        st.subheader("Bollinger Bands Strategy Backtesting Results")
        fig = trade_evaluator.plot_graph()
        st.pyplot(fig)


st.header("Stock Trade Evaluator")

ticker = st.text_input("Enter Ticker Symbol (e.g. META):")

specific_date = st.checkbox("Evaluate Specific Date")
if specific_date:
    evaluation_date = st.date_input("Select Date:", datetime.now())
else:
    evaluation_date = datetime.now()

window = st.number_input("Enter Bollinger Bands Window:", value=20)
num_std = st.number_input("Enter Number of Standard Deviations:", value=2)

generate_graph = st.checkbox("Generate Matplotlib Graph")


if st.button("Analyze"):
    analyze_trade(ticker, evaluation_date, window, num_std, generate_graph)


