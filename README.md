# 🏭 Warehouse Management RAG System

A real-time warehouse management system powered by Retrieval-Augmented Generation (RAG) using Pathway and Gemini AI. This system enables intelligent inventory querying, real-time data updates, and seamless warehouse operations management.

## ✨ Features

- **AI-Powered Queries**: Ask natural language questions about your inventory
- **Real-Time Updates**: Live data synchronization with automatic change detection
- **Interactive Dashboard**: Web-based interface for querying and data management
- **Natural Language Editing**: Update inventory data using conversational commands
- **Mock Data Generator**: Simulate real-time warehouse operations
- **Comprehensive Testing**: Batch and interactive testing capabilities
- **Live Monitoring**: Real-time inventory alerts and status tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Pathway RAG    │    │   Gemini AI     │
│   Frontend      │◄──►│     Engine       │◄──►│    Models       │
│   (app.py)      │    │ (main-fixed.py)  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        
         │                        │                        
         ▼                        ▼                        
┌─────────────────┐    ┌──────────────────┐               
│  CSV Data       │    │ Data Generator   │               
│  (inventory.csv)│◄──►│(data_generator.py)│               
└─────────────────┘    └──────────────────┘               
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gemini API Key (Get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd warehouse_rag
```

2. **Install required packages**
```bash
pip install -U pathway
pip install "pathway[xpack-llm]"
pip install python-dotenv
pip install streamlit
pip install pandas
pip install requests
```

3. **Set up environment variables**

Edit the `.env` file and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

4. **Configure API key in main-fixed.py**

Open `main-fixed.py` and update the API key on line 15:
```python
os.environ['GEMINI_API_KEY'] = 'your_actual_gemini_api_key_here'
```

5. **Update file paths**

Update the CSV file path in the following files to match your system:

**main-fixed.py** (line 87):
```python
inventory_table = pw.io.csv.read(
    "/your/absolute/path/to/data/inventory.csv",  # Update this path
    schema=InventorySchema,
    mode="streaming",
    autocommit_duration_ms=1000
)
```

**app.py** (line 18):
```python
CSV_FILE_PATH = "/your/absolute/path/to/data/inventory.csv"  # Update this path
```

**data_generator.py** (line 92 and 130):
```python
csv_path = '/your/absolute/path/to/data/inventory.csv'  # Update this path
```

## 🎮 Running the System

The system consists of multiple components that work together. Run each in a separate terminal:

### Terminal 1: RAG Engine (Core System)
```bash
python main-fixed.py
```
This starts the Pathway RAG engine that:
- Monitors CSV file for changes
- Processes data through Gemini embeddings
- Serves API endpoints on `http://localhost:8080`
- Provides real-time AI-powered responses

### Terminal 2: Web Interface (Recommended)
```bash
streamlit run app.py
```
This launches the interactive web dashboard at `http://localhost:8501` featuring:
- AI query assistant
- Live data editor with natural language commands
- Real-time inventory monitoring
- Data visualization and alerts

### Terminal 3: Data Generator (Optional)
```bash
python data_generator.py
```
This simulates real-time warehouse operations:
- Generates realistic inventory updates
- Simulates sales, restocking, and movement
- Creates expiry alerts and stock notifications
- Updates CSV file automatically

### Terminal 4: Testing Interface (Optional)
```bash
python test-queries-fixed.py
```
Choose from testing modes:
- **Interactive mode**: Chat-like interface for testing queries
- **Batch mode**: Run predefined test queries
- **Real-time test**: Verify live data updates

## 💬 Example Queries

Try these natural language queries with the system:

### Inventory Status
- "Which products are running low on stock?"
- "Show me all out of stock items"
- "What is the current stock level of product 11023?"

### Expiry Management
- "What products are expiring soon?"
- "List all expired items"
- "Show products expiring in the next 30 days"

### Sales Analytics
- "Which products have high demand?"
- "What were the recent sales?"
- "Show products with low sales last month"

### Location & Logistics
- "Which items are in SectionA?"
- "What products should be moved closer to the factory?"
- "Show products by location"

### Data Updates (via Web Interface)
- "Update product 11023 stock to 50"
- "Update Organic Apples location to SectionB"
- "Update product 11025 expiry date to 2025-12-15"

## 📊 System Components

| Component | Purpose | Port | Status |
|-----------|---------|------|--------|
| `main-fixed.py` | RAG Engine & API Server | 8080 | Core Service |
| `app.py` | Streamlit Web Interface | 8501 | User Interface |
| `data_generator.py` | Mock Data Simulator | - | Optional |
| `test-queries-fixed.py` | Testing Framework | - | Development |

## 🔧 Configuration

### Data Schema
The system expects CSV data with these columns:
```csv
ProductID,ProductName,Location,CurrentStock,LastSoldDate,ExpiryDate,SalesLastMonth,TotalSales,FactoryDistanceKM
```

### API Endpoints
- **Query Endpoint**: `POST http://localhost:8080`
- **Request Format**: `{"messages": "your query here"}`
- **Response Format**: `{"result": "AI response"}`

## 🚀 Deployment

### Local Development
Follow the installation steps above for local development and testing.

### Production Deployment

#### Option 1: Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -U pathway "pathway[xpack-llm]" streamlit python-dotenv pandas requests

EXPOSE 8080 8501

CMD ["bash", "-c", "python main-fixed.py & streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
```

#### Option 2: Cloud Deployment (AWS/GCP/Azure)

1. **Prepare environment**
   - Set up cloud VM instance
   - Install Python and dependencies
   - Configure firewall rules for ports 8080 and 8501

2. **Deploy files**
   - Upload all project files
   - Set environment variables
   - Update file paths for cloud storage

3. **Use process manager**
   ```bash
   # Install PM2 for process management
   npm install -g pm2
   
   # Start services
   pm2 start main-fixed.py --name "rag-engine"
   pm2 start "streamlit run app.py" --name "web-interface"
   pm2 startup
   pm2 save
   ```

#### Option 3: Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: warehouse-rag
spec:
  replicas: 1
  selector:
    matchLabels:
      app: warehouse-rag
  template:
    metadata:
      labels:
        app: warehouse-rag
    spec:
      containers:
      - name: rag-engine
        image: your-registry/warehouse-rag:latest
        ports:
        - containerPort: 8080
        - containerPort: 8501
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-secret
              key: api-key
```

## 🛠️ Troubleshooting

### Common Issues

1. **Server not starting**
   - Check if ports 8080/8501 are available
   - Verify Gemini API key is correct
   - Ensure all dependencies are installed

2. **CSV file not found**
   - Verify file paths are correct and use absolute paths
   - Check file permissions
   - Ensure data directory exists

3. **No responses from RAG**
   - Confirm `main-fixed.py` is running
   - Check server logs for errors
   - Verify CSV file has proper schema

4. **Real-time updates not working**
   - Ensure file modification timestamps are updating
   - Check Pathway streaming configuration
   - Verify data generator is running

### Debug Commands
```bash
# Check if services are running
curl http://localhost:8080
curl http://localhost:8501

# Test API directly
curl -X POST -H "Content-Type: application/json" \
     -d '{"messages": "test query"}' \
     http://localhost:8080

# Check logs
tail -f pathway.log
```

## 📈 Performance Tips

- Use SSD storage for better CSV file I/O
- Increase `max_tokens` in LLM configuration for detailed responses
- Adjust `autocommit_duration_ms` for faster/slower update detection
- Use proper indexing for large inventories

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pathway](https://pathway.com) for the real-time RAG framework
- [Google Gemini](https://ai.google.dev) for AI capabilities
- [Streamlit](https://streamlit.io) for the web interface
- The open-source community for various dependencies

## 📧 Support

For support and questions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Contact the development team

---

**Built with ❤️ for modern warehouse management**
