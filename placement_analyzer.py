"""
╔══════════════════════════════════════════════════════════════════╗
║   CAREERLENS AI — ENHANCED CAREER CO-PILOT SYSTEM               ║
║   Run: pip install streamlit plotly pandas numpy PyPDF2          ║
║        reportlab                                                  ║
║        streamlit run placement_analyzer.py                       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import re
import io
import time
import random
from datetime import datetime, timedelta, date

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerLens AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

THEMES = {
    "dark": {
        "--bg":       "#0a0e1a",
        "--surface":  "#111827",
        "--border":   "#1e2d45",
        "--accent1":  "#00f5d4",
        "--accent2":  "#f72585",
        "--accent3":  "#7209b7",
        "--text":     "#e2e8f0",
        "--muted":    "#64748b",
        "--success":  "#10b981",
        "--warn":     "#f59e0b",
        "--danger":   "#ef4444",
        "--card-bg":  "#111827",
        "--prog-bg":  "#1e2d45",
    },
    "light": {
        "--bg":       "#f0f4f8",
        "--surface":  "#ffffff",
        "--border":   "#cbd5e1",
        "--accent1":  "#0891b2",
        "--accent2":  "#e11d48",
        "--accent3":  "#7c3aed",
        "--text":     "#0f172a",
        "--muted":    "#64748b",
        "--success":  "#059669",
        "--warn":     "#d97706",
        "--danger":   "#dc2626",
        "--card-bg":  "#ffffff",
        "--prog-bg":  "#e2e8f0",
    },
}

def get_css_vars():
    t = THEMES[st.session_state.theme]
    return "\n".join(f"    {k}: {v};" for k, v in t.items())

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {{
{get_css_vars()}
}}

html, body, [class*="css"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}}

.stApp {{ background: var(--bg); }}

section[data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}}

h1, h2, h3, h4 {{ font-family: 'Syne', sans-serif !important; font-weight: 800; }}

.card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color .2s;
}}
.card:hover {{ border-color: var(--accent1); }}

.metric-tile {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}}
.metric-val {{
    font-size: 2.4rem;
    font-weight: 800;
    font-family: 'Space Mono', monospace;
    background: linear-gradient(90deg, var(--accent1), #4cc9f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.metric-label {{ font-size: .78rem; color: var(--muted); text-transform: uppercase; letter-spacing: .12em; margin-top: .2rem; }}

.pill {{
    display: inline-block;
    padding: .25rem .7rem;
    border-radius: 999px;
    font-size: .75rem;
    font-weight: 700;
    margin: .2rem;
}}
.pill-green  {{ background: #052e16; color: #34d399; border: 1px solid #065f46; }}
.pill-red    {{ background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }}
.pill-yellow {{ background: #2d1f00; color: #fbbf24; border: 1px solid #78350f; }}
.pill-blue   {{ background: #0a1628; color: #60a5fa; border: 1px solid #1e3a5f; }}
.pill-purple {{ background: #1a0a2e; color: #c084fc; border: 1px solid #4c1d95; }}

.prog-wrap {{ background: var(--prog-bg); border-radius: 999px; height: 10px; overflow: hidden; margin: .5rem 0; }}
.prog-fill  {{ height: 100%; border-radius: 999px; transition: width .6s ease; }}

.step {{
    display: flex;
    gap: 1rem;
    margin-bottom: 1.2rem;
    align-items: flex-start;
}}
.step-num {{
    min-width: 32px; height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent1), var(--accent3));
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: .85rem; color: #000;
    font-family: 'Space Mono', monospace;
}}
.step-body {{ flex: 1; }}
.step-title {{ font-weight: 700; font-size: .95rem; }}
.step-sub   {{ color: var(--muted); font-size: .8rem; }}

.role-badge {{
    padding: .4rem 1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: .85rem;
    border: 1px solid;
    display: inline-block;
    margin: .2rem;
    font-family: 'Space Mono', monospace;
}}

.bubble-ai   {{ background: #0f2040; border-left: 3px solid var(--accent1); padding: .75rem 1rem; border-radius: 0 10px 10px 0; margin: .5rem 0; }}
.bubble-user {{ background: #1a0a2e; border-left: 3px solid var(--accent2); padding: .75rem 1rem; border-radius: 0 10px 10px 0; margin: .5rem 0; }}

div[data-baseweb="tab-list"] {{
    background: var(--surface) !important;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}}
div[data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}}

button[kind="primary"] {{
    background: linear-gradient(135deg, var(--accent1), #4cc9f0) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
}}

.stSlider > div {{ color: var(--text) !important; }}

.xp-bar-wrap {{ background: var(--prog-bg); border-radius: 999px; height: 14px; overflow: hidden; margin: .4rem 0; position: relative; }}
.xp-bar-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, #7209b7, #00f5d4); transition: width .8s ease; }}

.badge {{
    display: inline-flex; align-items: center; gap: .4rem;
    padding: .4rem .9rem;
    border-radius: 10px;
    font-size: .8rem; font-weight: 700;
    border: 1px solid;
    margin: .25rem;
}}
.badge-gold   {{ background: #2d1f00; color: #fbbf24; border-color: #92400e; }}
.badge-silver {{ background: #1a1f2e; color: #94a3b8; border-color: #475569; }}
.badge-locked {{ background: #111827; color: #475569; border-color: #1e2d45; }}

.company-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .9rem 1.1rem;
    margin-bottom: .6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.eligibility-safe     {{ color: #10b981; background: #052e16; padding: .2rem .7rem; border-radius: 6px; font-size: .8rem; font-weight: 700; }}
.eligibility-moderate {{ color: #f59e0b; background: #2d1f00; padding: .2rem .7rem; border-radius: 6px; font-size: .8rem; font-weight: 700; }}
.eligibility-dream    {{ color: #f87171; background: #2d0a0a; padding: .2rem .7rem; border-radius: 6px; font-size: .8rem; font-weight: 700; }}

.notif {{
    padding: .75rem 1rem;
    border-radius: 10px;
    margin-bottom: .5rem;
    border-left: 4px solid;
    font-size: .88rem;
}}
.notif-info  {{ background: #0a1628; border-color: #60a5fa; }}
.notif-warn  {{ background: #2d1f00; border-color: #f59e0b; }}
.notif-success{{ background: #052e16; border-color: #10b981; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────────────────────

ROLE_REQUIREMENTS = {
    "Software Developer": {
        "core":    ["DSA", "OOP", "OS", "DBMS", "Computer Networks", "Git"],
        "tech":    ["Python", "Java", "C++", "SQL", "REST APIs", "Linux"],
        "plus":    ["System Design", "Docker", "Cloud (AWS/GCP)", "CI/CD"],
        "weights": {"cgpa": 0.20, "projects": 0.20, "skills": 0.30, "internship": 0.15, "coding_rating": 0.15},
        "color":   "#00f5d4",
        "min_cgpa": 6.5,
    },
    "Data Analyst": {
        "core":    ["SQL", "Statistics", "Excel", "Data Visualization", "Python"],
        "tech":    ["Pandas", "Tableau/PowerBI", "NumPy", "Matplotlib", "R"],
        "plus":    ["Machine Learning basics", "BigQuery", "Spark", "Storytelling"],
        "weights": {"cgpa": 0.25, "projects": 0.20, "skills": 0.35, "internship": 0.10, "coding_rating": 0.10},
        "color":   "#f72585",
        "min_cgpa": 6.0,
    },
    "AI/ML Engineer": {
        "core":    ["Python", "Mathematics", "Statistics", "ML Algorithms", "Deep Learning"],
        "tech":    ["TensorFlow/PyTorch", "Scikit-learn", "Pandas", "NumPy", "SQL"],
        "plus":    ["NLP", "Computer Vision", "MLOps", "Hugging Face", "LLMs"],
        "weights": {"cgpa": 0.20, "projects": 0.25, "skills": 0.30, "internship": 0.10, "coding_rating": 0.15},
        "color":   "#7209b7",
        "min_cgpa": 7.0,
    },
    "Web Developer": {
        "core":    ["HTML", "CSS", "JavaScript", "React/Vue", "REST APIs", "Git"],
        "tech":    ["Node.js", "SQL/NoSQL", "TypeScript", "Responsive Design"],
        "plus":    ["Next.js", "Docker", "Testing", "Performance Optimization"],
        "weights": {"cgpa": 0.15, "projects": 0.30, "skills": 0.35, "internship": 0.12, "coding_rating": 0.08},
        "color":   "#f59e0b",
        "min_cgpa": 5.5,
    },
    "DevOps Engineer": {
        "core":    ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "Bash Scripting"],
        "tech":    ["AWS/GCP/Azure", "Terraform", "Jenkins", "Ansible", "Monitoring"],
        "plus":    ["Security", "Networking", "Python automation", "Helm"],
        "weights": {"cgpa": 0.15, "projects": 0.20, "skills": 0.35, "internship": 0.20, "coding_rating": 0.10},
        "color":   "#10b981",
        "min_cgpa": 6.0,
    },
}

ALL_SKILLS = sorted(set(
    s for r in ROLE_REQUIREMENTS.values()
    for cat in ["core", "tech", "plus"] for s in r[cat]
))

ROADMAP_DB = {
    "DSA":               {"time": "45 days",  "resources": ["LeetCode (Easy→Hard)", "Striver's SDE Sheet", "GeeksforGeeks"], "priority": "🔴 Critical"},
    "Python":            {"time": "14 days",  "resources": ["Python.org docs", "Real Python", "Automate the Boring Stuff"], "priority": "🔴 Critical"},
    "SQL":               {"time": "10 days",  "resources": ["SQLZoo", "Mode Analytics", "LeetCode SQL"], "priority": "🔴 Critical"},
    "Machine Learning basics": {"time": "30 days", "resources": ["Coursera ML (Andrew Ng)", "fast.ai", "Kaggle Learn"], "priority": "🟡 Important"},
    "Deep Learning":     {"time": "30 days",  "resources": ["fast.ai", "d2l.ai", "PyTorch tutorials"], "priority": "🟡 Important"},
    "System Design":     {"time": "21 days",  "resources": ["Grokking System Design", "System Design Primer (GitHub)"], "priority": "🟡 Important"},
    "Docker":            {"time": "7 days",   "resources": ["Docker official docs", "TechWorld with Nana (YouTube)"], "priority": "🟢 Good-to-have"},
    "Git":               {"time": "3 days",   "resources": ["Pro Git book (free)", "GitHub Learning Lab"], "priority": "🔴 Critical"},
    "React/Vue":         {"time": "21 days",  "resources": ["React docs", "Scrimba", "The Odin Project"], "priority": "🟡 Important"},
    "Statistics":        {"time": "14 days",  "resources": ["Khan Academy Statistics", "StatQuest (YouTube)"], "priority": "🟡 Important"},
    "Tableau/PowerBI":   {"time": "10 days",  "resources": ["Tableau Public tutorials", "Microsoft Learn"], "priority": "🟢 Good-to-have"},
    "Linux":             {"time": "7 days",   "resources": ["Linux Journey", "The Linux Command Line (book)"], "priority": "🟡 Important"},
    "Kubernetes":        {"time": "14 days",  "resources": ["Kubernetes.io docs", "KodeKloud"], "priority": "🟡 Important"},
    "DBMS":              {"time": "10 days",  "resources": ["NPTEL DBMS", "CMU 15-445"], "priority": "🔴 Critical"},
    "Computer Networks": {"time": "10 days",  "resources": ["Tanenbaum Book", "NPTEL Networking"], "priority": "🟡 Important"},
    "OS":                {"time": "14 days",  "resources": ["Operating Systems: 3 Easy Pieces", "NPTEL OS"], "priority": "🔴 Critical"},
    "NLP":               {"time": "21 days",  "resources": ["Hugging Face NLP course", "Stanford CS224N"], "priority": "🟢 Good-to-have"},
    "TensorFlow/PyTorch":{"time": "14 days",  "resources": ["TensorFlow tutorials", "PyTorch docs"], "priority": "🟡 Important"},
    "AWS/GCP/Azure":     {"time": "14 days",  "resources": ["AWS Free tier + docs", "Google Qwiklabs"], "priority": "🟡 Important"},
}

DEFAULT_ROADMAP = {"time": "7 days", "resources": ["YouTube tutorials", "Official documentation"], "priority": "🟢 Good-to-have"}

CHAT_KNOWLEDGE = {
    "what should i learn next": "Based on your skill gap, focus on the 🔴 Critical items in your roadmap first. Start with the skill that appears in the most roles you're targeting.",
    "how to improve cgpa": "While current CGPA can't be changed retrospectively, focus on strong projects and certifications. A 7+ CGPA significantly boosts probability for AI/ML roles.",
    "how many projects": "Aim for 2–3 strong, deployed projects with GitHub links. Quality beats quantity. Each project should solve a real problem.",
    "internship tips": "Apply on LinkedIn, Internshala, and AngelList. Even a 1-month internship adds 10–15% to your placement probability.",
    "coding platform": "LeetCode (DSA), HackerRank (certificates), Codeforces (competitive). Aim for LeetCode rating > 1600 for top companies.",
    "resume tips": "Keep it to 1 page. Lead with projects. Quantify achievements. Use action verbs. ATS-friendly format (no tables/images in header).",
    "what is skill gap": "Skill gap = difference between skills you have vs. skills the industry requires for your target role. The gap section shows exactly what's missing.",
    "time to placement": "Your estimated time-to-placement is shown in the dashboard. It's based on learning speed of ~1 skill per 2 weeks on average.",
    "certification": "Google certifications (Data Analytics, IT Support), AWS Cloud Practitioner, Microsoft Azure Fundamentals, and Meta certifications add real value.",
}

COMPANY_DB = {
    "Service-Based": [
        {"name": "TCS",        "min_cgpa": 6.0, "min_prob": 30, "skills_needed": ["DSA", "SQL", "Python"], "package": "3.5–7 LPA"},
        {"name": "Infosys",    "min_cgpa": 6.0, "min_prob": 30, "skills_needed": ["DSA", "OOP", "SQL"],    "package": "3.6–6.5 LPA"},
        {"name": "Wipro",      "min_cgpa": 6.0, "min_prob": 28, "skills_needed": ["Python", "SQL", "Git"], "package": "3.5–6 LPA"},
        {"name": "Accenture",  "min_cgpa": 6.0, "min_prob": 35, "skills_needed": ["OOP", "SQL", "Linux"], "package": "4.5–8 LPA"},
        {"name": "Cognizant",  "min_cgpa": 6.0, "min_prob": 30, "skills_needed": ["DSA", "SQL", "Python"], "package": "4–7 LPA"},
        {"name": "HCL",        "min_cgpa": 5.5, "min_prob": 25, "skills_needed": ["Python", "SQL", "Git"], "package": "3–5.5 LPA"},
        {"name": "Tech Mahindra","min_cgpa": 6.0,"min_prob": 28, "skills_needed": ["OOP", "SQL", "Linux"],"package": "3.5–6 LPA"},
        {"name": "Capgemini",  "min_cgpa": 6.0, "min_prob": 32, "skills_needed": ["DSA", "OOP", "SQL"],   "package": "4–7.5 LPA"},
    ],
    "Product-Based (Mid)": [
        {"name": "Zoho",       "min_cgpa": 7.0, "min_prob": 55, "skills_needed": ["DSA", "OOP", "Python"], "package": "6–14 LPA"},
        {"name": "Freshworks", "min_cgpa": 7.0, "min_prob": 55, "skills_needed": ["DSA", "System Design", "OOP"], "package": "8–18 LPA"},
        {"name": "Paytm",      "min_cgpa": 6.5, "min_prob": 50, "skills_needed": ["DSA", "Python", "SQL"],  "package": "6–15 LPA"},
        {"name": "Flipkart",   "min_cgpa": 7.5, "min_prob": 65, "skills_needed": ["DSA", "System Design", "OS"], "package": "20–30 LPA"},
        {"name": "Swiggy",     "min_cgpa": 7.0, "min_prob": 60, "skills_needed": ["DSA", "Python", "System Design"], "package": "15–25 LPA"},
        {"name": "Zomato",     "min_cgpa": 7.0, "min_prob": 58, "skills_needed": ["DSA", "OOP", "SQL"],    "package": "12–22 LPA"},
        {"name": "CRED",       "min_cgpa": 7.5, "min_prob": 65, "skills_needed": ["DSA", "System Design", "Python"],"package": "18–28 LPA"},
        {"name": "Razorpay",   "min_cgpa": 7.5, "min_prob": 68, "skills_needed": ["DSA", "System Design", "REST APIs"],"package": "20–35 LPA"},
    ],
    "FAANG / Dream": [
        {"name": "Google",     "min_cgpa": 8.0, "min_prob": 80, "skills_needed": ["DSA", "System Design", "OS", "Computer Networks"], "package": "40–80 LPA"},
        {"name": "Microsoft",  "min_cgpa": 8.0, "min_prob": 78, "skills_needed": ["DSA", "System Design", "OOP", "OS"], "package": "35–65 LPA"},
        {"name": "Amazon",     "min_cgpa": 7.5, "min_prob": 72, "skills_needed": ["DSA", "System Design", "OOP", "Cloud (AWS/GCP)"], "package": "30–55 LPA"},
        {"name": "Meta",       "min_cgpa": 8.0, "min_prob": 80, "skills_needed": ["DSA", "System Design", "OS", "Computer Networks"], "package": "45–90 LPA"},
        {"name": "Apple",      "min_cgpa": 8.5, "min_prob": 82, "skills_needed": ["DSA", "System Design", "OOP", "OS"], "package": "50–100 LPA"},
        {"name": "Netflix",    "min_cgpa": 8.0, "min_prob": 80, "skills_needed": ["DSA", "System Design", "Cloud (AWS/GCP)"], "package": "60–120 LPA"},
        {"name": "Adobe",      "min_cgpa": 7.5, "min_prob": 70, "skills_needed": ["DSA", "OOP", "System Design"], "package": "25–45 LPA"},
        {"name": "Atlassian",  "min_cgpa": 7.5, "min_prob": 70, "skills_needed": ["DSA", "System Design", "Git"], "package": "30–55 LPA"},
    ],
}

SKILL_DEPENDENCIES = {
    "System Design":     ["DSA", "OS", "Computer Networks", "DBMS"],
    "Deep Learning":     ["Python", "Statistics", "Machine Learning basics"],
    "Machine Learning basics": ["Python", "Statistics", "SQL"],
    "NLP":               ["Python", "Deep Learning", "Statistics"],
    "TensorFlow/PyTorch":["Python", "Machine Learning basics", "Deep Learning"],
    "Kubernetes":        ["Docker", "Linux"],
    "Tableau/PowerBI":   ["SQL", "Statistics"],
    "CI/CD":             ["Git", "Docker", "Linux"],
    "React/Vue":         ["HTML", "CSS", "JavaScript"],
    "Node.js":           ["JavaScript"],
    "TypeScript":        ["JavaScript"],
    "Next.js":           ["React/Vue", "Node.js"],
    "Terraform":         ["Linux", "AWS/GCP/Azure"],
    "Ansible":           ["Linux", "Bash Scripting"],
    "Spark":             ["SQL", "Python"],
    "BigQuery":          ["SQL"],
    "MLOps":             ["Machine Learning basics", "Docker", "CI/CD"],
}

SALARY_MAP = {
    "Software Developer": {"base": 6, "mid": 15, "top": 40},
    "Data Analyst":       {"base": 5, "mid": 12, "top": 25},
    "AI/ML Engineer":     {"base": 8, "mid": 20, "top": 50},
    "Web Developer":      {"base": 4, "mid": 10, "top": 20},
    "DevOps Engineer":    {"base": 7, "mid": 18, "top": 35},
}

INTERVIEW_QUESTIONS = {
    "Software Developer": {
        "Technical": [
            "Explain the difference between a stack and a queue.",
            "What is Big-O notation? Give examples.",
            "Explain OOP principles with examples.",
            "What is a deadlock? How do you prevent it?",
            "Explain the difference between TCP and UDP.",
            "What is normalization in databases?",
            "How does garbage collection work in Java/Python?",
            "What is the difference between process and thread?",
            "Explain REST vs GraphQL.",
            "What is the CAP theorem?",
        ],
        "Behavioral": [
            "Tell me about a challenging project you built.",
            "How do you handle code reviews?",
            "Describe a time you debugged a complex bug.",
            "How do you prioritize tasks under tight deadlines?",
            "Tell me about a time you learned a new technology quickly.",
        ],
        "Coding": [
            "Reverse a linked list.",
            "Find the longest common subsequence.",
            "Implement a binary search.",
            "Check if a binary tree is balanced.",
            "Find all permutations of a string.",
        ],
    },
    "Data Analyst": {
        "Technical": [
            "What is the difference between INNER JOIN and OUTER JOIN?",
            "Explain window functions in SQL.",
            "What is the difference between correlation and causation?",
            "How do you handle missing data?",
            "What is p-value and statistical significance?",
            "Explain the difference between mean, median, and mode.",
            "What is a pivot table? When would you use it?",
            "How do you detect outliers?",
            "Explain normalization vs standardization.",
            "What is A/B testing?",
        ],
        "Behavioral": [
            "Describe a data analysis project you're proud of.",
            "How do you communicate insights to non-technical stakeholders?",
            "Tell me about a time your analysis influenced a business decision.",
            "How do you validate your data before analysis?",
            "Describe your data cleaning workflow.",
        ],
        "Coding": [
            "Write a SQL query to find the top 5 customers by revenue.",
            "Find duplicate rows in a dataset using Pandas.",
            "Calculate a rolling 7-day average in Python.",
            "Write a SQL query to find month-over-month growth.",
            "Group and aggregate a DataFrame by multiple columns.",
        ],
    },
    "AI/ML Engineer": {
        "Technical": [
            "Explain bias-variance tradeoff.",
            "What is gradient descent? Explain types.",
            "How does a neural network learn?",
            "What is overfitting? How do you prevent it?",
            "Explain precision, recall, and F1 score.",
            "What is the difference between supervised and unsupervised learning?",
            "How does backpropagation work?",
            "What is regularization? L1 vs L2?",
            "Explain the attention mechanism.",
            "What is transfer learning?",
        ],
        "Behavioral": [
            "Describe an ML project you built end-to-end.",
            "How do you choose the right model for a problem?",
            "Tell me about a time you improved model performance.",
            "How do you handle imbalanced datasets?",
            "Describe your experience with model deployment.",
        ],
        "Coding": [
            "Implement linear regression from scratch.",
            "Write a k-means clustering algorithm.",
            "Calculate cosine similarity between two vectors.",
            "Implement dropout regularization.",
            "Train a simple neural network using PyTorch.",
        ],
    },
    "Web Developer": {
        "Technical": [
            "Explain the difference between let, const, and var.",
            "What is event bubbling in JavaScript?",
            "How does the Virtual DOM work?",
            "Explain CSS specificity.",
            "What are React hooks? Name 5 commonly used ones.",
            "What is CORS and how do you handle it?",
            "Explain async/await vs Promises.",
            "What is the box model in CSS?",
            "How do you optimize a React application?",
            "What is SSR vs CSR?",
        ],
        "Behavioral": [
            "Describe a web app you built from scratch.",
            "How do you ensure your apps are accessible?",
            "Tell me about a performance optimization you implemented.",
            "How do you handle cross-browser compatibility issues?",
            "Describe your approach to responsive design.",
        ],
        "Coding": [
            "Build a debounce function in JavaScript.",
            "Create a custom React hook for API fetching.",
            "Implement infinite scrolling in React.",
            "Build a simple todo app with local storage.",
            "Write a CSS grid layout for a dashboard.",
        ],
    },
    "DevOps Engineer": {
        "Technical": [
            "Explain the difference between Docker and a VM.",
            "What is Kubernetes and why use it?",
            "Explain blue-green deployment.",
            "What is Infrastructure as Code?",
            "How does CI/CD improve software delivery?",
            "What is a load balancer? Types?",
            "Explain the 12-factor app methodology.",
            "What is a service mesh?",
            "How do you monitor a production system?",
            "What is GitOps?",
        ],
        "Behavioral": [
            "Describe an incident you handled in production.",
            "How do you ensure zero-downtime deployments?",
            "Tell me about a CI/CD pipeline you built.",
            "How do you handle secret management?",
            "Describe your approach to infrastructure security.",
        ],
        "Coding": [
            "Write a Dockerfile for a Python Flask app.",
            "Create a Kubernetes deployment YAML.",
            "Write a bash script to automate backups.",
            "Build a Terraform config for an EC2 instance.",
            "Write a GitHub Actions workflow for CI.",
        ],
    },
}

BADGES = {
    "🏆 Project Builder":    {"desc": "Built 3+ projects",    "condition": lambda p: p.get("projects", 0) >= 3},
    "🎯 DSA Master":         {"desc": "Knows DSA skill",       "condition": lambda p: "DSA" in p.get("skills", [])},
    "🌐 Cloud Certified":    {"desc": "Has cloud skills",      "condition": lambda p: any("Cloud" in s or "AWS" in s for s in p.get("skills", []))},
    "💼 Intern Veteran":     {"desc": "2+ internships",        "condition": lambda p: p.get("internships", 0) >= 2},
    "📜 Cert Collector":     {"desc": "3+ certifications",     "condition": lambda p: p.get("certs", 0) >= 3},
    "🐍 Pythonista":         {"desc": "Knows Python",          "condition": lambda p: "Python" in p.get("skills", [])},
    "⚡ High Achiever":      {"desc": "CGPA 8+",               "condition": lambda p: p.get("cgpa", 0) >= 8.0},
    "💻 LeetCode Warrior":   {"desc": "Rating 1500+",          "condition": lambda p: p.get("coding_rating", 0) >= 1500},
    "🗄️ Data Wizard":        {"desc": "Knows SQL + Pandas",    "condition": lambda p: "SQL" in p.get("skills", []) and "Pandas" in p.get("skills", [])},
    "🔥 Full Stack":         {"desc": "Front + Back skills",   "condition": lambda p: any(s in p.get("skills", []) for s in ["React/Vue", "HTML"]) and any(s in p.get("skills", []) for s in ["Node.js", "Python", "Java"])},
    "🌟 Placement Ready":    {"desc": "Probability 75%+",      "condition": lambda p: p.get("probability", 0) >= 75},
    "🚀 Elite Candidate":    {"desc": "Probability 90%+",      "condition": lambda p: p.get("probability", 0) >= 90},
}


# ─────────────────────────────────────────────────────────────────────────────
# ✅ FIX 1: ROBUST SALARY PARSING UTILITY
# Replaces the broken: float(p[2].split("–")[0].replace(" LPA","").replace("+",""))
# which crashed on "6-10 LPA" because em-dash split returns "6-10" which isn't a float.
# ─────────────────────────────────────────────────────────────────────────────

def parse_salary_low(salary_str: str) -> float:
    """
    Robustly extract the lower salary bound from strings like:
      '6-10 LPA', '20–35 LPA', '80+ LPA', '100+ LPA'
    Strategy: regex-extract the first integer/decimal in the string.
    Works with hyphens, en-dashes, em-dashes, and '+' notation.
    """
    cleaned = salary_str.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(match.group(1)) if match else 0.0


def parse_salary_range(salary_str: str):
    """
    Parse full salary range → (low, high) floats.
    Handles: '6-10 LPA', '20–35 LPA', '80+ LPA'
    """
    cleaned = salary_str.replace(" LPA", "").replace("LPA", "").replace("+", "").strip()
    # Try split on em-dash, en-dash, or hyphen
    for sep in ["–", "—", "-"]:
        if sep in cleaned:
            parts = cleaned.split(sep)
            try:
                return float(parts[0].strip()), float(parts[1].strip())
            except (ValueError, IndexError):
                pass
    # Single number (e.g. "80+")
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    if match:
        val = float(match.group(1))
        return val, val * 1.3  # estimate a high end
    return 0.0, 0.0


# ─────────────────────────────────────────────────────────────────────────────
# ✅ FIX 2: SAFE HTML RENDERING HELPERS
# All HTML output goes through these — never use st.write() for HTML content.
# ─────────────────────────────────────────────────────────────────────────────

def render_html(html_str: str) -> None:
    """Single entry point for all custom HTML rendering. Always sets unsafe_allow_html=True."""
    st.markdown(html_str, unsafe_allow_html=True)


def pill(text: str, kind: str = "green") -> str:
    """Return an HTML pill span. Caller must pass output to render_html()."""
    return f'<span class="pill pill-{kind}">{text}</span>'


def progress_bar(pct: float, color: str = "#00f5d4") -> str:
    """Return HTML progress bar string."""
    pct = max(0.0, min(float(pct), 100.0))
    return (
        f'<div class="prog-wrap">'
        f'<div class="prog-fill" style="width:{pct:.1f}%;background:{color};"></div>'
        f'</div>'
    )


def render_pills(items: list, kind: str = "green") -> None:
    """Render a list of pill badges as HTML."""
    if not items:
        render_html('<span style="color:#64748b">None</span>')
        return
    render_html(" ".join(pill(s, kind) for s in items))


def render_card(body_html: str, border_color: str = "var(--border)") -> None:
    """Render a styled card div."""
    render_html(
        f'<div class="card" style="border-color:{border_color}">{body_html}</div>'
    )


def render_notif(message: str, kind: str = "info") -> None:
    """Render a notification banner. kind: info | warn | success"""
    render_html(f'<div class="notif notif-{kind}">{message}</div>')


def render_metric_tile(value: str, label: str, gradient: str = "linear-gradient(90deg,#00f5d4,#4cc9f0)") -> None:
    """Render a metric tile."""
    render_html(f"""
    <div class="metric-tile">
        <div class="metric-val" style="background:{gradient};-webkit-background-clip:text">{value}</div>
        <div class="metric-label">{label}</div>
    </div>""")


# ─────────────────────────────────────────────────────────────────────────────
# CORE LOGIC
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def compute_skill_match_cached(user_skills_tuple, role):
    return compute_skill_match(list(user_skills_tuple), role)


def compute_skill_match(user_skills: list, role: str) -> dict:
    req = ROLE_REQUIREMENTS[role]
    all_req = req["core"] + req["tech"] + req["plus"]
    user_lower = [s.lower() for s in user_skills]
    matched = [s for s in all_req if s.lower() in user_lower]
    missing = [s for s in req["core"] + req["tech"] if s.lower() not in user_lower]
    weak    = [s for s in req["plus"] if s.lower() not in user_lower]
    skill_score = (
        sum(3 for s in req["core"] if s.lower() in user_lower) +
        sum(2 for s in req["tech"] if s.lower() in user_lower) +
        sum(1 for s in req["plus"] if s.lower() in user_lower)
    )
    max_score = 3 * len(req["core"]) + 2 * len(req["tech"]) + 1 * len(req["plus"])
    return {
        "matched": matched,
        "missing": missing,
        "weak":    weak,
        "skill_pct": skill_score / max_score if max_score else 0,
    }


def predict_placement(cgpa, projects, internships, certs, coding_rating, skills, role):
    req  = ROLE_REQUIREMENTS[role]
    w    = req["weights"]
    sm   = compute_skill_match(skills, role)
    cgpa_norm   = min(cgpa / 10, 1.0)
    proj_norm   = min(projects / 5, 1.0)
    intern_norm = min(internships / 3, 1.0)
    cert_norm   = min(certs / 5, 1.0)
    code_norm   = min(coding_rating / 2500, 1.0)
    skill_norm  = sm["skill_pct"]
    raw = (
        w["cgpa"]          * cgpa_norm   +
        w["projects"]      * (proj_norm * 0.6 + cert_norm * 0.4) +
        w["skills"]        * skill_norm  +
        w["internship"]    * intern_norm +
        w["coding_rating"] * code_norm
    )
    if cgpa < req["min_cgpa"]:
        raw *= 0.85
    prob = round(min(max(raw * 100, 5), 97), 1)
    academic_score = round((cgpa_norm * 0.5 + intern_norm * 0.3 + cert_norm * 0.2) * 100)
    skill_score    = round(skill_norm * 100)
    activity_score = round((proj_norm * 0.5 + code_norm * 0.3 + cert_norm * 0.2) * 100)
    readiness      = round((academic_score * 0.35 + skill_score * 0.45 + activity_score * 0.20))
    return {
        "probability":     prob,
        "academic_score":  academic_score,
        "skill_score":     skill_score,
        "activity_score":  activity_score,
        "readiness":       readiness,
        "skill_match":     sm,
    }


def estimate_time_to_ready(missing_skills, current_prob):
    if current_prob >= 80:
        return 0.5
    days = sum(
        int(ROADMAP_DB.get(s, DEFAULT_ROADMAP)["time"].split()[0])
        for s in missing_skills
    )
    return round(days / 30, 1)


def whatif_simulation(base_prob, new_skills, skills, cgpa, projects, internships, certs, coding_rating, role):
    combined = list(set(skills + new_skills))
    result   = predict_placement(cgpa, projects, internships, certs, coding_rating, combined, role)
    return result["probability"]


def generate_learning_plan(missing_skills):
    plan = []
    day  = 1
    for skill in missing_skills[:8]:
        info = ROADMAP_DB.get(skill, DEFAULT_ROADMAP)
        days = int(info["time"].split()[0])
        plan.append({
            "day_start": day, "day_end": day + days - 1,
            "skill": skill, "resources": info["resources"], "priority": info["priority"],
        })
        day += days
    return plan


def chat_response(user_msg, gap_skills, role, prob):
    msg_l = user_msg.lower().strip()
    for key, resp in CHAT_KNOWLEDGE.items():
        if any(w in msg_l for w in key.split()):
            return resp
    if any(w in msg_l for w in ["missing", "learn", "next", "focus", "gap"]):
        if gap_skills:
            top = gap_skills[:3]
            return f"For **{role}**, your top priority gaps are: **{', '.join(top)}**. Start with these — they appear in 80%+ of job descriptions."
        return "Great news! You have a strong skill set. Now focus on building 1–2 strong projects and optimizing your resume."
    if any(w in msg_l for w in ["probability", "chance", "likely", "percent"]):
        tier = "strong" if prob >= 70 else "moderate" if prob >= 50 else "needs work"
        return f"Your current placement probability is **{prob}%** — that's a **{tier}** profile. Closing your top 3 skill gaps could push you above 80%."
    if any(w in msg_l for w in ["hello", "hi", "hey"]):
        return f"Hello! I'm your AI career assistant. I can help you understand your skill gaps for **{role}**, suggest what to learn next, or answer any placement-related questions. Ask away! 🚀"
    return (f"That's a great question! For the **{role}** path with your current probability of **{prob}%**, "
            f"I'd suggest focusing on your critical skill gaps first. "
            f"Would you like a detailed breakdown of your improvement roadmap?")


def extract_skills_from_resume(text: str) -> list:
    found = []
    for skill in ALL_SKILLS:
        if re.search(re.escape(skill), text, re.IGNORECASE):
            found.append(skill)
    return list(set(found))


def prob_color(p):
    if p >= 70: return "#10b981"
    if p >= 50: return "#f59e0b"
    return "#ef4444"


# ─────────────────────────────────────────────────────────────────────────────
# NEW FEATURE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def recommend_top_roles(cgpa, projects, internships, certs, coding_rating, skills):
    scores = {}
    for role in ROLE_REQUIREMENTS:
        result = predict_placement(cgpa, projects, internships, certs, coding_rating, skills, role)
        scores[role] = result["probability"]
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]


def compute_ats_score(user_skills, role, cgpa, projects, internships):
    req = ROLE_REQUIREMENTS[role]
    sm  = compute_skill_match(user_skills, role)
    score = 0
    feedback = []

    skill_pts = round(sm["skill_pct"] * 40)
    score += skill_pts
    if skill_pts < 20:
        feedback.append(("❌", f"Only {len(sm['matched'])} of {len(req['core']+req['tech'])} required skills present. Add more keywords."))
    elif skill_pts < 32:
        feedback.append(("⚠️", f"Skill coverage moderate. Add: {', '.join(sm['missing'][:3])}"))
    else:
        feedback.append(("✅", f"Strong skill coverage! {len(sm['matched'])} skills matched."))

    if cgpa >= 8.0:   cgpa_pts = 15
    elif cgpa >= 7.0: cgpa_pts = 12
    elif cgpa >= 6.0: cgpa_pts = 8
    else:             cgpa_pts = 4
    score += cgpa_pts
    if cgpa < req["min_cgpa"]:
        feedback.append(("❌", f"CGPA {cgpa} is below minimum {req['min_cgpa']} for {role}."))
    else:
        feedback.append(("✅", f"CGPA meets requirements for {role}."))

    proj_pts = min(projects * 6, 20)
    score += proj_pts
    if projects == 0:
        feedback.append(("❌", "No projects listed. ATS filters out zero-project resumes."))
    elif projects < 2:
        feedback.append(("⚠️", "Add 1–2 more projects. Aim for 3 strong, deployed projects."))
    else:
        feedback.append(("✅", f"{projects} projects detected. Good project coverage!"))

    intern_pts = min(internships * 7, 15)
    score += intern_pts
    if internships == 0:
        feedback.append(("⚠️", "No internship experience. Try to get at least 1 internship or freelance project."))
    else:
        feedback.append(("✅", f"{internships} internship(s) detected."))

    cert_pts = min(certs * 3, 10)
    score += cert_pts
    if certs < 2:
        feedback.append(("⚠️", "Few certifications. Add Google/AWS/Microsoft certs to boost ATS score."))
    else:
        feedback.append(("✅", f"{certs} certifications boost keyword density."))

    return min(score, 100), feedback


def compute_salary_prediction(role, prob, cgpa):
    s = SALARY_MAP.get(role, {"base": 5, "mid": 12, "top": 30})
    if prob >= 80:
        low, high, tier = s["mid"], s["top"], "Top Tier"
    elif prob >= 55:
        low, high, tier = round(s["base"] * 1.3, 1), s["mid"], "Mid Tier"
    else:
        low, high, tier = s["base"], round(s["base"] * 1.5, 1), "Entry Level"
    return low, high, tier


def compute_company_eligibility(prob, cgpa, user_skills):
    results = {}
    for category, companies in COMPANY_DB.items():
        cat_results = []
        for co in companies:
            user_has = sum(1 for s in co["skills_needed"] if s in user_skills)
            skill_ok = user_has >= len(co["skills_needed"]) // 2
            if prob >= co["min_prob"] and cgpa >= co["min_cgpa"] and skill_ok:
                eligibility = "Safe"
            elif prob >= co["min_prob"] * 0.75 and cgpa >= co["min_cgpa"] * 0.9:
                eligibility = "Moderate"
            else:
                eligibility = "Dream"
            cat_results.append({
                **co, "eligibility": eligibility,
                "skills_have": user_has, "skills_total": len(co["skills_needed"]),
            })
        results[category] = cat_results
    return results


def get_skill_order(missing_skills):
    ordered = []
    remaining = list(missing_skills)
    max_iters = len(remaining) * 2
    iteration = 0
    while remaining and iteration < max_iters:
        iteration += 1
        for skill in list(remaining):
            deps = SKILL_DEPENDENCIES.get(skill, [])
            deps_met = all(d not in missing_skills or d in ordered for d in deps)
            if deps_met:
                ordered.append(skill)
                remaining.remove(skill)
    ordered.extend(remaining)
    return ordered


def compute_xp(profile):
    xp = 0
    xp += profile.get("cgpa", 0) * 100
    xp += profile.get("projects", 0) * 200
    xp += profile.get("internships", 0) * 300
    xp += profile.get("certs", 0) * 150
    xp += min(profile.get("coding_rating", 0) * 0.5, 500)
    xp += len(profile.get("skills", [])) * 50
    xp += profile.get("probability", 0) * 10
    return int(xp)


def get_level(xp):
    if xp < 500:   return 1, "Beginner",          500
    if xp < 1500:  return 2, "Explorer",           1500
    if xp < 3000:  return 3, "Practitioner",       3000
    if xp < 5000:  return 4, "Skilled Developer",  5000
    if xp < 8000:  return 5, "Advanced Coder",     8000
    if xp < 12000: return 6, "Expert",             12000
    return 7, "Placement Ready 🚀", 15000


def generate_study_plan(missing_skills, hours_per_day):
    plan = []
    for skill in missing_skills[:6]:
        info = ROADMAP_DB.get(skill, DEFAULT_ROADMAP)
        total_days = int(info["time"].split()[0])
        adjusted_days = max(1, round(total_days * (4 / max(hours_per_day, 1))))
        plan.append({
            "skill": skill,
            "original_days": total_days,
            "adjusted_days": adjusted_days,
            "hours_total": total_days * 4,
            "priority": info["priority"],
            "resources": info["resources"],
        })
    return plan


def compute_behavioral_insights(profile):
    insights = []
    prob   = profile.get("probability", 0)
    skills = profile.get("skills", [])
    cgpa   = profile.get("cgpa", 0)

    if cgpa >= 8.5 and prob < 60:
        insights.append({"type": "warn", "msg": "📊 High CGPA but low probability — your technical skills need attention. CGPA alone won't land you a product role."})
    if profile.get("projects", 0) == 0 and prob > 40:
        insights.append({"type": "warn", "msg": "🚧 You have decent skills but zero projects. Recruiters want proof of work — build at least 1 deployed project immediately."})
    if profile.get("coding_rating", 0) < 400 and "DSA" not in skills:
        insights.append({"type": "warn", "msg": "⚡ No DSA + low coding rating is a red flag for technical interviews. Start LeetCode Easy problems today."})
    if len(skills) > 10 and profile.get("projects", 0) < 2:
        insights.append({"type": "info", "msg": "🎯 You know many skills but have few projects. Depth > breadth. Pick 2 skills and build something real with them."})
    if profile.get("internships", 0) == 0 and cgpa > 7.5:
        insights.append({"type": "info", "msg": "💼 Good CGPA but no internship — apply on Internshala NOW. Even a 1-month internship can change your shortlist rate."})
    if prob >= 80:
        insights.append({"type": "success", "msg": "🌟 Excellent profile! Focus on mock interviews, competitive coding, and system design for top-tier companies."})
    if not insights:
        insights.append({"type": "info", "msg": "📈 Keep building. Each skill you add and project you complete increases your placement probability."})
    return insights


def generate_smart_suggestions(missing_skills, prob, role, projects, internships):
    suggestions = []
    if prob < 50 and missing_skills:
        top_skill = missing_skills[0]
        suggestions.append(f"🎯 **Priority:** Start learning **{top_skill}** — it's required for {role} and learning it will improve your probability most.")
    if projects < 2:
        suggestions.append("🛠️ **Action:** Build a project this week using your existing skills. Deploy it on GitHub Pages or Heroku.")
    if internships == 0:
        suggestions.append("💼 **Opportunity:** Apply to 5 internships today on Internshala/LinkedIn. Even unpaid experience counts.")
    if prob >= 70:
        suggestions.append("⚡ **Next Level:** You're placement-ready! Start mock interviews on Pramp or Interviewing.io.")
    if prob >= 85:
        suggestions.append("🚀 **Elite Track:** Apply to FAANG off-campus. Polish your resume, practice system design daily.")
    return suggestions


def generate_career_path(role):
    """Generate career path data. Salary strings use '–' (en-dash) for display."""
    paths = {
        "Software Developer": [
            ("Junior Dev",      "0-1 yr",   "6–10 LPA"),
            ("Software Dev",    "1-3 yrs",  "10–20 LPA"),
            ("Senior Dev",      "3-6 yrs",  "20–35 LPA"),
            ("Tech Lead",       "6-9 yrs",  "35–55 LPA"),
            ("Principal Eng.",  "9-12 yrs", "55–80 LPA"),
            ("VP Engineering",  "12+ yrs",  "80–120 LPA"),
        ],
        "Data Analyst": [
            ("Jr. Data Analyst",    "0-1 yr",   "5–8 LPA"),
            ("Data Analyst",        "1-3 yrs",  "8–15 LPA"),
            ("Sr. Data Analyst",    "3-5 yrs",  "15–25 LPA"),
            ("Data Scientist",      "4-7 yrs",  "20–35 LPA"),
            ("Lead Data Scientist", "7-10 yrs", "35–50 LPA"),
            ("Head of Analytics",   "10+ yrs",  "50–80 LPA"),
        ],
        "AI/ML Engineer": [
            ("Jr. ML Engineer",       "0-1 yr",  "8–12 LPA"),
            ("ML Engineer",           "1-3 yrs", "15–25 LPA"),
            ("Sr. ML Engineer",       "3-6 yrs", "25–45 LPA"),
            ("ML Architect",          "6-9 yrs", "45–70 LPA"),
            ("AI Research Scientist", "5-8 yrs", "60–100 LPA"),
            ("Head of AI",            "10+ yrs", "100–150 LPA"),
        ],
        "Web Developer": [
            ("Jr. Web Dev",       "0-1 yr",   "4–7 LPA"),
            ("Web Developer",     "1-3 yrs",  "7–15 LPA"),
            ("Sr. Full Stack Dev","3-5 yrs",  "15–25 LPA"),
            ("Eng. Manager",      "5-8 yrs",  "25–40 LPA"),
            ("Director of Eng.",  "8-12 yrs", "40–60 LPA"),
            ("CTO (Startup)",     "10+ yrs",  "60–100 LPA"),
        ],
        "DevOps Engineer": [
            ("Jr. DevOps Eng.", "0-1 yr",   "7–11 LPA"),
            ("DevOps Engineer", "1-3 yrs",  "12–20 LPA"),
            ("Sr. DevOps / SRE","3-6 yrs",  "20–35 LPA"),
            ("Cloud Architect",  "5-8 yrs",  "35–55 LPA"),
            ("Platform Lead",    "8-11 yrs", "55–80 LPA"),
            ("VP of Infra",      "10+ yrs",  "80–120 LPA"),
        ],
    }
    return paths.get(role, paths["Software Developer"])


def export_report_pdf(profile, result):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=60, bottomMargin=40)
        styles = getSampleStyleSheet()
        story  = []

        title_style = ParagraphStyle("title", parent=styles["Title"],
                                     fontSize=22, textColor=HexColor("#00f5d4"), spaceAfter=6)
        head_style  = ParagraphStyle("head",  parent=styles["Heading2"],
                                     fontSize=14, textColor=HexColor("#7209b7"), spaceAfter=4)
        body_style  = ParagraphStyle("body",  parent=styles["Normal"],
                                     fontSize=10, textColor=HexColor("#222222"), spaceAfter=3)
        sub_style   = ParagraphStyle("sub",   parent=styles["Normal"],
                                     fontSize=9,  textColor=HexColor("#555555"), spaceAfter=2)

        story.append(Paragraph("CareerLens AI — Career Intelligence Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}  |  Role: {profile['role']}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#00f5d4")))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Profile Summary", head_style))
        profile_data = [
            ["Metric", "Value"],
            ["CGPA", str(profile["cgpa"])],
            ["Projects", str(profile["projects"])],
            ["Internships", str(profile["internships"])],
            ["Certifications", str(profile["certs"])],
            ["Coding Rating", str(profile["coding_rating"])],
            ["Target Role", profile["role"]],
            ["Placement Probability", f"{result['probability']}%"],
            ["Job Readiness Score", f"{result['readiness']}/100"],
            ["Estimated Time to Ready", f"{profile['months']} months"],
        ]
        t = Table(profile_data, colWidths=[3 * inch, 3.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#00f5d4")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), HexColor("#000000")),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("GRID",       (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f9f9f9"), HexColor("#ffffff")]),
            ("PADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Skills You Have", head_style))
        story.append(Paragraph(", ".join(profile["matched"]) if profile["matched"] else "None", body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Critical Missing Skills", head_style))
        story.append(Paragraph(", ".join(profile["missing"]) if profile["missing"] else "None — all covered!", body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Learning Roadmap", head_style))
        for i, step in enumerate(profile["plan"][:6], 1):
            info = ROADMAP_DB.get(step["skill"], DEFAULT_ROADMAP)
            story.append(Paragraph(f"{i}. {step['skill']} — {info['time']} — {info['priority']}", body_style))
            story.append(Paragraph(f"   Resources: {', '.join(info['resources'])}", sub_style))
        story.append(Spacer(1, 8))

        sal_low, sal_high, sal_tier = compute_salary_prediction(profile["role"], result["probability"], profile["cgpa"])
        story.append(Paragraph("Salary Prediction", head_style))
        story.append(Paragraph(f"Expected Package: Rs.{sal_low}–{sal_high} LPA ({sal_tier})", body_style))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Badges Earned", head_style))
        earned_badges = []
        profile_for_badges = {**profile, "probability": result["probability"]}
        for badge, info in BADGES.items():
            if info["condition"](profile_for_badges):
                earned_badges.append(badge)
        story.append(Paragraph(", ".join(earned_badges) if earned_badges else "Keep building to earn badges!", body_style))

        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc")))
        story.append(Paragraph("CareerLens AI — Your Personal Placement Intelligence System", sub_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "msg": "👋 Hi! I'm your AI career assistant. Enter your profile on the left and I'll help you ace placement season!"}
    ]
if "result"            not in st.session_state: st.session_state.result = None
if "profile"           not in st.session_state: st.session_state.profile = {}
if "completed_skills"  not in st.session_state: st.session_state.completed_skills = set()
if "streak_data"       not in st.session_state:
    st.session_state.streak_data = {"last_date": None, "current_streak": 0, "max_streak": 0}
if "xp_total"          not in st.session_state: st.session_state.xp_total = 0


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — INPUT FORM
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 CareerLens AI")
    st.markdown("*Your personal placement intelligence system*")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()
    with col_t2:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()

    st.markdown("---")
    st.markdown("### 💾 Save / Load Profile")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Save", use_container_width=True) and st.session_state.profile:
            profile_json = json.dumps(st.session_state.profile, indent=2)
            st.download_button("📥 Download JSON", profile_json,
                               file_name="careerlens_profile.json",
                               mime="application/json",
                               use_container_width=True)
    with col_s2:
        uploaded_profile = st.file_uploader("📤 Load", type=["json"], label_visibility="collapsed")
        if uploaded_profile:
            try:
                loaded = json.load(uploaded_profile)
                st.session_state.profile = loaded
                if "probability" in loaded:
                    st.success("✅ Profile loaded!")
            except Exception as e:
                st.error(f"Error loading profile: {e}")

    st.markdown("---")
    st.markdown("### 📄 Resume Upload (optional)")
    resume_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"], label_visibility="collapsed")
    auto_skills = []
    if resume_file:
        try:
            if resume_file.type == "application/pdf":
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                    text = " ".join(p.extract_text() or "" for p in reader.pages)
                except ImportError:
                    text = ""
                    st.warning("Install PyPDF2: `pip install PyPDF2`")
            else:
                text = resume_file.read().decode("utf-8", errors="ignore")
            auto_skills = extract_skills_from_resume(text)
            if auto_skills:
                st.success(f"✅ Detected {len(auto_skills)} skills from resume!")
        except Exception as e:
            st.error(f"Resume parse error: {e}")

    st.markdown("---")
    st.markdown("### 🎓 Academic Profile")
    cgpa          = st.slider("CGPA", 0.0, 10.0, 7.2, 0.1)
    projects      = st.number_input("Projects Built", 0, 20, 2, 1)
    internships   = st.number_input("Internships", 0, 10, 1, 1)
    certs         = st.number_input("Certifications", 0, 20, 2, 1)
    coding_rating = st.slider("Coding Platform Rating", 0, 2500, 800, 50)

    st.markdown("### 🧠 Skills")
    default_skills = auto_skills if auto_skills else ["Python", "SQL", "Git"]
    user_skills = st.multiselect(
        "Select your skills",
        options=ALL_SKILLS,
        default=[s for s in default_skills if s in ALL_SKILLS],
        label_visibility="collapsed",
    )

    st.markdown("### 🎯 Target Role")
    role = st.selectbox("Select role", list(ROLE_REQUIREMENTS.keys()), label_visibility="collapsed")

    st.markdown("---")
    analyze_btn = st.button("⚡ Analyze My Profile", use_container_width=True, type="primary")

    if analyze_btn:
        if not user_skills:
            st.error("Please select at least one skill.")
        else:
            result  = predict_placement(cgpa, projects, internships, certs, coding_rating, user_skills, role)
            sm      = result["skill_match"]
            missing = sm["missing"]
            months  = estimate_time_to_ready(missing, result["probability"])
            plan    = generate_learning_plan(missing)

            st.session_state.result  = result
            st.session_state.profile = {
                "cgpa": cgpa, "projects": projects, "internships": internships,
                "certs": certs, "coding_rating": coding_rating,
                "skills": user_skills, "role": role,
                "months": months, "plan": plan,
                "missing": missing, "weak": sm["weak"], "matched": sm["matched"],
                "probability": result["probability"],
            }
            xp = compute_xp(st.session_state.profile)
            st.session_state.xp_total = xp

            today = str(date.today())
            sd    = st.session_state.streak_data
            if sd["last_date"] != today:
                yesterday = str(date.today() - timedelta(days=1))
                sd["current_streak"] = sd["current_streak"] + 1 if sd["last_date"] == yesterday else 1
                sd["last_date"]  = today
                sd["max_streak"] = max(sd["max_streak"], sd["current_streak"])
                st.session_state.streak_data = sd

            st.session_state.chat_history.append({
                "role": "ai",
                "msg": f"✅ Analysis complete for **{role}**! Placement probability: **{result['probability']}%**. Check the dashboard tabs for full insights."
            })


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────

render_html("<h1 style='margin-bottom:.2rem'>🎯 CareerLens <span style='color:#00f5d4'>AI</span></h1>")
render_html("<p style='color:#64748b;margin-top:0'>Placement Prediction · Skill Gap Analysis · Career Roadmap · AI Co-Pilot</p>")

if st.session_state.result is None:
    render_html("""
    <div class="card" style="text-align:center;padding:3rem">
        <div style="font-size:3rem">🚀</div>
        <h2>Get Started</h2>
        <p style="color:#64748b;max-width:480px;margin:auto">
            Fill in your academic profile and skills on the left sidebar,
            then click <b>Analyze My Profile</b> to get your personalized
            placement prediction, skill gap analysis, and learning roadmap.
        </p>
    </div>""")

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("🎯", "Placement Prediction", "ML-powered probability scoring"),
        ("🧠", "Skill Gap Analysis",   "Know exactly what's missing"),
        ("🗺️", "Personalized Roadmap", "Day-by-day learning plan"),
        ("🏢", "Company Eligibility",  "See which companies you can target"),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
        with col:
            render_html(f"""
            <div class="card" style="text-align:center">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-weight:700;margin:.3rem 0">{title}</div>
                <div style="color:#64748b;font-size:.82rem">{desc}</div>
            </div>""")
    st.stop()

# ── Unpack session ────────────────────────────────────────────────────────────
R    = st.session_state.result
P    = st.session_state.profile
role = P["role"]
prob = R["probability"]
pc   = prob_color(prob)

# ─────────────────────────────────────────────────────────────────────────────
# SMART NOTIFICATIONS BANNER
# ─────────────────────────────────────────────────────────────────────────────
insights = compute_behavioral_insights(P)
with st.expander("💡 Smart Insights & Notifications", expanded=False):
    for ins in insights:
        render_notif(ins["msg"], ins["type"])

# ─────────────────────────────────────────────────────────────────────────────
# METRIC BANNER
# ─────────────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (f"{prob}%",              "Placement Probability"),
    (f"{R['readiness']}/100", "Job Readiness Score"),
    (f"{R['skill_score']}%",  "Skill Match"),
    (f"{R['academic_score']}%","Academic Score"),
    (f"{P['months']} mo",     "Time to Job-Ready"),
]
for col, (val, lbl) in zip([c1, c2, c3, c4, c5], metrics):
    with col:
        render_html(f"""
        <div class="metric-tile">
            <div class="metric-val">{val}</div>
            <div class="metric-label">{lbl}</div>
        </div>""")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# XP + GAMIFICATION BAR
# ─────────────────────────────────────────────────────────────────────────────
xp = st.session_state.xp_total
lvl, lvl_name, lvl_max = get_level(xp)
lvl_prev_map = {1: 0, 2: 0, 3: 500, 4: 1500, 5: 3000, 6: 5000, 7: 8000}
lvl_prev     = lvl_prev_map.get(lvl, 0)
xp_progress  = min((xp - lvl_prev) / max(lvl_max - lvl_prev, 1) * 100, 100)
streak       = st.session_state.streak_data["current_streak"]

xp_col, streak_col = st.columns([3, 1])
with xp_col:
    render_html(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:.5rem">
        <span style="font-family:'Space Mono';color:#7209b7;font-weight:700;font-size:1.1rem">Lv.{lvl}</span>
        <div style="flex:1">
            <div style="display:flex;justify-content:space-between;font-size:.78rem;color:#64748b;margin-bottom:3px">
                <span>{lvl_name}</span><span>{xp:,} XP / {lvl_max:,} XP</span>
            </div>
            <div class="xp-bar-wrap"><div class="xp-bar-fill" style="width:{xp_progress:.1f}%"></div></div>
        </div>
    </div>""")
with streak_col:
    render_html(f"""
    <div class="metric-tile" style="padding:.6rem 1rem">
        <div style="font-size:1.6rem;font-family:'Space Mono';font-weight:700;color:#f59e0b">🔥 {streak}</div>
        <div class="metric-label">Day Streak</div>
    </div>""")

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Dashboard", "🧠 Skill Gap", "🗺️ Roadmap", "🔮 What-If", "📈 Analytics", "💬 AI Chat",
    "🏢 Companies", "🎖️ Gamification", "📝 Resume ATS", "💰 Salary", "🎤 Interview Prep",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("#### Placement Probability")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob,
            number={"suffix": "%", "font": {"size": 48, "color": pc, "family": "Space Mono"}},
            gauge={
                "axis":       {"range": [0, 100], "tickcolor": "#64748b", "tickwidth": 1},
                "bar":        {"color": pc, "thickness": 0.25},
                "bgcolor":    "#111827",
                "bordercolor":"#1e2d45",
                "steps": [
                    {"range": [0, 40],   "color": "#2d0a0a"},
                    {"range": [40, 70],  "color": "#2d1f00"},
                    {"range": [70, 100], "color": "#052e16"},
                ],
                "threshold": {"line": {"color": pc, "width": 3}, "value": prob},
            },
            domain={"x": [0, 1], "y": [0, 1]},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(t=20, b=0, l=20, r=20),
            font={"color": "#e2e8f0"},
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("#### All-Role Probability Comparison")
        roles_all = list(ROLE_REQUIREMENTS.keys())
        probs_all  = [
            predict_placement(P["cgpa"], P["projects"], P["internships"],
                              P["certs"], P["coding_rating"], P["skills"], r)["probability"]
            for r in roles_all
        ]
        colors_all = [ROLE_REQUIREMENTS[r]["color"] for r in roles_all]
        fig_bar = go.Figure(go.Bar(
            x=probs_all, y=roles_all, orientation="h",
            marker_color=colors_all,
            text=[f"{p}%" for p in probs_all],
            textposition="outside",
            textfont={"color": "#e2e8f0", "family": "Space Mono"},
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"range": [0, 105], "color": "#64748b", "gridcolor": "#1e2d45"},
            yaxis={"color": "#e2e8f0"},
            height=240, margin=dict(t=10, b=10, l=10, r=50),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ✅ FIX 3: Top Role Recommendations — all HTML via render_html()
        st.markdown("#### 🎯 Top Role Recommendations")
        top_roles = recommend_top_roles(
            P["cgpa"], P["projects"], P["internships"],
            P["certs"], P["coding_rating"], P["skills"],
        )
        for rank, (r, p) in enumerate(top_roles, 1):
            color = ROLE_REQUIREMENTS[r]["color"]
            render_html(f"""
            <div class="card" style="border-left:4px solid {color};margin-bottom:.8rem">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div style="font-weight:700;font-size:1.1rem">{rank}. {r}</div>
                        <div style="color:#64748b;font-size:.9rem">Estimated Probability: {p}%</div>
                    </div>
                    <div style="font-size:1.5rem;color:{color}">➡️</div>
                </div>
            </div>""")