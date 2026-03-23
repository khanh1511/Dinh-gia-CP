import pandas as pd
from valuation_models import get_val

def is_bank(profile_df):
    if profile_df is None or profile_df.empty: return False
    for col in profile_df.columns:
        if 'industry' in col.lower() or 'ngành' in col.lower() or 'sector' in col.lower():
            val = str(profile_df.iloc[0].get(col, '')).lower()
            if 'ngân hàng' in val or 'bank' in val: return True
    symbol = profile_df.iloc[0].get('ticker', '')
    if isinstance(symbol, str) and symbol in ['VCB', 'BID', 'CTG', 'MBB', 'TCB', 'VPB', 'ACB', 'HDB', 'VIB', 'STB', 'SHB', 'LPB', 'EIB', 'MSB', 'OCB', 'SSB', 'BAB']:
        return True
    return False

def analyze_bank_ratios(bs_df, ratios_df):
    """
    Sử dụng kết hợp 2 DataFrame để lấy càng nhiều chỉ số Ngân hàng càng tốt.
    """
    bank_info = {}
    if ratios_df is None or ratios_df.empty: return bank_info
    
    bad_debt = get_val(ratios_df, ['npl', 'nợ xấu', 'bad debt'])
    llr = get_val(ratios_df, ['llr', 'bao phủ', 'coverage'])
    nim = get_val(ratios_df, ['nim', 'net interest margin', 'biên lãi thuần'])
    casa = get_val(ratios_df, ['casa'])
            
    def format_ratio(val, is_percentage=False):
        try:
            val = float(val)
            # Giả định nếu giá trị < 1 thì nó là số thập phân của phần trăm
            if val < 2 and is_percentage: return f"{val * 100:,.2f}%"
            elif val > 0: return f"{val:,.2f}%"
            return "N/A"
        except: return "N/A"

    bank_info['Tỷ lệ nợ xấu (NPL)'] = format_ratio(bad_debt, True)
    bank_info['Bao phủ nợ xấu (LLR)'] = format_ratio(llr, False)
    bank_info['Biên lãi thuần (NIM)'] = format_ratio(nim, True)
    if casa is not None:
        bank_info['Tỷ lệ CASA'] = format_ratio(casa, True)
    else:
        bank_info['Tỷ lệ CASA'] = "N/A"
        
    return bank_info
