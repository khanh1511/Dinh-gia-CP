import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from vnstock import Vnstock

try:
    stock = Vnstock().stock(symbol="VCB", source='VCI')
    
    print("--- Officers ---")
    officers = stock.company.officers()
    if not officers.empty:
        print(officers.head())
    else:
        print("Empty officers")
        
    print("\n--- Shareholders ---")
    shareholders = stock.company.shareholders()
    if not shareholders.empty:
        print(shareholders.head())
    else:
        print("Empty shareholders")

except Exception as e:
    print(e)
