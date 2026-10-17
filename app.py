
#!/usr/bin/env python3
"""
Flask Web Application for Intelligent Traffic Analysis Simulator
=================================================================
A web-based interface for analyzing traffic data.

Author: NLP Traffic Analyzer
Version: 1.0.0
"""

import os
import sys

# Configure UTF-8 encoding for stdout/stderr to prevent charmap UnicodeEncodeErrors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import json
import pandas as pd
from datetime import datetime
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, abort, session
from werkzeug.utils import secure_filename

# Import our traffic analyzer
from traffic_analysis_simulator import (
    TrafficAnalyzer, TrafficDataGenerator, TrafficVisualizer,
    TextPreprocessor, KeywordExtractor, PatternDetector
)

app = Flask(__name__)
app.secret_key = 'traffic_analysis_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('visualizations', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# Session-isolated analyzer cache and global fallback
ANALYZER_CACHE = {}
analyzer = None
analysis_results = None


def get_current_analysis():
    """Retrieve analyzer and results for current session, with fallback"""
    sid = session.get('sid')
    if sid and sid in ANALYZER_CACHE:
        return ANALYZER_CACHE[sid]['analyzer'], ANALYZER_CACHE[sid]['results']
    return analyzer, analysis_results


def set_current_analysis(new_analyzer, new_results):
    """Store analyzer and results for current session and global fallback"""
    global analyzer, analysis_results
    analyzer = new_analyzer
    analysis_results = new_results
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    ANALYZER_CACHE[session['sid']] = {
        'analyzer': new_analyzer,
        'results': new_results,
        'timestamp': datetime.now()
    }


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_visualization_files():
    """Get list of generated visualization files"""
    viz_dir = 'visualizations'
    files = []
    if os.path.exists(viz_dir):
        for f in os.listdir(viz_dir):
            if f.endswith(('.png', '.html')):
                files.append({
                    'name': f,
                    'path': os.path.join(viz_dir, f),
                    'url': f'/visualizations/{f}'
                })
    return files


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle data upload and analysis"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Create analyzer and run analysis
                new_analyzer = TrafficAnalyzer(data_path=filepath)
                new_results = new_analyzer.run_full_analysis()
                set_current_analysis(new_analyzer, new_results)
                
                flash('Analysis completed successfully!', 'success')
                return redirect(url_for('results'))
                
            except Exception as e:
                flash(f'Error during analysis: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file format. Please upload CSV, JSON, or Excel file.', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Generate sample data and analyze"""
    if request.method == 'POST':
        try:
            # Get number of records from form
            num_records = int(request.form.get('num_records', 500))
            
            # Generate sample data
            sample_data = TrafficDataGenerator.generate_sample_data(num_records)
            
            # Create analyzer
            new_analyzer = TrafficAnalyzer(data=sample_data)
            new_results = new_analyzer.run_full_analysis()
            set_current_analysis(new_analyzer, new_results)
            
            flash(f'Generated and analyzed {num_records} sample records!', 'success')
            return redirect(url_for('results'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('generate.html')


@app.route('/results')
def results():
    """Display analysis results"""
    curr_analyzer, curr_results = get_current_analysis()
    
    if curr_analyzer is None or curr_results is None:
        flash('No analysis results available. Please run an analysis first.', 'warning')
        return redirect(url_for('index'))
    
    # Get visualization image files (PNGs)
    viz_files = [f for f in get_visualization_files() if f['name'].endswith('.png')]
    
    # Prepare data for template
    context = {
        'total_records': len(curr_analyzer.df) if curr_analyzer.df is not None else 0,
        'keyword_freq': curr_results.get('keyword_freq', {}).most_common(15) if curr_results.get('keyword_freq') else [],
        'severity_counts': curr_results.get('severity_counts', {}),
        'categories': curr_results.get('categories', {}),
        'trends': curr_results.get('trends', {}),
        'congestion_patterns': curr_results.get('congestion_patterns', {}),
        'viz_files': viz_files,
        'df': curr_analyzer.df
    }
    
    return render_template('results.html', **context)


@app.route('/dashboard')
def dashboard():
    """Display interactive dashboard"""
    curr_analyzer, curr_results = get_current_analysis()
    
    if curr_analyzer is None or curr_results is None:
        flash('No analysis results available. Please run an analysis first.', 'warning')
        return redirect(url_for('index'))
    
    # Prepare data for template
    context = {
        'total_records': len(curr_analyzer.df) if curr_analyzer.df is not None else 0,
        'keyword_freq': curr_results.get('keyword_freq', {}).most_common(15) if curr_results.get('keyword_freq') else [],
        'severity_counts': curr_results.get('severity_counts', {}),
        'categories': curr_results.get('categories', {}),
        'trends': curr_results.get('trends', {}),
        'congestion_patterns': curr_results.get('congestion_patterns', {}),
        'bigrams': curr_results.get('bigrams', []),
        'trigrams': curr_results.get('trigrams', []),
        'viz_files': get_visualization_files(),
        'df': curr_analyzer.df
    }
    
    return render_template('dashboard.html', **context)


@app.route('/visualizations/<filename>')
def serve_visualization(filename):
    """Serve visualization files safely"""
    safe_name = secure_filename(filename)
    viz_path = os.path.join('visualizations', safe_name)
    if not os.path.isfile(viz_path):
        abort(404)
    return send_from_directory('visualizations', safe_name)


@app.route('/download/report')
def download_report():
    """Download analysis report"""
    report_path = 'traffic_analysis_report.txt'
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    flash('Report not found. Please run an analysis first.', 'warning')
    return redirect(url_for('results'))


@app.route('/download/data')
def download_data():
    """Download processed data"""
    curr_analyzer, _ = get_current_analysis()
    
    if curr_analyzer is None or curr_analyzer.df is None:
        flash('No data available. Please run an analysis first.', 'warning')
        return redirect(url_for('index'))
    
    output_path = os.path.join(OUTPUT_FOLDER, 'processed_traffic_data.csv')
    curr_analyzer.df.to_csv(output_path, index=False)
    
    return send_file(output_path, as_attachment=True)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large! Maximum allowed upload size is 16MB.', 'error')
    return redirect(url_for('upload'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print("  Starting Traffic Analysis Web Application")
    print(f"{'='*60}")
    print("\nOpen your browser and navigate to: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

