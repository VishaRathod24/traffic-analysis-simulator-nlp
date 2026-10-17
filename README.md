# 🚦 Intelligent Traffic Analysis Simulator (NLP Platform)

An intelligent, full-stack Natural Language Processing (NLP) and statistical analytics platform designed to analyze textual traffic reports, violation logs, and road event streams to detect congestion patterns, peak hours, severity distributions, and actionable traffic management insights.

---

## 🌟 Key Features

- **Text Preprocessing & NLP Pipeline:**
  - Tokenization, stopword filtering, punctuation cleaning, and POS-aware lemmatization using NLTK.
  - Extraction of traffic-specific n-grams (unigrams, bigrams, trigrams).
  - Hashtag extraction and categorical tagging (Congestion, Accidents, Road Conditions, Flow, Weather, Location).
- **Automated Schema Detection & Harmonization:**
  - Standardizes unstructured user datasets (e.g. `Indian_Traffic_Violations.csv` or tabular regional accident aggregates like `ADSI_Table_1A.2.csv`).
  - Automatically synthesizes textual representations and temporal features (`hour`, `date`, `day_of_week`) when explicit columns are absent.
- **Statistical Pattern Detection:**
  - Peak congestion hour identification based on deviation thresholds.
  - Directional traffic trend analysis (increasing/decreasing percentages over moving averages).
  - Severity level classification (`normal`, `low`, `medium`, `high`).
- **Interactive Visualizations & Reporting:**
  - **Keyword Frequency Chart:** Top traffic terminology visual distribution.
  - **Word Cloud:** High-density lexical traffic overview.
  - **Temporal Distribution:** Hourly reports and day-of-week volume bar charts.
  - **Severity & Category Distributions:** Multi-dimensional event breakdown.
  - **Interactive Plotly Dashboard:** Rich interactive multi-chart dashboard with zoom, hover, and filter capabilities.
  - **Exportable Artifacts:** One-click download for structured CSV data and comprehensive text reports.
- **Enterprise-Grade Web Application:**
  - Built with Flask, Bootstrap 5, FontAwesome, and modern glassmorphic styling.
  - Session-isolated state (multi-user concurrency safe).
  - Headless non-GUI Matplotlib engine (`Agg`) for thread-safe server execution.
  - Built-in upload file size limiter (16MB) and security path traversal sandboxing.

---

## 🛠️ Architecture & Tech Stack

- **Backend:** Python 3.10+, Flask, Werkzeug, Gunicorn
- **NLP & Data Science:** NLTK, Pandas, NumPy
- **Visualizations:** Matplotlib, Seaborn, WordCloud, Plotly
- **Frontend:** HTML5, Vanilla CSS3, Bootstrap 5, FontAwesome 6
- **Deployment:** Docker, Gunicorn WSGI, Procfile (Render / Railway / Heroku ready)

---

## 📂 Project Structure

```
├── app.py                         # Flask web application & API routes
├── traffic_analysis_simulator.py  # Core NLP, pattern detector & visualization engine
├── test_suite.py                  # Automated QA test suite (30 scenarios, 100% pass)
├── requirements.txt               # Python package dependencies
├── start_project.bat              # Windows one-click startup batch script
├── Procfile                       # PaaS production process runner (Gunicorn)
├── Dockerfile                     # Containerized production build
├── .gitignore                     # Git tracking exclusions
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Main layout with glassmorphic UI & spinner
│   ├── index.html                 # Homepage with overview & quick actions
│   ├── upload.html                # Custom dataset upload portal
│   ├── generate.html              # Synthetic traffic data generator
│   ├── results.html               # Analysis results & static chart gallery
│   ├── dashboard.html             # Interactive Plotly dashboard view
│   ├── about.html                 # Architecture & technology details
│   └── error.html                 # Custom 404/500/413 error templates
├── uploads/                       # Temporary storage for uploaded datasets (.gitkeep)
├── output/                        # Processed CSV exports (.gitkeep)
└── visualizations/                # Generated PNG charts & interactive HTML (.gitkeep)
```

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/nlp-traffic-analysis.git
cd nlp-traffic-analysis
```

### 2. Set Up Virtual Environment
On Windows:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
#### Windows One-Click:
Double-click `start_project.bat` or run:
```powershell
.\start_project.bat
```

#### Manual Run:
```bash
python app.py
```

Open your browser at **[http://localhost:5000](http://localhost:5000)**.

---

## 🧪 Running Automated QA Tests

The repository includes a comprehensive 30-scenario test suite verifying navigation, boundary conditions, input sanitization, directory traversal protection, file format compatibility, and artifact integrity:

```bash
python test_suite.py
```

Expected output:
```
======================================================================
  QA TEST EXECUTION REPORT - TRAFFIC ANALYSIS NLP PLATFORM
======================================================================
[PASS] [Smoke] GET /
[PASS] [Smoke] GET /about
[PASS] [Smoke] GET /upload
[PASS] [Smoke] GET /generate
[PASS] [Boundary/Stress] Generate: Boundary & Stress tests
[PASS] [Security/Validation] Upload: Disallowed extensions & empty files blocked
[PASS] [Compatibility] Process CSV, XLSX, Unstructured, & Aggregated Regional Data
[PASS] [Security] Path Traversal containment verified
[PASS] [Integrity] Report & Processed CSV Downloads verified
[PASS] [Visualization] Generated 7 PNG charts & interactive Plotly dashboard
[PASS] [UI/UX] GET /dashboard renders complete UI
======================================================================
  TEST SUMMARY: 30/30 Passed (100.0%)
======================================================================
```

---

## ☁️ Deployment

### Option 1: Render / Railway / Heroku (PaaS)
1. Push your repository to GitHub.
2. Link your repo in **[Render.com](https://render.com)** as a **Web Service**.
3. Render detects `requirements.txt` and `Procfile`:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers=2 --threads=4 --timeout=120`

### Option 2: Docker Container
Build and run the container locally or on any cloud server:
```bash
docker build -t traffic-nlp-analyzer .
docker run -p 5000:5000 traffic-nlp-analyzer
```
Navigate to `http://localhost:5000`.

---

## 📄 License
This project is licensed under the MIT License.
