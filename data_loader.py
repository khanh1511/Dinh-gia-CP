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
            df = stock.company.shareholders()
            if df is not None and not df.empty:
                if 'update_date' in df.columns:
                    df = df.sort_values(by='update_date', ascending=False)
                
                name_col = None
                for c in ['share_holder', 'shareHolder', 'shareholder', 'Tên Cổ Đông']:
                    if c in df.columns:
                        name_col = c
                        break
                
                if name_col:
                    df = df.drop_duplicates(subset=[name_col], keep='first')
            return df
    except: pass
    return pd.DataFrame()
