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

## Getting Started Locally

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/VishaRathod24/nlp-traffic-analysis.git
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


