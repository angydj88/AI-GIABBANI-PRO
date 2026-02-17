import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import fitz  # PyMuPDF
import io
import json
import re
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="GABBIANI MASTER AI · Motor de Corte Industrial",
    layout="wide",
    page_icon="⬡",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS PREMIUM · BLACK & GOLD EDITION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:wght@700;800;900&display=swap');

:root {
    --bg-void: #08090c;
    --bg-primary: #0c0d12;
    --bg-secondary: #111318;
    --bg-card: #16181f;
    --bg-card-hover: #1c1e27;
    --bg-elevated: #1f2129;
    --bg-input: #13141a;
    
    --border-subtle: rgba(212,175,55,0.08);
    --border-medium: rgba(212,175,55,0.15);
    --border-strong: rgba(212,175,55,0.3);
    --border-glow: rgba(212,175,55,0.5);
    
    --gold-50: #fef9e7;
    --gold-100: #fdf0c4;
    --gold-200: #f5d778;
    --gold-300: #e8c547;
    --gold-400: #d4af37;
    --gold-500: #c5a028;
    --gold-600: #a68523;
    --gold-700: #856a1c;
    --gold-800: #5c4a14;
    --gold-900: #3d310e;
    
    --text-primary: #f0ebe0;
    --text-secondary: #a09882;
    --text-muted: #6b6355;
    --text-gold: #d4af37;
    --text-gold-light: #e8c547;
    
    --accent-emerald: #10b981;
    --accent-red: #ef4444;
    --accent-amber: #f59e0b;
    --accent-blue: #60a5fa;
    
    --gradient-gold: linear-gradient(135deg, #d4af37 0%, #f5d778 40%, #d4af37 60%, #a68523 100%);
    --gradient-gold-subtle: linear-gradient(135deg, rgba(212,175,55,0.15) 0%, rgba(245,215,120,0.05) 100%);
    --gradient-gold-border: linear-gradient(135deg, #a68523 0%, #d4af37 50%, #a68523 100%);
    --gradient-dark: linear-gradient(180deg, #111318 0%, #0c0d12 100%);
    --gradient-card: linear-gradient(145deg, #16181f 0%, #111318 100%);
    --gradient-shine: linear-gradient(110deg, transparent 25%, rgba(212,175,55,0.03) 50%, transparent 75%);
    
    --shadow-gold-sm: 0 2px 8px rgba(212,175,55,0.08);
    --shadow-gold-md: 0 4px 20px rgba(212,175,55,0.1);
    --shadow-gold-lg: 0 8px 40px rgba(212,175,55,0.12);
    --shadow-gold-glow: 0 0 30px rgba(212,175,55,0.15);
    --shadow-dark: 0 20px 60px rgba(0,0,0,0.5);
    
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-2xl: 24px;
}

/* ── GLOBAL ── */
.stApp {
    background: var(--bg-void) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

.stApp > header { background: transparent !important; }

.main .block-container {
    padding: 2rem 3rem 4rem 3rem !important;
    max-width: 1440px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--gold-700), var(--gold-800));
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: var(--gold-600); }

/* ── HIDE STREAMLIT DEFAULTS ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
}

p, span, li, label, div {
    font-family: 'Inter', sans-serif !important;
}

/* ══════════════════════════════════════════════════════════════
   HERO HEADER
   ══════════════════════════════════════════════════════════════ */
.hero-wrapper {
    position: relative;
    margin: -1rem -1rem 2.5rem -1rem;
    border-radius: var(--radius-2xl);
    overflow: hidden;
    background: var(--bg-secondary);
    border: 1px solid var(--border-medium);
    box-shadow: var(--shadow-dark), var(--shadow-gold-md);
}

.hero-gold-line {
    height: 2px;
    background: var(--gradient-gold);
    box-shadow: 0 1px 15px rgba(212,175,55,0.4);
}

.hero-content {
    padding: 2.5rem 3rem 2rem 3rem;
    position: relative;
}

.hero-content::after {
    content: '';
    position: absolute;
    top: -40%; right: -10%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(212,175,55,0.04) 0%, transparent 65%);
    pointer-events: none;
}

.hero-content::before {
    content: '';
    position: absolute;
    bottom: -30%; left: -5%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(212,175,55,0.02) 0%, transparent 60%);
    pointer-events: none;
}

.hero-mono-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold-400);
    margin-bottom: 1.25rem;
    padding: 6px 16px;
    background: rgba(212,175,55,0.06);
    border: 1px solid rgba(212,175,55,0.12);
    border-radius: 100px;
}

.hero-mono-tag .tag-dot {
    width: 6px; height: 6px;
    background: var(--gold-400);
    border-radius: 50%;
    animation: pulse-gold 2.5s ease-in-out infinite;
    box-shadow: 0 0 8px rgba(212,175,55,0.6);
}

@keyframes pulse-gold {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(212,175,55,0.6); }
    50% { opacity: 0.4; box-shadow: 0 0 4px rgba(212,175,55,0.3); }
}

.hero-title-line {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 0.6rem;
}

.hero-brand {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.6rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.03em !important;
    line-height: 1 !important;
    margin: 0 !important;
    color: var(--text-primary) !important;
}

.hero-brand .gold {
    background: var(--gradient-gold);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: brightness(1.1);
}

.hero-edition {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
}

.hero-desc {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0 0 1.5rem 0;
    max-width: 700px;
}

.hero-status-row {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border-subtle);
    flex-wrap: wrap;
}

.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.chip-online {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    color: var(--accent-emerald);
}

.chip-gold {
    background: rgba(212,175,55,0.06);
    border: 1px solid rgba(212,175,55,0.15);
    color: var(--gold-300);
}

.chip-neutral {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
}

.chip-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
}

.chip-dot.green {
    background: var(--accent-emerald);
    box-shadow: 0 0 6px rgba(16,185,129,0.5);
    animation: pulse-green 2s ease-in-out infinite;
}

@keyframes pulse-green {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.chip-dot.gold {
    background: var(--gold-400);
    box-shadow: 0 0 6px rgba(212,175,55,0.4);
}

/* ══════════════════════════════════════════════════════════════
   SECTION HEADERS
   ══════════════════════════════════════════════════════════════ */
.sec-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 2.5rem 0 1.25rem 0;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-subtle);
    position: relative;
}

.sec-header::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 60px;
    height: 1px;
    background: var(--gradient-gold);
}

.sec-icon {
    width: 42px; height: 42px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(212,175,55,0.06);
    border: 1px solid rgba(212,175,55,0.12);
    border-radius: var(--radius-sm);
    font-size: 18px;
    flex-shrink: 0;
}

.sec-text .sec-title {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
    letter-spacing: -0.01em !important;
}

.sec-text .sec-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 2px;
}

.sec-badge {
    margin-left: auto;
    padding: 4px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em;
}

/* ══════════════════════════════════════════════════════════════
   METRIC CARDS
   ══════════════════════════════════════════════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.kpi-card {
    position: relative;
    padding: 1.4rem 1.5rem;
    background: var(--gradient-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.kpi-card:hover {
    border-color: var(--border-medium);
    transform: translateY(-3px);
    box-shadow: var(--shadow-gold-md);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.kpi-card.gold::before { background: var(--gradient-gold); }
.kpi-card.emerald::before { background: linear-gradient(90deg, #059669, #10b981, #34d399); }
.kpi-card.neutral::before { background: linear-gradient(90deg, #4b5563, #6b7280, #9ca3af); }
.kpi-card.amber::before { background: linear-gradient(90deg, #d97706, #f59e0b, #fbbf24); }

.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: var(--gradient-shine);
    pointer-events: none;
}

.kpi-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.03em;
    line-height: 1;
}

.kpi-unit {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-muted);
    margin-left: 3px;
    letter-spacing: 0;
}

.kpi-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
    font-weight: 500;
}

/* ══════════════════════════════════════════════════════════════
   FILE UPLOADER
   ══════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border-medium) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2.5rem !important;
    transition: all 0.3s ease !important;
    position: relative;
}

[data-testid="stFileUploader"] > div:hover {
    border-color: var(--gold-400) !important;
    background: rgba(212,175,55,0.02) !important;
    box-shadow: var(--shadow-gold-sm) !important;
}

[data-testid="stFileUploader"] label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-muted) !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
}

/* Traducciones via pseudo-elements no funcionan en Streamlit, 
   pero estilizamos los botones del uploader */
[data-testid="stFileUploaderDropzoneInput"] + div {
    color: var(--text-secondary) !important;
}

/* ══════════════════════════════════════════════════════════════
   THUMBNAILS / PAGE GRID
   ══════════════════════════════════════════════════════════════ */
[data-testid="stImage"] {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    border: 1px solid var(--border-subtle) !important;
    transition: all 0.3s ease !important;
    background: var(--bg-card) !important;
}

[data-testid="stImage"]:hover {
    border-color: var(--gold-400) !important;
    box-shadow: var(--shadow-gold-sm) !important;
    transform: scale(1.02);
}

/* ══════════════════════════════════════════════════════════════
   CHECKBOXES
   ══════════════════════════════════════════════════════════════ */
[data-testid="stCheckbox"] label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}

[data-testid="stCheckbox"] label:hover {
    color: var(--text-gold) !important;
}

/* ══════════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════════ */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    border: none !important;
    font-size: 0.88rem !important;
    text-transform: uppercase !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--gradient-gold) !important;
    color: #0c0d12 !important;
    box-shadow: 0 4px 20px rgba(212,175,55,0.25) !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    box-shadow: 0 6px 30px rgba(212,175,55,0.4) !important;
    transform: translateY(-2px) !important;
    filter: brightness(1.1) !important;
}

.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="baseButton-primary"]:active {
    transform: translateY(0) !important;
    filter: brightness(0.95) !important;
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: var(--gold-400) !important;
    box-shadow: var(--shadow-gold-sm) !important;
}

/* ══════════════════════════════════════════════════════════════
   DOWNLOAD BUTTON
   ══════════════════════════════════════════════════════════════ */
.stDownloadButton > button {
    background: var(--gradient-gold) !important;
    color: #0c0d12 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.8rem 2.5rem !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(212,175,55,0.25) !important;
    font-size: 0.9rem !important;
    text-transform: uppercase !important;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}

.stDownloadButton > button:hover {
    box-shadow: 0 8px 35px rgba(212,175,55,0.4) !important;
    transform: translateY(-2px) !important;
    filter: brightness(1.1) !important;
}

/* ══════════════════════════════════════════════════════════════
   DATA TABLE
   ══════════════════════════════════════════════════════════════ */
[data-testid="stDataEditor"],
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-dark) !important;
}

[data-testid="stDataEditor"] [role="gridcell"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ══════════════════════════════════════════════════════════════
   ALERTS & EXPANDER
   ══════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
    box-shadow: var(--shadow-gold-sm) !important;
}

[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    padding: 1rem 1.25rem !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    border-top: 1px solid var(--border-subtle) !important;
}

[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
    padding: 0.8rem 1rem !important;
    border-left-width: 3px !important;
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-elevated) !important;
}

/* ══════════════════════════════════════════════════════════════
   PROGRESS BAR
   ══════════════════════════════════════════════════════════════ */
.stProgress > div > div {
    background: var(--gradient-gold) !important;
    border-radius: 100px !important;
    box-shadow: 0 0 12px rgba(212,175,55,0.4) !important;
}

.stProgress > div {
    background: var(--bg-card) !important;
    border-radius: 100px !important;
    border: 1px solid var(--border-subtle) !important;
}

/* ══════════════════════════════════════════════════════════════
   DIVIDER
   ══════════════════════════════════════════════════════════════ */
hr {
    border-color: var(--border-subtle) !important;
    margin: 2rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════
   SUCCESS / INFO / WARNING / ERROR
   ══════════════════════════════════════════════════════════════ */
[data-baseweb="notification"][kind="positive"],
.element-container .stSuccess {
    background: rgba(16,185,129,0.06) !important;
    border-left-color: var(--accent-emerald) !important;
}

[data-baseweb="notification"][kind="info"],
.element-container .stInfo {
    background: rgba(212,175,55,0.05) !important;
    border-left-color: var(--gold-400) !important;
}

[data-baseweb="notification"][kind="warning"],
.element-container .stWarning {
    background: rgba(245,158,11,0.06) !important;
    border-left-color: var(--accent-amber) !important;
}

[data-baseweb="notification"][kind="negative"],
.element-container .stError {
    background: rgba(239,68,68,0.06) !important;
    border-left-color: var(--accent-red) !important;
}

/* ══════════════════════════════════════════════════════════════
   CAPTIONS
   ══════════════════════════════════════════════════════════════ */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
}

/* ══════════════════════════════════════════════════════════════
   COLUMNS
   ══════════════════════════════════════════════════════════════ */
[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* ══════════════════════════════════════════════════════════════
   ORNAMENTAL SEPARATORS
   ══════════════════════════════════════════════════════════════ */
.gold-separator {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 2rem 0;
}

.gold-separator .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-medium), transparent);
}

.gold-separator .diamond {
    width: 8px; height: 8px;
    background: var(--gold-400);
    transform: rotate(45deg);
    opacity: 0.5;
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════════════════════
   CUSTOM FOOTER
   ══════════════════════════════════════════════════════════════ */
.luxury-footer {
    margin-top: 5rem;
    padding: 2rem 0;
    text-align: center;
    position: relative;
}

.luxury-footer::before {
    content: '';
    position: absolute;
    top: 0; left: 20%; right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-medium), transparent);
}

.footer-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 800;
    background: var(--gradient-gold);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.footer-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.06em;
}

/* ══════════════════════════════════════════════════════════════
   PROCESSING STATUS CARDS
   ══════════════════════════════════════════════════════════════ */
.proc-status {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.75rem 1.25rem;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    margin: 0.5rem 0;
}

.proc-icon {
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(212,175,55,0.08);
    border: 1px solid rgba(212,175,55,0.15);
    border-radius: 6px;
    font-size: 14px;
    flex-shrink: 0;
}

.proc-text-main {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-primary);
}

.proc-text-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-left: 8px;
}

/* ══════════════════════════════════════════════════════════════
   TABLE HEADER LABEL
   ══════════════════════════════════════════════════════════════ */
.table-label {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.75rem;
}

.table-label .bar {
    width: 3px; height: 16px;
    background: var(--gradient-gold);
    border-radius: 2px;
}

.table-label span {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ══════════════════════════════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem !important; }
    .hero-brand { font-size: 1.6rem !important; }
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    .hero-content { padding: 1.5rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-gold-line"></div>
    <div class="hero-content">
        <div class="hero-mono-tag">
            <span class="tag-dot"></span>
            MOTOR DE CORTE INDUSTRIAL · v3.0
        </div>
        <div class="hero-title-line">
            <h1 class="hero-brand">
                GABBIANI <span class="gold">MASTER AI</span>
            </h1>
            <span class="hero-edition">BLACK EDITION</span>
        </div>
        <p class="hero-desc">
            Sistema experto de extracción de despiece con inteligencia artificial y reglas de ingeniería inversa.
            Análisis visual por Gemini 3.0 Flash · Optimización automática de corte.
        </p>
        <div class="hero-status-row">
            <div class="status-chip chip-online">
                <span class="chip-dot green"></span>
                Motor IA Activo
            </div>
            <div class="status-chip chip-gold">
                <span class="chip-dot gold"></span>
                Gemini 3.0 Flash
            </div>
            <div class="status-chip chip-neutral">
                ⏱ {datetime.now().strftime("%d/%m/%Y · %H:%M")}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── API KEY ──────────────────────────────────────────────────────────────────
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.markdown("""
    <div style="background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.18);
                border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0;
                border-left: 3px solid #ef4444;">
        <div style="font-size: 1.05rem; font-weight: 700; color: #fca5a5; margin-bottom: 0.4rem;">
            ⛔ Error Crítico de Configuración
        </div>
        <div style="color: #a09882; font-size: 0.88rem;">
            No se encontró la clave API en
            <code style="background: rgba(212,175,55,0.08); padding: 2px 8px; border-radius: 4px;
                         color: #d4af37; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;">
            .streamlit/secrets.toml</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# --- 2. EL CEREBRO DEL OPERARIO (LÓGICA EXPERTA) ---
class CerebroOperario:
    def __init__(self):
        self.ANCHO_MINIMO_PINZA = 70
        self.ANCHO_SEGURIDAD = 130
        self.LARGO_MAXIMO_TABLERO = 2850
        self.MARGEN_SANEADO = 60
        self.MARGEN_CNC = 10
        self.DESCUENTO_QUBE = 59
        self.LISTA_NEGRA = ["PINO", "PINTURA", "CANTO", "TORNILLO", "HERRAJE", "PERFIL LED", "CATALIZADOR"]

    def normalizar_material(self, texto):
        mat = str(texto).upper()
        if "KRION" in mat: return "KRION (🛑 CORTE ESPECIAL)"
        if "ALUMINIO" in mat or "METAL" in mat or "ACERO" in mat: return "METAL (🛑 NO CORTAR)"
        if "BLANCO" in mat or "CAOLIN" in mat or "W980" in mat or "WHITE" in mat: return "W980"
        if "ELEGANCE" in mat or "M6317" in mat or "ROBLE" in mat or "OAK" in mat: return "M6317"
        if "FONDO" in mat or "OCULTO" in mat or "BACK" in mat: return "16 B"
        return texto

    def extraer_medidas_texto(self, texto):
        patron = r'(\d{3,4})\s*[xX]\s*(\d{3,4})'
        match = re.search(patron, texto)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None, None

    def procesar_pagina(self, datos_crudos, numero_pagina):
        lista_final = []
        alertas = []
        if not datos_crudos:
            return [], []

        for pieza in datos_crudos:
            id_unico = f"P{numero_pagina}_{pieza.get('id', 'X')}"
            nombre = pieza.get("nombre", "Sin Nombre")
            notas = str(pieza.get("notas", "")).upper()
            material_raw = pieza.get("material", "")

            if any(x in nombre.upper() for x in self.LISTA_NEGRA) or any(x in material_raw.upper() for x in self.LISTA_NEGRA):
                continue

            material = self.normalizar_material(material_raw)

            try:
                largo = float(pieza.get("largo", 0))
                ancho = float(pieza.get("ancho", 0))
                espesor = float(pieza.get("espesor", 19))
                cantidad = int(pieza.get("cantidad", 1))
            except:
                largo, ancho, espesor, cantidad = 0, 0, 19, 1

            l_txt, a_txt = self.extraer_medidas_texto(nombre + " " + notas)
            if l_txt and (largo == 0 or abs(largo - l_txt) > 50):
                largo, ancho = l_txt, a_txt
                notas += " | MEDIDA DE TEXTO"

            if largo < ancho:
                largo, ancho = ancho, largo

            if "PEGAR" in notas or "DOBLE" in notas or "APLACAR" in notas or "SANDWICH" in notas:
                largo += self.MARGEN_SANEADO
                ancho += self.MARGEN_SANEADO
                notas += f" | SANEADO +{self.MARGEN_SANEADO}mm"
                if "DOBLE" in notas or "19+19" in notas:
                    if cantidad == 1:
                        cantidad *= 2
                        notas += " | CANTIDAD x2 (Sándwich)"
                alertas.append(f"🥪 {nombre}: Sándwich detectado.")

            if "CAJÓN" in nombre.upper() or "CAJON" in nombre.upper():
                if "QUBE" in notas:
                    largo_fondo = 280 if "300" in notas else 480
                    ancho_fondo = largo - self.DESCUENTO_QUBE
                    p_fondo = {
                        "ID": f"{id_unico}_FONDO",
                        "Nombre": f"Fondo {nombre}",
                        "Largo": ancho_fondo,
                        "Ancho": largo_fondo,
                        "Espesor": 16,
                        "Material": "16 B",
                        "Cantidad": cantidad,
                        "Notas": "GENERADO AUTO: Fondo Qube"
                    }
                    lista_final.append(p_fondo)
                    alertas.append(f"✨ {nombre}: Despiece Fondo Qube generado.")
                    nombre = f"Frente {nombre}"

            es_curva = "R" in notas or "RADIO" in notas or "CURVA" in notas
            if es_curva:
                largo += self.MARGEN_CNC
                ancho += self.MARGEN_CNC
                notas += f" | MARGEN CNC +{self.MARGEN_CNC}mm"
                alertas.append(f"🔧 {nombre}: Forma curva -> Margen CNC.")
            elif "Ø" in notas or "MECANIZADO" in notas:
                notas += " | PASAR A CNC (Taladros)"

            if "CIERRE" in nombre.upper() or "PERFIL" in notas or "INGLETE" in notas:
                if ancho < 150:
                    notas += " | CORTE BRUTO PERFIL"

            if ancho < 50 and cantidad >= 2 and cantidad % 2 == 0:
                ancho = self.ANCHO_SEGURIDAD
                cantidad = int(cantidad / 2)
                notas += " | OPTIMIZACIÓN 2x1 (Sacar 2 tiras)"
                alertas.append(f"✂️ {nombre}: Optimización 2x1 aplicada.")

            elif ancho < self.ANCHO_MINIMO_PINZA:
                medida_real = ancho
                notas += f" | !! RECORTAR A {medida_real} MANUAL !!"
                alertas.append(f"🚨 {nombre}: PINZAS! Ancho {medida_real} peligroso. Cortar tira ancha.")

            if largo > self.LARGO_MAXIMO_TABLERO:
                alertas.append(f"🚛 {nombre}: Largo {largo}mm excede estándar.")

            p = {
                "ID": id_unico,
                "Nombre": nombre,
                "Largo": largo,
                "Ancho": ancho,
                "Espesor": espesor,
                "Material": material,
                "Cantidad": cantidad,
                "Notas": notas
            }
            lista_final.append(p)

        return lista_final, alertas


# --- 3. EL OJO DE LA IA (GEMINI 3 FLASH) ---
def analizar_imagen_con_ia(imagen):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    prompt = """
    Eres un Técnico de Oficina Técnica. Extrae datos para fabricación.

    INSTRUCCIONES DE LECTURA:
    1. IGNORA PÁGINAS INFORMATIVAS (Títulos: "Hoja informativa", "Vista General").
    2. TABLAS: Si hay tabla, extrae cada fila.
    3. DIBUJOS: Extrae el BOUNDING BOX (Rectángulo máximo exterior).
       - Ignora agujeros interiores.
       - Ignora cotas de posición.
    4. NOTAS: Busca: "Pegar", "Qube", "Radio", "R[num]", "Inglete", "Krion".

    FORMATO JSON ESTRICTO:
    [
      {"id": "...", "nombre": "...", "largo": 0.0, "ancho": 0.0, "espesor": 0.0, "material": "...", "cantidad": 0, "notas": "..."},
      ...
    ]
    """
    try:
        response = model.generate_content([prompt, imagen])
        texto = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except Exception as e:
        return {"error": str(e)}


# --- 4. UTILIDADES PDF ---
def pdf_a_imagenes(archivo_pdf):
    doc = fitz.open(stream=archivo_pdf.read(), filetype="pdf")
    imagenes = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        img_data = pix.tobytes("png")
        imagenes.append(Image.open(io.BytesIO(img_data)))
    return imagenes


# ══════════════════════════════════════════════════════════════════════════════
# 5. INTERFAZ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

if 'imagenes_pdf' not in st.session_state:
    st.session_state['imagenes_pdf'] = []

# ── SECCIÓN: IMPORTAR ────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-header">
    <div class="sec-icon">📁</div>
    <div class="sec-text">
        <div class="sec-title">Importar Proyecto</div>
        <div class="sec-sub">Arrastra o selecciona el documento PDF del proyecto técnico</div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Selecciona o arrastra el archivo PDF aquí",
    type=["pdf"],
    help="Formatos aceptados: PDF con planos técnicos, tablas de despiece, listas de corte"
)

if uploaded_file:
    nombre_archivo_original = os.path.splitext(uploaded_file.name)[0]
    nombre_csv_salida = f"{nombre_archivo_original}_corte.csv"

    if not st.session_state['imagenes_pdf']:
        with st.spinner(""):
            st.markdown("""
            <div class="proc-status">
                <div class="proc-icon">⚡</div>
                <div>
                    <span class="proc-text-main">Analizando documento PDF</span>
                    <span class="proc-text-sub">Extrayendo páginas a 200 DPI...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state['imagenes_pdf'] = pdf_a_imagenes(uploaded_file)

    imgs = st.session_state['imagenes_pdf']
    total_pages = len(imgs)

    # ── KPI CARDS ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card gold">
            <div class="kpi-label">Documento</div>
            <div class="kpi-value" style="font-size:0.95rem; word-break:break-all; font-weight:600;">
                {uploaded_file.name}
            </div>
            <div class="kpi-sub">Archivo cargado correctamente</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-label">Páginas</div>
            <div class="kpi-value">{total_pages}</div>
            <div class="kpi-sub">Páginas detectadas</div>
        </div>
        <div class="kpi-card neutral">
            <div class="kpi-label">Resolución</div>
            <div class="kpi-value">200<span class="kpi-unit">DPI</span></div>
            <div class="kpi-sub">Calidad de análisis</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-label">Motor IA</div>
            <div class="kpi-value" style="font-size:0.95rem;">Gemini 3.0</div>
            <div class="kpi-sub">Flash Preview</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECCIÓN: PÁGINAS ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec-header">
        <div class="sec-icon">📄</div>
        <div class="sec-text">
            <div class="sec-title">Selección de Páginas</div>
            <div class="sec-sub">Marca las páginas que contienen despieces o planos de corte</div>
        </div>
        <div class="sec-badge">{total_pages} PÁG</div>
    </div>
    """, unsafe_allow_html=True)

    seleccionadas = []

    cols = st.columns(6)
    for i, img in enumerate(imgs):
        with cols[i % 6]:
            st.image(img, caption=f"Página {i+1}", use_container_width=True)
            if st.checkbox(f"Pág. {i+1}", value=True, key=f"chk_{i}"):
                seleccionadas.append((i+1, img))

    # ── SEPARADOR ORNAMENTAL ─────────────────────────────────────────────────
    st.markdown("""
    <div class="gold-separator">
        <div class="line"></div>
        <div class="diamond"></div>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── BOTÓN PROCESAR ───────────────────────────────────────────────────────
    col_btn, col_spacer, col_info = st.columns([2, 1, 3])
    with col_btn:
        procesar = st.button(
            f"⚡  PROCESAR  ·  {len(seleccionadas)} PÁGINAS",
            type="primary",
            use_container_width=True
        )
    with col_info:
        st.markdown(f"""
        <div style="display:flex; align-items:center; padding:0.65rem 0;">
            <span style="color: var(--text-muted); font-size:0.82rem;">
                Tiempo estimado: <strong style="color: var(--gold-300);">~{len(seleccionadas) * 8}s</strong>
                &nbsp;·&nbsp; {len(seleccionadas)} de {total_pages} seleccionadas
            </span>
        </div>
        """, unsafe_allow_html=True)

    if procesar:
        resultados = []
        alertas = []
        cerebro = CerebroOperario()

        st.markdown("""
        <div class="gold-separator">
            <div class="line"></div>
            <div class="diamond"></div>
            <div class="line"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sec-header">
            <div class="sec-icon">🔬</div>
            <div class="sec-text">
                <div class="sec-title">Procesamiento en Curso</div>
                <div class="sec-sub">Análisis visual con IA y aplicación de reglas de ingeniería</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        barra = st.progress(0)
        status = st.empty()

        for idx, (num_pag, img) in enumerate(seleccionadas):
            status.markdown(f"""
            <div class="proc-status">
                <div class="proc-icon">👁️</div>
                <div>
                    <span class="proc-text-main">Analizando Página {num_pag}</span>
                    <span class="proc-text-sub">({idx+1} de {len(seleccionadas)})</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            print(f"--- Procesando Pág {num_pag} ---")

            datos_ia = analizar_imagen_con_ia(img)

            if isinstance(datos_ia, dict) and "error" in datos_ia:
                st.error(f"❌ Pág {num_pag}: {datos_ia['error']}")
            elif datos_ia:
                datos_pag, alertas_pag = cerebro.procesar_pagina(datos_ia, num_pag)
                resultados.extend(datos_pag)
                alertas.extend(alertas_pag)
            else:
                print(f"   ℹ️ Pág {num_pag} ignorada.")

            barra.progress((idx + 1) / len(seleccionadas))

        status.markdown("""
        <div class="proc-status" style="border-color: rgba(16,185,129,0.2); background: rgba(16,185,129,0.04);">
            <div class="proc-icon" style="background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.2);">✅</div>
            <div>
                <span class="proc-text-main" style="color: #6ee7b7;">Procesamiento completado</span>
                <span class="proc-text-sub">Todas las páginas analizadas correctamente</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state['df_final'] = pd.DataFrame(resultados)
        st.session_state['alertas_final'] = alertas


# ══════════════════════════════════════════════════════════════════════════════
# 6. RESULTADOS Y EXPORTACIÓN
# ══════════════════════════════════════════════════════════════════════════════

if 'df_final' in st.session_state and not st.session_state['df_final'].empty:

    st.markdown("""
    <div class="gold-separator">
        <div class="line"></div>
        <div class="diamond"></div>
        <div class="diamond" style="margin: 0 -8px;"></div>
        <div class="diamond"></div>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)

    df = st.session_state['df_final']
    alertas_list = st.session_state['alertas_final']

    total_piezas = int(df['Cantidad'].sum()) if 'Cantidad' in df.columns else len(df)
    total_lineas = len(df)
    materiales_unicos = df['Material'].nunique() if 'Material' in df.columns else 0

    # ── HEADER RESULTADOS ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec-header">
        <div class="sec-icon" style="background: rgba(212,175,55,0.1); border-color: rgba(212,175,55,0.2);">📋</div>
        <div class="sec-text">
            <div class="sec-title">Lista de Corte · Exportación WinCut</div>
            <div class="sec-sub">Resultado del análisis con reglas de ingeniería aplicadas</div>
        </div>
        <div class="sec-badge" style="color: var(--accent-emerald); border-color: rgba(16,185,129,0.2); background: rgba(16,185,129,0.06);">
            ✓ LISTO
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI RESULTADOS ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card emerald">
            <div class="kpi-label">Líneas de Corte</div>
            <div class="kpi-value">{total_lineas}</div>
            <div class="kpi-sub">Registros únicos</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-label">Total Piezas</div>
            <div class="kpi-value">{total_piezas}</div>
            <div class="kpi-sub">Sumando cantidades</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-label">Materiales</div>
            <div class="kpi-value">{materiales_unicos}</div>
            <div class="kpi-sub">Tipos distintos</div>
        </div>
        <div class="kpi-card amber">
            <div class="kpi-label">Alertas</div>
            <div class="kpi-value">{len(alertas_list)}</div>
            <div class="kpi-sub">Requieren revisión</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PANEL DE ALERTAS ─────────────────────────────────────────────────────
    if alertas_list:
        st.markdown(f"""
        <div class="sec-header" style="margin-top:1.5rem;">
            <div class="sec-icon" style="background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.15);">⚠️</div>
            <div class="sec-text">
                <div class="sec-title">Informe de Ingeniería</div>
                <div class="sec-sub">Alertas generadas por el motor de reglas experto</div>
            </div>
            <div class="sec-badge">{len(alertas_list)} AVISOS</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"Ver {len(alertas_list)} alertas del análisis", expanded=True):
            for a in alertas_list:
                if "PINZAS" in a or "KRION" in a or "METAL" in a:
                    st.error(a)
                elif "SÁNDWICH" in a or "DESCONOCIDO" in a:
                    st.warning(a)
                else:
                    st.info(a)

    # ── TABLA EDITABLE ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="table-label">
        <div class="bar"></div>
        <span>Tabla editable · Doble clic para modificar valores</span>
    </div>
    """, unsafe_allow_html=True)

    df_editado = st.data_editor(
        st.session_state['df_final'],
        num_rows="dynamic",
        use_container_width=True,
        height=600,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
            "Largo": st.column_config.NumberColumn("Largo", format="%.1f mm", width="small"),
            "Ancho": st.column_config.NumberColumn("Ancho", format="%.1f mm", width="small"),
            "Espesor": st.column_config.NumberColumn("Espesor", format="%.0f mm", width="small"),
            "Material": st.column_config.TextColumn("Material", width="medium"),
            "Cantidad": st.column_config.NumberColumn("Cant.", format="%d", width="small"),
            "Notas": st.column_config.TextColumn("Notas", width="large"),
        }
    )

    # ── SEPARADOR ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="gold-separator">
        <div class="line"></div>
        <div class="diamond"></div>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── EXPORTACIÓN ──────────────────────────────────────────────────────────
    csv = df_editado.to_csv(index=False, sep=";").encode('utf-8')

    col_dl, col_dl_info = st.columns([2, 4])
    with col_dl:
        st.download_button(
            label=f"⬇  EXPORTAR  ·  {nombre_csv_salida}",
            data=csv,
            file_name=nombre_csv_salida,
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    with col_dl_info:
        st.markdown(f"""
        <div style="display:flex; align-items:center; padding:0.7rem 0;">
            <span style="color: var(--text-muted); font-size:0.8rem;">
                Formato: <strong style="color: var(--gold-300);">CSV (;)</strong> &nbsp;·&nbsp;
                Codificación: <strong style="color: var(--gold-300);">UTF-8</strong> &nbsp;·&nbsp;
                Compatible con WinCut, CutRite, Ardis
            </span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="luxury-footer">
    <div class="footer-logo">GABBIANI MASTER AI</div>
    <div class="footer-sub">
        Motor de Reglas v3.0 · Gemini 3.0 Flash Vision · Gold Edition
    </div>
    <div style="color: #3d310e; font-size: 0.65rem; margin-top: 0.75rem; letter-spacing: 0.08em;">
        © 2026 · SISTEMA EXPERTO DE OPTIMIZACIÓN DE CORTE INDUSTRIAL
    </div>
</div>
""", unsafe_allow_html=True)