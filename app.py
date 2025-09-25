import streamlit as st
import requests
import json
import pandas as pd
import time
import os
import re
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="Warehouse RAG System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data refresh
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Constants
RAG_ENDPOINT = "http://localhost:8080"
CSV_FILE_PATH = "./data/inventory.csv"

def load_inventory_data():
    """Load inventory data from CSV file"""
    try:
        if os.path.exists(CSV_FILE_PATH):
            df = pd.read_csv(CSV_FILE_PATH)
            return df
        else:
            st.error(f"CSV file not found at {CSV_FILE_PATH}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading inventory data: {str(e)}")
        return pd.DataFrame()

def save_inventory_data(df):
    """Save inventory data to CSV file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
        df.to_csv(CSV_FILE_PATH, index=False)
        st.session_state.last_update = time.time()
        return True
    except Exception as e:
        st.error(f"Error saving inventory data: {str(e)}")
        return False

def send_rag_query(query, timeout=30):
    """Send query to RAG system following test-queries-fixed.py method"""
    try:
        payload = {"messages": query}
        headers = {"Content-Type": "application/json"}
        
        # Show request details for debugging
        with st.expander("🔍 Request Details", expanded=False):
            st.json({"url": RAG_ENDPOINT, "payload": payload, "headers": headers})
        
        response = requests.post(RAG_ENDPOINT, json=payload, headers=headers, timeout=timeout)
        
        # Show response details for debugging
        with st.expander("📡 Response Details", expanded=False):
            st.write(f"**Status Code:** {response.status_code}")
            st.write(f"**Headers:** {dict(response.headers)}")
        
        response.raise_for_status()
        
        # Handle both string and JSON responses
        try:
            result = response.json()
            return {"success": True, "data": result}
        except ValueError:
            # If it's not JSON, return the text as result
            return {"success": True, "data": {"result": response.text}}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e), "response_text": getattr(e, 'response', {}).get('text', '')}

def check_rag_server_status():
    """Check if RAG server is running"""
    try:
        response = requests.get(RAG_ENDPOINT, timeout=5)
        return response.status_code in [200, 404, 405]  # 405 is method not allowed, which is fine
    except:
        return False

def parse_update_query(query):
    """Parse natural language update queries into structured updates"""
    query = query.lower().strip()
    updates = {}
    
    # Patterns for different update types
    patterns = {
        'product_name': r'update.*product.*name.*?(\w+).*?(?:as|to)\s*(\w+)',
        'current_stock': r'update.*(?:stock|current.*?stock).*?(?:to|as)\s*(\d+)',
        'last_sold_date': r'update.*last.*?sold.*?date.*?(?:to|as)\s*([0-9-]+)',
        'expiry_date': r'update.*expiry.*?date.*?(?:to|as)\s*([0-9-]+)',
        'sales_last_month': r'update.*(?:sales.*?last.*?month|last.*?month.*?sales).*?(?:to|as)\s*(\d+)',
        'location': r'update.*location.*?(?:to|as)\s*(\w+)',
        'factory_distance': r'update.*(?:factory.*?distance|distance.*?factory).*?(?:to|as)\s*(\d+)'
    }
    
    # Extract ProductID if mentioned
    product_id_match = re.search(r'product.*?(?:id|number)?\s*(\d+)', query)
    if product_id_match:
        updates['ProductID'] = int(product_id_match.group(1))
    
    # Extract updates based on patterns
    for field, pattern in patterns.items():
        match = re.search(pattern, query)
        if match:
            if field == 'product_name':
                updates['old_name'] = match.group(1)
                updates['ProductName'] = match.group(2)
            elif field in ['current_stock', 'sales_last_month', 'factory_distance']:
                updates[field.replace('_', ' ').title().replace(' ', '')] = int(match.group(1))
            elif field in ['last_sold_date', 'expiry_date']:
                updates[field.replace('_', ' ').title().replace(' ', '')] = match.group(1)
            elif field == 'location':
                updates['Location'] = match.group(1)
    
    return updates

def apply_data_updates(df, updates):
    """Apply parsed updates to the dataframe"""
    if df.empty:
        return df, "No data to update"
    
    # Find the row to update
    if 'ProductID' in updates:
        mask = df['ProductID'] == updates['ProductID']
    elif 'old_name' in updates:
        mask = df['ProductName'].str.lower() == updates['old_name'].lower()
    else:
        return df, "Could not identify which product to update. Please specify ProductID or product name."
    
    if not mask.any():
        return df, f"Product not found in inventory"
    
    # Apply updates
    updated_fields = []
    for key, value in updates.items():
        if key in df.columns:
            df.loc[mask, key] = value
            updated_fields.append(f"{key}: {value}")
    
    if updated_fields:
        return df, f"Successfully updated: {', '.join(updated_fields)}"
    else:
        return df, "No valid updates found"

# Main App Layout
st.title("🏭 Real-Time Warehouse Management RAG System")
st.write("Advanced inventory management with AI-powered querying and live data editing capabilities")

# Sidebar for system status
with st.sidebar:
    st.header("🔄 System Status")
    
    # Check RAG server status
    server_status = check_rag_server_status()
    if server_status:
        st.success("✅ RAG Server Online")
    else:
        st.error("❌ RAG Server Offline")
        st.warning("Make sure main-fixed.py is running")
    
    # Data file status
    if os.path.exists(CSV_FILE_PATH):
        st.success("✅ Data File Found")
        file_stat = os.stat(CSV_FILE_PATH)
        st.info(f"Last modified: {datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.error("❌ Data File Missing")
    
    st.header("📖 Instructions")
    with st.expander("Setup Guide", expanded=False):
        st.write("""
        **Required Services:**
        1. `python main-fixed.py` (RAG server)
        2. `python data-generator.py` (optional: live updates)
        3. `streamlit run warehouse-app.py` (this app)
        
        **Features:**
        - AI-powered inventory queries
        - Live data editing with natural language
        - Real-time data visualization
        - Automatic system monitoring
        """)

# Create two main tabs
tab1, tab2 = st.tabs(["🤖 AI Query Assistant", "📝 Live Data Editor"])

# Tab 1: RAG Query Interface
with tab1:
    st.header("💬 Ask Questions About Your Inventory")
    
    # Load and display current inventory summary
    df = load_inventory_data()
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", len(df))
        with col2:
            low_stock = len(df[df['CurrentStock'] < 10])
            st.metric("Low Stock Items", low_stock, delta=f"{low_stock} products" if low_stock > 0 else None)
        with col3:
            out_of_stock = len(df[df['CurrentStock'] == 0])
            st.metric("Out of Stock", out_of_stock, delta=f"{out_of_stock} products" if out_of_stock > 0 else None)
        with col4:
            try:
                expired_items = 0
                current_date = date.today()
                for _, row in df.iterrows():
                    try:
                        expiry_date = datetime.strptime(row['ExpiryDate'], '%Y-%m-%d').date()
                        if expiry_date < current_date:
                            expired_items += 1
                    except:
                        pass
                st.metric("Expired Items", expired_items, delta=f"{expired_items} products" if expired_items > 0 else None)
            except:
                st.metric("Expired Items", "N/A")
    
    # Suggested queries based on test-queries-fixed.py
    st.subheader("🎯 Suggested Queries")
    suggested_queries = [
        "Which products are running low on stock?",
        "What products are expiring soon?",
        "Is product 11023 expired?",
        "Show me products with high demand",
        "Which items should be moved closer to the factory?",
        "List all out of stock products",
        "What products were sold recently?",
        "Which products are in SectionA?",
        "Show products expiring in the next 30 days",
        "What is the status of product 11025?"
    ]
    
    # Quick action buttons
    st.write("**Quick Actions:**")
    cols = st.columns(3)
    with cols[0]:
        if st.button("📉 Low Stock Alert", use_container_width=True):
            st.session_state.selected_query = "Which products are running low on stock?"
    with cols[1]:
        if st.button("⏰ Expiring Soon", use_container_width=True):
            st.session_state.selected_query = "What products are expiring soon?"
    with cols[2]:
        if st.button("🏭 Factory Distance", use_container_width=True):
            st.session_state.selected_query = "Which items should be moved closer to the factory?"
    
    # Query selection and input
    selected_query = st.selectbox("Or choose from suggested queries:", [""] + suggested_queries)
    
    # Get the query to use
    query_to_use = ""
    if 'selected_query' in st.session_state:
        query_to_use = st.session_state.selected_query
        del st.session_state.selected_query
    elif selected_query:
        query_to_use = selected_query
    
    user_query = st.text_area("Enter your question:", value=query_to_use, height=100, 
                             placeholder="Ask about inventory, stock levels, expiry dates, product locations, sales data, etc.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_button = st.button("🔍 Ask AI Assistant", type="primary", use_container_width=True)
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    if ask_button and user_query.strip():
        if not server_status:
            st.error("❌ RAG server is not running. Please start main-fixed.py first.")
        else:
            with st.spinner("🤖 AI is analyzing your inventory data..."):
                start_time = time.time()
                result = send_rag_query(user_query)
                end_time = time.time()
                
                if result["success"]:
                    st.success("✅ Analysis Complete!")
                    
                    # Display the answer
                    st.subheader("📋 Answer")
                    if isinstance(result["data"], dict):
                        answer = result["data"].get('result', 'No result available')
                    else:
                        answer = str(result["data"])
                    
                    st.markdown(answer)
                    
                    # Show response time
                    st.info(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
                else:
                    st.error(f"❌ Query failed: {result['error']}")
                    if result.get('response_text'):
                        st.error(f"Server response: {result['response_text']}")
    elif ask_button:
        st.warning("⚠️ Please enter a question first")

# Tab 2: Live Data Editor
with tab2:
    st.header("📝 Live Inventory Data Management")
    
    # Load current data
    df = load_inventory_data()
    
    if not df.empty:
        # Display current inventory with editing capabilities
        st.subheader("📊 Current Inventory Data")
        
        # Add refresh button and auto-refresh option
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"📄 Showing {len(df)} products")
        with col2:
            if st.button("🔄 Refresh View", use_container_width=True):
                st.rerun()
        with col3:
            auto_refresh = st.checkbox("Auto-refresh", help="Refresh data every 10 seconds")
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True, height=400)
        
        # Natural Language Data Updates
        st.subheader("🗣️ Natural Language Data Updates")
        st.write("Use natural language to update inventory data. Examples:")
        
        # Example queries
        with st.expander("💡 Example Update Commands", expanded=False):
            st.write("""
            - "Update product 11023 stock to 50"
            - "Update product name Anand as Dubey"
            - "Update product 11025 last sold date to 2025-09-23"
            - "Update Organic Apples location to SectionB"
            - "Update product 11020 sales last month to 75"
            - "Update product 11030 expiry date to 2025-10-15"
            """)
        
        # Update query input
        update_query = st.text_area(
            "Enter update command:",
            placeholder="Example: Update product 11023 stock to 50",
            height=80
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            update_button = st.button("📝 Apply Updates", type="primary", use_container_width=True)
        with col2:
            if st.button("👁️ Preview Only", use_container_width=True):
                if update_query.strip():
                    updates = parse_update_query(update_query)
                    if updates:
                        st.json(updates)
                    else:
                        st.warning("Could not parse update query")
        
        if update_button and update_query.strip():
            with st.spinner("Processing update..."):
                # Parse the update query
                updates = parse_update_query(update_query)
                
                if updates:
                    st.write("**Parsed Updates:**")
                    st.json(updates)
                    
                    # Apply updates
                    updated_df, message = apply_data_updates(df.copy(), updates)
                    
                    if updated_df is not None and not updated_df.equals(df):
                        # Save the updated data
                        if save_inventory_data(updated_df):
                            st.success(f"✅ {message}")
                            st.success("💾 Data saved successfully!")
                            
                            # Show the changes
                            st.subheader("📋 Changes Applied")
                            
                            # Find changed rows
                            if 'ProductID' in updates:
                                mask = updated_df['ProductID'] == updates['ProductID']
                            elif 'old_name' in updates:
                                mask = updated_df['ProductName'].str.contains(updates.get('ProductName', ''), case=False, na=False)
                            else:
                                mask = updated_df.index >= 0  # Show all if we can't identify specific row
                            
                            changed_rows = updated_df[mask]
                            st.dataframe(changed_rows, use_container_width=True)
                            
                            # Auto-refresh after successful update
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to save data")
                    else:
                        st.warning(f"⚠️ {message}")
                else:
                    st.error("❌ Could not parse the update command. Please check the format.")
                    st.info("💡 Try: 'Update product [ID/name] [field] to [value]'")
        
        # Manual CSV Upload
        st.subheader("📁 Manual Data Upload")
        uploaded_file = st.file_uploader("Upload new inventory CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                new_df = pd.read_csv(uploaded_file)
                st.write("**Preview of uploaded data:**")
                st.dataframe(new_df.head(), use_container_width=True)
                
                if st.button("📤 Replace Current Data", type="secondary"):
                    if save_inventory_data(new_df):
                        st.success("✅ Data replaced successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to save uploaded data")
            except Exception as e:
                st.error(f"❌ Error reading uploaded file: {str(e)}")
        
        # Auto-refresh functionality
        if auto_refresh:
            time.sleep(10)
            st.rerun()
            
    else:
        st.error("❌ No inventory data found")
        st.info("Please ensure the CSV file exists at: " + CSV_FILE_PATH)
        
        # Option to create sample data
        if st.button("🆕 Create Sample Data"):
            sample_data = {
                'ProductID': [11020, 11021, 11022, 11023, 11024],
                'ProductName': ['Organic Apples', 'Premium Bananas', 'Fresh Oranges', 'Organic Tomatoes', 'Green Lettuce'],
                'Location': ['SectionA', 'SectionB', 'SectionA', 'SectionC', 'SectionA'],
                'CurrentStock': [5, 0, 75, 15, 25],
                'LastSoldDate': ['2025-09-20', '2025-09-19', '2025-09-21', '2025-09-18', '2025-09-22'],
                'ExpiryDate': ['2025-09-25', '2025-09-28', '2025-10-15', '2025-09-23', '2025-09-30'],
                'SalesLastMonth': [45, 0, 120, 80, 95],
                'TotalSales': [320, 180, 650, 420, 380],
                'FactoryDistanceKM': [8, 12, 8, 15, 8]
            }
            sample_df = pd.DataFrame(sample_data)
            
            if save_inventory_data(sample_df):
                st.success("✅ Sample data created!")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("🏭 **Warehouse RAG System** | Powered by Pathway & Streamlit | Real-time AI inventory management")