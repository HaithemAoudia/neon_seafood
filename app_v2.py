import streamlit as st
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import altair as alt
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import os
import zipfile
from io import BytesIO
from PyPDF2 import PdfMerger
import base64
import json
from gspread_dataframe import set_with_dataframe, get_as_dataframe
import plotly.graph_objects as go
import plotly.express as px
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


names = ["Chems"]
usernames = ["Neon Seafood"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)


authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "Neon_Seafood_Analytics",  # no spaces for cookie name
    "abcdef", 
    cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username or Password is Incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:

# ========== PAGE CONFIG ==========
    st.set_page_config(
        page_title="NOEN Seafood Analytics",
        page_icon="🐟",
        layout="wide",
        initial_sidebar_state="collapsed"
    )


        # ========== PAGE CONFIG ==========
    st.set_page_config(
        page_title="NOEN Seafood Analytics",
        page_icon="🐟",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

        # ========== API CREDENTIALS ==========
    API_EMAIL = st.secrets["API_EMAIL"]
    API_KEY = st.secrets["API_KEY"]

    google_cred = {
  "type": st.secrets["service_account"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["client_x509_cert_url"],
  "universe_domain": st.secrets["universe_domain"]
}

    # ========== CUSTOM CSS ==========
    st.markdown("""
    <style>
        .stApp {
            background-color: #f0f9ff;
        }
        
        .main {
            background-color: #f0f9ff;
        }
        
        [data-testid="stAppViewContainer"] {
            background-color: #f0f9ff;
        }
        
        [data-testid="stHeader"] {
            background-color: #f0f9ff;
        }
        /* Header styling */
        h1 {
            color: #0c4a6e;
            font-weight: 700;
            padding-bottom: 0.5rem;
        }
        
        h2 {
            color: #075985;
            font-weight: 600;
            padding-top: 1rem;
            padding-bottom: 0.5rem;
        }
        
        h3 {
            color: #0369a1;
            font-weight: 600;
            font-size: 1.2rem;
        }
        
        /* Logo header container */
        .logo-header {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1.5rem 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(14, 116, 144, 0.1);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 2px solid #bae6fd;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        .logo-image {
            max-height: 120px;
            width: auto;
        }
        
        .company-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0c4a6e 0%, #0891b2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        }
        
        .tagline {
            color: #0369a1;
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }
        
        /* Metric cards with light blue theme */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(14, 116, 144, 0.12);
            border: 1px solid #bae6fd;
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 12px rgba(14, 116, 144, 0.2);
            transform: translateY(-2px);
        }
        
        [data-testid="stMetricLabel"] {
            font-weight: 600;
            color: #0369a1;
            font-size: 0.9rem;
        }
        
        [data-testid="stMetricValue"] {
            color: #0c4a6e;
        }
        
        /* Dataframe styling */
        [data-testid="stDataFrame"] {
            border-radius: 0.75rem;
            overflow: hidden;
            border: 1px solid #bae6fd;
        }
        
        /* Filter section */
        .filter-container {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(14, 116, 144, 0.12);
            margin-bottom: 2rem;
            border: 1px solid #bae6fd;
        }
        
        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #bae6fd;
        }
        
        /* Tab styling with light blue */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(14, 116, 144, 0.12);
            border: 1px solid #bae6fd;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            padding: 0 2rem;
            font-weight: 600;
            color: #0369a1;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e0f2fe;
            color: #0c4a6e;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
            color: white !important;
            box-shadow: 0 2px 4px rgba(8, 145, 178, 0.3);
        }
        
        /* Checkbox styling */
        [data-testid="stCheckbox"] {
            padding: 0.5rem;
        }
        
        /* Button styling with light blue theme */
        .stButton > button {
            font-weight: 600;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
            color: white;
            border: none;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(8, 145, 178, 0.3);
            background: linear-gradient(135deg, #0e7490 0%, #0891b2 100%);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%);
        }
        
        /* Input fields */
        .stTextInput input, .stSelectbox select, .stMultiSelect select {
            border: 1px solid #bae6fd;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus, .stMultiSelect select:focus {
            border-color: #0891b2;
            box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.2);
        }
        
        /* Success/Info messages */
        .stSuccess {
            background-color: #cffafe;
            border-left: 4px solid #06b6d4;
        }
        
        .stInfo {
            background-color: #e0f2fe;
            border-left: 4px solid #0891b2;
        }
    </style>
    """, unsafe_allow_html=True)

    

    
    # ========== DATA LOADING ==========
    @st.cache_data(ttl=300)
    def load_data():
        """Load and cache data from Google Sheets"""
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_cred, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_id = "1E59oS6DXSHIs1GfyZeE2q8WeoUbfxCk_O-ZK0A04NcM"
        workbook = client.open_by_key(sheet_id)
        
        df_sales = pd.DataFrame(workbook.worksheet("OneUp - Invoices").get_all_records()).drop_duplicates()
        df_product = pd.DataFrame(workbook.worksheet("OneUp - Products").get_all_records()).drop_duplicates()
        df_customers = pd.DataFrame(workbook.worksheet("OneUp - Customers").get_all_records()).drop_duplicates()
        df_transactions_sumup = pd.DataFrame(workbook.worksheet("SumUp - Product Transaction").get_all_records()).drop_duplicates()
        df_product_inventory_analysis = pd.DataFrame(workbook.worksheet("Product Inventory Consumption - Merged").get_all_records()).drop_duplicates()
        df_product_inventory = pd.DataFrame(workbook.worksheet("Product Inventory").get_all_records()).drop_duplicates()
        return df_sales, df_product, df_customers, df_transactions_sumup, df_product_inventory_analysis, df_product_inventory

    @st.cache_data(ttl=300)
    def prepare_data(_df_sales, _df_product, _df_transactions_sumup):
        """Prepare and transform data once - cached for performance"""
        df_sales = _df_sales.copy()
        df_product = _df_product.copy()
        df_transactions_sumup = _df_transactions_sumup.copy()
        
        # Convert data types
        df_sales["date"] = pd.to_datetime(df_sales["date"], errors="coerce")
        df_sales["paid"] = pd.to_numeric(df_sales["paid"], errors="coerce")
        df_sales["quantity"] = pd.to_numeric(df_sales["quantity"], errors="coerce")
        df_sales["unit_price"] = pd.to_numeric(df_sales["unit_price"], errors="coerce")
        df_sales["total_order_line"] = pd.to_numeric(df_sales["total_order_line"], errors="coerce")
        df_product["purchase_price"] = pd.to_numeric(df_product["purchase_price"], errors="coerce")
        df_transactions_sumup["date"] = pd.to_datetime(df_transactions_sumup["timestamp"], errors="coerce")
        
        # Filter successful transactions only
        df_transactions_sumup = df_transactions_sumup[df_transactions_sumup["status"] == "SUCCESSFUL"]
        
        # Create sales order dataframe
        df_sales_order = df_sales[
            ["invoice_id", "date", "paid", "customer_name", "country", "city", "source"]
        ].drop_duplicates()
        
        # Create invoices metadata dataframe
        df_invoices = df_sales[
            ["invoice_id", "customer_name", "country", "city", "date", "due_date", "amount", "sent", "paid", "source"]
        ].drop_duplicates()
        
        # SumUp sales
        df_sales_sumup = df_transactions_sumup[
            ["id", "date", "paid", "customer_name", "country", "city", "source"]
        ].drop_duplicates()
        
        # Merge sales orders
        df_sales_order_merged = pd.concat([
            df_sales_order.rename(columns={'invoice_id': 'id'}),
            df_sales_sumup
        ], ignore_index=True)
        
        # Prepare product sales data
        df_product_sales_oneup = df_sales[
            ["invoice_id", "item_id", "item_description", "country", "date", "unit_price", "total_order_line", "quantity", "source"]
        ]
        
        df_product_sales_sumup = df_transactions_sumup[
            ["id", "product_name", "country", "timestamp", "price", "total_price", "quantity", "source"]
        ].rename(columns={
            "product_name": "item_description",
            "timestamp": "date",
            "price": "unit_price",
            "total_price": "total_order_line"
        })
        
        df_product_sales_sumup["item_id"] = 0
        df_product_sales_sumup = df_product_sales_sumup[
            ["id", "item_id", "item_description", "country", "date", "unit_price", "total_order_line", "quantity", "source"]
        ]
        
        df_product_sales_merged = pd.concat([
            df_product_sales_oneup.rename(columns={"invoice_id": "id"}),
            df_product_sales_sumup
        ], ignore_index=True)
        
        df_product_sales_merged["date"] = pd.to_datetime(df_product_sales_merged["date"])
        
        return df_sales_order_merged, df_invoices, df_product_sales_merged, df_product

    # Load data
    with st.spinner("Loading data..."):
        df_sales, df_product, df_customers, df_transactions_sumup, df_product_inventory_analysis, df_product_inventory  = load_data()
        df_sales_order_merged, df_invoices, df_product_sales_merged, df_product_clean = prepare_data(
            df_sales, df_product, df_transactions_sumup
        )

    # ========== HELPER FUNCTIONS ==========
    def print_invoice(invoice_id, format):
        url = f"https://api.oneup.com/v1/invoices/{invoice_id}/print.{format}"
        response = requests.get(url, auth=HTTPBasicAuth(API_EMAIL, API_KEY), verify=False)
        
        if response.status_code == 200:
            if format == 'pdf':
                with open(f"invoice_{invoice_id}.pdf", "wb") as f:
                    f.write(response.content)
                print("PDF saved successfully!")
            elif format == 'json':
                return json.loads(response.content)["url"]
        else:
            error = f"Error {response.status_code}: {response.text}"
            return error

    # ========== FILTER FUNCTIONS ==========
    def apply_date_filter(df, start_date, end_date, date_column='date'):
        """Apply date filter efficiently"""
        return df[(df[date_column] >= pd.to_datetime(start_date)) & 
                (df[date_column] <= pd.to_datetime(end_date))]

    def apply_country_filter(df, country):
        """Apply country filter efficiently"""
        if country != "All":
            return df[df["country"] == country]
        return df

    def apply_source_filter(df, sources):
        """Apply source filter efficiently"""
        if sources:
            return df[df["source"].isin(sources)]
        return df

    # ========== ANALYTICS FUNCTIONS ==========
    def calculate_customer_metrics(df):
        """Calculate customer metrics"""
        if len(df) == 0:
            return pd.DataFrame(columns=["customer_name", "num_transactions", "total_revenue", "AOV", "transaction_frequency"])
        
        metrics = (
            df.groupby("customer_name", as_index=False)
            .agg({
                "id": "nunique",
                "paid": "sum"
            })
            .rename(columns={"id": "num_transactions", "paid": "total_revenue"})
        )
        
        metrics["AOV"] = metrics["total_revenue"] / metrics["num_transactions"]
        metrics["transaction_frequency"] = metrics["num_transactions"] / metrics["total_revenue"]
        
        return metrics

    def calculate_product_metrics(df, df_product):
        """Calculate product metrics"""
        if len(df) == 0:
            return pd.DataFrame(columns=["item_description", "quantity", "revenue", "gross_margin", "margin_%", "margin_contribution_%"])
        
        df_merged = df.merge(
            df_product[["id", "purchase_price"]],
            how="left",
            left_on="item_id",
            right_on="id"
        )

        # df_merged = df_merged[df_merged["purchase_price"] > 0]
        df_merged = df_merged[df_merged["item_description"] != '']
        
        df_merged["total_cost"] = df_merged["purchase_price"] * df_merged["quantity"]
        df_merged["total_gross_margin"] = df_merged["total_order_line"] - df_merged["total_cost"]
      
        product_metrics = (
            df_merged.groupby(["item_description"], as_index=False)
            .agg({
                "quantity": "sum",
                "total_order_line": "sum",
                "total_gross_margin": "sum"
            })
            .rename(columns={"total_order_line": "revenue"})
        )
        
        product_metrics["margin_%"] = (product_metrics["total_gross_margin"] / product_metrics["revenue"]) * 100
        product_metrics["margin_contribution_%"] = (
            (product_metrics["total_gross_margin"] / product_metrics["total_gross_margin"].sum()) * 100
        )
        
        return product_metrics


    # ========= INVENTORY FUNCTIONS ============
    def get_product_inventory(product_name:str):
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("google_sheets_credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_id = "1E59oS6DXSHIs1GfyZeE2q8WeoUbfxCk_O-ZK0A04NcM"
        workbook = client.open_by_key(sheet_id)
        sheet = workbook.worksheet("Product Inventory")
        
        row = sheet.find(product_name).row
        quantity_available = sheet.get(f"X{row}")[0][0]
        return int(quantity_available)




    #Update Inventory value for a given product name
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("google_sheets_credentials.json", scopes=scope)
    client = gspread.authorize(creds)

    sheet_id = "1E59oS6DXSHIs1GfyZeE2q8WeoUbfxCk_O-ZK0A04NcM"
    workbook = client.open_by_key(sheet_id)

    def update_product_inventory(new_df):
        sheet_id = "1E59oS6DXSHIs1GfyZeE2q8WeoUbfxCk_O-ZK0A04NcM"
        workbook = client.open_by_key(sheet_id)
        sheet = workbook.worksheet("Product Inventory")
        set_with_dataframe(sheet, new_df)



    # ========== HEADER ==========
        # ========== HEADER WITH LOGO ==========
    authenticator.logout("logout", "sidebar")
    
    # Create logo header
    col1, col2 = st.columns([3, 1])
    with open("NOEN-logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    with col1:
        st.markdown(f"""
        <div class="logo-header">
            <div class="logo-container">
                <img src="data:image/png;base64,{data}" class="logo-image" alt="NOEN Logo">
                <div>
                    <h1 class="company-title">NOEN Seafood Analytics</h1>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)

    # ========== TABS ==========
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "📈 Analytics" 


    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analytics", "📦 Inventory", "🚀 Forecast", "🧾 Invoice Manager"])

    # ========================================
    # TAB 1: ANALYTICS DASHBOARD
    # ========================================
    with tab1:
        # ========== FILTERS ==========
        # st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.subheader("🔍 Filters")

        col1, col2, col3 = st.columns([2, 2, 2])

        min_date = df_sales_order_merged["date"].min()
        max_date = df_sales_order_merged["date"].max()
        today = datetime.today()

        with col1:
            date_options = ["Past Month", "Last 3 Months", "Last 6 Months", "YTD", "Custom Range"]
            selected_range = st.selectbox("📅 Date Range", date_options, index=0)

            if selected_range == "Past Month":
                start_date = max_date - pd.DateOffset(months=1)
                end_date = max_date
            elif selected_range == "Last 3 Months":
                start_date = max_date - pd.DateOffset(months=3)
                end_date = max_date
            elif selected_range == "Last 6 Months":
                start_date = max_date - pd.DateOffset(months=6)
                end_date = max_date
            elif selected_range == "YTD":
                start_date = datetime(max_date.year, 1, 1)
                end_date = max_date
            elif selected_range == "Custom Range":
                start_date = st.date_input("📅 Start Date", value=min_date, min_value=min_date, max_value=max_date)
                end_date = st.date_input("📅 End Date", value=max_date, min_value=min_date, max_value=max_date)
            else:
                start_date, end_date = min_date, max_date

        with col2:
            countries = ["All"] + sorted(df_sales_order_merged["country"].dropna().unique().tolist())
            selected_country = st.selectbox("🌍 Country", countries)

        with col3:  
            source = st.multiselect("Data Source", ["OneUp", "SumUp"])

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== APPLY FILTERS ==========
        filtered_df = apply_date_filter(df_sales_order_merged, start_date, end_date)
        filtered_df = apply_country_filter(filtered_df, selected_country)
        filtered_df = apply_source_filter(filtered_df, source)

        # ========== CUSTOMER ANALYSIS ==========
        st.header("👥 Customer Analytics")

        # Calculate customer metrics using cached function
        metrics = calculate_customer_metrics(filtered_df)

        # Top customers
        top_revenue = metrics.nlargest(10, "total_revenue")
        top_transactions = metrics.nlargest(10, "num_transactions")

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💰 Total Revenue", f"${metrics['total_revenue'].sum():,.0f}")

        with col2:
            top_customer = top_revenue.iloc[0]
            name = top_customer["customer_name"][:20] + "..." if len(top_customer["customer_name"]) > 20 else top_customer["customer_name"]
            st.metric("🏆 Top Customer", name, f"${top_customer['total_revenue']:,.0f}")

        with col3:
            st.metric("📦 Average Order Value", f"${metrics['AOV'].mean():,.0f}")

        with col4:
            most_active = top_transactions.iloc[0]
            name = most_active["customer_name"][:20] + "..." if len(most_active["customer_name"]) > 20 else most_active["customer_name"]
            st.metric("🔄 Most Active Customer", name, f"{int(most_active['num_transactions'])} orders")

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Top 10 Customers by Revenue")
            chart_revenue = (
                alt.Chart(top_revenue)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("total_revenue:Q", title="Revenue ($)", axis=alt.Axis(format="$,.0f")),
                    y=alt.Y("customer_name:N", sort="-x", title=None),
                    color=alt.value("#10b981"),
                    tooltip=[
                        alt.Tooltip("customer_name:N", title="Customer"),
                        alt.Tooltip("total_revenue:Q", title="Revenue", format="$,.2f"),
                        alt.Tooltip("num_transactions:Q", title="Orders"),
                        alt.Tooltip("AOV:Q", title="AOV", format="$,.2f")
                    ]
                )
                .properties(height=400)
                .configure(background='#f0f9ff;')
            )
            st.altair_chart(chart_revenue, use_container_width=True)

        with col2:
            st.subheader("🔁 Top 10 by Transaction Count")
            chart_transactions = (
                alt.Chart(top_transactions)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("num_transactions:Q", title="Number of Transactions"),
                    y=alt.Y("customer_name:N", sort="-x", title=None),
                    color=alt.value("#3b82f6"),
                    tooltip=[
                        alt.Tooltip("customer_name:N", title="Customer"),
                        alt.Tooltip("num_transactions:Q", title="Transactions"),
                        alt.Tooltip("total_revenue:Q", title="Revenue", format="$,.2f"),
                        alt.Tooltip("AOV:Q", title="AOV", format="$,.2f")
                    ]
                )
                .properties(height=400)
                .configure(background='#f0f9ff;')
            )
            st.altair_chart(chart_transactions, use_container_width=True)

        # ========== PRODUCT ANALYSIS ==========
        st.header("📦 Product Performance")

        # Apply filters to product data
        filtered_sales = apply_date_filter(df_product_sales_merged, start_date, end_date)
        filtered_sales = apply_country_filter(filtered_sales, selected_country)
        filtered_sales = apply_source_filter(filtered_sales, source)

        # Calculate product metrics using cached function
        product_metrics = calculate_product_metrics(filtered_sales, df_product_clean)
        # st.write(product_metrics)
        # Top products
        top_units = product_metrics.nlargest(10, "quantity")
        top_product_revenue = product_metrics.nlargest(10, "revenue")
        # top_margin = product_metrics.nlargest(10, "total_gross_margin")
        top_margin = product_metrics[product_metrics["margin_%"] != 100].nlargest(10, "total_gross_margin")

        # Product KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📊 Total Units Sold", f"{int(product_metrics['quantity'].sum()):,}")

        with col2:
            best_seller = top_units.iloc[0]
            name = best_seller["item_description"][:20] + "..." if len(best_seller["item_description"]) > 20 else best_seller["item_description"]
            st.metric("🏅 Best Seller", name, f"{int(best_seller['quantity']):,} units")

        with col3:
            st.metric("💵 Total Gross Margin", f"${product_metrics[product_metrics["margin_%"] != 100]['total_gross_margin'].sum():,.0f}")

        with col4:
            avg_margin = product_metrics[product_metrics["margin_%"] != 100]["margin_%"].mean()
            st.metric("📈 Avg Margin %", f"{avg_margin:.1f}%")

        st.markdown("---")

        # Product charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📦 Top 10 Products by Units Sold")
            chart_units = (
                alt.Chart(top_units)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("quantity:Q", title="Units Sold"),
                    y=alt.Y("item_description:N", sort="-x", title=None),
                    color=alt.value("#10b981"),
                    tooltip=[
                        alt.Tooltip("item_description:N", title="Product"),
                        alt.Tooltip("quantity:Q", title="Units Sold", format=","),
                        alt.Tooltip("revenue:Q", title="Revenue", format="$,.2f"),
                        # alt.Tooltip("margin_%:Q", title="Margin %", format=".1f")
                    ]
                )
                .properties(height=400)
                .configure(background='#f0f9ff;')
            )
            st.altair_chart(chart_units, use_container_width=True)

        with col2:
            st.subheader("💰 Top 10 Products by Revenue")
            chart_prod_revenue = (
                alt.Chart(top_product_revenue)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                .encode(
                    x=alt.X("revenue:Q", title="Revenue ($)", axis=alt.Axis(format="$,.0f")),
                    y=alt.Y("item_description:N", sort="-x", title=None),
                    color=alt.value("#3b82f6"),
                    tooltip=[
                        alt.Tooltip("item_description:N", title="Product"),
                        alt.Tooltip("revenue:Q", title="Revenue", format="$,.2f"),
                        alt.Tooltip("quantity:Q", title="Units Sold", format=","),
                        # alt.Tooltip("margin_%:Q", title="Margin %", format=".1f")
                    ]
                )
                .properties(height=400)
                .configure(background='#f0f9ff;')
            )
            st.altair_chart(chart_prod_revenue, use_container_width=True)

        st.subheader("🏅 Top 10 Products by Gross Margin")
        chart_margin = (
            alt.Chart(top_margin)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("total_gross_margin:Q", title="Gross Margin ($)", axis=alt.Axis(format="$,.0f")),
                y=alt.Y("item_description:N", sort="-x", title=None),
                color=alt.value("#f59e0b"),
                tooltip=[
                    alt.Tooltip("item_description:N", title="Product"),
                    alt.Tooltip("total_gross_margin:Q", title="Total Gross Margin", format="$,.2f"),
                    alt.Tooltip("margin_%:Q", title="Margin %", format=".1f"),
                    alt.Tooltip("revenue:Q", title="Revenue", format="$,.2f")
                ]
            )
            .properties(height=400)
            .configure(background='#f0f9ff;')
        )
        st.altair_chart(chart_margin, use_container_width=True)



    # ========================================
    # TAB 2: INVENTORY
    # ========================================

    with tab2:

        # --- 🧾 Inventory display ---
        st.write("### Product Inventory")

        # Display headers
        product_list = df_product_inventory["product_name"].tolist()

        search_selection = st.selectbox(
            "Search or select a product",
            options=[""] + product_list,
            index=0,
            placeholder="Type to search for a product..."
        )

        # Filter dataframe
        if search_selection:
            filtered_df = df_product_inventory[df_product_inventory["product_name"] == search_selection]
        else:
            filtered_df = df_product_inventory

        # --- 🧾 Display headers ---
        cols = st.columns([4, 1])
        headers = ["Product Name", "Available Quantity"]
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        # --- 🧮 Editable quantities ---
        updated_quantities = {}

        for idx, row in filtered_df.iterrows():
            cols = st.columns([4, 1])
            with cols[0]:
                st.text(row["product_name"])
            with cols[1]:
                updated_quantities[idx] = st.number_input(
                    "",
                    value=int(row["current_quantity"]),
                    min_value=0,
                    key=f"qty_{idx}"
                )

        # --- 💾 Save updates ---
        if st.button("Save Changes"):
            for idx, qty in updated_quantities.items():
                df_product_inventory.at[idx, "current_quantity"] = qty
            update_product_inventory(df_product_inventory)
            st.success("Quantities updated successfully!")



    # ========================================
    # TAB 3: FORECAST
    # ========================================
    # --- Page Layout ---
    with tab3:
        
        st.session_state.active_tab = "🚀 Forecast"
        # ---- Product detail view ----
        st.subheader("📈 Historical and Forecast Product Units Sold")

        product_options = df_product_inventory_analysis["product_name"].unique()
        
        selected_product = st.selectbox("Select a product to view trend", product_options)

        if selected_product:
            # Prepare product data
            product_df = (
                df_product_inventory_analysis[
                    df_product_inventory_analysis["product_name"] == selected_product
                ]
                .drop(columns=["product_name"])
                .T
                .reset_index()
            )
            product_df.columns = ["Month", "Quantity"]

            # Parse month columns
            product_df["Month"] = pd.to_datetime(product_df["Month"], errors="coerce")

            # Determine historical vs forecast cutoff (based on today's date)
            today = pd.Timestamp(datetime.today().strftime("%Y-%m-01"))  # Start of current month
            product_df["Type"] = product_df["Month"].apply(
                lambda x: "Historical" if x < today else "Forecast"
            )

            # Split data
            hist_df = product_df[product_df["Type"] == "Historical"]
            forecast_df = product_df[product_df["Type"] == "Forecast"]

            # ---- Plot ----
            fig = go.Figure()

            # Historical line
            fig.add_trace(go.Scatter(
                x=hist_df["Month"],
                y=hist_df["Quantity"],
                mode="lines+markers",
                name="Historical",
                line=dict(color="royalblue", width=2),
                marker=dict(size=6),
            ))

            # Forecast line
            fig.add_trace(go.Scatter(
                x=forecast_df["Month"],
                y=forecast_df["Quantity"],
                mode="lines+markers",
                name="Forecast",
                line=dict(color="orange", width=2, dash="dash"),
                marker=dict(size=6),
            ))


            fig.update_layout(
                title=f"📆 Quantity Sold Over Time: {selected_product}",
                xaxis_title="Month",
                yaxis_title="Quantity Sold",
                hovermode="x unified",
                legend_title="Data Type",
                template="plotly_white",
                plot_bgcolor="#f0f9ff",   
                paper_bgcolor="#f0f9ff"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Full Data Inventory Consumption")
        # search = st.text_input("🔍 Search product name", "")
        filtered = df_product_inventory_analysis[
            df_product_inventory_analysis["product_name"].str.contains(selected_product, case=False, na=False)
        ]
        st.dataframe(filtered, use_container_width=True, height=400)





    # ========================================
    # TAB 3: INVOICE MANAGER
    # ========================================
    with tab4:
        st.header("🧾 Invoice Manager")
        st.markdown("**Select and download invoices in bulk**")
        st.markdown("---")
        
        # ========== INVOICE FILTERS ==========
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.subheader("🔍 Filter Invoices")
        
        col1, col2, col3 = st.columns(3)

        min_date = df_sales_order_merged["date"].min()
        max_date = df_sales_order_merged["date"].max()
        
        with col1:
            date_options = ["Past Month", "Last 3 Months", "Last 6 Months", "YTD", "Custom Range"]
            selected_range = st.selectbox("📅 Invoice Date Range", date_options, index=0)
            # inv_start_date = df_invoices["date"].min()
            # inv_end_date = df_invoices["date"].max()

            if selected_range == "Past Month":
                inv_start_date = max_date - pd.DateOffset(months=1)
                inv_end_date = max_date
            elif selected_range == "Last 3 Months":
                inv_start_date = max_date - pd.DateOffset(months=3)
                inv_end_date = max_date
            elif selected_range == "Last 6 Months":
                inv_start_date = max_date - pd.DateOffset(months=6)
                inv_end_date = max_date
            elif selected_range == "YTD":
                inv_start_date = datetime(max_date.year, 1, 1)
                inv_end_date = max_date
            elif selected_range == "Custom Range":
                inv_start_date = st.date_input("📅 Start Date", value=min_date, min_value=min_date, max_value=max_date)
                inv_end_date = st.date_input("📅 End Date", value=max_date, min_value=min_date, max_value=max_date)
            else:
                inv_start_date, inv_end_date = min_date, max_date

        
        with col2:
            inv_countries = ["All"] + sorted(df_invoices["country"].dropna().unique().tolist())
            inv_selected_country = st.selectbox("🌍 Country", inv_countries, key="invoice_country")
        
        with col3:
            payment_status = st.selectbox(
                "💳 Payment Status", 
                ["All", "Paid", "Unpaid"],
                key="payment_status"
            )
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            sent_status = st.selectbox(
                "📧 Sent Status", 
                ["All", "Sent", "Not Sent"],
                key="sent_status"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ========== APPLY INVOICE FILTERS ==========
        filtered_invoices = apply_date_filter(df_invoices, inv_start_date, inv_end_date)
        filtered_invoices = apply_country_filter(filtered_invoices, inv_selected_country)
        
        if payment_status == "Paid":
            filtered_invoices = filtered_invoices[filtered_invoices["paid"] > 0]
        elif payment_status == "Unpaid":
            filtered_invoices = filtered_invoices[filtered_invoices["paid"] == 0]
        
        if sent_status == "Sent":
            filtered_invoices = filtered_invoices[filtered_invoices["sent"] == True]
        elif sent_status == "Not Sent":
            filtered_invoices = filtered_invoices[filtered_invoices["sent"] == False]
        
        # ========== SUMMARY METRICS ==========
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Invoices", len(filtered_invoices))
        
        with col2:
            total_amount = filtered_invoices["amount"].sum()
            st.metric("💰 Total Amount", f"${total_amount:,.2f}")
        
        with col3:
            paid_count = len(filtered_invoices[filtered_invoices["paid"] > 0])
            st.metric("✅ Paid Invoices", paid_count)
        
        with col4:
            unpaid_count = len(filtered_invoices[filtered_invoices["paid"] == 0])
            st.metric("⏳ Unpaid Invoices", unpaid_count)
        
        st.markdown("---")
        
        # ========== INVOICE SELECTION ==========
        st.subheader("📋 Select Invoices to Download")
        
        # Initialize session state for selections
        if 'selected_invoices' not in st.session_state:
            st.session_state.selected_invoices = set()
        
        # Initialize a flag to track if we need to update the selection
        if 'force_select_all' not in st.session_state:
            st.session_state.force_select_all = False
        if 'force_deselect_all' not in st.session_state:
            st.session_state.force_deselect_all = False
        
        # Select All / Deselect All buttons
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            if st.button("✅ Select All", use_container_width=True, key="btn_select_all"):
                st.session_state.selected_invoices = set(filtered_invoices["invoice_id"].tolist())
                st.session_state.force_select_all = True
                st.session_state.force_deselect_all = False
        
        with col2:
            if st.button("❌ Deselect All", use_container_width=True, key="btn_deselect_all"):
                st.session_state.selected_invoices = set()
                st.session_state.force_deselect_all = True
                st.session_state.force_select_all = False
        
        st.markdown("---")
        
        # ========== INVOICE TABLE WITH CHECKBOXES ==========
        if len(filtered_invoices) > 0:
            st.markdown("##### Select invoices to download:")
            
            # Use pagination for large datasets
            items_per_page = 50
            total_pages = (len(filtered_invoices) - 1) // items_per_page + 1
            
            if total_pages > 1:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
                start_idx = (page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, len(filtered_invoices))
                display_invoices = filtered_invoices.iloc[start_idx:end_idx]
                st.info(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_invoices)} invoices")
            else:
                display_invoices = filtered_invoices
            
            # Create columns for the header
            header_cols = st.columns([0.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1.5])
            headers = ["Select", "Invoice ID", "Customer", "Country", "City", "Date", "Amount", "Sent", "Status"]
            
            for col, header in zip(header_cols, headers):
                col.markdown(f"**{header}**")
            
            st.markdown("---")
            
            # Display each invoice with checkbox
            for idx, row in display_invoices.iterrows():
                cols = st.columns([0.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1.5])
                
                with cols[0]:
                    is_selected = row["invoice_id"] in st.session_state.selected_invoices
                    checkbox_changed = st.checkbox(
                        "", 
                        value=is_selected, 
                        key=f"check_{row['invoice_id']}_{is_selected}"  # Dynamic key forces re-render
                    )
                    
                    # Update selection based on checkbox state
                    if checkbox_changed:
                        st.session_state.selected_invoices.add(row["invoice_id"])
                    else:
                        st.session_state.selected_invoices.discard(row["invoice_id"])
                    
                    # Reset the force flags after processing
                    if idx == display_invoices.index[-1]:  # Last item
                        st.session_state.force_select_all = False
                        st.session_state.force_deselect_all = False
                
                with cols[1]:
                    st.text(row["invoice_id"])
                
                with cols[2]:
                    customer_name = row["customer_name"]
                    st.text(customer_name[:25] + "..." if len(customer_name) > 25 else customer_name)
                
                with cols[3]:
                    st.text(row["country"])
                
                with cols[4]:
                    st.text(row["city"])
                
                with cols[5]:
                    st.text(row["date"].strftime("%Y-%m-%d"))
                
                with cols[6]:
                    st.text(f"${row['amount']:,.2f}")
                
                with cols[7]:
                    st.text("✅" if row["sent"] else "❌")
                
                with cols[8]:
                    status = "✅ Paid" if row["paid"] > 0 else "⏳ Unpaid"
                    st.text(status)
            
            st.markdown("---")
            
            # ========== DOWNLOAD SECTION ==========
            st.subheader(f"📥 Download Selected Invoices ({len(st.session_state.selected_invoices)} selected)")
            
            if len(st.session_state.selected_invoices) > 0:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.info(f"Ready to download {len(st.session_state.selected_invoices)} invoice(s)")
                
                with col2:
                    if st.button("🚀 Download PDFs", type="primary", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        total_invoices = len(st.session_state.selected_invoices)
                        
                        # Fetch PDF URLs
                        status_text.text("🔄 Fetching invoice URLs...")
                        pdf_urls = []
                        for i, invoice_id in enumerate(st.session_state.selected_invoices):
                            pdf_urls.append(print_invoice(invoice_id, 'json'))
                            progress_bar.progress((i + 1) / total_invoices)
                        
                        # Merge PDFs
                        merger = PdfMerger()
                        status_text.text("🔄 Merging PDFs...")

                        for i, url in enumerate(pdf_urls, start=1):
                            try:
                                response = requests.get(url)
                                response.raise_for_status()
                                merger.append(BytesIO(response.content))
                            except Exception as e:
                                st.error(f"❌ Failed to load PDF {url}: {e}")

                        # Write merged PDF to in-memory buffer
                        merged_pdf = BytesIO()
                        merger.write(merged_pdf)
                        merger.close()
                        merged_pdf.seek(0)

                        # Encode for new tab view
                        b64_pdf = base64.b64encode(merged_pdf.read()).decode("utf-8")
                        merged_pdf.seek(0)

                        status_text.text("✅ PDFs merged successfully!")
                        progress_bar.progress(1.0)

                        # Display link to open in new tab
                        pdf_display_link = f'<a href="data:application/pdf;base64,{b64_pdf}" target="_blank">📂 Open Merged PDF in New Tab</a>'
                        st.markdown(pdf_display_link, unsafe_allow_html=True)

                        # Also allow download
                        st.download_button(
                            label="⬇️ Download Merged PDF",
                            data=merged_pdf,
                            file_name="merged_invoices.pdf",
                            mime="application/pdf"
                        )
            else:
                st.warning("⚠️ Please select at least one invoice to download")
        else:
            st.info("No invoices found matching the selected filters")