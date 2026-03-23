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


def evaluate_shareholder_strength(shareholders_df):
    """Đánh giá sức mạnh nội tại dựa trên cơ cấu cổ đông."""
    if shareholders_df is None or shareholders_df.empty:
        return "Không có dữ liệu đủ để đánh giá."
        
    analysis = []
    
    # Chuẩn hóa tên cột để xử lý
    df = shareholders_df.rename(columns=lambda x: str(x).lower().strip())
    
    name_col = None
    pct_col = None
    for col in df.columns:
        if 'name' in col or 'cổ đông' in col or 'shareholder' in col:
            name_col = col
        if 'percent' in col or 'tỷ lệ' in col or 'own' in col:
            pct_col = col
            
    if not name_col or not pct_col:
        return "Cấu trúc dữ liệu cổ đông không chuẩn, không thể tự động phân tích."
        
    names = df[name_col].astype(str).str.lower().tolist()
    try:
        pcts = pd.to_numeric(df[pct_col], errors='coerce').fillna(0).tolist()
    except:
        pcts = [0]*len(names)
        
    total_large_shareholders = 0
    state_owned = 0
    foreign_funds = 0
    management = 0
    
    for name, pct in zip(names, pcts):
        pct_val = pct if pct < 1.5 else pct / 100.0 # Chuẩn hóa về dạng decimal (0.##)
        total_large_shareholders += pct_val
        
        # Nhóm Nhà nước
        if 'ủy ban' in name or 'ubnd' in name or 'bộ ' in name or 'scic' in name or 'nhà nước' in name or 'tập đoàn' in name:
            state_owned += pct_val
        # Nhóm Quỹ ngoại / Tổ chức lớn
        elif 'dragon' in name or 'vinacapital' in name or 'fund' in name or 'bank' in name or 'ltd' in name or 'holding' in name or 'pyn' in name or 'vanguard' in name:
            foreign_funds += pct_val
        # Cá nhân lãnh đạo (Tên người Việt 2-4 chữ không có từ khóa tổ chức)
        else:
            if len(name.split()) <= 4 and 'ctcp' not in name and 'công ty' not in name:
                management += pct_val
                
    if state_owned > 0.3:
        analysis.append("🏛️ **Tiềm lực Nhà nước:** Doanh nghiệp có bóng dáng Nhà nước nắm giữ tỷ trọng lớn. Điểm mạnh là cực kỳ an toàn, có lợi thế về pháp lý hoặc trúng thầu. Điểm yếu là tốc độ quyết định chiến lược có thể chậm, thiếu linh hoạt.")
        
    if foreign_funds > 0.05:
        analysis.append("🌍 **Bảo chứng từ Quỹ Ngoại / Tổ chức:** Có sự tham gia của các tổ chức chuyên nghiệp, khẳng định chất lượng tài sản và tính minh bạch tài chính cao (bị kiểm toán gắt gao).")
        
    if management > 0.15:
        analysis.append("👨‍💼 **Cam kết của Ban Lãnh đạo:** Lãnh đạo hoặc cá nhân nắm giữ lượng lớn cổ phiếu, cho thấy họ gắn chặt quyền lợi " + ("(skin in the game)" if management > 0.3 else "") + " với công ty. Cổ phần càng cô đặc vào ban điều hành, động lực đẩy giá trị doanh nghiệp càng cao.")
        
    free_float = max(0, 1.0 - total_large_shareholders)
    if free_float > 0.6:
        analysis.append("⚠️ **Cổ đông phân tán (Free-float cao):** Hơn một nửa công ty trôi nổi trên sàn. Cổ phiếu dễ bị đầu cơ, biến động mạnh theo tin đồn, thiếu " + '"người cầm lái"' + " kiểm soát cung cầu.")
    elif total_large_shareholders > 0.7:
        analysis.append("🔒 **Cô đặc (Free-float thấp):** Hầu hết cổ phần nằm trong két của cổ đông lớn. Nguồn cung khan hiếm, giá cổ phiếu dễ tăng mạnh nếu có kích vĩ mô tốt.")
        
    if not analysis:
        return "Cơ cấu phân bổ khá trung tính, không có nhóm quyền lực nào thực sự làm chủ hoặc dữ liệu đang bị ẩn."
        
    return "\n\n".join(analysis)
