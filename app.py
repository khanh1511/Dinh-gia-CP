import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import (fetch_historical_price, fetch_company_profile, 
                         fetch_financial_ratio, fetch_balance_sheet, fetch_officers, fetch_shareholders)
from valuation_models import intrinsic_valuation_pe, graham_valuation, evaluate_stock, get_val, evaluate_macro_industry, evaluate_shareholder_strength
from bank_analysis import is_bank, analyze_bank_ratios

st.set_page_config(page_title="Hệ Thống Định Giá Cổ Phiếu", layout="wide", page_icon="💹")

def local_css():
    st.markdown("""
    <style>
    .main-header { font-family: 'Inter', sans-serif; font-size: 38px !important; font-weight: 800; color: #1E3A8A; margin-bottom: -15px; }
    .sub-header { font-size: 18px; color: #64748B; margin-bottom: 25px; }
    .card-box { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; margin-bottom: 20px; transition: transform 0.2s; }
    .card-box:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    .val-title { font-size: 14px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .val-value { font-size: 28px; font-weight: 700; color: #0F172A; margin-top: 5px; }
    .val-highlight { color: #059669; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 25px; background-color: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0; font-weight: 600; color: #475569; transition: all 0.3s; }
    .stTabs [aria-selected="true"] { background-color: #2563EB !important; color: white !important; border: None; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3); }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Sidebar
st.sidebar.markdown('<h2>🔍 Bộ Lọc Cổ Phiếu</h2>', unsafe_allow_html=True)
ticker = st.sidebar.text_input("Nhập mã cổ phiếu (VD: FPT, VCB, HPG):", "FPT").upper().strip()
year_back = st.sidebar.slider("Lịch sử giá (Năm):", 1, 5, 1)

analyze_btn = st.sidebar.button("📊 Bắt Đầu Phân Tích", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Gợi ý:** Nhập mã Ngân hàng như VCB, BID, MBB để kích hoạt chức năng lọc nợ xấu chuyên sâu.")

if analyze_btn:
    if ticker:
        with st.spinner(f"🚀 Đang thu thập và phân tích dữ liệu `{ticker}`..."):
            profile_df = fetch_company_profile(ticker)
            price_df = fetch_historical_price(ticker, year_back)
            ratios_df = fetch_financial_ratio(ticker)
            bs_df = fetch_balance_sheet(ticker)
            officers_df = fetch_officers(ticker)
            shareholders_df = fetch_shareholders(ticker)
            
            
            if (profile_df is None or profile_df.empty) and (price_df is None or price_df.empty):
                st.error(f"❌ Không tìm thấy dữ liệu cho mã cổ phiếu {ticker}. Vui lòng kiểm tra lại mã.")
                st.warning("⚠️ **Lưu ý đối với Streamlit Cloud (Github):** Vì bạn đang triển khai trên server nước ngoài, các nhà mạng/nguồn cấp dữ liệu chứng khoán Việt Nam (VCI, SSI...) thường sẽ chặn các dải IP quốc tế để chống Scraping. Điều này khiến Streamlit Cloud không kéo được Data tự động và trả về Rỗng. Bạn nên chạy App nội bộ trên máy cá nhân, hoặc cấu hình HTTP Proxy VN trong mã nguồn.")
            else:
                st.markdown(f'<div class="main-header">Báo Cáo Phân Tích Chi Tiết: {ticker}</div>', unsafe_allow_html=True)
                info = profile_df.iloc[0] if profile_df is not None and not profile_df.empty else {}
                company_name = info.get('companyName', info.get('ticker', ticker))
                industry = info.get("industry", info.get("sector", "N/A"))
                exchange = info.get("exchange", "N/A")
                st.markdown(f'<div class="sub-header">{company_name} | Lĩnh vực: {industry} | Sàn: {exchange}</div>', unsafe_allow_html=True)
                
                # Format to 2 decimals utility
                def format_2_dec(val):
                    try: return f"{float(val):,.2f}"
                    except: return val
                
                # --- Xây dựng Tabs ---
                tabs = ["📈 Kỹ Thuật & Giá", "💰 Sức Khoẻ Tài Chính", "🎯 Định Giá Nội Tại", "🕵️ Chất Lượng Doanh Nghiệp (Vĩ Mô & Cán Bộ)", "🏦 Phân Tích Ngân Hàng"]
                bank_flag = is_bank(profile_df)
                if not bank_flag:
                    tabs.remove("🏦 Phân Tích Ngân Hàng")
                    
                ui_tabs = st.tabs(tabs)
                
                # Tab 1: Kỹ Thuật 
                with ui_tabs[0]:
                    if price_df is not None and not price_df.empty:
                        if all(x in price_df.columns for x in ['open', 'high', 'low', 'close', 'time']):
                            fig = go.Figure(data=[go.Candlestick(x=price_df['time'], open=price_df['open'], high=price_df['high'], low=price_df['low'], close=price_df['close'])])
                            fig.update_layout(title="", xaxis_rangeslider_visible=False, height=500, template="plotly_white", margin=dict(l=0,r=0,t=10,b=0))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            fig = px.area(price_df, x='time', y='close', title="")
                            fig.update_layout(height=400, template="plotly_white", margin=dict(l=0,r=0,t=10,b=0))
                            st.plotly_chart(fig, use_container_width=True)
                
                # Tab 2: Sức khỏe Tài chính
                with ui_tabs[1]:
                    if ratios_df is not None and not ratios_df.empty:
                        st.markdown("**Bảng Chỉ số (Làm tròn 2 chữ số thập phân)**")
                        # Format all data to 2 decimal places properly regardless of DF shape
                        try:
                            if 'item' in ratios_df.columns or 'item_id' in ratios_df.columns or any(c for c in ratios_df.columns if str(ratios_df[c].dtype)=='object'):
                                styled_ratios = ratios_df.head(15).map(lambda x: format_2_dec(x) if pd.notna(x) and not isinstance(x, str) else x)
                            else:
                                styled_ratios = ratios_df.head(5).T.map(lambda x: format_2_dec(x) if pd.notna(x) else "N/A")
                        except:
                            styled_ratios = ratios_df.head(5).T
                            
                        st.dataframe(styled_ratios, use_container_width=True, height=500)
                    else:
                        st.warning("Không có dữ liệu chi tiết báo cáo tài chính.")
                
                # Tab 3: Định Giá
                with ui_tabs[2]:
                    if ratios_df is not None and not ratios_df.empty:
                        eps = get_val(ratios_df, ['eps', 'thu nhập trên mỗi cổ phần'])
                        bvps = get_val(ratios_df, ['bvps', 'giá trị sổ sách'])
                        pe = get_val(ratios_df, ['p/e', 'price to earning']) 
                        
                        eps_val = eps if pd.notna(eps) and float(eps) > 0 else 0
                        bvps_val = bvps if pd.notna(bvps) and float(bvps) > 0 else 0
                        pe_val = pe if pd.notna(pe) and float(pe) > 0 else 15
                        
                        graham_val = graham_valuation(eps_val, bvps_val)
                        intrinsic_pe = intrinsic_valuation_pe(eps_val, pe_val)
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.markdown(f'<div class="card-box"><div class="val-title">EPS Trượt (Thu nhập/CP)</div><div class="val-value">{eps_val:,.2f} <span style="font-size: 16px; color:#64748B">VNĐ</span></div></div>', unsafe_allow_html=True)
                        with c2:
                            st.markdown(f'<div class="card-box"><div class="val-title">Giá Trị Thực (Benjamin Graham)</div><div class="val-value val-highlight">{graham_val:,.2f} <span style="font-size: 16px; color:#64748B">VNĐ</span></div></div>', unsafe_allow_html=True)
                        with c3:
                            st.markdown(f'<div class="card-box"><div class="val-title">Chiết khấu theo P/E</div><div class="val-value val-highlight">{intrinsic_pe:,.2f} <span style="font-size: 16px; color:#64748B">VNĐ</span></div></div>', unsafe_allow_html=True)
                        
                        st.markdown("### ⚖️ Bảng So Sánh & Lựa Chọn Giá Trị Định Giá")
                        # Average with safety margin or similar logic
                        if graham_val > 0 and intrinsic_pe > 0:
                            final_val = (graham_val + intrinsic_pe) / 2
                            method_choice = "Trung bình Trọng số (Kết hợp cả dòng tiền và tài sản)"
                        elif graham_val > 0:
                            final_val = graham_val
                            method_choice = "Benjamin Graham (Do thiếu P/E hợp lệ)"
                        else:
                            final_val = intrinsic_pe
                            method_choice = "Nhân P/E Tương đối (Do thiếu BVPS bổ trợ)"
                        
                        current_price_raw = price_df.iloc[-1]['close'] if price_df is not None and not price_df.empty else 0
                        # Nếu current_price_raw < 1000, có khả năng đang hiển thị theo đơn vị nghìn VNĐ, cần nhân 1000
                        current_price = current_price_raw * 1000 if current_price_raw > 0 and current_price_raw < 1000 else current_price_raw
                        
                        margin_of_safety = ((final_val - current_price) / final_val * 100) if final_val > 0 else 0
                        upside = ((final_val - current_price) / current_price * 100) if current_price > 0 else 0
                        
                        comp_data = {
                            "Phương Pháp": ["Benjamin Graham", "P/E Tương Đối", "**Giá Hiện Tại (Thị Trường)**"],
                            "Giá Trị Định Giá": [f"{graham_val:,.0f} VNĐ", f"{intrinsic_pe:,.0f} VNĐ", f"{current_price:,.0f} VNĐ"],
                            "Cơ sở Phân tích": ["Đại diện cho sức mạnh Tài sản (BVPS) & Lợi nhuận nội tại (EPS)", "Đại diện cho Sự chấp nhận của thị trường (Trung bình ngành)", "Giá khớp lệnh trên sàn chứng khoán hiện tại"]
                        }
                        st.table(pd.DataFrame(comp_data))
                        
                        st.markdown(f'''
                        <div style="background-color: #ECFDF5; padding: 25px; border-radius: 12px; border-left: 6px solid #10B981; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            <h4 style="color: #047857; margin-top: 0; font-size: 22px;">🎯 KẾT LUẬN ĐỊNH GIÁ: <span style="color: #059669;">{final_val:,.0f} VNĐ</span></h4>
                            <p style="font-size: 16px; color: #374151;">Dựa trên phân tích nhiều mô hình, hệ thống khuyến nghị <b>{method_choice}</b> để có cái nhìn khách quan nhất.</p>
                            <p style="font-size: 18px; margin-top: 15px;">Tiềm năng tăng giá (Upside): <span style="color: {'#059669' if upside > 0 else '#DC2626'}; font-weight: bold; font-size: 24px;">{upside:+.2f}%</span></p>
                            <p style="font-size: 18px; margin-top: 5px;">Biên An Toàn (Margin of Safety): <span style="color: {'#059669' if margin_of_safety > 0 else '#DC2626'}; font-weight: bold; font-size: 20px;">{margin_of_safety:+.2f}%</span></p>
                            <p style="font-style: italic; color: #6B7280; font-size: 14px;">(Nguyên tắc Margin of Safety của Benjamin Graham: Cổ phiếu chỉ nên mua khi Biên an toàn > 30%. Nếu (-) cổ phiếu đang bị định giá đắt so với giá trị nội tại).</p>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        st.markdown("### 🔍 Phân Tích Cơ Bản (Trí Tuệ Nhân Tạo)")
                        pros, cons = evaluate_stock(ratios_df)
                        cp1, cp2 = st.columns(2)
                        with cp1: st.success("**🚀 ĐIỂM SÁNG (Ưu Điểm):**\n\n" + (" \n\n".join(["- " + p for p in pros]) if pros else "Cần theo dõi báo cáo quý. "))
                        with cp2: st.error("**⚠️ RỦI RO (Nhược Điểm):**\n\n" + (" \n\n".join(["- " + c for c in cons]) if cons else "Chưa phát hiện rủi ro cơ bản rõ rệt."))
                            
                # Tab 4: Chất lượng Doanh nghiệp (Vĩ mô & Lãnh đạo)
                idx = 3
                with ui_tabs[idx]:
                    st.markdown("### 🌍 Bối cảnh Vĩ mô & Ngành")
                    st.info(evaluate_macro_industry(industry))
                    
                    st.markdown("---")
                    cr1, cr2 = st.columns(2)
                    with cr1:
                        st.markdown("### 👥 Ban Lãnh Đạo (Officers)")
                        if officers_df is not None and not officers_df.empty:
                            display_off = officers_df.rename(columns={'officer_name': 'Họ Tên', 'officer_position': 'Chức vụ'}).head(10)
                            st.dataframe(display_off[['Họ Tên', 'Chức vụ'] if 'Chức vụ' in display_off.columns else display_off.columns], use_container_width=True, hide_index=True)
                        else:
                            st.warning("Dữ liệu Ban lãnh đạo chưa được cập nhật.")
                            
                    with cr2:
                        st.markdown("### 🏦 Cơ cấu Cổ đông (Shareholders)")
                        if shareholders_df is not None and not shareholders_df.empty:
                            display_sh = shareholders_df.rename(columns={'shareHolder': 'Tên Cổ Đông', 'ownPercent': 'Tỷ lệ sở hữu (%)'}).head(10)
                            
                            # Vẽ biểu đồ tròn cơ cấu cổ đông
                            try:
                                if 'Tỷ lệ sở hữu (%)' in display_sh.columns:
                                    pie_data = display_sh.copy()
                                    # Ép kiểu về float để tính toán
                                    pie_data['Tỷ lệ sở hữu (%)'] = pd.to_numeric(pie_data['Tỷ lệ sở hữu (%)'], errors='coerce').fillna(0)
                                    total_own = pie_data['Tỷ lệ sở hữu (%)'].sum()
                                    
                                    # Thêm dòng 'Cổ đông khác / Free-float' nếu tổng < 1.0 (hoặc nếu là % thì < 100)
                                    threshold = 1.0 if total_own <= 1.5 else 100.0
                                    if total_own < threshold:
                                        other_row = pd.DataFrame([{'Tên Cổ Đông': 'Cổ đông khác (Free-float)', 'Tỷ lệ sở hữu (%)': threshold - total_own}])
                                        pie_data = pd.concat([pie_data, other_row], ignore_index=True)
                                    
                                    fig_pie = px.pie(pie_data, values='Tỷ lệ sở hữu (%)', names='Tên Cổ Đông', hole=0.4, title="")
                                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                                    fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=350)
                                    st.plotly_chart(fig_pie, use_container_width=True)
                            except Exception as e:
                                pass
                            
                            if 'Tỷ lệ sở hữu (%)' in display_sh.columns:
                                display_sh['Tỷ lệ sở hữu (%)'] = display_sh['Tỷ lệ sở hữu (%)'].apply(lambda x: format_2_dec(float(x) * 100 if float(x) < 1.5 else float(x)))
                            st.dataframe(display_sh, use_container_width=True, hide_index=True)
                            
                            st.markdown("---")
                            st.markdown("#### 🧠 AI Phân Tích Sức Mạnh Cổ Đông")
                            strength_analysis = evaluate_shareholder_strength(shareholders_df)
                            st.info(strength_analysis)
                        else:
                            st.warning("Dữ liệu Cổ đông chưa được cập nhật.")
                
                # Tab 5: Ngân hàng
                if bank_flag:
                    with ui_tabs[-1]:
                        bank_info = analyze_bank_ratios(bs_df, ratios_df)
                        if bank_info:
                            st.markdown('<h5>Chỉ số An Toàn & Hiệu Quả Hoạt Động Ngân Hàng</h5>', unsafe_allow_html=True)
                            st.info("💡 **Tỷ lệ nợ xấu (NPL):** Dưới 3% là mức an toàn.\n\n💡 **Tỷ lệ bao phủ nợ xấu (LLR):** Càng cao (>100%) nghĩa là ngân hàng dự phòng càng dư dả, lợi nhuận tiềm năng trong tương lai sẽ lớn.\n\n💡 **Tỷ lệ CASA:** Tiền gửi không kỳ hạn giá rẻ, tỷ lệ càng cao thì biên lãi thuần (NIM) càng hưởng lợi.")
                            cols = st.columns(len(bank_info))
                            i = 0
                            for k, v in bank_info.items():
                                with cols[i]:
                                    st.markdown(f'<div class="card-box" style="text-align: center;"><div class="val-title">{k}</div><div class="val-value" style="color: #0369a1;">{v}</div></div>', unsafe_allow_html=True)
                                i += 1
                        else:
                            st.warning("Dữ liệu chỉ số Ngân hàng không khả dụng.")
