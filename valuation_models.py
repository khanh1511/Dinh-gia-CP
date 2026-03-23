import pandas as pd

def intrinsic_valuation_pe(eps, avg_pe):
    try:
        if pd.isna(eps) or pd.isna(avg_pe): return 0
        return float(eps) * float(avg_pe)
    except: return 0

def graham_valuation(eps, bvps):
    try:
        if pd.isna(eps) or pd.isna(bvps): return 0
        eps, bvps = float(eps), float(bvps)
        if eps > 0 and bvps > 0: return (22.5 * eps * bvps) ** 0.5
        return 0
    except: return 0
    
def get_val(latest, keywords):
    for col in latest.index:
        for kw in keywords:
            if kw.lower() in str(col).lower():
                return latest[col]
    return 0
    
def evaluate_stock(ratios_df):
    pros, cons = [], []
    if ratios_df.empty: return pros, cons
    latest = ratios_df.iloc[0]
    roe = get_val(latest, ['roe'])
    debt = get_val(latest, ['debt/equity', 'debt on equity', 'tỷ lệ nợ'])
    
    if pd.notna(roe) and float(roe) > 0.15:
        val = float(roe)
        roe_fmt = f"{val * 100:,.2f}%" if val < 1 else f"{val:,.2f}%"
        pros.append(f"Mức sinh lời cổ đông (ROE) rất tốt: {roe_fmt}.")
    elif pd.notna(roe) and float(roe) > 0 and float(roe) < 0.1:
        cons.append("Hiệu quả sử dụng vốn (ROE) khá thấp (<10%).")
        
    if pd.notna(debt) and float(debt) > 1.5:
        cons.append("Đòn bẩy tài chính (Debt/Equity) lớn (>1.5), tiềm ẩn rủi ro trả nợ.")
    elif pd.notna(debt) and float(debt) > 0 and float(debt) < 0.5:
        pros.append("Cấu trúc vốn an toàn, dư địa vay mượn tốt.")
        
    return pros, cons

def evaluate_macro_industry(industry):
    """Đánh giá cơ bản Vĩ mô dựa trên ngành nghề."""
    industry = str(industry).lower()
    macro = ""
    if 'ngân hàng' in industry or 'bank' in industry:
        macro = "Ngành Ngân hàng nhạy cảm với chính sách tiền tệ, lãi suất điều hành và tăng trưởng tín dụng quốc gia. Trong môi trường nới lỏng tiền tệ, ngân hàng có biên lãi thuần (NIM) tốt hơn và giảm áp lực nợ xấu."
    elif 'bất động sản' in industry or 'real estate' in industry:
        macro = "Ngành Bất động sản bị ảnh hưởng mạnh bởi cung tiền, lãi suất vay mua nhà và chính sách gỡ vướng pháp lý từ Chính phủ. Chu kỳ vĩ mô phục hồi sẽ hỗ trợ lớn."
    elif 'vật liệu' in industry or 'thép' in industry or 'xây dựng' in industry:
        macro = "Nhóm Đầu tư công và Vật liệu xây dựng hưởng lợi trực tiếp từ các động thái giải ngân vốn ngân sách và đại công trình hạ tầng của Chính phủ."
    elif 'bán lẻ' in industry or 'tiêu dùng' in industry:
        macro = "Ngành Bán lẻ phụ thuộc vào tổng mức bán lẻ hàng hóa, dịch vụ và CPI. Chỉ báo vĩ mô về thu nhập khả dụng của dân cư quyết định động lực tăng trưởng."
    else:
        macro = "Cần theo dõi các chính sách kích cầu kinh tế, tỷ giá hối đoái và lạm phát. Lãi suất duy trì ở mức thấp sẽ là điểm tựa chung cho thị trường chứng khoán."
    return macro
