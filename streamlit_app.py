import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📊 Talent Acquisition Dashboard ")

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
        "TimeToHire": [12, 18, 22, 15, 19, 25, 17, 14] * 2
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

# --- Gap Analysis Only (No Empty Space) ---
with st.container():
    st.markdown("### 📉 Gap Analysis")
    months = [f"M-{i}" for i in range(1, 13)] + ["Current"]
    budgeted_hc = [300, 340, 370, 390, 400, 410, 420, 440, 450, 460, 470, 480, 4579]
    actual_hc = [290, 320, 350, 370, 380, 400, 410, 420, 430, 445, 460, 470, 4491]
    hc_df = pd.DataFrame({"Month": months, "Budgeted HC": budgeted_hc, "Actual HC": actual_hc})
    fig_hc = px.bar(hc_df, x="Month", y=["Budgeted HC", "Actual HC"], barmode="group")
    st.plotly_chart(fig_hc, use_container_width=True)

# --- Branch Overview Section ---
st.markdown("### 🏢 Branch Status Overview")
uploaded_abep = st.sidebar.file_uploader("📄 Upload ABEP Excel", type=["xlsx", "xlsb"])

if uploaded_abep:
    ext = uploaded_abep.name.split(".")[-1].lower()
    if ext == "xlsb":
        abep_df = pd.read_excel(uploaded_abep, sheet_name="Branch Wise", engine="pyxlsb", header=1, usecols="K:M")
    else:
        abep_df = pd.read_excel(uploaded_abep, sheet_name="Branch Wise", header=1, usecols="K:M")

    abep_df.columns = abep_df.columns.str.strip()

    # --- Robust date conversion for Branch Opening ---
    def convert_excel_date(val):
        try:
            if pd.isna(val):
                return pd.NaT
            if isinstance(val, (int, float)):
                # Excel serial date
                return pd.to_datetime("1899-12-30") + pd.to_timedelta(val, "D")
            if isinstance(val, pd.Timestamp):
                return val
            # If it's a string that's a date, try to parse
            return pd.to_datetime(val, errors='coerce')
        except Exception:
            return pd.NaT

    # Keep "Hold" and "Dropped" as is; else convert
    abep_df["Branch Opening"] = abep_df["Branch Opening"].apply(
        lambda x: x if x in ["Hold", "Dropped"] else convert_excel_date(x)
    )

    unique_statuses = abep_df["Branch Status"].dropna().unique().tolist()
    selected_statuses = st.sidebar.multiselect("Filter by Branch Status", unique_statuses, default=unique_statuses)
    abep_filtered = abep_df[abep_df["Branch Status"].isin(selected_statuses)]

    # --- Branch Status grouping for summary/chart ---
    def adjust_status(row):
        if row["Branch Status"] == "To be Live":
            if row["Branch Opening"] == "Hold":
                return "Hold"
            elif row["Branch Opening"] == "Dropped":
                return "Dropped"
            elif isinstance(row["Branch Opening"], pd.Timestamp):
                return "To be Live"
            elif isinstance(row["Branch Opening"], (int, float)):
                return "To be Live"
            else:
                return "To be Live"
        else:
            return row["Branch Status"]

    abep_filtered["Branch Status Adjusted"] = abep_filtered.apply(adjust_status, axis=1)

    status_counts = abep_filtered["Branch Status Adjusted"].value_counts().reset_index()
    status_counts.columns = ["Branch Status", "Count"]

 #   st.markdown("#### 🧮 Branch Summary")
 #  st.dataframe(status_counts)

    chart_type = st.radio("Choose Chart Type", ["Bar Chart", "Pie Chart"], horizontal=True)

    with st.container():
        st.markdown("#### 📊 Current Branch Status Counts")
        if chart_type == "Bar Chart":
            fig_status = px.bar(status_counts, x="Branch Status", y="Count", text="Count", color="Branch Status")
        else:
            fig_status = px.pie(status_counts, names="Branch Status", values="Count", hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)

    with st.container():
        st.markdown("#### 📅 To be Live Branches by Month")
        # Only those to be live with a real date
        to_be_live = abep_filtered[abep_filtered["Branch Status Adjusted"] == "To be Live"].copy()
        # Only keep valid datetimes
        to_be_live = to_be_live[pd.to_datetime(to_be_live["Branch Opening"], errors='coerce').notna()]
        to_be_live["Month-Year"] = pd.to_datetime(to_be_live["Branch Opening"], errors='coerce').dt.strftime("%b-%y")

        month_counts = to_be_live["Month-Year"].value_counts().reset_index()
        month_counts.columns = ["Month", "Branches"]

        # Sort by month correctly
        month_counts["Month"] = pd.to_datetime(month_counts["Month"], format="%b-%y")
        month_counts = month_counts.sort_values("Month")
        month_counts["Month"] = month_counts["Month"].dt.strftime("%b-%y")

        fig_month = px.bar(month_counts, x="Month", y="Branches", text="Branches", color="Month")
        st.plotly_chart(fig_month, use_container_width=True)

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

# --- Export to CSV (Filtered) ---
st.sidebar.markdown("---")
st.sidebar.download_button("⬇ Export Filtered Dashboard", filtered_data.to_csv(index=False), file_name="ta_dashboard_filtered_export.csv")
