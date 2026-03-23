from vnstock import Vnstock
import pandas as pd
import datetime

def get_stock(symbol):
    try:
        return Vnstock().stock(symbol=symbol, source='VCI')
    except:
        try:
            return Vnstock().stock(symbol=symbol, source='KBS')
        except:
            return None

def fetch_historical_price(symbol, years_back=1):
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365*years_back)).strftime('%Y-%m-%d')
    try:
        stock = get_stock(symbol)
        if stock:
            return stock.quote.history(start=start_date, end=end_date)
    except: pass
    return pd.DataFrame()

def fetch_company_profile(symbol):
    try:
        stock = get_stock(symbol)
        if stock:
            try: return stock.company.overview()
            except: pass
    except: pass
    return pd.DataFrame()

def flatten_multi_index(df):
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns]
    return df

def fetch_financial_ratio(symbol):
    try:
        stock = get_stock(symbol)
        if stock:
            ratios = stock.finance.ratio(period='year', get_all=True)
            return flatten_multi_index(ratios)
    except: pass
    return pd.DataFrame()

def fetch_balance_sheet(symbol):
    try:
        stock = get_stock(symbol)
        if stock:
            bs = stock.finance.balance_sheet(period='year')
            return flatten_multi_index(bs)
    except: pass
    return pd.DataFrame()

def fetch_officers(symbol):
    try:
        stock = get_stock(symbol)
        if stock:
            return stock.company.officers()
    except: pass
    return pd.DataFrame()

def fetch_shareholders(symbol):
    try:
        stock = get_stock(symbol)
        if stock:
            return stock.company.shareholders()
    except: pass
    return pd.DataFrame()
