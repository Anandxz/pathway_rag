import requests
import json
import time
import sys

# Test queries for warehouse management
TEST_QUERIES = [
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

def send_query(query, base_url="http://localhost:8080"):
    """Send a query to the RAG system and return the response"""
    try:
        # Correct payload format for Pathway REST connector
        payload = {"messages": query}
        headers = {"Content-Type": "application/json"}
        
        print(f"Sending payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(base_url, json=payload, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        # Handle both string and JSON responses
        try:
            result = response.json()
            print(f"JSON response received: {result}")
            return result
        except ValueError:
            # If it's not JSON, return the text as result
            print(f"Text response received: {response.text}")
            return {"result": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return {"error": str(e)}

def wait_for_server(base_url="http://localhost:8080", max_attempts=30):
    """Wait for the server to become available"""
    print("Waiting for server to start...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code in [200, 404, 405]:  # 405 is method not allowed, which is fine
                print("✅ Server is running!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - Server not ready yet...")
        time.sleep(2)
    
    print("❌ Server did not start within the expected time")
    return False

def run_interactive_test():
    """Interactive testing mode"""
    print("Real-Time Warehouse RAG System - Interactive Testing")
    print("=" * 50)
    
    # Wait for server to be ready
    if not wait_for_server():
        print("Cannot proceed without server. Please start main.py first.")
        return
    
    print("Enter queries to test the system. Type 'quit' to exit.")
    print("Type 'samples' to see sample queries.")
    print()
    
    while True:
        query = input("Query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if query.lower() == 'samples':
            print("\nSample queries:")
            for i, q in enumerate(TEST_QUERIES, 1):
                print(f"{i:2d}. {q}")
            print()
            continue
        
        if not query:
            continue
        
        print(f"\nSending query: {query}")
        print("-" * 40)
        
        start_time = time.time()
        result = send_query(query)
        end_time = time.time()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Response:")
            # Handle both dict and string responses
            if isinstance(result, dict):
                response_text = result.get('result', 'No result returned')
            else:
                response_text = str(result)
            
            print(response_text)
        
        print(f"\nResponse time: {end_time - start_time:.2f} seconds")
        print("=" * 50)
        print()

def run_batch_test():
    """Run all test queries in batch mode"""
    print("Real-Time Warehouse RAG System - Batch Testing")
    print("=" * 50)
    
    # Wait for server to be ready
    if not wait_for_server():
        print("Cannot proceed without server. Please start main.py first.")
        return
    
    successful_queries = 0
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\nTest {i}/{len(TEST_QUERIES)}: {query}")
        print("-" * 40)
        
        start_time = time.time()
        result = send_query(query)
        end_time = time.time()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Response:")
            # Handle both dict and string responses
            if isinstance(result, dict):
                response_text = result.get('result', 'No result returned')
            else:
                response_text = str(result)
            
            # Truncate long responses for batch mode
            if len(response_text) > 200:
                response_text = response_text[:200] + "..."
            
            print(response_text)
            successful_queries += 1
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        # Small delay between queries
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print(f"Batch testing completed! {successful_queries}/{len(TEST_QUERIES)} queries successful.")

def test_real_time_updates():
    """Test real-time functionality by sending the same query twice"""
    print("Real-Time Update Test")
    print("=" * 30)
    
    # Wait for server to be ready
    if not wait_for_server():
        print("Cannot proceed without server. Please start main.py first.")
        return
    
    print("This test sends the same query twice to demonstrate real-time updates.")
    print("Make sure the data_generator.py is running to see changes!")
    print()
    
    test_query = "Which products are running low on stock?"
    
    print("First query (current state):")
    print(f"Query: {test_query}")
    result1 = send_query(test_query)
    
    if "error" not in result1:
        print("Response 1:")
        print(result1.get('result', 'No result'))
    
    print("\nWaiting 30 seconds for potential data updates...")
    time.sleep(30)
    
    print("\nSecond query (after potential updates):")
    result2 = send_query(test_query)
    
    if "error" not in result2:
        print("Response 2:")
        print(result2.get('result', 'No result'))
    
    print("\nCompare the two responses to see if data has updated in real-time!")

def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Select testing mode:")
        print("1. Interactive mode (recommended)")
        print("2. Batch test all queries")
        print("3. Real-time update test")
        mode = input("Enter choice (1-3): ").strip()
    
    if mode in ['1', 'interactive']:
        run_interactive_test()
    elif mode in ['2', 'batch']:
        run_batch_test()
    elif mode in ['3', 'realtime']:
        test_real_time_updates()
    else:
        print("Invalid mode. Use 'interactive', 'batch', or 'realtime'")

if __name__ == "__main__":
    main()