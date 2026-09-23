<div align="center">
  <h1>Warehouse Management RAG System</h1>

  <p>
    <a href="#"><img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/Pathway-RAG-orange.svg" alt="Pathway RAG"></a>
    <a href="#"><img src="https://img.shields.io/badge/Google-Gemini%20AI-00A4EF.svg" alt="Gemini AI"></a>
    <a href="#"><img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg" alt="Streamlit"></a>
  </p>

  <p><em>An intelligent, real-time warehouse management solution powered by Retrieval-Augmented Generation (RAG).</em></p>
</div>

<hr>

<h2>Overview</h2>
<p>The <strong>Warehouse Management RAG System</strong> leverages the Pathway framework and Google's Gemini AI to provide an intelligent, conversational interface for warehouse operations. Designed for real-time responsiveness, the system automatically detects inventory changes, synchronizes live data, and allows operators to query and manage stock using natural language.</p>

<h2>System Architecture</h2>
<p>The application is built on a decoupled, event-driven architecture to ensure high availability and real-time synchronization between the data layer and the frontend interface.</p>

<pre><code>
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
</code></pre>

<h2>Key Features</h2>
<ul>
  <li><strong>AI-Powered Analytics:</strong> Query complex inventory metrics and statuses using natural language.</li>
  <li><strong>Real-Time Synchronization:</strong> Live data monitoring with automatic change detection via Pathway's streaming engine.</li>
  <li><strong>Interactive Dashboard:</strong> A comprehensive, Streamlit-based web interface for seamless data visualization and management.</li>
  <li><strong>Natural Language Operations:</strong> Update and edit inventory data conversationally without writing SQL or manual data entry.</li>
  <li><strong>Event Simulation Framework:</strong> Built-in mock data generator for testing high-throughput warehouse operations (sales, restocking, expiration alerts).</li>
  <li><strong>Live Monitoring:</strong> Automated alerts for critical inventory thresholds and product life-cycles.</li>
</ul>

<hr>

<h2>Getting Started</h2>

<h3>Prerequisites</h3>
<ul>
  <li>Python 3.8 or higher</li>
  <li><a href="https://aistudio.google.com/app/apikey">Google Gemini API Key</a></li>
</ul>

<h3>Installation</h3>

<ol>
  <li>
    <strong>Clone the repository</strong>
<pre><code>git clone &lt;repository-url&gt;
cd warehouse_rag</code></pre>
  </li>
  <li>
    <strong>Install dependencies</strong>
<pre><code>pip install -U pathway "pathway[xpack-llm]"
pip install python-dotenv streamlit pandas requests</code></pre>
  </li>
  <li>
    <strong>Configure Environment Variables</strong>
    <p>Create a <code>.env</code> file in the root directory and add your Gemini API key:</p>
<pre><code>GEMINI_API_KEY=your_actual_gemini_api_key_here</code></pre>
    <p><em>Note: Ensure your API key is also updated on line 15 of <code>main-fixed.py</code> if environment variable loading requires it.</em></p>
  </li>
  <li>
    <strong>Configure Data Paths</strong>
    <p>Update the absolute path to your <code>inventory.csv</code> file across the following system components:</p>
    <ul>
      <li><strong><code>main-fixed.py</code> (Line 87)</strong>
<pre><code>inventory_table = pw.io.csv.read(
    "/your/absolute/path/to/data/inventory.csv", 
    schema=InventorySchema,
    mode="streaming",
    autocommit_duration_ms=1000
)</code></pre>
      </li>
      <li><strong><code>app.py</code> (Line 18)</strong>
<pre><code>CSV_FILE_PATH = "/your/absolute/path/to/data/inventory.csv"</code></pre>
      </li>
      <li><strong><code>data_generator.py</code> (Lines 92 &amp; 130)</strong>
<pre><code>csv_path = '/your/absolute/path/to/data/inventory.csv'</code></pre>
      </li>
    </ul>
  </li>
</ol>

<hr>

<h2>Running the System</h2>
<p>For full system functionality, it is recommended to run the microservices in separate terminal windows.</p>

<h3>1. Core Service: RAG Engine</h3>
<p>Initializes the Pathway streaming engine, generates embeddings, and serves the API on <code>http://localhost:8080</code>.</p>
<pre><code>python main-fixed.py</code></pre>

<h3>2. User Interface: Web Dashboard</h3>
<p>Launches the interactive Streamlit dashboard on <code>http://localhost:8501</code>.</p>
<pre><code>streamlit run app.py</code></pre>

<h3>3. Background Service: Data Simulator (Optional)</h3>
<p>Simulates warehouse operations like sales, restocking, and movements to test real-time data processing.</p>
<pre><code>python data_generator.py</code></pre>

<h3>4. Development Tool: Testing Framework (Optional)</h3>
<p>Provides an interactive or batch-mode CLI for testing RAG query accuracy and response latency.</p>
<pre><code>python test-queries-fixed.py</code></pre>

<hr>

<h2>Usage Examples</h2>
<p>The system interprets natural language to perform complex inventory checks and updates.</p>

<ul>
  <li><strong>Inventory Status</strong>
    <ul>
      <li><em>"Which products are running low on stock?"</em></li>
      <li><em>"What is the current stock level of product 11023?"</em></li>
    </ul>
  </li>
  <li><strong>Expiry Management</strong>
    <ul>
      <li><em>"Show products expiring in the next 30 days."</em></li>
      <li><em>"List all expired items."</em></li>
    </ul>
  </li>
  <li><strong>Logistics &amp; Location</strong>
    <ul>
      <li><em>"Which items are currently stored in Section A?"</em></li>
      <li><em>"What products should be moved closer to the factory?"</em></li>
    </ul>
  </li>
  <li><strong>Data Mutability (via UI)</strong>
    <ul>
      <li><em>"Update product 11023 stock to 50."</em></li>
      <li><em>"Change Organic Apples location to Section B."</em></li>
    </ul>
  </li>
</ul>

<hr>

<h2>System Components</h2>

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Purpose</th>
      <th>Port</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>main-fixed.py</code></td>
      <td>RAG Engine &amp; API Server</td>
      <td><code>8080</code></td>
      <td>Core Service</td>
    </tr>
    <tr>
      <td><code>app.py</code></td>
      <td>Streamlit Web Interface</td>
      <td><code>8501</code></td>
      <td>User Interface</td>
    </tr>
    <tr>
      <td><code>data_generator.py</code></td>
      <td>Mock Data Simulator</td>
      <td><code>-</code></td>
      <td>Optional/Dev</td>
    </tr>
    <tr>
      <td><code>test-queries-fixed.py</code></td>
      <td>Testing Framework</td>
      <td><code>-</code></td>
      <td>Development</td>
    </tr>
  </tbody>
</table>

<p><strong>Data Schema Requirement:</strong><br>
The system expects a CSV format with the following headers:<br>
<code>ProductID, ProductName, Location, CurrentStock, LastSoldDate, ExpiryDate, SalesLastMonth, TotalSales, FactoryDistanceKM</code></p>

<hr>

<h2>Deployment Options</h2>

<h3>1. Docker Deployment</h3>
<pre><code>FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -U pathway "pathway[xpack-llm]" streamlit python-dotenv pandas requests
EXPOSE 8080 8501
CMD ["bash", "-c", "python main-fixed.py &amp; streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]</code></pre>

<h3>2. Cloud Virtual Machine (AWS/GCP/Azure)</h3>
<p>For traditional VM deployments, a process manager like PM2 is recommended:</p>
<pre><code># Install process manager
npm install -g pm2

# Start services
pm2 start main-fixed.py --name "rag-engine"
pm2 start "streamlit run app.py" --name "web-interface"
pm2 startup &amp;&amp; pm2 save</code></pre>

<h3>3. Kubernetes</h3>
<pre><code>apiVersion: apps/v1
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
              key: api-key</code></pre>

<hr>

<h2>Troubleshooting &amp; Optimization</h2>

<h3>Debugging Commands</h3>
<p>Verify system health and API responsiveness:</p>
<pre><code># Check service status
curl http://localhost:8080
curl http://localhost:8501

# Test API directly
curl -X POST -H "Content-Type: application/json" \
     -d '{"messages": "test query"}' \
     http://localhost:8080

# Monitor Pathway engine logs
tail -f pathway.log</code></pre>

<h3>Performance Best Practices</h3>
<ul>
  <li><strong>Storage:</strong> Utilize SSD storage for optimal CSV file I/O performance during streaming.</li>
  <li><strong>LLM Config:</strong> Adjust <code>max_tokens</code> in your Gemini configuration based on the desired response verbosity.</li>
  <li><strong>Sync Rate:</strong> Tune <code>autocommit_duration_ms</code> in <code>main-fixed.py</code> to balance update latency with compute overhead.</li>
</ul>

<hr>

<h2>Contributing</h2>
<p>Contributions are welcome. Please adhere to the following workflow:</p>
<ol>
  <li>Fork the repository.</li>
  <li>Create a feature branch (<code>git checkout -b feature/enhancement</code>).</li>
  <li>Commit your changes (<code>git commit -m 'Implement enhancement'</code>).</li>
  <li>Push to the branch (<code>git push origin feature/enhancement</code>).</li>
  <li>Open a Pull Request.</li>
</ol>

<h2>License</h2>
<p>This project is licensed under the MIT License. See the <code>LICENSE</code> file for details.</p>
