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
    page_icon="🔷",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS PROFESIONAL · CORPORATE BLUE & WHITE EDITION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-body: #f0f2f5;
    --bg-white: #ffffff;
    --bg-card: #ffffff;
    --bg-card-hover: #f8fafc;
    --bg-elevated: #f8f9fb;
    --bg-input: #f5f6f8;
    --bg-sidebar: #1e293b;
    --bg-header: #0f172a;
    --bg-header-gradient: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #1a4b8c 100%);

    --border-light: #e2e8f0;
    --border-medium: #cbd5e1;
    --border-strong: #94a3b8;
    --border-focus: #2563eb;

    --blue-50: #eff6ff;
    --blue-100: #dbeafe;
    --blue-200: #bfdbfe;
    --blue-300: #93c5fd;
    --blue-400: #60a5fa;
    --blue-500: #3b82f6;
    --blue-600: #2563eb;
    --blue-700: #1d4ed8;
    --blue-800: #1e40af;
    --blue-900: #1e3a5f;

    --gray-50: #f8fafc;
    --gray-100: #f1f5f9;
    --gray-200: #e2e8f0;
    --gray-300: #cbd5e1;
    --gray-400: #94a3b8;
    --gray-500: #64748b;
    --gray-600: #475569;
    --gray-700: #334155;
    --gray-800: #1e293b;
    --gray-900: #0f172a;

    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --text-blue: #2563eb;
    --text-white: #ffffff;

    --accent-emerald: #059669;
    --accent-emerald-light: #d1fae5;
    --accent-red: #dc2626;
    --accent-red-light: #fee2e2;
    --accent-amber: #d97706;
    --accent-amber-light: #fef3c7;
    --accent-blue-light: #dbeafe;

    --gradient-blue: linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #60a5fa 100%);
    --gradient-header: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1a4b8c 100%);
    --gradient-subtle: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);

    --shadow-xs: 0 1px 2px rgba(0,0,0,0.04);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
    --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.03);
    --shadow-blue: 0 4px 14px rgba(37,99,235,0.18);
    --shadow-blue-lg: 0 8px 25px rgba(37,99,235,0.22);

    --radius-xs: 6px;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-2xl: 24px;
}

/* ── GLOBAL ── */
.stApp {
    background: var(--bg-body) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stApp > header { background: transparent !important; }

.main .block-container {
    padding: 1.5rem 3rem 4rem 3rem !important;
    max-width: 1440px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--gray-100); }
::-webkit-scrollbar-thumb {
    background: var(--gray-300);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: var(--gray-400); }

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
    margin: -0.5rem -1rem 2rem -1rem;
    border-radius: var(--radius-xl);
    overflow: hidden;
    background: var(--bg-white);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-lg);
}

.hero-blue-line {
    height: 4px;
    background: var(--gradient-blue);
}

.hero-content {
    padding: 2rem 2.5rem 1.8rem 2.5rem;
    position: relative;
    background: var(--bg-white);
}

.hero-content::after {
    content: '';
    position: absolute;
    top: -50%; right: -15%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(37,99,235,0.03) 0%, transparent 65%);
    pointer-events: none;
}

.hero-mono-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--blue-600);
    margin-bottom: 1rem;
    padding: 5px 14px;
    background: var(--blue-50);
    border: 1px solid var(--blue-100);
    border-radius: 100px;
}

.hero-mono-tag .tag-dot {
    width: 6px; height: 6px;
    background: var(--blue-500);
    border-radius: 50%;
    animation: pulse-blue 2.5s ease-in-out infinite;
    box-shadow: 0 0 6px rgba(37,99,235,0.5);
}

@keyframes pulse-blue {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px rgba(37,99,235,0.5); }
    50% { opacity: 0.3; box-shadow: 0 0 3px rgba(37,99,235,0.2); }
}

.hero-title-line {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0.5rem;
}

.hero-brand {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.03em !important;
    line-height: 1 !important;
    margin: 0 !important;
    color: var(--gray-900) !important;
}

.hero-brand .blue {
    color: var(--blue-600);
}

.hero-edition {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    color: var(--gray-500);
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border: 1px solid var(--border-light);
    border-radius: 4px;
    background: var(--gray-50);
}

.hero-desc {
    font-size: 0.92rem;
    color: var(--text-secondary);
    line-height: 1.65;
    margin: 0 0 1.25rem 0;
    max-width: 720px;
}

.hero-status-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border-light);
    flex-wrap: wrap;
}

.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.chip-online {
    background: var(--accent-emerald-light);
    border: 1px solid rgba(5,150,105,0.2);
    color: var(--accent-emerald);
}

.chip-blue {
    background: var(--blue-50);
    border: 1px solid var(--blue-100);
    color: var(--blue-700);
}

.chip-neutral {
    background: var(--gray-50);
    border: 1px solid var(--border-light);
    color: var(--gray-500);
}

.chip-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
}

.chip-dot.green {
    background: var(--accent-emerald);
    box-shadow: 0 0 5px rgba(5,150,105,0.4);
    animation: pulse-green 2s ease-in-out infinite;
}

@keyframes pulse-green {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
}

.chip-dot.blue {
    background: var(--blue-500);
    box-shadow: 0 0 5px rgba(37,99,235,0.3);
}

/* ══════════════════════════════════════════════════════════════
   SECTION HEADERS
   ══════════════════════════════════════════════════════════════ */
.sec-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 2rem 0 1.25rem 0;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-light);
    position: relative;
}

.sec-header::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 50px;
    height: 2px;
    background: var(--gradient-blue);
    border-radius: 2px;
}

.sec-icon {
    width: 40px; height: 40px;
    display: flex; align-items: center; justify-content: center;
    background: var(--blue-50);
    border: 1px solid var(--blue-100);
    border-radius: var(--radius-sm);
    font-size: 17px;
    flex-shrink: 0;
    color: var(--blue-600);
}

.sec-text .sec-title {
    font-size: 1.05rem !important;
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
    background: var(--gray-50);
    border: 1px solid var(--border-light);
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    color: var(--gray-500);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em;
}

/* ══════════════════════════════════════════════════════════════
   METRIC / KPI CARDS
   ══════════════════════════════════════════════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.25rem 0;
}

.kpi-card {
    position: relative;
    padding: 1.3rem 1.4rem;
    background: var(--bg-white);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-xs);
}

.kpi-card:hover {
    border-color: var(--border-medium);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}

.kpi-card.blue::before { background: var(--gradient-blue); }
.kpi-card.emerald::before { background: linear-gradient(90deg, #059669, #10b981, #34d399); }
.kpi-card.neutral::before { background: linear-gradient(90deg, #94a3b8, #cbd5e1); }
.kpi-card.amber::before { background: linear-gradient(90deg, #d97706, #f59e0b, #fbbf24); }

.kpi-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.03em;
    line-height: 1;
}

.kpi-unit {
    font-size: 0.78rem;
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
   FILE UPLOADER · TRADUCIDO + ESTILIZADO
   ══════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    background: var(--bg-white) !important;
    border: 2px dashed var(--border-medium) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow-xs) !important;
}

[data-testid="stFileUploader"] > div:hover {
    border-color: var(--blue-400) !important;
    background: var(--blue-50) !important;
    box-shadow: var(--shadow-blue) !important;
}

[data-testid="stFileUploader"] label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
}

/* ── Traducir "Drag and drop file here" ── */
[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] p {
    font-size: 0px !important;
    line-height: 0 !important;
    color: transparent !important;
}

[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] p::after {
    content: 'Arrastra y suelta el archivo aquí' !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Traducir "Limit 200MB per file • PDF" ── */
[data-testid="stFileUploaderDropzone"] > div > span {
    font-size: 0px !important;
    color: transparent !important;
}

[data-testid="stFileUploaderDropzone"] > div > span::after {
    content: 'Límite 200MB por archivo · PDF' !important;
    font-size: 0.75rem !important;
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    letter-spacing: 0.01em !important;
}

/* ── Traducir botón "Browse files" ── */
[data-testid="stFileUploaderDropzone"] button {
    font-size: 0px !important;
    color: transparent !important;
    background: var(--blue-50) !important;
    border: 1px solid var(--blue-200) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 1.5rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    min-height: 38px !important;
    position: relative !important;
}

[data-testid="stFileUploaderDropzone"] button::after {
    content: 'Seleccionar archivo' !important;
    font-size: 0.82rem !important;
    color: var(--blue-700) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background: var(--blue-100) !important;
    border-color: var(--blue-400) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Icono de subida visible ── */
[data-testid="stFileUploaderDropzone"] svg {
    color: var(--blue-400) !important;
    stroke: var(--blue-400) !important;
    opacity: 0.8 !important;
}

/* ── Archivo subido (chip con nombre) ── */
[data-testid="stFileUploaderFile"] {
    background: var(--blue-50) !important;
    border: 1px solid var(--blue-100) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.4rem 0.8rem !important;
}

[data-testid="stFileUploaderFile"] span {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}

[data-testid="stFileUploaderFile"] button {
    color: var(--accent-red) !important;
    font-size: 0.85rem !important;
    min-height: auto !important;
    background: transparent !important;
    border: none !important;
    padding: 0.2rem !important;
}

[data-testid="stFileUploaderFile"] button::after {
    content: '' !important;
    display: none !important;
}

/* ══════════════════════════════════════════════════════════════
   THUMBNAILS / PAGE GRID
   ══════════════════════════════════════════════════════════════ */
[data-testid="stImage"] {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    border: 1px solid var(--border-light) !important;
    transition: all 0.25s ease !important;
    background: var(--bg-white) !important;
    box-shadow: var(--shadow-xs) !important;
}

[data-testid="stImage"]:hover {
    border-color: var(--blue-400) !important;
    box-shadow: var(--shadow-blue) !important;
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
    color: var(--text-blue) !important;
}

/* ══════════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════════ */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.7rem 2rem !important;
    transition: all 0.2s ease !important;
    border: none !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--gradient-blue) !important;
    color: var(--text-white) !important;
    box-shadow: var(--shadow-blue) !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    box-shadow: var(--shadow-blue-lg) !important;
    transform: translateY(-2px) !important;
    filter: brightness(1.08) !important;
}

.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="baseButton-primary"]:active {
    transform: translateY(0) !important;
    filter: brightness(0.95) !important;
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background: var(--bg-white) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: var(--blue-400) !important;
    background: var(--blue-50) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ══════════════════════════════════════════════════════════════
   DOWNLOAD BUTTON
   ══════════════════════════════════════════════════════════════ */
.stDownloadButton > button {
    background: var(--gradient-blue) !important;
    color: var(--text-white) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.8rem 2.5rem !important;
    border: none !important;
    box-shadow: var(--shadow-blue) !important;
    font-size: 0.88rem !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover {
    box-shadow: var(--shadow-blue-lg) !important;
    transform: translateY(-2px) !important;
    filter: brightness(1.08) !important;
}

/* ══════════════════════════════════════════════════════════════
   DATA TABLE
   ══════════════════════════════════════════════════════════════ */
[data-testid="stDataEditor"],
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-md) !important;
    background: var(--bg-white) !important;
}

[data-testid="stDataEditor"] [role="gridcell"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ══════════════════════════════════════════════════════════════
   ALERTS & EXPANDER  (FIXED ARROW ICON)
   ══════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--bg-white) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
    box-shadow: var(--shadow-sm) !important;
}

[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    padding: 1rem 1.25rem !important;
    cursor: pointer;
}

/* ── FIX: Ocultar texto "arrow" del marker nativo ── */
[data-testid="stExpander"] summary::marker,
[data-testid="stExpander"] summary::-webkit-details-marker {
    display: none !important;
    content: '' !important;
    font-size: 0 !important;
    color: transparent !important;
}

/* ── FIX: Asegurar que el SVG del toggle se muestre ── */
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] svg {
    display: inline-block !important;
    visibility: visible !important;
    width: 1rem !important;
    height: 1rem !important;
    fill: var(--text-muted) !important;
    stroke: var(--text-muted) !important;
    flex-shrink: 0 !important;
}

[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0 !important;
    line-height: 0 !important;
    overflow: hidden !important;
}

/* ── FIX: Si Streamlit usa texto como fallback del icono ── */
[data-testid="stExpander"] summary > span[data-testid="stExpanderToggleIcon"] {
    font-size: 0px !important;
    color: transparent !important;
}

[data-testid="stExpander"] summary > span[data-testid="stExpanderToggleIcon"] svg {
    font-size: 1rem !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    border-top: 1px solid var(--border-light) !important;
}

[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
    padding: 0.8rem 1rem !important;
    border-left-width: 3px !important;
    font-family: 'Inter', sans-serif !important;
}

/* ══════════════════════════════════════════════════════════════
   PROGRESS BAR
   ══════════════════════════════════════════════════════════════ */
.stProgress > div > div {
    background: var(--gradient-blue) !important;
    border-radius: 100px !important;
    box-shadow: 0 0 10px rgba(37,99,235,0.3) !important;
}

.stProgress > div {
    background: var(--gray-100) !important;
    border-radius: 100px !important;
    border: 1px solid var(--border-light) !important;
}

/* ══════════════════════════════════════════════════════════════
   DIVIDER
   ══════════════════════════════════════════════════════════════ */
hr {
    border-color: var(--border-light) !important;
    margin: 2rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════
   SUCCESS / INFO / WARNING / ERROR
   ══════════════════════════════════════════════════════════════ */
.element-container .stSuccess {
    background: var(--accent-emerald-light) !important;
    border-left-color: var(--accent-emerald) !important;
}

.element-container .stInfo {
    background: var(--blue-50) !important;
    border-left-color: var(--blue-500) !important;
}

.element-container .stWarning {
    background: var(--accent-amber-light) !important;
    border-left-color: var(--accent-amber) !important;
}

.element-container .stError {
    background: var(--accent-red-light) !important;
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
.section-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem 0;
}

.section-divider .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-light), transparent);
}

.section-divider .dot {
    width: 6px; height: 6px;
    background: var(--blue-300);
    border-radius: 50%;
    flex-shrink: 0;
    opacity: 0.6;
}

/* ══════════════════════════════════════════════════════════════
   CUSTOM FOOTER
   ══════════════════════════════════════════════════════════════ */
.corp-footer {
    margin-top: 4rem;
    padding: 2rem 0 1rem 0;
    text-align: center;
    position: relative;
}

.corp-footer::before {
    content: '';
    position: absolute;
    top: 0; left: 15%; right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-light), transparent);
}

.footer-logo-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 800;
    color: var(--blue-700);
    letter-spacing: -0.01em;
    margin-bottom: 0.3rem;
}

.footer-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.04em;
}

.footer-copy {
    color: var(--gray-300);
    font-size: 0.62rem;
    margin-top: 0.6rem;
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
    background: var(--bg-white);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    margin: 0.5rem 0;
    box-shadow: var(--shadow-xs);
}

.proc-icon {
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    background: var(--blue-50);
    border: 1px solid var(--blue-100);
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
    background: var(--gradient-blue);
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
   SHIELD / TRUST BADGE
   ══════════════════════════════════════════════════════════════ */
.trust-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    padding: 0.6rem 1rem;
    background: var(--gray-50);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    margin: 1rem 0 0.5rem 0;
}

.trust-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--gray-500);
    letter-spacing: 0.02em;
}

.trust-item .t-icon {
    font-size: 13px;
    color: var(--blue-500);
}

/* ══════════════════════════════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem !important; }
    .hero-brand { font-size: 1.5rem !important; }
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    .hero-content { padding: 1.5rem !important; }
    .trust-bar { flex-direction: column; gap: 0.5rem; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-blue-line"></div>
    <div class="hero-content">
        <div class="hero-mono-tag">
            <span class="tag-dot"></span>
            SISTEMA EXPERTO DE CORTE INDUSTRIAL · v3.0
        </div>
        <div class="hero-title-line">
            <h1 class="hero-brand">
                GABBIANI <span class="blue">MASTER AI</span>
            </h1>
            <span class="hero-edition">PRO</span>
        </div>
        <p class="hero-desc">
            Plataforma de extracción automática de despieces con inteligencia artificial y motor de reglas de ingeniería.
            Análisis visual por Gemini 3.0 Flash · Validación experta · Exportación directa a optimizador.
        </p>
        <div class="hero-status-row">
            <div class="status-chip chip-online">
                <span class="chip-dot green"></span>
                Sistema Operativo
            </div>
            <div class="status-chip chip-blue">
                <span class="chip-dot blue"></span>
                Gemini 3.0 Flash
            </div>
            <div class="status-chip chip-neutral">
                🕐 {datetime.now().strftime("%d/%m/%Y · %H:%M")}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TRUST BAR ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="trust-bar">
    <div class="trust-item"><span class="t-icon">🛡️</span> Procesamiento seguro</div>
    <div class="trust-item"><span class="t-icon">🔒</span> Datos no almacenados</div>
    <div class="trust-item"><span class="t-icon">✅</span> Validación por reglas de ingeniería</div>
    <div class="trust-item"><span class="t-icon">📐</span> Precisión industrial</div>
</div>
""", unsafe_allow_html=True)


# ── API KEY ──────────────────────────────────────────────────────────────────
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.markdown("""
    <div style="background: #fee2e2; border: 1px solid #fecaca;
                border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0;
                border-left: 3px solid #dc2626;">
        <div style="font-size: 1rem; font-weight: 700; color: #991b1b; margin-bottom: 0.4rem;">
            ⛔ Error Crítico de Configuración
        </div>
        <div style="color: #475569; font-size: 0.88rem;">
            No se encontró la clave API en
            <code style="background: #f1f5f9; padding: 2px 8px; border-radius: 4px;
                         color: #1e40af; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;">
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
                notas += f" | ⚠ RECORTAR A {medida_real} MANUAL"
                alertas.append(f"🚨 {nombre}: PINZAS! Ancho {medida_real} peligroso. Cortar tira ancha.")

            if largo > self.LARGO_MAXIMO_TABLERO:
                alertas.append(f"📏 {nombre}: Largo {largo}mm excede estándar.")

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
                <div class="proc-icon">📄</div>
                <div>
                    <span class="proc-text-main">Procesando documento PDF</span>
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
        <div class="kpi-card blue">
            <div class="kpi-label">Documento</div>
            <div class="kpi-value" style="font-size:0.92rem; word-break:break-all; font-weight:600;">
                {uploaded_file.name}
            </div>
            <div class="kpi-sub">Archivo cargado correctamente</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Páginas Detectadas</div>
            <div class="kpi-value">{total_pages}</div>
            <div class="kpi-sub">Disponibles para análisis</div>
        </div>
        <div class="kpi-card neutral">
            <div class="kpi-label">Resolución</div>
            <div class="kpi-value">200<span class="kpi-unit">DPI</span></div>
            <div class="kpi-sub">Calidad de extracción</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Motor IA</div>
            <div class="kpi-value" style="font-size:0.92rem;">Gemini 3.0</div>
            <div class="kpi-sub">Flash Preview</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECCIÓN: PÁGINAS ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sec-header">
        <div class="sec-icon">📑</div>
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

    # ── SEPARADOR ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-divider">
        <div class="line"></div>
        <div class="dot"></div>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── BOTÓN PROCESAR ───────────────────────────────────────────────────────
    col_btn, col_spacer, col_info = st.columns([2, 1, 3])
    with col_btn:
        procesar = st.button(
            f"▶  ANALIZAR  ·  {len(seleccionadas)} PÁGINAS",
            type="primary",
            use_container_width=True
        )
    with col_info:
        st.markdown(f"""
        <div style="display:flex; align-items:center; padding:0.65rem 0;">
            <span style="color: #94a3b8; font-size:0.82rem;">
                Tiempo estimado: <strong style="color: #2563eb;">~{len(seleccionadas) * 8}s</strong>
                &nbsp;·&nbsp; {len(seleccionadas)} de {total_pages} seleccionadas
            </span>
        </div>
        """, unsafe_allow_html=True)

    if procesar:
        resultados = []
        alertas = []
        cerebro = CerebroOperario()

        st.markdown("""
        <div class="section-divider">
            <div class="line"></div>
            <div class="dot"></div>
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
                <div class="proc-icon">🔍</div>
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
        <div class="proc-status" style="border-color: #a7f3d0; background: #ecfdf5;">
            <div class="proc-icon" style="background: #d1fae5; border-color: #a7f3d0;">✅</div>
            <div>
                <span class="proc-text-main" style="color: #065f46;">Procesamiento completado</span>
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
    <div class="section-divider">
        <div class="line"></div>
        <div class="dot"></div>
        <div class="dot" style="margin: 0 -4px;"></div>
        <div class="dot"></div>
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
        <div class="sec-icon">📋</div>
        <div class="sec-text">
            <div class="sec-title">Lista de Corte · Exportación WinCut</div>
            <div class="sec-sub">Resultado del análisis con reglas de ingeniería aplicadas</div>
        </div>
        <div class="sec-badge" style="color: #059669; border-color: #a7f3d0; background: #ecfdf5;">
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
        <div class="kpi-card blue">
            <div class="kpi-label">Total Piezas</div>
            <div class="kpi-value">{total_piezas}</div>
            <div class="kpi-sub">Sumando cantidades</div>
        </div>
        <div class="kpi-card blue">
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
            <div class="sec-icon" style="background: #fef3c7; border-color: #fde68a;">⚠️</div>
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
    <div class="section-divider">
        <div class="line"></div>
        <div class="dot"></div>
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
            <span style="color: #94a3b8; font-size:0.8rem;">
                Formato: <strong style="color: #2563eb;">CSV (;)</strong> &nbsp;·&nbsp;
                Codificación: <strong style="color: #2563eb;">UTF-8</strong> &nbsp;·&nbsp;
                Compatible con WinCut, CutRite, Ardis
            </span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="corp-footer">
    <div class="footer-logo-text">GABBIANI MASTER AI</div>
    <div class="footer-sub">
        Motor de Reglas v3.0 · Gemini 3.0 Flash Vision · Edición Profesional
    </div>
    <div class="footer-copy">
        © 2026 · SISTEMA EXPERTO DE OPTIMIZACIÓN DE CORTE INDUSTRIAL
    </div>
</div>
""", unsafe_allow_html=True)
