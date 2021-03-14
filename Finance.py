# Import data from YahooFinancials
import pandas as pd
from yahoofinancials import YahooFinancials
import datetime as dt
from flatten_json import flatten
import numpy as np


def volatility(df):
    "function to calculate annualised volatility of daily freqency prices"
    df = df.copy()
    df["daily_ret"] = df["adjclose"].pct_change()
    vol = df["daily_ret"].std() * np.sqrt(252)
    return vol


def sharpe(df, rf):
    "function to calculate sharpe ratio, rf is the risk free rate"
    df = df.copy()
    c = CAGR(df)
    v = volatility(df)
    sr = (c - rf)/v
    return sr


def sortino(df, rf):
    "function to calculate sortino ratio, rf is the risk free rate"
    df = df.copy()
    df["daily_ret"] = df["adjclose"].pct_change()
    neg_vol = df[df["daily_ret"] < 0]["daily_ret"].std() * np.sqrt(252)
    sr = (CAGR(df) - rf)/neg_vol
    return sr


def CAGR(df):
    "Calculate the Cumm Annual Growth Rate for daily frequency data"
    df = df.copy()

    df["daily_ret"] = df["adjclose"].pct_change()
    df["cum_return"] = (1 + df["daily_ret"]).cumprod()
    n = len(df)/252  # trading days in year
    CAGR = (df["cum_return"][-1])**(1/n) - 1
    return CAGR


def FixItemName(items):
    item_list = items.tolist()
    res = []

    # loop to iterate all strings
    for ele in item_list:
        temp = [[]]
        for char in ele:
            # checking for upper case character
            if char.isupper():
                temp.append([])

            # appending character at latest list
            temp[-1].append(char)

        # joining lists after adding space and converting to title case
        res.append(' '.join(''.join(ele) for ele in temp).title())

    return pd.Series(res)


def ExtractPrices(all_tickers):
    # extracting stock data (ohlcv)
    ohlv_dict = {}
    end_date = (dt.date.today()).strftime('%Y-%m-%d')
    beg_date = (dt.date.today()-dt.timedelta(1825)).strftime('%Y-%m-%d')
    prices = pd.DataFrame({"formatted_date": [], "adjclose": [], "open": [], "low": [], "high": [], "volume": [], "ticker": []})

    for ticker in all_tickers:
        yahoo_financials=YahooFinancials(ticker)
        json_obj=yahoo_financials.get_historical_price_data(
            beg_date, end_date, "daily")
        ohlv=json_obj[ticker]['prices']
        temp=pd.DataFrame(
            ohlv)[["formatted_date", "adjclose", "open", "low", "high", "volume"]]
        temp.set_index("formatted_date", inplace=True)
        temp.dropna(inplace=True)
        temp['ticker']=ticker
        prices=pd.concat([prices, temp])
        #prices.set_index("formatted_date", inplace=True)
    return prices


def ExtractIncomeStatement(all_tickers):

    # Extract Income Statement
    dict_df={}
    for ticker in all_tickers:
        yahoo_financials=YahooFinancials(ticker)
        income_statement_qt=yahoo_financials.get_financial_stmts(
            'quarterly', 'income', reformat=True)
        i=income_statement_qt.get('incomeStatementHistoryQuarterly')
        flattenJSON=flatten(i)
        dict_df.update(flattenJSON)

    keys=[key.split('_') for key in dict_df.keys()]
    values=list(dict_df.values())
    df=pd.DataFrame(keys)
    df['Value']=values
    df.rename(columns={0: 'Ticker', 1: 'Ref',
                       2: 'Period', 3: 'Item'}, inplace=True)
    df=df.drop(columns="Ref")
    df.index=[x for x in range(0, len(df.values))]
    df.index.name='id'
    modDf=df.apply(lambda x: FixItemName(x) if x.name == 'Item' else x)
    return modDf


all_tickers=["AAPL", "MSFT"]
income=ExtractIncomeStatement(all_tickers)
prices=ExtractPrices(all_tickers)


t="MSFT"
riskfreereturn=0.02
price=prices[(prices.ticker == t)]


cagr=CAGR(price)
vol=volatility(price)
sharpe=sharpe(price, riskfreereturn)
sortino=sortino(price, riskfreereturn)

print(f"CAGR for {t} is {cagr:.3%}")
print(f"Volatility for {t} is {vol:.3%}")
print(f"Sharpe Index for {t} is {sharpe:.3}")
print(f"Sortino for {t} is {sortino:.3}")

#print(prices)
#print(income)
