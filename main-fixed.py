import pathway as pw
import os
from dotenv import load_dotenv
from pathway.xpacks.llm import llms
from pathway.xpacks.llm import embedders
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.stdlib.indexing.nearest_neighbors import BruteForceKnnFactory
import json

# Load environment variables
load_dotenv()

# Set Gemini API key
os.environ['GEMINI_API_KEY'] = 'your_api_key'

class InventorySchema(pw.Schema):
    ProductID: int
    ProductName: str
    Location: str
    CurrentStock: int
    LastSoldDate: str
    ExpiryDate: str
    SalesLastMonth: int
    TotalSales: int
    FactoryDistanceKM: int

class QuerySchema(pw.Schema):
    messages: str

@pw.udf
def create_document_text(product_id: int, product_name: str, location: str,
                        current_stock: int, last_sold_date: str, expiry_date: str,
                        sales_last_month: int, total_sales: int,
                        factory_distance_km: int) -> str:
    """Transform inventory row into searchable document text"""
    
    # Calculate stock status
    if current_stock == 0:
        stock_status = "OUT OF STOCK"
    elif current_stock < 10:
        stock_status = "CRITICAL LOW STOCK"
    elif current_stock < 50:
        stock_status = "LOW STOCK"
    else:
        stock_status = "ADEQUATE STOCK"
    
    # Calculate expiry status
    from datetime import datetime, date
    try:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        current_date = date(2025, 9, 22)  # Updated to current date
        days_to_expiry = (expiry - current_date).days
        
        if days_to_expiry < 0:
            expiry_status = "EXPIRED"
        elif days_to_expiry <= 7:
            expiry_status = "EXPIRES SOON - URGENT"
        elif days_to_expiry <= 30:
            expiry_status = "EXPIRES THIS MONTH"
        else:
            expiry_status = "FRESH"
    except:
        expiry_status = "UNKNOWN EXPIRY"
    
    # Calculate demand status
    if sales_last_month > 100:
        demand_status = "HIGH DEMAND"
    elif sales_last_month > 50:
        demand_status = "MEDIUM DEMAND"
    elif sales_last_month > 0:
        demand_status = "LOW DEMAND"
    else:
        demand_status = "NO RECENT SALES"
    
    # Calculate distance status
    if factory_distance_km <= 5:
        distance_status = "CLOSE TO FACTORY"
    elif factory_distance_km <= 15:
        distance_status = "MODERATE DISTANCE"
    else:
        distance_status = "FAR FROM FACTORY"
    
    # Build comprehensive document
    document_text = f"""
Product Information:
Product ID: {product_id}
Product Name: {product_name}
Location: {location}
Current Stock: {current_stock} units ({stock_status})
Last Sold Date: {last_sold_date}
Expiry Date: {expiry_date} ({expiry_status})
Sales Last Month: {sales_last_month} units ({demand_status})
Total Sales: {total_sales} units
Factory Distance: {factory_distance_km} km ({distance_status})
Status Summary: {stock_status}, {expiry_status}, {demand_status}
Priority: {"HIGH PRIORITY" if stock_status in ["CRITICAL LOW STOCK", "OUT OF STOCK"] or expiry_status == "EXPIRES SOON - URGENT" else "NORMAL PRIORITY"}
"""
    
    return document_text.strip()

@pw.udf
def build_warehouse_prompt(docs: list, query: str) -> str:
    """Build context-aware prompt for warehouse management queries"""
    
    # Extract context from documents
    context_parts = []
    if docs:
        for doc in docs:
            if hasattr(doc, 'text'):
                context_parts.append(str(doc.text))
            elif isinstance(doc, dict):
                # Extract text from the document
                text = doc.get('text', doc.get('chunk', doc.get('data', '')))
                if text:
                    context_parts.append(str(text))
            elif isinstance(doc, str):
                context_parts.append(doc)
            else:
                # Handle other types by converting to string
                context_parts.append(str(doc))
    
    context = "\n\n---\n\n".join(context_parts) if context_parts else "No inventory data found."
    
    prompt = f"""You are a warehouse management AI assistant. Use the following real-time inventory data to answer the query.

CURRENT INVENTORY DATA:
{context}

USER QUERY: {query}

Provide a helpful response that:
1. Directly answers the question with specific details (product IDs, names, stock levels)
2. Highlights urgent issues (low stock, expiring items)
3. Provides actionable recommendations
4. Uses exact numbers and dates from the data

RESPONSE:"""
    
    return prompt

def main():
    print("Starting Real-Time Warehouse Management RAG System...")
    print("=" * 60)
    
    # Read inventory data from CSV
    print("Loading inventory data from ./data/inventory.csv...")
    inventory_table = pw.io.csv.read(
        "./data/inventory.csv",  # Fixed path - removed incorrect /bin/python prefix
        schema=InventorySchema,
        mode="streaming",
        autocommit_duration_ms=1000
    )
    
    # Transform CSV rows into documents with proper schema
    print("Transforming inventory data into searchable documents...")
    documents_table = inventory_table.select(
        
        text=create_document_text(
            pw.this.ProductID,
            pw.this.ProductName,
            pw.this.Location,
            pw.this.CurrentStock,
            pw.this.LastSoldDate,
            pw.this.ExpiryDate,
            pw.this.SalesLastMonth,
            pw.this.TotalSales,
            pw.this.FactoryDistanceKM
        )

        
         
    )

    documents_table = inventory_table.select(
        
        data=create_document_text(
            pw.this.ProductID,
            pw.this.ProductName,
            pw.this.Location,
            pw.this.CurrentStock,
            pw.this.LastSoldDate,
            pw.this.ExpiryDate,
            pw.this.SalesLastMonth,
            pw.this.TotalSales,
            pw.this.FactoryDistanceKM
        )

        
         
    )
    
    
    # Set up embedding model
    print("Initializing Gemini embedder...")
    embedder = embedders.GeminiEmbedder(
        model="gemini-embedding-001",  # Fixed model name
        api_key='GEMINI_API_KEY'
    )
    
    # Create document store with the transformed documents
    print("Building document store for retrieval...")
    splitter = TokenCountSplitter(max_tokens=400)
    retriever_factory = BruteForceKnnFactory(embedder=embedder)
    
    doc_store = DocumentStore(
        docs=documents_table,
        retriever_factory=retriever_factory,
        splitter=splitter
    )
    
    # Set up web server for queries
    print("Starting HTTP server on port 8080...")
    webserver = pw.io.http.PathwayWebserver(
        host="0.0.0.0",
        port=8080
    )
    
    # Create REST endpoint for queries
    queries, response_writer = pw.io.http.rest_connector(
        webserver=webserver,
        schema=QuerySchema,
        autocommit_duration_ms=500,
        delete_completed_queries=False
    )
    
    # Process queries and retrieve relevant documents
    print("Setting up query processing pipeline...")
    
    # Retrieve relevant documents for each query
    retrieval_results = queries + doc_store.retrieve_query(
        queries.select(
            query=pw.this.messages,
            k=5,  # Number of documents to retrieve
            metadata_filter=pw.cast(str | None, None),
            filepath_globpattern=pw.cast(str | None, None)
        )
    )
    
    # Build prompts with retrieved context
    prompts = retrieval_results.select(
        prompt=build_warehouse_prompt(pw.this.result, pw.this.messages)
    )
    
    # Set up LLM for response generation
    print("Initializing Gemini chat model...")
    chat_model = llms.LiteLLMChat(
        model="gemini/gemini-1.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
        max_tokens=500
    )
    
    # Generate responses
    responses = prompts.select(
        result=chat_model(llms.prompt_chat_single_qa(pw.this.prompt))
    )
    
    # Send responses back to clients
    response_writer(responses)
    
    print("\n" + "=" * 60)
    print("✅ RAG pipeline initialized successfully!")
    print("\n📡 Server running on http://localhost:8080")
    print("\n📝 Send POST requests with JSON: {'messages': 'your query here'}")
    print("\nExample queries:")
    print(" • 'Which products are running low on stock?'")
    print(" • 'What products are expiring soon?'")
    print(" • 'Show me high demand items'")
    print(" • 'Which products need to be moved closer to the factory?'")
    print("\n⚡ System is monitoring ./data/inventory.csv for real-time updates")
    print("=" * 60)
    
    # Run the pipeline
    pw.run()

if __name__ == "__main__":
    main()
