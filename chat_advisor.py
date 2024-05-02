import json
from openai import OpenAI 
import pandas as pd
import matplotlib.pyplot as plt  
from dotenv import load_dotenv, find_dotenv 
import os

import streamlit as st
import yfinance as yf

#Based on your version of installation of openai, you can use the following code to set the api key
#Delete the code that is not applicable to you

#For gpt 0.0.28
# openai.api_key = open('api_key.txt').read().strip()



#The newest version

#or...
#openai.api_key = 'your-api-key'


#Functions to be used in the chatbot

def get_stock_data(self):
    return str(yf.Ticker(self.ticker).history(period="1y").iloc[-1].Close)





def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y")["Close"]
    return str(data.rolling(window=window).mean().iloc[-1]) 





def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period="1y")["Close"]
    return str(data.ewm(span=window, adjust=False).mean().iloc[-1]) 



def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period="1y")["Close"]
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=14 - 1, adjust=False).mean()
    ema_down = down.ewm(com=14 - 1, adjust=False).mean()
    rs =  ema_up/ema_down
    return str(100 - (100/(1 + rs.iloc[-1])))




def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period="1y")["Close"]
    shortEMA = data.ewm(span=12, adjust=False).mean()
    longEMA = data.ewm(span=26, adjust=False).mean()
    MACD = shortEMA - longEMA
    signal = MACD.ewm(span=9, adjust=False).mean()
    MACD_histogram = MACD - signal
    return f'{MACD.iloc[-1]}, {signal[-1]}, {MACD_histogram.iloc[-1]}'





def get_stock_price(ticker):
    data = yf.Ticker(ticker).history(period="1y")["Close"]
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data.Close)  # Fix: Removed incorrect use of **args and fixed the arguments passed to plt.plot()
    plt.title(f"{ticker} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.show()
    plt.savefig("stock_price.png")
    plt.close()


#descriptions
functions = [
    {
        'name': 'get_stock_data',
        'description': 'Get the stock price of a given ticker',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type':'string',
                    'description': 'The stock ticker to get the price for'
                }
            }  # Added closing curly brace here
        },
        'required': ['ticker']
    },
     {
        'name': 'calculate_SMA',
        'description': 'calculate SMA of a given ticker',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type':'string',
                    'description': 'The stock ticker to get the price for'
                }
            }  # Added closing curly brace here
        },
        'required': ['ticker']
    },
     {
        'name': 'calculate_EMA',
        'description': 'calculate_EMA  of a given ticker',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type':'string',
                    'description': 'The stock ticker to get the price for'
                }
            }  # Added closing curly brace here
        },
        'required': ['ticker']
    },
     {
        'name': 'calculate_RSI',
        'description': 'calculate RSI of a given ticker',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type':'string',
                    'description': 'The stock ticker to get the price for'
                }
            }  # Added closing curly brace here
        },
        'required': ['ticker']
    },
     {
        'name': 'calculate_MACD',
        'description': 'Calculate MACD of a given ticker',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type':'string',
                    'description': 'The stock ticker to get the price for'
                }
            }  # Added closing curly brace here
        },
        'required': ['ticker']
    },
     {
        'name': 'get_stock_price',
        'description': 'Get the stock price of a given ticker',
        'parameters': {
            'type': 'object',
            'properties': {
                'ticker': {
                    'type':'string',
                    'description': 'The stock ticker to get the price for'
                }
            }  # Added closing curly brace here
        },
        'required': ['ticker']
    }
]













available_functions = {
    'get_stock_data': get_stock_data,
    'calculate_SMA': calculate_SMA,
    'calculate_EMA': calculate_EMA,
    'calculate_RSI': calculate_RSI,
    'calculate_MACD': calculate_MACD,
}
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

st.title("Stock Analysis Chat Advisor")

user_input = st.text_input("What you want?: ")

if user_input:
    try:
        st.session_state['messages'].append({'role': 'user', 'content': f'{user_input}'})

        response = client.chat.completions.create(
            model='gpt-3.5-turbo-0613',
            messages=st.session_state['messages'],
            functions=functions,
            function_call='auto'
        )

        response_message = response['choices'][0]['message']

        if 'function_call' in response_message:
            function_name = response_message['function_call']['name']
            function_args = json.loads(response_message['function_call']['arguments'])
            if function_name in ['get_stock_data', 'calculate_SMA', 'calculate_EMA', 'calculate_RSI', 'calculate_MACD']:
                args_dict = {'ticker': function_args.get('ticker')}
            elif function_name in ['calculate_SMA', 'calculate_EMA']:
                args_dict = {'ticker': function_args.get('ticker'), 'window': function_args.get('window')}

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**args_dict)

            if function_name == 'get_stock_price':
                st.image("stock_price.png")
            else:
                st.session_state['messages'].append(response_message)
                st.session_state['messages'].append(
                    {
                        'role': 'function',
                        'name': function_name,
                        'content': function_response,
                    }
                )
                second_response = client.chat.completions.create(
                    model='gpt-3.5-turbo-0613',
                    messages=st.session_state['messages'],
                    functions=functions,
                    function_call='auto'
                )
                st.text(second_response['choices'][0]['message']['content'])
                st.session_state['messages'].append({'role': 'assistant', 'content': second_response['choices'][0]['message']['content']})
        else:
            st.text(response_message['content'])
            st.session_state['messages'].append({'role': 'assistant', 'content': response_message['content']})

    except Exception as e:
        raise e
    


     