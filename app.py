import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. إعدادات الواجهة المتجاوبة (Responsive)
st.set_page_config(
    page_title="Khadija Fashion System",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. تصميم عصري يناسب الملابس والعناية بالبشرة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #fdfaf7; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3em;
        background-color: #d4a373; color: white; border: none; font-weight: bold;
    }
    .stMetric { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    @media (max-width: 600px) { .stButton>button { font-size: 16px !important; } }
    </style>
    """, unsafe_allow_html=True)

# 3. وظائف إدارة البيانات
def load_data(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame()

SALES_FILE = "sales_log.csv"
INV_FILE = "inventory_log.csv"

# 4. واجهة تسجيل الدخول
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("✨ Khadija Fashion")
    st.subheader("تسجيل الدخول للمنظومة")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "admin" and pw == "khadija2026":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
    st.stop()

# 5. القائمة الجانبية
st.sidebar.title("القائمة الرئيسية")
choice = st.sidebar.radio("انتقل إلى:", ["🛒 نقطة البيع", "📦 المخزن والتنبيهات", "📊 التقارير والإحصائيات"])

# --- القسم الأول: نقطة البيع ---
if choice == "🛒 نقطة البيع":
    st.header("إصدار فاتورة جديدة")
    inv = load_data(INV_FILE)
    
    if inv.empty:
        st.warning("المخزن فارغ! أضف منتجات أولاً من قسم المخزن.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            prod = st.selectbox("اختر المنتج", inv['المنتج'].unique())
            qty = st.number_input("الكمية", min_value=1, step=1)
            disc = st.number_input("خصم إضافي (ج.م)", min_value=0.0, value=0.0)
            
        item_info = inv[inv['المنتج'] == prod].iloc[0]
        price = item_info['سعر_البيع']
        total = (price * qty) - disc
        
        with col2:
            st.metric("سعر الوحدة", f"{price} ج.م")
            st.metric("الإجمالي النهائي", f"{total} ج.م")
            
        if st.button("إتمام البيع وطباعة الفاتورة"):
            if item_info['الكمية'] < qty:
                st.error(f"الكمية غير كافية! المتاح: {item_info['الكمية']}")
            else:
                # تسجيل البيع
                new_s = {"التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                         "المنتج": prod, "الكمية": qty, "الخصم": disc, "الإجمالي": total, "القسم": item_info['القسم']}
                s_df = load_data(SALES_FILE)
                s_df = pd.concat([s_df, pd.DataFrame([new_s])], ignore_index=True)
                s_df.to_csv(SALES_FILE, index=False)
                
                # خصم من المخزن
                inv.loc[inv['المنتج'] == prod, 'الكمية'] -= qty
                inv.to_csv(INV_FILE, index=False)
                st.success("تم تسجيل الفاتورة بنجاح!")
                st.balloons()

# --- القسم الثاني: المخزن ---
elif choice == "📦 المخزن والتنبيهات":
    st.header("إدارة المنتجات والمخزون")
    
    with st.expander("➕ إضافة منتج جديد أو توريد بضاعة"):
        with st.form("add_form"):
            n = st.text_input("اسم المنتج")
            c = st.selectbox("القسم", ["ملابس", "عناية بالبشرة"])
            q = st.number_input("الكمية", min_value=0)
            p = st.number_input("سعر البيع للجمهور", min_value=0.0)
            d = st.date_input("تاريخ انتهاء الصلاحية (اختياري)")
            if st.form_submit_button("حفظ"):
                inv_df = load_data(INV_FILE)
                new_i = {"المنتج": n, "القسم": c, "الكمية": q, "سعر_البيع": p, "تاريخ_الصلاحية": d}
                inv_df = pd.concat([inv_df, pd.DataFrame([new_i])], ignore_index=True)
                inv_df.to_csv(INV_FILE, index=False)
                st.success("تم التحديث")

    inv_df = load_data(INV_FILE)
    if not inv_df.empty:
        st.subheader("⚠️ حالة المخزن")
        low = inv_df[inv_df['الكمية'] <= 5]
        if not low.empty:
            for _, r in low.iterrows():
                st.error(f"انتبه: منتج '{r['المنتج']}' شارف على الانتهاء! المتبقي: {r['الكمية']}")
        st.dataframe(inv_df, use_container_width=True)

# --- القسم الثالث: التقارير ---
elif choice == "📊 التقارير والإحصائيات":
    st.header("تقارير الأرباح والمبيعات")
    s_df = load_data(SALES_FILE)
    if not s_df.empty:
        st.metric("إجمالي الدخل", f"{s_df['الإجمالي'].sum()} ج.م")
        
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.pie(s_df, values='الإجمالي', names='القسم', title="مبيعات الأقسام")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(s_df, x="التاريخ", y="الإجمالي", title="حركة المبيعات اليومية")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.download_button("تصدير التقرير لـ Excel (CSV)", s_df.to_csv(index=False), "Khadija_Fashion_Report.csv")
    else:
        st.info("لا توجد مبيعات مسجلة حتى الآن.")
        
