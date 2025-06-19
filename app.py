import os, csv
import yfinance as yf
import pandas as pd
import talib as ta
from flask import Flask, render_template, request
from pattern import patterns

app = Flask(__name__)

@app.route("/")
def index():
    pattern = request.args.get('pattern', None) #request object has information about the current request
    stocks = {}

    with open('datasets/companies.csv') as file:
        for row in csv.reader(file):
            stocks[row[0]] = {'company': row[1]}

    if pattern:
        datafiles = os.listdir('datasets/daily') #os object uses the listdir() to list all files in a given directory
        for filename in datafiles:
            df = pd.read_csv(f"datasets/daily/{filename}", on_bad_lines="skip")
            pattern_func = getattr(ta, pattern) #this takes in the string name of a class attribute and returns that attribute itself
            
            symbol = filename.split(".")[0]
            result = pattern_func(df['Open'], df['High'], df['Low'], df['Close'])
            last = result.tail(1).values
            if len(last) != 0: 
                if last[0] > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last[0] < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None

    return render_template('index.html', patterns = patterns, stocks=stocks, detected_pattern = pattern)

@app.route("/snapshot")
def snapshot():
    with open('./datasets/companies.csv') as file:
        campanies= file.read().splitlines() # reads into the file and the splitlines splits each line and creates a list of all lines
        for campany in campanies:
            #get dataframe for each symbol
            symbol = campany.split(",")[0]
            ticker = yf.Ticker(symbol)
            data = ticker.history(start="2020-01-01", end="2020-08-01")
            df = pd.DataFrame(data=data)
            df.to_csv("datasets/daily/{}.csv".format(symbol)) # df.to_csv(f"datasets/daily/{symbol}.csv")
            

if __name__=="__main__":
    app.run(debug=True)
