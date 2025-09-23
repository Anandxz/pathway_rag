import pandas as pd
import random
import time
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def create_initial_inventory():
    """Create initial inventory CSV with sample warehouse data"""
    
    # Realistic product catalog
    products = [
        ("Widget A - Heavy Duty", "SectionA-Aisle3-Shelf2"),
        ("Electronic Component B", "SectionC-Aisle2-Shelf5"), 
        ("Packaging Material C", "SectionB-Aisle7-Shelf1"),
        ("Storage Box D", "SectionA-Aisle1-Shelf3"),
        ("Power Tool E", "SectionD-Aisle6-Shelf4"),
        ("Food Product F", "ColdStorage-Zone2"),
        ("Medical Supply G", "SecureArea-Aisle5"),
        ("Spare Part H", "SectionB-Aisle2-Shelf6"),
        ("Electronic Device I", "SectionD-Aisle1-Shelf2"),
        ("Office Supply J", "SectionA-Aisle5-Shelf1"),
        ("Raw Material K", "BulkStorage-Zone1"),
        ("Consumer Good L", "SectionC-Aisle3-Shelf4"),
        ("Industrial Item M", "HeavyGoods-Area3"),
        ("Seasonal Product N", "SectionB-Aisle4-Shelf2"),
        ("Fragile Item O", "SpecialHandling-Zone1")
    ]
    
    # Generate realistic inventory data
    inventory_data = []
    base_date = datetime.now() - timedelta(days=10)
    
    for i, (product_name, location) in enumerate(products, start=11023):
        # Generate realistic stock levels
        if "Heavy" in product_name or "Industrial" in product_name:
            current_stock = random.randint(5, 50)
            sales_last_month = random.randint(10, 40)
        elif "Medical" in product_name or "Food" in product_name:
            current_stock = random.randint(20, 150)
            sales_last_month = random.randint(50, 120)
        else:
            current_stock = random.randint(0, 200)
            sales_last_month = random.randint(0, 150)
        
        # Some products should be out of stock or low
        if i % 5 == 0:  # Every 5th product is low/out
            current_stock = random.randint(0, 8)
        
        # Generate dates
        last_sold_days_ago = random.randint(0, 30)
        last_sold_date = (base_date + timedelta(days=last_sold_days_ago)).strftime('%Y-%m-%d')
        
        # Expiry dates - some expired, some expiring soon
        if "Food" in product_name or "Medical" in product_name:
            expiry_days = random.randint(-5, 60)  # Can be expired
        else:
            expiry_days = random.randint(30, 365)  # Longer shelf life
        
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')
        
        # Sales and distance data
        total_sales = sales_last_month * random.randint(6, 24)  # 6-24 months of history
        factory_distance = random.randint(1, 25)
        
        inventory_data.append({
            'ProductID': i,
            'ProductName': product_name,
            'Location': location,
            'CurrentStock': current_stock,
            'LastSoldDate': last_sold_date,
            'ExpiryDate': expiry_date,
            'SalesLastMonth': sales_last_month,
            'TotalSales': total_sales,
            'FactoryDistanceKM': factory_distance
        })
    
    # Create DataFrame
    df = pd.DataFrame(inventory_data)
    
    # Ensure data directory exists
    os.makedirs('./data', exist_ok=True)
    
    # Save with proper file handling
    csv_path = '/home/anax/Documents/warehouse_rag3/data/inventory.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Created initial inventory with {len(df)} products")
    print("\nSample of inventory data:")
    print(df.head(5).to_string())
    print(f"\n📊 Stock Status Summary:")
    print(f"  • Out of Stock: {len(df[df['CurrentStock'] == 0])} products")
    print(f"  • Low Stock (<10): {len(df[df['CurrentStock'] < 10])} products")
    print(f"  • Expired: {len(df[df['ExpiryDate'] < datetime.now().strftime('%Y-%m-%d')])} products")
    
    return df

def atomic_csv_update(df, csv_path):
    """Atomically update CSV file to ensure Pathway detects changes"""
    # Write to temporary file first
    temp_path = csv_path + '.tmp'
    df.to_csv(temp_path, index=False)
    
    # Atomic rename (this ensures Pathway sees the change)
    os.replace(temp_path, csv_path)

def simulate_real_time_updates(df, update_interval=10):
    """Simulate real-time warehouse operations"""
    
    csv_path = '/home/anax/Documents/warehouse_rag3/data/inventory.csv'
    
    print(f"\n🚀 Starting real-time warehouse simulator")
    print(f"📊 Updates every {update_interval} seconds")
    print("⏹️  Press Ctrl+C to stop\n")
    
    update_count = 0
    
    try:
        while True:
            time.sleep(update_interval)
            update_count += 1
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n{'='*50}")
            print(f"📦 Update #{update_count} at {timestamp}")
            print(f"{'='*50}")
            
            # Simulate various warehouse events
            num_events = random.randint(2, 5)
            events = []
            
            for _ in range(num_events):
                idx = random.randint(0, len(df) - 1)
                product_id = df.at[idx, 'ProductID']
                product_name = df.at[idx, 'ProductName']
                current_stock = df.at[idx, 'CurrentStock']
                
                # Choose event type based on warehouse patterns
                event_weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Sales, restock, returns, move, expiry
                event_type = random.choices(
                    ['sale', 'restock', 'return', 'move', 'expiry_update'],
                    weights=event_weights,
                    k=1
                )[0]
                
                if event_type == 'sale':
                    # Customer purchase
                    if current_stock > 0:
                        units_sold = min(random.randint(1, 10), current_stock)
                        df.at[idx, 'CurrentStock'] = current_stock - units_sold
                        df.at[idx, 'SalesLastMonth'] += units_sold
                        df.at[idx, 'TotalSales'] += units_sold
                        df.at[idx, 'LastSoldDate'] = datetime.now().strftime('%Y-%m-%d')
                        events.append(f"📉 SALE: {product_name} - Sold {units_sold} units (Stock: {current_stock} → {df.at[idx, 'CurrentStock']})")
                
                elif event_type == 'restock':
                    # Inventory replenishment
                    restock_amount = random.randint(20, 100)
                    df.at[idx, 'CurrentStock'] = current_stock + restock_amount
                    # New batch might have new expiry
                    if random.random() < 0.5:
                        new_expiry = datetime.now() + timedelta(days=random.randint(60, 180))
                        df.at[idx, 'ExpiryDate'] = new_expiry.strftime('%Y-%m-%d')
                        events.append(f"📈 RESTOCK: {product_name} - Added {restock_amount} units (New expiry: {df.at[idx, 'ExpiryDate']})")
                    else:
                        events.append(f"📈 RESTOCK: {product_name} - Added {restock_amount} units (Stock: {current_stock} → {df.at[idx, 'CurrentStock']})")
                
                elif event_type == 'return':
                    # Customer returns
                    if df.at[idx, 'SalesLastMonth'] > 0:
                        return_units = min(random.randint(1, 5), df.at[idx, 'SalesLastMonth'])
                        df.at[idx, 'CurrentStock'] += return_units
                        df.at[idx, 'SalesLastMonth'] = max(0, df.at[idx, 'SalesLastMonth'] - return_units)
                        events.append(f"🔄 RETURN: {product_name} - {return_units} units returned (Stock: {current_stock} → {df.at[idx, 'CurrentStock']})")
                
                elif event_type == 'move':
                    # Warehouse reorganization
                    sections = ['SectionA', 'SectionB', 'SectionC', 'SectionD', 'BulkStorage', 'ColdStorage']
                    aisles = ['Aisle1', 'Aisle2', 'Aisle3', 'Aisle4', 'Aisle5', 'Aisle6']
                    shelves = ['Shelf1', 'Shelf2', 'Shelf3', 'Shelf4', 'Shelf5']
                    
                    old_location = df.at[idx, 'Location']
                    new_location = f"{random.choice(sections)}-{random.choice(aisles)}-{random.choice(shelves)}"
                    df.at[idx, 'Location'] = new_location
                    events.append(f"📍 MOVED: {product_name} - {old_location} → {new_location}")
                
                elif event_type == 'expiry_update':
                    # Quality check found expiry issue
                    if random.random() < 0.3:  # 30% chance of expiry issue
                        # Product expiring soon
                        days_until_expiry = random.randint(1, 7)
                        new_expiry = datetime.now() + timedelta(days=days_until_expiry)
                        df.at[idx, 'ExpiryDate'] = new_expiry.strftime('%Y-%m-%d')
                        events.append(f"⚠️ EXPIRY ALERT: {product_name} - Expires in {days_until_expiry} days!")
            
            # Display events
            print("\n📋 Warehouse Events:")
            for event in events:
                print(f"  {event}")
            
            # Save updated data using atomic write
            atomic_csv_update(df, csv_path)
            
            # Show summary statistics
            print(f"\n📊 Current Warehouse Status:")
            out_of_stock = len(df[df['CurrentStock'] == 0])
            low_stock = len(df[(df['CurrentStock'] > 0) & (df['CurrentStock'] < 10)])
            expired = len(df[df['ExpiryDate'] < datetime.now().strftime('%Y-%m-%d')])
            expiring_soon = len(df[
                (df['ExpiryDate'] >= datetime.now().strftime('%Y-%m-%d')) & 
                (df['ExpiryDate'] <= (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
            ])
            
            print(f"  🔴 Out of Stock: {out_of_stock} products")
            print(f"  🟡 Low Stock (<10): {low_stock} products")
            print(f"  ⛔ Expired: {expired} products")
            print(f"  ⚠️  Expiring within 7 days: {expiring_soon} products")
            
            print(f"\n✅ CSV updated - Pathway should detect changes automatically")
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Simulator stopped after {update_count} updates")
        print(f"📁 Final inventory saved to {csv_path}")
        print("\nFinal Statistics:")
        print(df.describe()[['CurrentStock', 'SalesLastMonth', 'FactoryDistanceKM']])

def verify_file_system():
    """Verify that the file system is working correctly"""
    test_path = './data/test_write.txt'
    try:
        os.makedirs('./data', exist_ok=True)
        with open(test_path, 'w') as f:
            f.write("test")
        os.remove(test_path)
        print("✅ File system write test: PASSED")
        return True
    except Exception as e:
        print(f"❌ File system write test: FAILED - {e}")
        return False

def main():
    print("🏭 Real-Time Warehouse Data Simulator")
    print("="*50)
    
    # Verify file system
    if not verify_file_system():
        print("⚠️ Warning: File system issues detected. Updates may not work properly.")
        return
    
    # Check existing inventory
    csv_path = '/home/anax/Documents/warehouse_rag3/data/inventory.csv'
    if os.path.exists(csv_path):
        print(f"📁 Found existing inventory at {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"📦 Loaded {len(df)} products from file")
        
        print("\n🔧 Options:")
        print("1. Continue with existing data (start simulation)")
        print("2. Recreate inventory with fresh data")
        print("3. View current inventory summary")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '2':
            df = create_initial_inventory()
    else:
        print("📦 No existing inventory found. Creating new warehouse data...")
        df = create_initial_inventory()
        choice = '1'  # Auto-start simulation with new data
    
    if choice == '1' or (not os.path.exists(csv_path) and choice != '3'):
        print("\n" + "="*50)
        interval = input("Update interval in seconds (default=10): ").strip()
        interval = int(interval) if interval.isdigit() else 10
        simulate_real_time_updates(df, update_interval=interval)
    elif choice == '3':
        print("\n📊 Current Inventory Summary:")
        print("="*50)
        print(df.to_string())
        print("\n📈 Statistics:")
        print(df.describe())

if __name__ == "__main__":
    main()