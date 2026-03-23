import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from data_loader import fetch_company_profile, fetch_financial_ratio
from bank_analysis import is_bank, analyze_bank_ratios
from valuation_models import evaluate_stock, graham_valuation, intrinsic_valuation_pe, get_val

for symbol in ["FPT", "VCB"]:
    print(f"\n--- Testing {symbol} ---")
    profile = fetch_company_profile(symbol)
    print("Is Bank?", is_bank(profile))
    
    ratios = fetch_financial_ratio(symbol)
    if not ratios.empty:
        latest = ratios.iloc[0]
        eps = get_val(latest, ['eps'])
        bvps = get_val(latest, ['bvps'])
        pe = get_val(latest, ['p/e'])
        print(f"EPS: {eps}, BVPS: {bvps}, PE: {pe}")
        
        pros, cons = evaluate_stock(ratios)
        print("Pros:", len(pros), "Cons:", len(cons))
        
        if is_bank(profile):
            bank_info = analyze_bank_ratios(ratios)
            print("Bank Metrics:", bank_info)
    else:
        print("Ratios empty")
