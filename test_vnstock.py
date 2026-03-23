import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from vnstock3 import Vnstock

try:
    stock = Vnstock().stock(symbol='TCB', source='VCI')
    print("History:")
    print(stock.quote.history(start='2024-01-01', end='2024-01-10'))
    
    print("\nFinance Ratio:")
    print(stock.finance.ratio(period='year', get_all=False).head(2))
    
    print("\nBalance Sheet:")
    print(stock.finance.balance_sheet(period='year').head(2))

except Exception as e:
    print("Error:", e)
