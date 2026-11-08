"""Content Impact Lab — synthetic attribution and prioritization sandbox."""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Content Impact Lab", page_icon="📈", layout="wide")
st.title("Content Impact Lab")
st.caption("Explore how editorial investment and attribution assumptions change a B2B content portfolio's apparent impact.")
st.warning("All figures are synthetic and illustrative, not actual employer, campaign or Salesforce data.", icon="ℹ️")
data = pd.DataFrame([
    {"Program":"Executive thought leadership","Spend":24000,"Views":62000,"Engaged":7100,"Influenced pipeline":540000,"Sourced pipeline":85000,"Tier":1},
    {"Program":"Flagship original research","Spend":36000,"Views":88000,"Engaged":12400,"Influenced pipeline":880000,"Sourced pipeline":185000,"Tier":1},
    {"Program":"Product launch narrative","Spend":21000,"Views":51000,"Engaged":5800,"Influenced pipeline":690000,"Sourced pipeline":125000,"Tier":2},
    {"Program":"SEO educational articles","Spend":11000,"Views":112000,"Engaged":9600,"Influenced pipeline":260000,"Sourced pipeline":42000,"Tier":3},
    {"Program":"Automated social derivatives","Spend":4000,"Views":74000,"Engaged":3400,"Influenced pipeline":110000,"Sourced pipeline":12000,"Tier":4},
])
with st.sidebar:
    st.header("Attribution assumptions")
    credit = st.slider("Credit applied to influenced pipeline", 0, 100, 20, 5, format="%d%%") / 100
    sourced_credit = st.slider("Credit applied to sourced pipeline", 0, 100, 100, 5, format="%d%%") / 100
    budget = st.number_input("Incremental investment to allocate ($)", min_value=0, value=20000, step=5000)
    st.caption("Influenced and sourced pipeline can overlap. The model is a scenario index, not audited ROI.")
data["Weighted pipeline index"] = data["Influenced pipeline"] * credit + data["Sourced pipeline"] * sourced_credit
data["Index / spend"] = (data["Weighted pipeline index"] / data["Spend"]).round(2)
a,b,c=st.columns(3)
a.metric("Synthetic spend", f"${data['Spend'].sum():,.0f}")
b.metric("Synthetic influenced pipeline", f"${data['Influenced pipeline'].sum():,.0f}")
c.metric("Weighted pipeline index", f"${data['Weighted pipeline index'].sum():,.0f}")
st.subheader("Portfolio comparison")
st.bar_chart(data.set_index("Program")[["Spend","Weighted pipeline index"]])
st.dataframe(data, use_container_width=True, hide_index=True)
st.subheader("Scenario: allocate incremental budget")
top = data.sort_values("Index / spend", ascending=False).iloc[0]
st.write(f"Under these assumptions, **{top['Program']}** has the highest weighted pipeline index per dollar of synthetic spend ({top['Index / spend']:.2f}).")
st.write(f"Allocating ${budget:,.0f} at the same modeled efficiency would imply a **${budget * top['Index / spend']:,.0f} weighted pipeline index**. This is a linear what-if calculation, not a forecast or causal estimate.")
st.download_button("Download synthetic scenario CSV", data.to_csv(index=False), "content-impact-synthetic.csv", "text/csv")
