import os
import io
import time
import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def log_test(category, name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] [{category}] {name} :: {details}")
    return passed

def run_tests():
    print("=" * 70)
    print("  QA TEST EXECUTION REPORT - TRAFFIC ANALYSIS NLP PLATFORM")
    print("  Tester Experience: 5+ Years QA & Automation Lead")
    print("=" * 70)

    total = 0
    passed = 0

    # Test Suite 1: Navigation & Smoke Tests
    for endpoint in ["/", "/about", "/upload", "/generate"]:
        r = session.get(f"{BASE_URL}{endpoint}")
        total += 1
        if log_test("Smoke", f"GET {endpoint}", r.status_code == 200, f"HTTP {r.status_code}"):
            passed += 1

    # Test Suite 2: Boundary Value Analysis (Data Generation)
    gen_cases = [
        ("0 records", {"num_records": "0"}),
        ("Negative records (-5)", {"num_records": "-5"}),
        ("Non-numeric ('abc')", {"num_records": "abc"}),
        ("Special characters ('!@#$')", {"num_records": "!@#$"}),
        ("Stress load (1000 records)", {"num_records": "1000"}),
    ]
    for label, payload in gen_cases:
        r = session.post(f"{BASE_URL}/generate", data=payload)
        total += 1
        # Should gracefully redirect to /results or /generate with flash message, no 500
        ok = r.status_code in [200, 302]
        if log_test("Boundary/Stress", f"Generate: {label}", ok, f"HTTP {r.status_code}, Final URL: {r.url}"):
            passed += 1

    # Test Suite 3: Security & Input Validation (File Upload)
    bad_files = [
        ("Disallowed extension (.py)", "script.py", b"print('hack')", "text/x-python"),
        ("Disallowed extension (.exe)", "malware.exe", b"MZ", "application/octet-stream"),
        ("Disallowed extension (.sh)", "run.sh", b"#!/bin/bash", "text/x-sh"),
        ("Empty file (0 bytes)", "empty.csv", b"", "text/csv"),
    ]
    for label, fname, content, mtype in bad_files:
        r = session.post(f"{BASE_URL}/upload", files={"file": (fname, content, mtype)})
        total += 1
        # System should reject and not crash
        ok = r.status_code in [200, 302] and "results" not in r.url
        if log_test("Security/Validation", f"Upload: {label}", ok, f"HTTP {r.status_code}, Redirected: {r.url}"):
            passed += 1

    # Test Suite 4: Multi-format Compatibility & NLP Engine
    formats = [
        ("CSV (Standard)", "uploads/traffic_data_2025.csv"),
        ("XLSX (Excel)", "uploads/traffic_data_2025.xlsx"),
        ("Real-world Custom Schema", "uploads/Indian_Traffic_Violations.csv"),
        ("Aggregated Regional Data", "uploads/ADSI_Table_1A.2.csv"),
    ]
    for label, filepath in formats:
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                r = session.post(f"{BASE_URL}/upload", files={"file": f})
                total += 1
                ok = r.status_code == 200 and "/results" in r.url
                if log_test("Compatibility", f"Process {label}", ok, f"HTTP {r.status_code}, Final: {r.url}"):
                    passed += 1

    # Test Suite 5: Web Security - Directory Traversal & XSS
    traversal_paths = [
        "/visualizations/..%2f..%2fapp.py",
        "/visualizations/....//....//app.py",
        "/visualizations/app.py",
    ]
    for path in traversal_paths:
        r = session.get(f"{BASE_URL}{path}")
        total += 1
        # Must return 400, 404, or fail, never disclose app.py
        ok = r.status_code in [400, 404] and "app = Flask" not in r.text
        if log_test("Security", f"Path Traversal: {path}", ok, f"HTTP {r.status_code}"):
            passed += 1

    # Test Suite 6: Data Integrity & Downloads
    r_rep = session.get(f"{BASE_URL}/download/report")
    total += 1
    rep_ok = r_rep.status_code == 200 and "TRAFFIC ANALYSIS REPORT" in r_rep.text
    if log_test("Integrity", "Download Report Content", rep_ok, f"Size: {len(r_rep.content)} bytes"):
        passed += 1

    r_csv = session.get(f"{BASE_URL}/download/data")
    total += 1
    csv_ok = r_csv.status_code == 200 and "text" in r_csv.text
    if log_test("Integrity", "Download Processed Data CSV", csv_ok, f"Size: {len(r_csv.content)} bytes"):
        passed += 1

    # Test Suite 7: Visualization Generation & Display
    viz_files = [
        "keyword_frequency.png",
        "wordcloud.png",
        "time_distribution.png",
        "severity_distribution.png",
        "category_distribution.png",
        "trends.png",
        "dashboard.html",
    ]
    for vf in viz_files:
        p = os.path.join("visualizations", vf)
        total += 1
        exists_and_valid = os.path.exists(p) and os.path.getsize(p) > 500
        if log_test("Visualization", f"Artifact generated: {vf}", exists_and_valid, f"Size: {os.path.getsize(p) if os.path.exists(p) else 0} bytes"):
            passed += 1

    r_dash = session.get(f"{BASE_URL}/dashboard")
    total += 1
    dash_ok = r_dash.status_code == 200 and "Interactive Dashboard" in r_dash.text
    if log_test("UI/UX", "GET /dashboard renders complete UI", dash_ok, f"HTTP {r_dash.status_code}"):
        passed += 1

    print("=" * 70)
    print(f"  TEST SUMMARY: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
