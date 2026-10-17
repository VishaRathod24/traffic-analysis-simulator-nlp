#!/usr/bin/env python3
"""
Intelligent Traffic Analysis Simulator
=======================================
A simulator that analyzes traffic-related textual data to identify 
congestion patterns and trends using NLP and statistical analysis.

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

import re
import json
import time
import random
import string
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

# Data Processing
import pandas as pd
import numpy as np

# NLP Libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag, ngrams

# Visualization
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Download required NLTK data
def download_nltk_resources():
    """Download required NLTK resources"""
    resources = [
        'punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng'
    ]
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except:
            pass

download_nltk_resources()

# ============================================================================
# CONFIGURATION AND UTILITIES
# ============================================================================

class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class TrafficAnalyzerConfig:
    """Configuration for the traffic analyzer"""
    
    # Traffic-related keywords
    TRAFFIC_KEYWORDS = {
        'congestion': ['congestion', 'traffic', 'jam', 'gridlock', 'bottleneck', 'delay'],
        'road_condition': ['road', 'highway', 'expressway', 'lane', 'construction', 'maintenance'],
        'accident': ['accident', 'crash', 'collision', 'incident', 'breakdown'],
        'weather': ['rain', 'fog', 'snow', 'storm', 'weather', 'visibility'],
        'time_related': ['morning', 'evening', 'rush hour', 'peak hour', 'weekend', 'holiday'],
        'location': ['highway', 'interstate', 'route', 'street', 'avenue', 'expressway'],
        'transport': ['vehicle', 'car', 'truck', 'bus', 'motorcycle', 'sedan', 'suv'],
        'flow': ['slow', 'fast', 'moving', 'stopped', 'queue', 'backed up', 'clear']
    }
    
    # Severity indicators
    SEVERITY_WORDS = {
        'high': ['severe', 'heavy', 'major', 'extreme', 'worst', 'critical', 'stuck'],
        'medium': ['moderate', 'moderate', 'delayed', 'building', 'increased'],
        'low': ['light', 'minor', 'slight', 'clearing', 'improving']
    }
    
    # Time patterns
    TIME_PATTERNS = {
        'rush_hour_morning': r'\b(6|7|8|9)\s*(am|AM|morning)\b',
        'rush_hour_evening': r'\b(4|5|6|7)\s*(pm|PM|evening)\b',
        'night': r'\b(9|10|11)\s*(pm|PM|night)\b|\b(12|1|2|3|4|5)\s*(am|AM|midnight)\b'
    }


# ============================================================================
# TEXT PREPROCESSING MODULE
# ============================================================================

class TextPreprocessor:
    """Handles all text preprocessing operations"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
        # Add custom stop words
        self.stop_words.update(['rt', 'http', 'https', 'amp', 'via', 'like', 'just'])
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove mentions and hashtags symbols (keep the word)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#', '', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text: str) -> List[str]:
        """Remove stopwords from text"""
        tokens = word_tokenize(text)
        return [word for word in tokens if word not in self.stop_words]
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return word_tokenize(text.lower())
    
    def stem(self, words: List[str]) -> List[str]:
        """Apply stemming to words"""
        return [self.stemmer.stem(word) for word in words]
    
    def lemmatize(self, words: List[str]) -> List[str]:
        """Apply lemmatization to words"""
        return [self.lemmatizer.lemmatize(word) for word in words]
    
    def get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """Get Part-of-Speech tags"""
        tokens = word_tokenize(text)
        return pos_tag(tokens)
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#(\w+)', text)
    
    def preprocess(self, text: str, remove_stop: bool = True) -> str:
        """Complete preprocessing pipeline"""
        text = self.clean_text(text)
        if remove_stop:
            words = self.remove_stopwords(text)
            return ' '.join(words)
        return text


# ============================================================================
# KEYWORD EXTRACTION MODULE
# ============================================================================

class KeywordExtractor:
    """Extracts and analyzes keywords from traffic data"""
    
    def __init__(self):
        self.config = TrafficAnalyzerConfig()
        self.preprocessor = TextPreprocessor()
    
    def extract_traffic_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract traffic-related keywords from text"""
        text = text.lower()
        keywords_found = {}
        
        for category, keywords in self.config.TRAFFIC_KEYWORDS.items():
            found = [kw for kw in keywords if kw in text]
            if found:
                keywords_found[category] = found
        
        return keywords_found
    
    def calculate_keyword_frequency(self, texts: List[str]) -> Counter:
        """Calculate frequency of keywords across all texts"""
        all_words = []
        for text in texts:
            processed = self.preprocessor.preprocess(text)
            words = self.preprocessor.tokenize(processed)
            all_words.extend(words)
        
        # Filter out short words and numbers
        all_words = [w for w in all_words if len(w) > 2 and not w.isdigit()]
        return Counter(all_words)
    
    def extract_bigrams(self, texts: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        """Extract most common bigrams"""
        all_bigrams = []
        for text in texts:
            processed = self.preprocessor.preprocess(text)
            words = self.preprocessor.tokenize(processed)
            bigrams_list = list(ngrams(words, 2))
            all_bigrams.extend(bigrams_list)
        
        bigram_counts = Counter(all_bigrams)
        return bigram_counts.most_common(top_n)
    
    def extract_trigrams(self, texts: List[str], top_n: int = 15) -> List[Tuple[str, int]]:
        """Extract most common trigrams"""
        all_trigrams = []
        for text in texts:
            processed = self.preprocessor.preprocess(text)
            words = self.preprocessor.tokenize(processed)
            trigrams_list = list(ngrams(words, 3))
            all_trigrams.extend(trigrams_list)
        
        trigram_counts = Counter(all_trigrams)
        return trigram_counts.most_common(top_n)


# ============================================================================
# PATTERN DETECTION MODULE
# ============================================================================

class PatternDetector:
    """Detects patterns and trends in traffic data"""
    
    def __init__(self):
        self.config = TrafficAnalyzerConfig()
    
    def detect_severity(self, text: str) -> str:
        """Detect traffic severity level"""
        text = text.lower()
        
        for level, words in self.config.SEVERITY_WORDS.items():
            if any(word in text for word in words):
                return level
        return 'normal'
    
    def detect_time_patterns(self, text: str) -> Dict[str, bool]:
        """Detect time-related patterns in text"""
        patterns = {}
        for pattern_name, regex in self.config.TIME_PATTERNS.items():
            patterns[pattern_name] = bool(re.search(regex, text))
        return patterns
    
    def detect_congestion_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze congestion patterns from dataframe"""
        patterns = {
            'peak_hours': [],
            'problem_locations': [],
            'common_causes': [],
            'time_distribution': {}
        }
        
        if 'timestamp' in df.columns:
            # Extract hour distribution
            df['hour'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.hour
            hour_counts = df['hour'].value_counts().to_dict()
            patterns['time_distribution'] = hour_counts
            
            # Identify peak hours (hours with above average traffic)
            mean_count = np.mean(list(hour_counts.values()))
            patterns['peak_hours'] = [h for h, c in hour_counts.items() 
                                       if c > mean_count * 1.2 and not pd.isna(h)]
        
        return patterns
    
    def analyze_trends(self, df: pd.DataFrame, window: int = 7) -> Dict:
        """Analyze traffic trends over time"""
        trends = {}
        
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.date
            daily_counts = df['date'].value_counts().sort_index()
            
            if len(daily_counts) > window:
                # Calculate moving average
                trends['moving_average'] = daily_counts.rolling(window=window).mean().to_dict()
                trends['daily_counts'] = daily_counts.to_dict()
                
                # Calculate trend direction
                if len(daily_counts) >= 2:
                    first_half = daily_counts.iloc[:len(daily_counts)//2].mean()
                    second_half = daily_counts.iloc[len(daily_counts)//2:].mean()
                    trends['direction'] = 'increasing' if second_half > first_half else 'decreasing'
                    trends['change_percentage'] = abs((second_half - first_half) / first_half * 100)
        
        return trends


# ============================================================================
# DATA VISUALIZATION MODULE
# ============================================================================

class TrafficVisualizer:
    """Creates visualizations for traffic analysis"""
    
    def __init__(self, output_dir: str = 'visualizations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
    
    def plot_keyword_frequency(self, freq: Counter, title: str = "Top Keywords", 
                               filename: str = "keyword_frequency.png"):
        """Plot keyword frequency bar chart"""
        if not freq:
            print(f"{Color.YELLOW}No frequency data to plot{Color.END}")
            return
        
        top_words = freq.most_common(15)
        if not top_words:
            print(f"{Color.YELLOW}No frequency data to plot{Color.END}")
            return
        words, counts = zip(*top_words)
        
        plt.figure(figsize=(12, 6))
        bars = plt.barh(range(len(words)), counts, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(words))))
        plt.yticks(range(len(words)), words)
        plt.xlabel('Frequency')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Add value labels
        for bar, count in zip(bars, counts):
            plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                    str(count), va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")
    
    def plot_wordcloud(self, text: str, filename: str = "wordcloud.png"):
        """Generate and save word cloud"""
        if not text.strip():
            print(f"{Color.YELLOW}No text data for word cloud{Color.END}")
            return
        
        wordcloud = WordCloud(
            width=1200, height=600,
            background_color='white',
            colormap='viridis',
            max_words=100,
            min_font_size=10,
            random_state=42
        ).generate(text)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Traffic Text Word Cloud', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")
    
    def plot_time_distribution(self, df: pd.DataFrame, filename: str = "time_distribution.png"):
        """Plot traffic distribution over time"""
        if 'timestamp' not in df.columns:
            print(f"{Color.YELLOW}No timestamp data available{Color.END}")
            return
        
        df['hour'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.hour
        hour_counts = df['hour'].value_counts().sort_index()
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Hourly distribution
        hours = range(24)
        counts = [hour_counts.get(h, 0) for h in hours]
        colors = ['#ff6b6b' if 7 <= h <= 9 or 16 <= h <= 19 else '#4ecdc4' for h in hours]
        
        axes[0].bar(hours, counts, color=colors)
        axes[0].set_xlabel('Hour of Day')
        axes[0].set_ylabel('Number of Reports')
        axes[0].set_title('Traffic Reports by Hour', fontsize=14, fontweight='bold')
        axes[0].set_xticks(hours)
        
        # Add legend
        legend_elements = [Patch(facecolor='#ff6b6b', label='Peak Hours'),
                          Patch(facecolor='#4ecdc4', label='Off-Peak Hours')]
        axes[0].legend(handles=legend_elements)
        
        # Daily distribution
        if 'date' in df.columns:
            df['day_of_week'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.day_name()
            day_counts = df['day_of_week'].value_counts()
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_values = [day_counts.get(day, 0) for day in days]
            
            axes[1].bar(days, day_values, color=sns.color_palette("husl", 7))
            axes[1].set_xlabel('Day of Week')
            axes[1].set_ylabel('Number of Reports')
            axes[1].set_title('Traffic Reports by Day', fontsize=14, fontweight='bold')
            axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")
    
    def plot_severity_distribution(self, severity_counts: Dict, 
                                   filename: str = "severity_distribution.png"):
        """Plot severity distribution pie chart"""
        if not severity_counts:
            print(f"{Color.YELLOW}No severity data to plot{Color.END}")
            return
        
        labels = list(severity_counts.keys())
        sizes = list(severity_counts.values())
        colors = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4ecdc4']
        
        plt.figure(figsize=(10, 8))
        wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors[:len(labels)], startangle=90,
                                           explode=[0.05] * len(labels))
        plt.setp(autotexts, size=12, weight="bold")
        plt.setp(texts, size=12)
        plt.title('Traffic Severity Distribution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")
    
    def plot_category_distribution(self, category_data: Dict,
                                    filename: str = "category_distribution.png"):
        """Plot category distribution bar chart"""
        if not category_data:
            print(f"{Color.YELLOW}No category data to plot{Color.END}")
            return
        
        categories = list(category_data.keys())
        counts = list(category_data.values())
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(categories, counts, color=sns.color_palette("viridis", len(categories)))
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.title('Traffic Categories Distribution', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")
    
    def plot_trends(self, trends: Dict, filename: str = "trends.png"):
        """Plot traffic trends over time"""
        if 'daily_counts' not in trends or not trends['daily_counts']:
            print(f"{Color.YELLOW}No trend data to plot{Color.END}")
            return
        
        daily_counts = trends['daily_counts']
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[d] for d in dates]
        
        plt.figure(figsize=(14, 6))
        
        # Plot daily counts
        plt.plot(dates, counts, 'o-', color='#4ecdc4', linewidth=2, markersize=6, label='Daily Reports')
        
        # Plot moving average if available
        if 'moving_average' in trends:
            ma = trends['moving_average']
            ma_dates = sorted(ma.keys())
            ma_values = [ma[d] for d in ma_dates if not pd.isna(ma[d])]
            ma_dates = [d for d in ma_dates if not pd.isna(ma[d])]
            if ma_dates:
                plt.plot(ma_dates, ma_values, '--', color='#ff6b6b', linewidth=2, 
                        label=f'{7}-Day Moving Average')
        
        plt.xlabel('Date')
        plt.ylabel('Number of Reports')
        plt.title('Traffic Trend Over Time', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add trend direction annotation
        if 'direction' in trends:
            direction = trends['direction']
            change = trends.get('change_percentage', 0)
            annotation = f"Trend: {direction.capitalize()} ({change:.1f}% change)"
            plt.annotate(annotation, xy=(0.02, 0.95), xycoords='axes fraction',
                        fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")
    
    def generate_dashboard(self, df: pd.DataFrame, analysis_results: Dict,
                          filename: str = "dashboard.html"):
        """Generate interactive HTML dashboard using Plotly"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Hourly Distribution', 'Daily Distribution', 
                          'Severity Distribution', 'Top Keywords'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Hourly distribution
        if 'timestamp' in df.columns:
            df_copy = df.copy()
            df_copy['hour'] = pd.to_datetime(df_copy['timestamp'], errors='coerce').dt.hour
            hour_counts = df_copy['hour'].value_counts().sort_index()
            hours = list(range(24))
            counts = [hour_counts.get(h, 0) for h in hours]
            
            fig.add_trace(
                go.Bar(x=hours, y=counts, name='Reports', marker_color='#4ecdc4'),
                row=1, col=1
            )
        
        # Severity distribution
        if 'severity' in df.columns:
            severity_counts = df['severity'].value_counts()
            fig.add_trace(
                go.Pie(labels=severity_counts.index, values=severity_counts.values,
                      name='Severity', marker=dict(colors=['#ff6b6b', '#ffd93d', '#6bcb77'])),
                row=1, col=2
            )
        
        # Daily distribution
        if 'timestamp' in df.columns:
            df_copy = df.copy()
            df_copy['day'] = pd.to_datetime(df_copy['timestamp'], errors='coerce').dt.day_name()
            day_counts = df_copy['day'].value_counts()
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_values = [day_counts.get(day, 0) for day in days]
            
            fig.add_trace(
                go.Bar(x=days, y=day_values, name='By Day', marker_color='#95e1d3'),
                row=2, col=1
            )
        
        # Top keywords
        if 'keyword_freq' in analysis_results and analysis_results['keyword_freq']:
            top_kw = analysis_results['keyword_freq'].most_common(10)
            if top_kw:
                words, freqs = zip(*top_kw)
                fig.add_trace(
                    go.Bar(x=list(freqs), y=list(words), name='Keywords', 
                          orientation='h', marker_color='#a8e6cf'),
                    row=2, col=2
                )
        
        fig.update_layout(
            height=800,
            width=1200,
            title_text="Traffic Analysis Dashboard",
            title_x=0.5,
            showlegend=False
        )
        
        fig.write_html(os.path.join(self.output_dir, filename))
        print(f"{Color.GREEN}✓ Saved: {filename}{Color.END}")


# ============================================================================
# SAMPLE DATA GENERATOR
# ============================================================================

class TrafficDataGenerator:
    """Generates sample traffic data for demonstration"""
    
    # Sample templates for traffic reports
    TRAFFIC_TEMPLATES = [
        "Heavy {location} traffic due to {cause}, expect delays",
        "Accident reported on {location}, {severity} congestion reported",
        "Road construction on {location}, traffic {condition}",
        "{severity} traffic jam on {location} near {landmark}",
        "Weather alert: {condition} causing {severity} traffic on {location}",
        "Rush hour {condition} on {location}, delays expected",
        "Vehicle breakdown on {location}, {severity} delays",
        "Traffic {condition} on {location} due to {cause}",
        "{severity} congestion reported at {location}",
        "Lane closure on {location} causing {severity} backup"
    ]
    
    LOCATIONS = [
        "Highway 101", "Interstate 95", "Main Street", "Broadway",
        "Expressway", "Park Avenue", "Oak Street", "Maple Avenue",
        "Downtown", "Central Avenue", "River Road", "Harbor Bridge"
    ]
    
    LANDMARKS = [
        "the shopping center", "the stadium", "the school zone",
        "the hospital", "the downtown area", "the industrial district"
    ]
    
    CAUSES = [
        "accident", "construction", "road work", "vehicle breakdown",
        "event", "holiday traffic", "lane closure", "disabled vehicle"
    ]
    
    CONDITIONS = [
        "heavy", "moderate", "light", "slow-moving", "stop-and-go",
        "congested", "clear", "improving", "building"
    ]
    
    SEVERITIES = ["severe", "moderate", "light", "minimal"]
    
    @classmethod
    def generate_sample_data(cls, num_records: int = 500, 
                             start_date: datetime = None) -> pd.DataFrame:
        """Generate sample traffic data"""
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        
        data = []
        
        for i in range(num_records):
            # Random timestamp within the date range
            random_days = random.randint(0, 30)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            timestamp = start_date + timedelta(days=random_days, 
                                               hours=random_hours,
                                               minutes=random_minutes)
            
            # Generate text using template
            template = random.choice(cls.TRAFFIC_TEMPLATES)
            text = template.format(
                location=random.choice(cls.LOCATIONS),
                landmark=random.choice(cls.LANDMARKS),
                cause=random.choice(cls.CAUSES),
                condition=random.choice(cls.CONDITIONS),
                severity=random.choice(cls.SEVERITIES)
            )
            
            # Add some hashtags
            hashtags = f"#{random.choice(['traffic', 'road', 'commute'])} #{random.choice(['delay', 'update', 'news'])}"
            full_text = f"{text} {hashtags}"
            
            # Determine severity based on text
            severity = "normal"
            if "severe" in text.lower() or "heavy" in text.lower():
                severity = "high"
            elif "moderate" in text.lower():
                severity = "medium"
            elif "light" in text.lower() or "clear" in text.lower():
                severity = "low"
            
            # Determine if peak hour
            is_peak = 7 <= random_hours <= 9 or 16 <= random_hours <= 19
            
            data.append({
                'id': i + 1,
                'timestamp': timestamp.isoformat(),
                'text': full_text,
                'severity': severity,
                'is_peak_hour': is_peak,
                'source': random.choice(['twitter', 'traffic_api', 'user_report', 'sensor'])
            })
        
        return pd.DataFrame(data)


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================

class TrafficAnalyzer:
    """Main class that orchestrates the entire traffic analysis process"""
    
    def __init__(self, data: pd.DataFrame = None, data_path: str = None):
        """Initialize the analyzer with data"""
        
        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.END}")
        print(f"{Color.CYAN}  INTELLIGENT TRAFFIC ANALYSIS SIMULATOR{Color.END}")
        print(f"{Color.CYAN}{'='*60}{Color.END}\n")
        
        self.preprocessor = TextPreprocessor()
        self.keyword_extractor = KeywordExtractor()
        self.pattern_detector = PatternDetector()
        self.visualizer = TrafficVisualizer()
        
        # Load or generate data
        if data is not None:
            self.df = data.copy()
        elif data_path and os.path.exists(data_path):
            self.df = self.load_data(data_path)
        else:
            print(f"{Color.YELLOW}No data provided. Generating sample data...{Color.END}")
            self.df = TrafficDataGenerator.generate_sample_data(1000)
        
        self._standardize_dataframe()
        
        # Performance safeguard for large datasets
        if len(self.df) > 10000:
            print(f"{Color.YELLOW}Large dataset detected ({len(self.df)} records). Sampling 10,000 records for optimal NLP processing speed.{Color.END}")
            self.df = self.df.sample(10000, random_state=42).reset_index(drop=True)
            
        self.analysis_results = {}
        
        print(f"{Color.GREEN}✓ Loaded {len(self.df)} records{Color.END}")
    
    def _standardize_dataframe(self):
        """Standardize columns to ensure 'text', 'timestamp', and 'id' exist for analysis"""
        if self.df is None or len(self.df) == 0:
            return

        cols_lower = {str(col).lower(): col for col in self.df.columns}

        # 1. Standardize / synthesize 'text'
        if 'text' not in self.df.columns:
            matched_col = None
            for candidate in ['text', 'comment', 'comments', 'description', 'details',
                              'message', 'notes', 'violation_type', 'title', 'summary',
                              'incident', 'report', 'state/ut/city']:
                if candidate in cols_lower:
                    matched_col = cols_lower[candidate]
                    break
            
            if matched_col:
                text_series = self.df[matched_col].astype(str)
                for aux in ['location', 'weather_condition', 'road_condition', 'violation_type']:
                    if aux in cols_lower and cols_lower[aux] != matched_col:
                        text_series = text_series + ". " + aux.replace('_', ' ').title() + ": " + self.df[cols_lower[aux]].astype(str)
                self.df['text'] = text_series
            else:
                obj_cols = self.df.select_dtypes(include=['object', 'string']).columns.tolist()
                if obj_cols:
                    self.df['text'] = self.df[obj_cols].astype(str).agg(' | '.join, axis=1)
                else:
                    self.df['text'] = self.df.apply(
                        lambda row: ', '.join([f"{col}: {val}" for col, val in row.items()]),
                        axis=1
                    )
        
        self.df['text'] = self.df['text'].fillna('').astype(str)

        # 2. Standardize / synthesize 'timestamp'
        if 'timestamp' not in self.df.columns:
            if 'date' in cols_lower and 'time' in cols_lower:
                d_col, t_col = cols_lower['date'], cols_lower['time']
                self.df['timestamp'] = pd.to_datetime(
                    self.df[d_col].astype(str) + ' ' + self.df[t_col].astype(str),
                    errors='coerce'
                )
            elif 'date' in cols_lower:
                self.df['timestamp'] = pd.to_datetime(self.df[cols_lower['date']], errors='coerce')
            elif 'time' in cols_lower:
                self.df['timestamp'] = pd.to_datetime(self.df[cols_lower['time']], errors='coerce')
            elif 'datetime' in cols_lower:
                self.df['timestamp'] = pd.to_datetime(self.df[cols_lower['datetime']], errors='coerce')
            else:
                self.df['timestamp'] = pd.NaT

        # If timestamps are missing or invalid, synthesize realistic timestamps
        if self.df['timestamp'].isna().sum() > len(self.df) * 0.5:
            start_date = datetime.now() - timedelta(days=30)
            self.df['timestamp'] = [
                start_date + timedelta(minutes=random.randint(0, 30 * 24 * 60))
                for _ in range(len(self.df))
            ]

        # 3. Standardize 'id'
        if 'id' not in self.df.columns:
            for id_cand in ['id', 'violation_id', 'sl. no.', 'sl_no', 'slno']:
                if id_cand in cols_lower:
                    self.df['id'] = self.df[cols_lower[id_cand]]
                    break
            if 'id' not in self.df.columns:
                self.df['id'] = list(range(1, len(self.df) + 1))

        # 4. Standardize derived date/time fields
        self.df['hour'] = pd.to_datetime(self.df['timestamp'], errors='coerce').dt.hour
        self.df['date'] = pd.to_datetime(self.df['timestamp'], errors='coerce').dt.date
        self.df['day_of_week'] = pd.to_datetime(self.df['timestamp'], errors='coerce').dt.day_name()

    def load_data(self, path: str) -> pd.DataFrame:
        """Load data from file with encoding fallback"""
        ext = os.path.splitext(path)[1].lower()
        
        if ext == '.csv':
            try:
                return pd.read_csv(path, encoding='utf-8')
            except UnicodeDecodeError:
                return pd.read_csv(path, encoding='latin-1')
        elif ext == '.json':
            return pd.read_json(path)
        elif ext in ('.xlsx', '.xls'):
            return pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def preprocess_data(self) -> pd.DataFrame:
        """Preprocess all text data"""
        print(f"\n{Color.BLUE}{Color.BOLD}[Step 1] Text Preprocessing{Color.END}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Clean text
        self.df['cleaned_text'] = self.df['text'].apply(self.preprocessor.clean_text)
        
        # Remove stopwords
        self.df['processed_text'] = self.df['cleaned_text'].apply(
            lambda x: self.preprocessor.preprocess(x)
        )
        
        # Extract hashtags
        self.df['hashtags'] = self.df['text'].apply(self.preprocessor.extract_hashtags)
        
        elapsed = time.time() - start_time
        print(f"{Color.GREEN}✓ Preprocessing complete ({elapsed:.2f}s){Color.END}")
        
        return self.df
    
    def extract_keywords(self) -> Dict:
        """Extract keywords from traffic data"""
        print(f"\n{Color.BLUE}{Color.BOLD}[Step 2] Keyword Extraction{Color.END}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Calculate keyword frequency
        keyword_freq = self.keyword_extractor.calculate_keyword_frequency(
            self.df['processed_text'].tolist()
        )
        
        # Extract bigrams
        bigrams = self.keyword_extractor.extract_bigrams(
            self.df['processed_text'].tolist()
        )
        
        # Extract trigrams
        trigrams = self.keyword_extractor.extract_trigrams(
            self.df['processed_text'].tolist()
        )
        
        # Categorize keywords
        categories = defaultdict(int)
        for text in self.df['processed_text']:
            keywords = self.keyword_extractor.extract_traffic_keywords(text)
            for cat in keywords.keys():
                categories[cat] += 1
        
        self.analysis_results['keyword_freq'] = keyword_freq
        self.analysis_results['bigrams'] = bigrams
        self.analysis_results['trigrams'] = trigrams
        self.analysis_results['categories'] = dict(categories)
        
        elapsed = time.time() - start_time
        
        # Display top keywords
        print(f"\n{Color.CYAN}Top 10 Keywords:{Color.END}")
        for word, count in keyword_freq.most_common(10):
            print(f"  • {word}: {count}")
        
        print(f"\n{Color.CYAN}Top 5 Bigrams:{Color.END}")
        for bigram, count in bigrams[:5]:
            print(f"  • {' '.join(bigram)}: {count}")
        
        print(f"\n{Color.GREEN}✓ Keyword extraction complete ({elapsed:.2f}s){Color.END}")
        
        return self.analysis_results
    
    def detect_patterns(self) -> Dict:
        """Detect patterns in traffic data"""
        print(f"\n{Color.BLUE}{Color.BOLD}[Step 3] Pattern Detection{Color.END}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Detect severity for each record
        self.df['severity'] = self.df['text'].apply(self.pattern_detector.detect_severity)
        
        # Severity distribution
        severity_counts = self.df['severity'].value_counts().to_dict()
        
        # Detect time patterns
        time_patterns = []
        for text in self.df['text']:
            patterns = self.pattern_detector.detect_time_patterns(text)
            time_patterns.append(patterns)
        
        # Congestion patterns
        congestion_patterns = self.pattern_detector.detect_congestion_patterns(self.df)
        
        # Trends analysis
        trends = self.pattern_detector.analyze_trends(self.df)
        
        self.analysis_results['severity_counts'] = severity_counts
        self.analysis_results['congestion_patterns'] = congestion_patterns
        self.analysis_results['trends'] = trends
        
        elapsed = time.time() - start_time
        
        # Display pattern analysis
        print(f"\n{Color.CYAN}Severity Distribution:{Color.END}")
        for severity, count in severity_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"  • {severity}: {count} ({percentage:.1f}%)")
        
        if congestion_patterns.get('peak_hours'):
            print(f"\n{Color.CYAN}Peak Hours Identified:{Color.END}")
            print(f"  {sorted(congestion_patterns['peak_hours'])}")
        
        if trends.get('direction'):
            print(f"\n{Color.CYAN}Traffic Trend:{Color.END}")
            print(f"  Direction: {trends['direction']}")
            print(f"  Change: {trends.get('change_percentage', 0):.1f}%")
        
        print(f"\n{Color.GREEN}✓ Pattern detection complete ({elapsed:.2f}s){Color.END}")
        
        return self.analysis_results
    
    def visualize_results(self):
        """Generate visualizations"""
        print(f"\n{Color.BLUE}{Color.BOLD}[Step 4] Generating Visualizations{Color.END}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Prepare combined text for word cloud
        combined_text = ' '.join(self.df['processed_text'].tolist())
        
        # Generate all visualizations
        self.visualizer.plot_keyword_frequency(
            self.analysis_results.get('keyword_freq', Counter()),
            "Top Traffic Keywords"
        )
        
        self.visualizer.plot_wordcloud(combined_text)
        
        self.visualizer.plot_time_distribution(self.df)
        
        self.visualizer.plot_severity_distribution(
            self.analysis_results.get('severity_counts', {})
        )
        
        self.visualizer.plot_category_distribution(
            self.analysis_results.get('categories', {})
        )
        
        self.visualizer.plot_trends(
            self.analysis_results.get('trends', {})
        )
        
        # Generate HTML dashboard
        self.visualizer.generate_dashboard(self.df, self.analysis_results)
        
        elapsed = time.time() - start_time
        print(f"\n{Color.GREEN}✓ Visualizations complete ({elapsed:.2f}s){Color.END}")
    
    def generate_report(self, output_path: str = 'traffic_analysis_report.txt'):
        """Generate a comprehensive text report"""
        print(f"\n{Color.BLUE}{Color.BOLD}[Step 5] Generating Report{Color.END}")
        print("-" * 40)
        
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("INTELLIGENT TRAFFIC ANALYSIS REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Records Analyzed: {len(self.df)}")
        
        # Data Overview
        report_lines.append("\n" + "=" * 70)
        report_lines.append("DATA OVERVIEW")
        report_lines.append("=" * 70)
        
        if 'timestamp' in self.df.columns:
            start_date = pd.to_datetime(self.df['timestamp'], errors='coerce').min()
            end_date = pd.to_datetime(self.df['timestamp'], errors='coerce').max()
            report_lines.append(f"Date Range: {start_date} to {end_date}")
        
        # Keyword Analysis
        report_lines.append("\n" + "=" * 70)
        report_lines.append("KEYWORD ANALYSIS")
        report_lines.append("=" * 70)
        
        if 'keyword_freq' in self.analysis_results:
            report_lines.append("\nTop 15 Keywords:")
            for word, count in self.analysis_results['keyword_freq'].most_common(15):
                report_lines.append(f"  {word}: {count}")
        
        if 'bigrams' in self.analysis_results:
            report_lines.append("\nTop 10 Bigrams:")
            for bigram, count in self.analysis_results['bigrams'][:10]:
                report_lines.append(f"  {' '.join(bigram)}: {count}")
        
        # Severity Analysis
        report_lines.append("\n" + "=" * 70)
        report_lines.append("SEVERITY ANALYSIS")
        report_lines.append("=" * 70)
        
        if 'severity_counts' in self.analysis_results:
            for severity, count in self.analysis_results['severity_counts'].items():
                percentage = (count / len(self.df)) * 100
                report_lines.append(f"  {severity}: {count} ({percentage:.1f}%)")
        
        # Patterns and Trends
        report_lines.append("\n" + "=" * 70)
        report_lines.append("PATTERNS AND TRENDS")
        report_lines.append("=" * 70)
        
        if 'congestion_patterns' in self.analysis_results:
            cp = self.analysis_results['congestion_patterns']
            if cp.get('peak_hours'):
                report_lines.append(f"\nPeak Hours: {sorted(cp['peak_hours'])}")
        
        if 'trends' in self.analysis_results:
            trends = self.analysis_results['trends']
            if trends.get('direction'):
                report_lines.append(f"Trend Direction: {trends['direction']}")
                report_lines.append(f"Change Percentage: {trends.get('change_percentage', 0):.1f}%")
        
        # Category Analysis
        report_lines.append("\n" + "=" * 70)
        report_lines.append("CATEGORY DISTRIBUTION")
        report_lines.append("=" * 70)
        
        if 'categories' in self.analysis_results:
            for cat, count in sorted(self.analysis_results['categories'].items(), 
                                     key=lambda x: x[1], reverse=True):
                percentage = (count / len(self.df)) * 100
                report_lines.append(f"  {cat}: {count} ({percentage:.1f}%)")
        
        # Recommendations
        report_lines.append("\n" + "=" * 70)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("=" * 70)
        
        # Analyze and provide recommendations
        if 'severity_counts' in self.analysis_results:
            severity = self.analysis_results['severity_counts']
            if severity.get('high', 0) > len(self.df) * 0.3:
                report_lines.append("\n⚠ High traffic severity detected in significant portion of reports.")
                report_lines.append("  Consider implementing additional traffic management measures.")
        
        if 'congestion_patterns' in self.analysis_results:
            peak = self.analysis_results['congestion_patterns'].get('peak_hours', [])
            if peak:
                hours_str = ', '.join([str(h) for h in sorted(peak)])
                report_lines.append(f"\n⚡ Peak congestion hours: {hours_str}")
                report_lines.append("  Recommend traffic signal optimization during these hours.")
        
        report_lines.append("\n" + "=" * 70)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 70)
        
        # Write report
        report_content = '\n'.join(report_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"{Color.GREEN}✓ Report saved to: {output_path}{Color.END}")
        
        # Also print the report
        print(f"\n{Color.CYAN}{report_content}{Color.END}")
        
        return report_content
    
    def run_full_analysis(self) -> Dict:
        """Run the complete analysis pipeline"""
        print(f"\n{Color.MAGENTA}{Color.BOLD}Starting Full Analysis Pipeline...{Color.END}\n")
        
        # Step 1: Preprocess
        self.preprocess_data()
        
        # Step 2: Extract keywords
        self.extract_keywords()
        
        # Step 3: Detect patterns
        self.detect_patterns()
        
        # Step 4: Visualize
        self.visualize_results()
        
        # Step 5: Generate report
        self.generate_report()
        
        print(f"\n{Color.GREEN}{Color.BOLD}{'='*60}{Color.END}")
        print(f"{Color.GREEN}{Color.BOLD}  ANALYSIS COMPLETE!{Color.END}")
        print(f"{Color.GREEN}{Color.BOLD}{'='*60}{Color.END}")
        print(f"\n{Color.YELLOW}Visualizations saved in: ./visualizations/{Color.END}")
        print(f"{Color.YELLOW}Report saved as: traffic_analysis_report.txt{Color.END}\n")
        
        return self.analysis_results
    
    def save_processed_data(self, output_path: str = 'processed_traffic_data.csv'):
        """Save processed data to file"""
        self.df.to_csv(output_path, index=False)
        print(f"{Color.GREEN}✓ Processed data saved to: {output_path}{Color.END}")


# ============================================================================
# DEMO AND USAGE
# ============================================================================

def run_demo():
    """Run a demonstration of the traffic analyzer"""
    
    print(f"\n{Color.CYAN}{Color.BOLD}")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "TRAFFIC ANALYSIS SIMULATOR DEMO" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"{Color.END}\n")
    
    # Generate sample data
    print(f"{Color.YELLOW}Generating sample traffic data...{Color.END}")
    sample_data = TrafficDataGenerator.generate_sample_data(500)
    
    # Create analyzer
    analyzer = TrafficAnalyzer(data=sample_data)
    
    # Run full analysis
    results = analyzer.run_full_analysis()
    
    return analyzer, results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Intelligent Traffic Analysis Simulator'
    )
    parser.add_argument('--data', '-d', type=str, 
                       help='Path to traffic data file (CSV, JSON, or Excel)')
    parser.add_argument('--generate', '-g', action='store_true',
                       help='Generate sample data and run demo')
    parser.add_argument('--records', '-n', type=int, default=500,
                       help='Number of sample records to generate')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    if args.generate:
        # Run demo with sample data
        analyzer, results = run_demo()
    elif args.data:
        # Analyze provided data
        analyzer = TrafficAnalyzer(data_path=args.data)
        analyzer.run_full_analysis()
    else:
        # Default: run demo
        analyzer, results = run_demo()


if __name__ == "__main__":
    main()

