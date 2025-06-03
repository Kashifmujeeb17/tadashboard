import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📊 Talent Acquisition Dashboard - Prototype")

# --- Load Data from CSV or Use Sample ---
uploaded_file = st.sidebar.file_uploader("📂 Upload TA Data CSV", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, parse_dates=["Date"])
    st.sidebar.success("✅ CSV loaded successfully!")
else:
    st.sidebar.info("ℹ️ No CSV uploaded. Using sample data.")
    data = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=16, freq="W"),
        "Partner": ["Aniya", "Asif Noor", "Fahad Saeed", "Fatima", "Hira Yaqoob", "Mujtaba", "Munira", "Waqas Zaheer"] * 2,
        "Stage": ["Interview in Process", "Documents", "Salary Negotiation", "Under Decision", "Approval in Process", "Yet to Accept", "Yet to Join", "Interview in Process"] * 2,
        "Cases": [10, 5, 3, 4, 2, 6, 7, 8] * 2,
        "Joiners": [20, 5, 10, 7, 3, 8, 6, 9] * 2,
        "Leavers": [5, 2, 4, 3, 1, 2, 3, 4] * 2,
        "Gender": ["Male", "Female"] * 8,
        "Source": ["LinkedIn", "Referral", "Indeed", "Website", "LinkedIn", "Referral", "Indeed", "Website"] * 2,
        "TimeToHire": [12, 18, 22, 15, 19, 25, 17, 14] * 2,
        "Position": ["Analyst", "Manager", "Analyst", "Lead", "Manager", "Analyst", "Lead", "Manager"] * 2
    })

# --- Sidebar Filter ---
st.sidebar.header("Filter TA Dashboard")
ta_filter = st.sidebar.selectbox("Select TA Partner", ["All"] + sorted(data["Partner"].unique().tolist()))
date_range = st.sidebar.date_input("Select Date Range", [data["Date"].min(), data["Date"].max()])

filtered_data = data.copy()
if ta_filter != "All":
    filtered_data = filtered_data[filtered_data["Partner"] == ta_filter]
filtered_data = filtered_data[(filtered_data["Date"] >= pd.to_datetime(date_range[0])) & (filtered_data["Date"] <= pd.to_datetime(date_range[1]))]

# --- Download CSV ---
st.sidebar.download_button("📥 Download Filtered Data", filtered_data.to_csv(index=False), file_name="filtered_ta_data.csv")

# --- Top Metrics ---
with st.container():
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        st.metric("📨 Offer Letters Issued", "105")
        st.metric("📊 Budgeted HC", "4,579")
        st.metric("👥 YTD Joiners", "1,279")
    with col2:
        st.metric("🔄 In Process Cases", "144")
        st.metric("✅ Actual HC", "4,491")
        st.metric("👋 YTD Leavers", "1,009")
    with col3:
        st.metric("🧮 HC Variance", "88")
        st.metric("💼 Cost Variance", "-285")

# --- 3x3 Layout with Drill-down and Interactivity ---
with st.container():
    col1, col2, col3 = st.columns([1.1, 1.1, 0.8])
    with col1:
        st.markdown("### 👥 TA Partners")
        partner_cases = data.groupby("Partner")["Cases"].sum().reset_index()
        fig_partner = px.bar(partner_cases, x="Partner", y="Cases", text="Cases")
        st.plotly_chart(fig_partner, use_container_width=True)

    with col2:
        st.markdown("### 🛠️ Hiring in Process")
        hiring_stages = filtered_data.groupby("Stage")["Cases"].sum().reset_index()
        fig_hiring = px.bar(hiring_stages, x="Cases", y="Stage", orientation="h", text="Cases")
        st.plotly_chart(fig_hiring, use_container_width=True)

    with col3:
        st.markdown("### 🧬 DEI (Gender Diversity)")
        dei_data = filtered_data["Gender"].value_counts().reset_index()
        dei_data.columns = ["Gender", "Count"]
        fig_dei = px.pie(dei_data, names='Gender', values='Count', hole=0.5)
        st.plotly_chart(fig_dei, use_container_width=True)

with st.container():
    col1, col2, col3 = st.columns([1.3, 1, 1.1])
    with col1:
        st.markdown("### 📉 Budget vs Actual Headcount")
        months = [f"M-{i}" for i in range(1, 13)] + ["Current"]
        budgeted_hc = [300, 340, 370, 390, 400, 410, 420, 440, 450, 460, 470, 480, 4579]
        actual_hc = [290, 320, 350, 370, 380, 400, 410, 420, 430, 445, 460, 470, 4491]
        hc_df = pd.DataFrame({"Month": months, "Budgeted HC": budgeted_hc, "Actual HC": actual_hc})
        fig_hc = px.bar(hc_df, x="Month", y=["Budgeted HC", "Actual HC"], barmode="group")
        st.plotly_chart(fig_hc, use_container_width=True)

    with col2:
        st.markdown("### 💸 Budget vs Actual Cost")
        cost_df = pd.DataFrame({
            "Category": ["Budget", "Actual"],
            "Amount": [6211, 6496]
        })
        fig_cost = px.bar(cost_df, x="Category", y="Amount", color="Category", text="Amount")
        st.plotly_chart(fig_cost, use_container_width=True)

    with col3:
        st.markdown("### 👥 Joiner vs Leaver by Gender")
        joiner_leaver_df = filtered_data.groupby("Gender")[["Joiners", "Leavers"]].sum().reset_index()
        fig_jl = px.bar(joiner_leaver_df, x="Gender", y=["Joiners", "Leavers"], barmode="group")
        st.plotly_chart(fig_jl, use_container_width=True)

# --- Funnel Chart for Candidate Pipeline ---
with st.container():
    st.markdown("### 🔽 Candidate Pipeline Funnel")
    funnel_data = filtered_data.groupby("Stage")["Cases"].sum().reset_index()
    funnel_data = funnel_data.sort_values(by="Cases", ascending=False)
    fig_funnel = px.funnel(funnel_data, x="Cases", y="Stage", title="Candidate Funnel by Stage")
    st.plotly_chart(fig_funnel, use_container_width=True)

# --- New Feature: Time to Hire by Partner ---
with st.container():
    st.markdown("### ⏱️ Average Time to Hire by Partner")
    time_to_hire_df = filtered_data.groupby("Partner")["TimeToHire"].mean().reset_index()
    fig_time = px.bar(time_to_hire_df, x="Partner", y="TimeToHire", text="TimeToHire", color="Partner")
    st.plotly_chart(fig_time, use_container_width=True)

# --- New Feature: Candidate Source Effectiveness ---
with st.container():
    st.markdown("### 📌 Candidate Source Effectiveness")
    source_effectiveness = filtered_data.groupby("Source")["Joiners"].sum().reset_index().sort_values(by="Joiners", ascending=False)
    fig_source = px.bar(source_effectiveness, x="Source", y="Joiners", text="Joiners", color="Source")
    st.plotly_chart(fig_source, use_container_width=True)

# --- New Feature: Position-wise Hiring Progress ---
with st.container():
    st.markdown("### 📍 Position-wise Hiring Progress")
    position_df = filtered_data.groupby("Position")["Joiners"].sum().reset_index().sort_values(by="Joiners", ascending=False)
    fig_position = px.bar(position_df, x="Position", y="Joiners", text="Joiners", color="Position")
    st.plotly_chart(fig_position, use_container_width=True)

# --- Export to CSV (Filtered) ---
st.sidebar.markdown("---")
st.sidebar.download_button("⬇ Export Filtered Dashboard", filtered_data.to_csv(index=False), file_name="ta_dashboard_filtered_export.csv")
