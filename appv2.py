import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd
import fitz  # PyMuPDF
import io
import json
import re
import os
import hashlib
import time
import logging
import typing_extensions as typing
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="GABBIANI MASTER AI v6", layout="wide",
                   page_icon="🔷", initial_sidebar_state="collapsed")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("GABBIANI")

BACKEND = st.secrets.get("BACKEND", "google_ai")
GEMINI_MODEL = st.secrets.get("GEMINI_MODEL", "gemini-2.5-pro-preview-06-05")
MAX_WORKERS = int(st.secrets.get("MAX_WORKERS", 5))
MAX_TEXTO_VECTORIAL = 5000

# ══════════════════════════════════════════════════════════════════════════════
# 2. CSS COMPLETO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
:root{
--bg-body:#f0f2f5;--bg-white:#fff;--border-light:#e2e8f0;--border-medium:#cbd5e1;
--blue-50:#eff6ff;--blue-100:#dbeafe;--blue-200:#bfdbfe;--blue-300:#93c5fd;
--blue-400:#60a5fa;--blue-500:#3b82f6;--blue-600:#2563eb;--blue-700:#1d4ed8;
--blue-800:#1e40af;--blue-900:#1e3a5f;
--gray-50:#f8fafc;--gray-100:#f1f5f9;--gray-200:#e2e8f0;--gray-300:#cbd5e1;
--gray-400:#94a3b8;--gray-500:#64748b;--gray-600:#475569;--gray-700:#334155;
--gray-800:#1e293b;--gray-900:#0f172a;
--text-primary:#0f172a;--text-secondary:#475569;--text-muted:#94a3b8;
--text-blue:#2563eb;--text-white:#fff;
--accent-emerald:#059669;--accent-emerald-light:#d1fae5;
--accent-red:#dc2626;--accent-red-light:#fee2e2;
--accent-amber:#d97706;--accent-amber-light:#fef3c7;
--gradient-blue:linear-gradient(135deg,#2563eb 0%,#3b82f6 50%,#60a5fa 100%);
--shadow-sm:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
--shadow-md:0 4px 6px -1px rgba(0,0,0,.07),0 2px 4px -1px rgba(0,0,0,.04);
--shadow-lg:0 10px 15px -3px rgba(0,0,0,.08),0 4px 6px -2px rgba(0,0,0,.04);
--shadow-blue:0 4px 14px rgba(37,99,235,.18);
--shadow-blue-lg:0 8px 25px rgba(37,99,235,.22);
--radius-sm:8px;--radius-md:12px;--radius-xl:20px;
}
.stApp{background:var(--bg-body)!important;font-family:'Inter',sans-serif!important}
.stApp>header{background:transparent!important}
.main .block-container{padding:1.5rem 3rem 4rem!important;max-width:1440px!important}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--gray-100)}
::-webkit-scrollbar-thumb{background:var(--gray-300);border-radius:10px}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;visibility:hidden!important}
h1,h2,h3,h4,h5,h6{font-family:'Inter',sans-serif!important;color:var(--text-primary)!important;letter-spacing:-.02em!important}
.hero-wrapper{position:relative;margin:-.5rem -1rem 2rem;border-radius:var(--radius-xl);overflow:hidden;background:var(--bg-white);border:1px solid var(--border-light);box-shadow:var(--shadow-lg)}
.hero-blue-line{height:4px;background:var(--gradient-blue)}
.hero-content{padding:2rem 2.5rem 1.8rem;background:var(--bg-white)}
.hero-content::after{content:'';position:absolute;top:-50%;right:-15%;width:500px;height:500px;background:radial-gradient(circle,rgba(37,99,235,.03) 0%,transparent 65%);pointer-events:none}
.hero-mono-tag{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--blue-600);margin-bottom:1rem;padding:5px 14px;background:var(--blue-50);border:1px solid var(--blue-100);border-radius:100px}
.hero-mono-tag .tag-dot{width:6px;height:6px;background:var(--blue-500);border-radius:50%;animation:pblu 2.5s ease-in-out infinite;box-shadow:0 0 6px rgba(37,99,235,.5)}
@keyframes pblu{0%,100%{opacity:1}50%{opacity:.3}}
.hero-title-line{display:flex;align-items:center;gap:16px;margin-bottom:.5rem}
.hero-brand{font-size:2.2rem!important;font-weight:900!important;letter-spacing:-.03em!important;line-height:1!important;margin:0!important;color:var(--gray-900)!important}
.hero-brand .blue{color:var(--blue-600)}
.hero-edition{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;color:var(--gray-500);letter-spacing:.06em;padding:3px 10px;border:1px solid var(--border-light);border-radius:4px;background:var(--gray-50)}
.hero-desc{font-size:.92rem;color:var(--text-secondary);line-height:1.65;margin:0 0 1.25rem;max-width:720px}
.hero-status-row{display:flex;align-items:center;gap:1rem;padding-top:1.25rem;border-top:1px solid var(--border-light);flex-wrap:wrap}
.status-chip{display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:100px;font-size:11px;font-weight:600}
.chip-online{background:var(--accent-emerald-light);border:1px solid rgba(5,150,105,.2);color:var(--accent-emerald)}
.chip-blue{background:var(--blue-50);border:1px solid var(--blue-100);color:var(--blue-700)}
.chip-neutral{background:var(--gray-50);border:1px solid var(--border-light);color:var(--gray-500)}
.chip-dot{width:6px;height:6px;border-radius:50%}
.chip-dot.green{background:var(--accent-emerald);box-shadow:0 0 5px rgba(5,150,105,.4);animation:pg 2s ease-in-out infinite}
.chip-dot.blue{background:var(--blue-500)}
@keyframes pg{0%,100%{opacity:1}50%{opacity:.35}}
.sec-header{display:flex;align-items:center;gap:14px;margin:2rem 0 1.25rem;padding-bottom:1rem;border-bottom:1px solid var(--border-light);position:relative}
.sec-header::after{content:'';position:absolute;bottom:-1px;left:0;width:50px;height:2px;background:var(--gradient-blue);border-radius:2px}
.sec-icon{width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:var(--blue-50);border:1px solid var(--blue-100);border-radius:var(--radius-sm);font-size:17px;flex-shrink:0}
.sec-text .sec-title{font-size:1.05rem!important;font-weight:700!important;color:var(--text-primary)!important;margin:0!important}
.sec-text .sec-sub{font-size:.78rem;color:var(--text-muted);margin-top:2px}
.sec-badge{margin-left:auto;padding:4px 14px;background:var(--gray-50);border:1px solid var(--border-light);border-radius:100px;font-size:11px;font-weight:700;color:var(--gray-500);font-family:'JetBrains Mono',monospace}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:1.25rem 0}
.kpi-card{position:relative;padding:1.3rem 1.4rem;background:var(--bg-white);border:1px solid var(--border-light);border-radius:var(--radius-md);overflow:hidden;transition:all .3s;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.kpi-card:hover{border-color:var(--border-medium);transform:translateY(-2px);box-shadow:var(--shadow-md)}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.kpi-card.blue::before{background:var(--gradient-blue)}
.kpi-card.emerald::before{background:linear-gradient(90deg,#059669,#10b981,#34d399)}
.kpi-card.neutral::before{background:linear-gradient(90deg,#94a3b8,#cbd5e1)}
.kpi-card.amber::before{background:linear-gradient(90deg,#d97706,#f59e0b,#fbbf24)}
.kpi-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.5rem}
.kpi-value{font-size:1.75rem;font-weight:800;color:var(--text-primary);font-family:'JetBrains Mono',monospace;letter-spacing:-.03em;line-height:1}
.kpi-unit{font-size:.78rem;font-weight:500;color:var(--text-muted);margin-left:3px}
.kpi-sub{font-size:.72rem;color:var(--text-muted);margin-top:.5rem;font-weight:500}
.stButton>button{font-family:'Inter',sans-serif!important;font-weight:700!important;letter-spacing:.03em!important;border-radius:var(--radius-sm)!important;padding:.7rem 2rem!important;transition:all .2s!important;border:none!important;font-size:.85rem!important;text-transform:uppercase!important}
.stButton>button[kind="primary"],.stButton>button[data-testid="baseButton-primary"]{background:var(--gradient-blue)!important;color:var(--text-white)!important;box-shadow:var(--shadow-blue)!important}
.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="baseButton-primary"]:hover{box-shadow:var(--shadow-blue-lg)!important;transform:translateY(-2px)!important}
.stButton>button[kind="secondary"],.stButton>button[data-testid="baseButton-secondary"]{background:var(--bg-white)!important;color:var(--text-primary)!important;border:1px solid var(--border-medium)!important}
.stDownloadButton>button{background:var(--gradient-blue)!important;color:var(--text-white)!important;font-family:'Inter',sans-serif!important;font-weight:700!important;border-radius:var(--radius-sm)!important;padding:.8rem 2.5rem!important;border:none!important;box-shadow:var(--shadow-blue)!important;font-size:.88rem!important;text-transform:uppercase!important;transition:all .2s!important}
.stDownloadButton>button:hover{box-shadow:var(--shadow-blue-lg)!important;transform:translateY(-2px)!important}
[data-testid="stDataEditor"],[data-testid="stDataFrame"]{border:1px solid var(--border-light)!important;border-radius:var(--radius-md)!important;overflow:hidden!important;box-shadow:var(--shadow-md)!important;background:var(--bg-white)!important}
[data-testid="stExpander"]{background:var(--bg-white)!important;border:1px solid var(--border-light)!important;border-radius:var(--radius-md)!important;overflow:hidden;box-shadow:var(--shadow-sm)!important}
[data-testid="stExpander"] summary{color:var(--text-primary)!important;font-weight:600!important;padding:1rem 1.25rem!important}
[data-testid="stExpander"] summary::marker,[data-testid="stExpander"] summary::-webkit-details-marker{display:none!important}
[data-testid="stExpander"] summary svg{display:inline-block!important;visibility:visible!important;width:1rem!important;height:1rem!important;fill:var(--text-muted)!important;stroke:var(--text-muted)!important}
[data-testid="stAlert"]{border-radius:var(--radius-sm)!important;font-size:.85rem!important;padding:.8rem 1rem!important;border-left-width:3px!important}
.stProgress>div>div{background:var(--gradient-blue)!important;border-radius:100px!important}
.stProgress>div{background:var(--gray-100)!important;border-radius:100px!important;border:1px solid var(--border-light)!important}
[data-testid="stImage"]{border-radius:var(--radius-sm)!important;overflow:hidden!important;border:1px solid var(--border-light)!important;transition:all .25s!important;background:var(--bg-white)!important}
[data-testid="stImage"]:hover{border-color:var(--blue-400)!important;box-shadow:var(--shadow-blue)!important;transform:scale(1.02)}
[data-testid="stFileUploaderFile"]{background:var(--blue-50)!important;border:1px solid var(--blue-200)!important;border-radius:var(--radius-sm)!important;padding:.5rem .75rem!important;margin-top:.75rem!important}
[data-testid="stCheckbox"] label{color:var(--text-secondary)!important;font-weight:500!important;font-size:.82rem!important}
.section-divider{display:flex;align-items:center;gap:12px;margin:2rem 0}
.section-divider .line{flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--border-light),transparent)}
.section-divider .dot{width:6px;height:6px;background:var(--blue-300);border-radius:50%;flex-shrink:0;opacity:.6}
.table-label{display:flex;align-items:center;gap:10px;margin-bottom:.75rem}
.table-label .bar{width:3px;height:16px;background:var(--gradient-blue);border-radius:2px}
.table-label span{font-size:.78rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em}
.trust-bar{display:flex;align-items:center;justify-content:center;gap:2rem;padding:.6rem 1rem;background:var(--gray-50);border:1px solid var(--border-light);border-radius:var(--radius-sm);margin:1rem 0 .5rem}
.trust-item{display:flex;align-items:center;gap:6px;font-size:.72rem;font-weight:600;color:var(--gray-500)}
.trust-item .t-icon{font-size:13px;color:var(--blue-500)}
.corp-footer{margin-top:4rem;padding:2rem 0 1rem;text-align:center;position:relative}
.corp-footer::before{content:'';position:absolute;top:0;left:15%;right:15%;height:1px;background:linear-gradient(90deg,transparent,var(--border-light),transparent)}
.footer-logo-text{font-family:'Inter',sans-serif;font-size:.95rem;font-weight:800;color:var(--blue-700);margin-bottom:.3rem}
.footer-sub{font-size:.7rem;color:var(--text-muted);letter-spacing:.04em}
.footer-copy{color:var(--gray-300);font-size:.62rem;margin-top:.6rem;letter-spacing:.06em}
.proc-status{display:flex;align-items:center;gap:12px;padding:.75rem 1.25rem;background:var(--bg-white);border:1px solid var(--border-light);border-radius:var(--radius-sm);margin:.5rem 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.proc-icon{width:32px;height:32px;display:flex;align-items:center;justify-content:center;background:var(--blue-50);border:1px solid var(--blue-100);border-radius:6px;font-size:14px;flex-shrink:0}
.proc-text-main{font-size:.88rem;font-weight:600;color:var(--text-primary)}
.proc-text-sub{font-size:.78rem;color:var(--text-muted);margin-left:8px}
@media(max-width:768px){.main .block-container{padding:1rem!important}.hero-brand{font-size:1.5rem!important}.kpi-grid{grid-template-columns:repeat(2,1fr)}.hero-content{padding:1.5rem!important}.trust-bar{flex-direction:column;gap:.5rem}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. SCHEMA PARA STRUCTURED OUTPUTS
# ══════════════════════════════════════════════════════════════════════════════

# Google AI Studio (TypedDict)
class PiezaSchema(typing.TypedDict):
    id: str
    nombre: str
    largo: float
    ancho: float
    espesor: float
    material: str
    cantidad: int
    notas: str

# Vertex AI (OpenAPI dict)
SCHEMA_VERTEX = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "id": {"type": "STRING"}, "nombre": {"type": "STRING"},
            "largo": {"type": "NUMBER"}, "ancho": {"type": "NUMBER"},
            "espesor": {"type": "NUMBER"}, "material": {"type": "STRING"},
            "cantidad": {"type": "INTEGER"}, "notas": {"type": "STRING"}
        },
        "required": ["id","nombre","largo","ancho","espesor","material",
                      "cantidad","notas"]
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# 4. MODELOS DE TRAZABILIDAD
# ══════════════════════════════════════════════════════════════════════════════
class OrigenDato(Enum):
    VECTOR_PDF = "PDF_VECTORIAL"
    VISION_IA = "GEMINI_IA"
    REGLA_MOTOR = "REGLA_TALLER"

class NivelConfianza(Enum):
    DETERMINISTA = "DET"
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"

@dataclass
class CampoTrazable:
    valor: object
    valor_original: object = None
    origen: OrigenDato = OrigenDato.VISION_IA
    confianza: NivelConfianza = NivelConfianza.MEDIA
    regla_aplicada: str = ""
    def fue_modificado(self) -> bool:
        return self.valor_original is not None and self.valor != self.valor_original

@dataclass
class PiezaIndustrial:
    id: str
    nombre: str
    largo: CampoTrazable
    ancho: CampoTrazable
    espesor: CampoTrazable
    material: CampoTrazable
    cantidad: CampoTrazable
    notas: str = ""
    pagina_origen: int = 0
    hash_pieza: str = ""
    alertas: list = field(default_factory=list)

    def __post_init__(self):
        c = f"{self.nombre}_{self.largo.valor}_{self.ancho.valor}_{self.material.valor}"
        self.hash_pieza = hashlib.md5(c.encode()).hexdigest()[:10]

    def to_row_debug(self) -> dict:
        return {
            "ID": self.id, "Nombre": self.nombre,
            "Largo_IA": self.largo.valor_original or self.largo.valor,
            "Largo_Corte": self.largo.valor,
            "Ancho_IA": self.ancho.valor_original or self.ancho.valor,
            "Ancho_Corte": self.ancho.valor,
            "Espesor": self.espesor.valor, "Material": self.material.valor,
            "Cantidad": self.cantidad.valor,
            "Confianza": self._conf_global().value,
            "Regla": self._reglas_str(),
            "Notas": self.notas, "Pág": self.pagina_origen
        }

    def to_csv_row(self) -> dict:
        return {
            "Nombre": self.nombre, "Largo": self.largo.valor,
            "Ancho": self.ancho.valor, "Espesor": self.espesor.valor,
            "Material": self.material.valor, "Cantidad": self.cantidad.valor,
            "Notas": self.notas
        }

    def _conf_global(self) -> NivelConfianza:
        ns = [self.largo.confianza, self.ancho.confianza,
              self.material.confianza, self.cantidad.confianza]
        if NivelConfianza.BAJA in ns: return NivelConfianza.BAJA
        if NivelConfianza.MEDIA in ns: return NivelConfianza.MEDIA
        return NivelConfianza.ALTA

    def _reglas_str(self) -> str:
        r = [c.regla_aplicada for c in
             [self.largo,self.ancho,self.espesor,self.cantidad] if c.regla_aplicada]
        return " | ".join(r) if r else "Corte Neto"

# ══════════════════════════════════════════════════════════════════════════════
# 5. PERFILES DE CLIENTE
# ══════════════════════════════════════════════════════════════════════════════
PERFILES = {
    "ESTÁNDAR": {
        "display": "Estándar (Sin reglas de cajón)",
        "ancho_pinza": 70, "ancho_seguro": 130, "margen_sandwich": 60,
        "margen_cnc": 10, "largo_max": 2850, "ancho_max": 2100, "kerf_mm": 4.2,
        "espesores_validos": [3,4,5,6,8,10,12,15,16,18,19,22,25,30,38,40,50],
        "cajon_qube": False, "descuento_qube": 0,
        "canteado_auto": False, "espesor_canto_mm": 2.0,
        "lista_negra": ["PINO","PINTURA","CANTO","TORNILLO","HERRAJE",
                        "PERFIL LED","CATALIZADOR","COLA","SILICONA","TIRADOR","BISAGRA"],
        "alias_material": {
            "BLANCO":"W980","CAOLIN":"W980","W980":"W980","WHITE":"W980",
            "ELEGANCE":"M6317","M6317":"M6317","ROBLE":"M6317","OAK":"M6317",
            "FONDO":"16B","OCULTO":"16B","BACK":"16B",
            "KRION":"KRION (CORTE ESPECIAL)",
            "ALUMINIO":"METAL (NO CORTAR)","METAL":"METAL (NO CORTAR)",
            "ACERO":"METAL (NO CORTAR)"}},
    "APOTHEKA": {
        "display": "Apotheka / Ilusion (Cajones QUBE)",
        "ancho_pinza": 70, "ancho_seguro": 130, "margen_sandwich": 60,
        "margen_cnc": 10, "largo_max": 2850, "ancho_max": 2100, "kerf_mm": 4.2,
        "espesores_validos": [3,4,5,6,8,10,12,15,16,18,19,22,25,30,38,40,50],
        "cajon_qube": True, "descuento_qube": 59,
        "canteado_auto": False, "espesor_canto_mm": 2.0,
        "lista_negra": ["PINO","PINTURA","CANTO","TORNILLO","HERRAJE",
                        "PERFIL LED","CATALIZADOR","COLA","SILICONA","TIRADOR","BISAGRA"],
        "alias_material": {
            "BLANCO":"W980","CAOLIN":"W980","W980":"W980","WHITE":"W980",
            "ELEGANCE":"M6317","M6317":"M6317","ROBLE":"M6317","OAK":"M6317",
            "FONDO":"16B","OCULTO":"16B","BACK":"16B",
            "KRION":"KRION (CORTE ESPECIAL)",
            "ALUMINIO":"METAL (NO CORTAR)","METAL":"METAL (NO CORTAR)"}},
    "CANTEADO_AUTO": {
        "display": "Con descuento de canteado automático",
        "ancho_pinza": 70, "ancho_seguro": 130, "margen_sandwich": 60,
        "margen_cnc": 10, "largo_max": 2850, "ancho_max": 2100, "kerf_mm": 4.2,
        "espesores_validos": [3,4,5,6,8,10,12,15,16,18,19,22,25,30,38,40,50],
        "cajon_qube": False, "descuento_qube": 0,
        "canteado_auto": True, "espesor_canto_mm": 2.0,
        "lista_negra": ["PINO","PINTURA","CANTO","TORNILLO","HERRAJE",
                        "PERFIL LED","CATALIZADOR","COLA","SILICONA","TIRADOR","BISAGRA"],
        "alias_material": {
            "BLANCO":"W980","CAOLIN":"W980","W980":"W980",
            "ELEGANCE":"M6317","M6317":"M6317","ROBLE":"M6317",
            "FONDO":"16B","OCULTO":"16B"}}
}

# ══════════════════════════════════════════════════════════════════════════════
# 6. VALIDADOR FÍSICO
# ══════════════════════════════════════════════════════════════════════════════
class ValidadorFisico:
    @classmethod
    def validar(cls, p: dict, perfil: dict) -> tuple:
        al, conf = [], NivelConfianza.ALTA
        l,a,e,n,c = p.get("largo",0),p.get("ancho",0),p.get("espesor",19),p.get("nombre","?"),p.get("cantidad",1)
        if l>3660: al.append(f"🚫 {n}: Largo {l}mm > máx 3660"); conf=NivelConfianza.BAJA
        if a>2100: al.append(f"🚫 {n}: Ancho {a}mm > máx 2100"); conf=NivelConfianza.BAJA
        if 0<l<50: al.append(f"⚠️ {n}: Largo {l}mm sospechoso"); conf=NivelConfianza.MEDIA
        if 0<a<15: al.append(f"⚠️ {n}: Ancho {a}mm bajo mínimo"); conf=NivelConfianza.MEDIA
        if e not in perfil.get("espesores_validos",[19]):
            ce = min(perfil["espesores_validos"], key=lambda x:abs(x-e))
            al.append(f"⚠️ {n}: Espesor {e}mm no comercial (¿{ce}?)"); conf=NivelConfianza.MEDIA
        if a>0 and l/a>30: al.append(f"⚠️ {n}: Ratio L/A={l/a:.0f}:1 extremo"); conf=NivelConfianza.MEDIA
        if c>50: al.append(f"⚠️ {n}: Cantidad {c} inusual"); conf=NivelConfianza.MEDIA
        if c<=0: return False,al,NivelConfianza.BAJA
        return conf!=NivelConfianza.BAJA, al, conf

# ══════════════════════════════════════════════════════════════════════════════
# 7. DATOS DE PÁGINA (thread-safe — todo pre-extraído)
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class DatosPagina:
    """Pre-extraído en main thread. Seguro para pasar a workers."""
    num: int               # 0-based
    imagen: Image.Image
    texto: str             # Texto vectorial del PDF
    tablas: list           # list[pd.DataFrame] de find_tables
    tiene_texto: bool
    tiene_tablas: bool

# ══════════════════════════════════════════════════════════════════════════════
# 8. EXTRACTOR VECTORIAL (parsea tablas pre-extraídas, thread-safe)
# ══════════════════════════════════════════════════════════════════════════════
class ExtractorVectorial:
    MAPEO = {
        "nombre": ["nombre","pieza","descripcion","desc","name","part",
                    "elemento","denominación","denominacion"],
        "largo":  ["largo","longitud","length","l","long","alto","altura"],
        "ancho":  ["ancho","anchura","width","w","a","prof","profundidad"],
        "espesor":["espesor","grosor","thickness","e","esp","th","grueso"],
        "cantidad":["cantidad","cant","qty","quantity","ud","uds","pcs",
                     "n","nº","num"],
        "material":["material","mat","acabado","color","ref","referencia"]
    }

    @classmethod
    def parsear_tablas(cls, tablas: list, num_pag: int) -> list:
        """Intenta extraer piezas de DataFrames pre-extraídos."""
        for df in tablas:
            if len(df) < 2 or len(df.columns) < 3:
                continue
            piezas = cls._parsear_df(df, num_pag)
            if piezas:
                return piezas
        return []

    @classmethod
    def _parsear_df(cls, df, num_pag):
        headers = [str(h).strip().lower() for h in df.columns]
        cmap = {}
        for campo, vars_ in cls.MAPEO.items():
            for idx, h in enumerate(headers):
                if any(v in h for v in vars_):
                    cmap[campo] = idx; break
        if "largo" not in cmap or "ancho" not in cmap:
            return []
        piezas = []
        for ri, row in df.iterrows():
            try:
                vals = list(row)
                nombre = str(vals[cmap["nombre"]]).strip() if "nombre" in cmap else f"Pieza_{ri}"
                lr = re.search(r'(\d+\.?\d*)', str(vals[cmap["largo"]]).replace(",","."))
                ar = re.search(r'(\d+\.?\d*)', str(vals[cmap["ancho"]]).replace(",","."))
                if not lr or not ar: continue
                largo, ancho = float(lr.group(1)), float(ar.group(1))
                if largo==0 and ancho==0: continue
                espesor = 19.0
                if "espesor" in cmap:
                    em = re.search(r'(\d+\.?\d*)', str(vals[cmap["espesor"]]).replace(",","."))
                    if em: espesor = float(em.group(1))
                cantidad = 1
                if "cantidad" in cmap:
                    cm = re.search(r'(\d+)', str(vals[cmap["cantidad"]]))
                    if cm: cantidad = int(cm.group(1))
                material = str(vals[cmap["material"]]).strip() if "material" in cmap else ""
                piezas.append({
                    "id":f"V{num_pag}_{ri}","nombre":nombre,"largo":largo,"ancho":ancho,
                    "espesor":espesor,"cantidad":cantidad,"material":material,"notas":""})
            except (ValueError,IndexError,TypeError): continue
        return piezas

# ══════════════════════════════════════════════════════════════════════════════
# 9. MOTOR VISIÓN IA — Vertex AI + Google AI · Prompt Híbrido · Structured
# ══════════════════════════════════════════════════════════════════════════════
PROMPT_BASE = """Eres técnico de oficina técnica experto en despieces de mobiliario industrial.

INSTRUCCIONES ESTRICTAS:
1. Extrae TODAS las piezas de madera/tablero visibles.
2. Las cotas principales más grandes = largo y ancho en mm.
3. Si NO puedes leer una medida con certeza, pon 0.
4. Espesor por defecto: 19mm. Cantidad por defecto: 1.
5. NO inventes medidas. Si no las ves, pon 0.
6. NO incluyas herrajes, tornillos, cantos, pinturas, accesorios.
7. Si hay tabla con columnas (ID/DESCRIPCION/UDS) extrae TODAS las filas.
8. En notas incluye: si dice Qube, Pegar, Doble, Radio, Krion, etc.
"""

def _preparar_imagen(img: Image.Image) -> bytes:
    g = img.convert("L")
    c = ImageEnhance.Contrast(g).enhance(1.5)
    s = c.filter(ImageFilter.SHARPEN).convert("RGB")
    buf = io.BytesIO(); s.save(buf, format="PNG"); buf.seek(0)
    return buf.getvalue()


class MotorVision:
    """Soporta Vertex AI y Google AI Studio. Thread-safe para generate_content."""

    def __init__(self):
        self.backend = BACKEND
        if self.backend == "vertex_ai":
            self._init_vertex()
        else:
            self._init_google_ai()
        logger.info(f"MotorVision: backend={self.backend}, model={GEMINI_MODEL}")

    def _init_vertex(self):
        import vertexai
        from google.oauth2 import service_account
        from vertexai.generative_models import GenerativeModel
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_info)
        vertexai.init(project=st.secrets["GCP_PROJECT"],
                      location=st.secrets.get("GCP_LOCATION","europe-west1"),
                      credentials=creds)
        self._model = GenerativeModel(GEMINI_MODEL)

    def _init_google_ai(self):
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        self._genai = genai
        self._model = genai.GenerativeModel(GEMINI_MODEL)

    def analizar(self, imagen: Image.Image, texto_vectorial: str = "",
                 max_intentos: int = 3) -> list:
        """Análisis híbrido: imagen + texto vectorial inyectado en prompt."""
        img_bytes = _preparar_imagen(imagen)

        # Construir prompt híbrido (innovación V2)
        prompt = PROMPT_BASE
        if texto_vectorial and texto_vectorial.strip():
            prompt += f"""
FUENTE SECUNDARIA — TEXTO VECTORIAL EXACTO DEL PDF:
'''
{texto_vectorial[:MAX_TEXTO_VECTORIAL]}
'''
Usa este texto para verificar nombres, cantidades y medidas.
Si hay discrepancia entre texto e imagen, prioriza el texto vectorial.
"""

        for intento in range(max_intentos):
            try:
                if self.backend == "vertex_ai":
                    texto = self._call_vertex(prompt, img_bytes)
                else:
                    texto = self._call_google_ai(prompt, img_bytes)

                datos = json.loads(texto)
                if isinstance(datos, dict): datos = [datos]
                logger.info(f"  ✓ IA: {len(datos)} piezas (intento {intento+1})")
                return datos

            except json.JSONDecodeError:
                logger.warning(f"  ⚠ JSON inválido (intento {intento+1})")
                if intento < max_intentos-1:
                    time.sleep(2**intento); continue
                try:
                    return self._fallback_fix(texto if 'texto' in dir() else "")
                except Exception:
                    return [{"error":"JSON irreparable"}]
            except Exception as e:
                logger.error(f"  ✗ Error API (intento {intento+1}): {e}")
                if intento < max_intentos-1:
                    time.sleep(2**intento); continue
                return [{"error": str(e)}]
        return []

    def _call_vertex(self, prompt, img_bytes):
        from vertexai.generative_models import Part, GenerationConfig
        img_part = Part.from_data(data=img_bytes, mime_type="image/png")
        resp = self._model.generate_content(
            [prompt, img_part],
            generation_config=GenerationConfig(
                temperature=0.1, response_mime_type="application/json",
                response_schema=SCHEMA_VERTEX))
        return resp.text

    def _call_google_ai(self, prompt, img_bytes):
        resp = self._model.generate_content(
            [prompt, {"mime_type":"image/png","data":img_bytes}],
            generation_config=self._genai.GenerationConfig(
                temperature=0.1, response_mime_type="application/json",
                response_schema=list[PiezaSchema]))
        return resp.text

    def _fallback_fix(self, texto_roto):
        pf = f"Corrige este JSON y devuelve SOLO el array JSON válido:\n{texto_roto}"
        if self.backend == "vertex_ai":
            from vertexai.generative_models import GenerationConfig
            resp = self._model.generate_content([pf],
                generation_config=GenerationConfig(
                    temperature=0.0, response_mime_type="application/json",
                    response_schema=SCHEMA_VERTEX))
        else:
            resp = self._model.generate_content([pf],
                generation_config=self._genai.GenerationConfig(
                    temperature=0.0, response_mime_type="application/json",
                    response_schema=list[PiezaSchema]))
        d = json.loads(resp.text)
        return [d] if isinstance(d,dict) else d

# ══════════════════════════════════════════════════════════════════════════════
# 10. CEREBRO OPERARIO V5
# ══════════════════════════════════════════════════════════════════════════════
class CerebroOperarioV5:
    def __init__(self, perfil_nombre: str):
        self.p = PERFILES.get(perfil_nombre, PERFILES["ESTÁNDAR"])
        self.hash_vistos = {}

    def normalizar_material(self, texto):
        mat = str(texto).upper().strip()
        for k,v in self.p["alias_material"].items():
            if k in mat: return v, NivelConfianza.ALTA
        return (texto, NivelConfianza.MEDIA) if mat and len(mat)>1 else ("SIN MATERIAL", NivelConfianza.BAJA)

    def es_basura(self, nombre, material):
        t = f"{nombre} {material}".upper()
        return any(x in t for x in self.p["lista_negra"])

    def procesar(self, datos, num_pag, origen):
        piezas, alertas = [], []
        for idx, raw in enumerate(datos):
            nombre = raw.get("nombre","Sin Nombre")
            mat_raw = raw.get("material","")
            if self.es_basura(nombre, mat_raw): continue
            try:
                largo=float(raw.get("largo",0)); ancho=float(raw.get("ancho",0))
                espesor=float(raw.get("espesor",19)); cantidad=int(float(raw.get("cantidad",1)))
            except (ValueError,TypeError):
                alertas.append(f"⚠️ Pág {num_pag}: '{nombre}' no numérico"); continue
            if largo==0 and ancho==0: continue
            if largo<ancho: largo,ancho=ancho,largo
            material,conf_mat = self.normalizar_material(mat_raw)
            notas = str(raw.get("notas","")).upper()
            conf_dim = NivelConfianza.DETERMINISTA if origen==OrigenDato.VECTOR_PDF else NivelConfianza.MEDIA
            id_p = f"P{num_pag}_{raw.get('id',idx)}"
            pieza = PiezaIndustrial(
                id=id_p, nombre=nombre,
                largo=CampoTrazable(largo,origen=origen,confianza=conf_dim),
                ancho=CampoTrazable(ancho,origen=origen,confianza=conf_dim),
                espesor=CampoTrazable(espesor,origen=origen,confianza=conf_dim),
                material=CampoTrazable(material,valor_original=mat_raw,origen=origen,confianza=conf_mat),
                cantidad=CampoTrazable(cantidad,origen=origen,confianza=conf_dim),
                notas=notas, pagina_origen=num_pag)

            # ── Sándwich ──
            if any(k in notas for k in ["PEGAR","DOBLE","APLACAR","SANDWICH"]):
                m=self.p["margen_sandwich"]
                pieza.largo.valor_original=largo; pieza.largo.valor+=m; pieza.largo.regla_aplicada=f"Sándwich +{m}"
                pieza.ancho.valor_original=ancho; pieza.ancho.valor+=m; pieza.ancho.regla_aplicada=f"Sándwich +{m}"
                if "DOBLE" in notas and cantidad==1:
                    pieza.cantidad.valor_original=1; pieza.cantidad.valor=2; pieza.cantidad.regla_aplicada="Sándwich x2"
                alertas.append(f"🥪 Pág {num_pag} — {nombre}: Sándwich +{m}mm")

            # ── Cajón Qube ──
            if self.p["cajon_qube"] and ("CAJÓN" in nombre.upper() or "CAJON" in nombre.upper()) and "QUBE" in notas:
                d=self.p["descuento_qube"]; lf=280 if "300" in notas else 480; af=pieza.largo.valor-d
                fondo = PiezaIndustrial(
                    id=f"{id_p}_F", nombre=f"Fondo {nombre}",
                    largo=CampoTrazable(af,origen=OrigenDato.REGLA_MOTOR,confianza=NivelConfianza.ALTA,regla_aplicada=f"Qube -{d}"),
                    ancho=CampoTrazable(lf,origen=OrigenDato.REGLA_MOTOR,confianza=NivelConfianza.ALTA),
                    espesor=CampoTrazable(16,origen=OrigenDato.REGLA_MOTOR,confianza=NivelConfianza.DETERMINISTA),
                    material=CampoTrazable("16B",origen=OrigenDato.REGLA_MOTOR,confianza=NivelConfianza.DETERMINISTA),
                    cantidad=CampoTrazable(pieza.cantidad.valor,origen=OrigenDato.REGLA_MOTOR,confianza=NivelConfianza.ALTA),
                    notas="AUTO: Fondo Qube", pagina_origen=num_pag)
                piezas.append(fondo); pieza.nombre=f"Frente {nombre}"
                alertas.append(f"✨ Pág {num_pag} — {nombre}: Fondo Qube generado")

            # ── CNC / Curva ──
            if any(k in notas for k in ["RADIO","CURVA"]) or (notas.startswith("R") and any(c.isdigit() for c in notas)):
                mc=self.p["margen_cnc"]
                pieza.largo.valor_original=pieza.largo.valor_original or pieza.largo.valor; pieza.largo.valor+=mc
                pieza.largo.regla_aplicada=((pieza.largo.regla_aplicada+" ") if pieza.largo.regla_aplicada else "")+f"CNC +{mc}"
                pieza.ancho.valor_original=pieza.ancho.valor_original or pieza.ancho.valor; pieza.ancho.valor+=mc
                pieza.ancho.regla_aplicada=((pieza.ancho.regla_aplicada+" ") if pieza.ancho.regla_aplicada else "")+f"CNC +{mc}"

            # ── 2x1 ──
            if pieza.ancho.valor<50 and pieza.cantidad.valor>=2 and pieza.cantidad.valor%2==0:
                pieza.ancho.valor_original=pieza.ancho.valor; pieza.ancho.valor=self.p["ancho_seguro"]; pieza.ancho.regla_aplicada="2x1"
                pieza.cantidad.valor_original=pieza.cantidad.valor; pieza.cantidad.valor//=2; pieza.cantidad.regla_aplicada="2x1 (÷2)"
                alertas.append(f"✂️ Pág {num_pag} — {nombre}: Optimización 2x1")
            elif pieza.ancho.valor<self.p["ancho_pinza"]:
                alertas.append(f"🚨 Pág {num_pag} — {nombre}: Ancho {pieza.ancho.valor}mm < pinza")
                pieza.ancho.confianza=NivelConfianza.BAJA

            # ── Canteado ──
            if self.p["canteado_auto"] and "SIN CANTO" not in notas and "OCULTO" not in notas:
                ec=self.p["espesor_canto_mm"]
                pieza.largo.valor_original=pieza.largo.valor_original or pieza.largo.valor; pieza.largo.valor-=ec*2
                pieza.largo.regla_aplicada=((pieza.largo.regla_aplicada+" ") if pieza.largo.regla_aplicada else "")+f"Canto -{ec*2}"
                pieza.ancho.valor_original=pieza.ancho.valor_original or pieza.ancho.valor; pieza.ancho.valor-=ec*2
                pieza.ancho.regla_aplicada=((pieza.ancho.regla_aplicada+" ") if pieza.ancho.regla_aplicada else "")+f"Canto -{ec*2}"

            # ── Excede tablero ──
            if pieza.largo.valor>self.p["largo_max"]:
                alertas.append(f"📏 Pág {num_pag} — {nombre}: Largo {pieza.largo.valor}mm > tablero")

            # ── Validación física ──
            ok,af,cf = ValidadorFisico.validar(
                {"largo":pieza.largo.valor,"ancho":pieza.ancho.valor,
                 "espesor":pieza.espesor.valor,"cantidad":pieza.cantidad.valor,"nombre":nombre}, self.p)
            alertas.extend(af)
            if not ok: pieza.largo.confianza=NivelConfianza.BAJA; pieza.ancho.confianza=NivelConfianza.BAJA

            # ── Deduplicación ──
            if pieza.hash_pieza in self.hash_vistos:
                alertas.append(f"🔄 Pág {num_pag} — '{nombre}' duplicada (pág {self.hash_vistos[pieza.hash_pieza]})")
                continue
            self.hash_vistos[pieza.hash_pieza] = num_pag
            piezas.append(pieza)
        return piezas, alertas

# ══════════════════════════════════════════════════════════════════════════════
# 11. WORKER PARA ThreadPoolExecutor (thread-safe, no toca Streamlit)
# ══════════════════════════════════════════════════════════════════════════════
def _worker_pagina(datos_pag: DatosPagina, motor: MotorVision) -> tuple:
    """
    Ejecutado en thread separado. Retorna (num_pag, datos_raw, origen, estrategia).
    NO llama a st.* ni a CerebroOperario (eso va en main thread).
    """
    num = datos_pag.num + 1  # 1-based para display

    # 1. Intentar extracción vectorial (0 coste, determinista)
    if datos_pag.tiene_tablas:
        piezas_v = ExtractorVectorial.parsear_tablas(datos_pag.tablas, num)
        if piezas_v:
            return (num, piezas_v, OrigenDato.VECTOR_PDF,
                    f"VECTORIAL ({len(piezas_v)} pzs)")

    # 2. Visión IA con prompt híbrido (imagen + texto vectorial)
    datos_ia = motor.analizar(datos_pag.imagen, datos_pag.texto)
    if datos_ia and not (isinstance(datos_ia[0], dict) and "error" in datos_ia[0]):
        fuente = "HÍBRIDO" if datos_pag.tiene_texto else "VISIÓN"
        return (num, datos_ia, OrigenDato.VISION_IA,
                f"GEMINI {fuente} ({len(datos_ia)} pzs)")

    err = datos_ia[0].get("error","?") if datos_ia else "sin datos"
    return (num, [{"error": err}], OrigenDato.VISION_IA, "ERROR")

# ══════════════════════════════════════════════════════════════════════════════
# 12. EXTRACCIÓN DE PDF (todo en main thread, thread-safe después)
# ══════════════════════════════════════════════════════════════════════════════
def pdf_a_datos(archivo, dpi=300) -> list:
    """Extrae TODAS las capas del PDF en una sola pasada.
    Retorna lista de DatosPagina listos para workers."""
    pdf_bytes = archivo.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    resultado = []
    for i, page in enumerate(doc):
        # Imagen
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        # Texto vectorial
        texto = page.get_text("text")
        # Tablas
        tablas = []
        try:
            tabs = page.find_tables()
            if tabs and tabs.tables:
                for t in tabs.tables:
                    df = t.to_pandas()
                    if len(df) >= 2 and len(df.columns) >= 3:
                        tablas.append(df)
        except Exception:
            pass

        resultado.append(DatosPagina(
            num=i, imagen=img, texto=texto, tablas=tablas,
            tiene_texto=len(texto.strip()) > 20,
            tiene_tablas=len(tablas) > 0))
    doc.close()
    return resultado

# ══════════════════════════════════════════════════════════════════════════════
# 13. AUDITORÍA
# ══════════════════════════════════════════════════════════════════════════════
class Auditoria:
    @staticmethod
    def generar(piezas, alertas, perfil, archivo):
        sep="="*70
        lns=[sep,"AUDITORÍA — GABBIANI MASTER AI v6.0 ENTERPRISE",sep,
             f"Fecha:   {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
             f"Archivo: {archivo}", f"Perfil:  {perfil}",
             f"Backend: {BACKEND} · Modelo: {GEMINI_MODEL}",
             f"Workers: {MAX_WORKERS} · Piezas: {len(piezas)} · Alertas: {len(alertas)}",
             "-"*70,"","MODIFICACIONES:",""]
        mod=0
        for p in piezas:
            cambios=[]
            if p.largo.fue_modificado(): cambios.append(f"  L: {p.largo.valor_original}→{p.largo.valor} [{p.largo.regla_aplicada}]")
            if p.ancho.fue_modificado(): cambios.append(f"  A: {p.ancho.valor_original}→{p.ancho.valor} [{p.ancho.regla_aplicada}]")
            if p.cantidad.fue_modificado(): cambios.append(f"  C: {p.cantidad.valor_original}→{p.cantidad.valor} [{p.cantidad.regla_aplicada}]")
            if cambios:
                mod+=1; lns.append(f"[{p.id}] {p.nombre} (Pág {p.pagina_origen})")
                lns.extend(cambios); lns.append("")
        lns.extend([f"Modificadas: {mod}","","-"*70,"ALERTAS:",""])
        lns.extend([f"  • {a}" for a in alertas])
        lns.extend(["",sep,"FIN",sep])
        return "\n".join(lns)

# ══════════════════════════════════════════════════════════════════════════════
# 14. AUTENTICACIÓN + MOTOR
# ══════════════════════════════════════════════════════════════════════════════
try:
    if BACKEND == "vertex_ai":
        _ = dict(st.secrets["gcp_service_account"])  # Verificar que existe
    else:
        _ = st.secrets["GEMINI_API_KEY"]
except Exception as e:
    st.markdown(f"""
    <div style="background:#fee2e2;border:1px solid #fecaca;border-radius:12px;
    padding:1.5rem;margin:1.5rem 0;border-left:3px solid #dc2626;">
    <div style="font-weight:700;color:#991b1b;">⛔ Error de Configuración</div>
    <div style="color:#475569;font-size:.88rem;">
    Backend: <code>{BACKEND}</code><br>
    Vertex AI: necesita <code>[gcp_service_account]</code> + <code>GCP_PROJECT</code><br>
    Google AI: necesita <code>GEMINI_API_KEY</code><br>
    Error: {e}</div></div>""", unsafe_allow_html=True)
    st.stop()

@st.cache_resource
def get_motor():
    return MotorVision()

# ══════════════════════════════════════════════════════════════════════════════
# 15. HERO + TRUST BAR
# ══════════════════════════════════════════════════════════════════════════════
backend_label = "Vertex AI" if BACKEND=="vertex_ai" else "Google AI Studio"
st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-blue-line"></div>
    <div class="hero-content">
        <div class="hero-mono-tag"><span class="tag-dot"></span>
            SISTEMA EXPERTO DE CORTE INDUSTRIAL · v6.0 ENTERPRISE</div>
        <div class="hero-title-line">
            <h1 class="hero-brand">GABBIANI <span class="blue">MASTER AI</span></h1>
            <span class="hero-edition">ENTERPRISE</span>
        </div>
        <p class="hero-desc">
            Pipeline dual con concurrencia {MAX_WORKERS}x: extracción vectorial + Gemini 2.5 Pro híbrido (visión+texto).
            {backend_label} · Structured Outputs · Trazabilidad · Validación física · Auditoría exportable.
        </p>
        <div class="hero-status-row">
            <div class="status-chip chip-online"><span class="chip-dot green"></span>Operativo</div>
            <div class="status-chip chip-blue"><span class="chip-dot blue"></span>{GEMINI_MODEL}</div>
            <div class="status-chip chip-blue"><span class="chip-dot blue"></span>{backend_label}</div>
            <div class="status-chip chip-neutral">🚀 {MAX_WORKERS}x hilos</div>
            <div class="status-chip chip-neutral">🕐 {datetime.now().strftime("%d/%m/%Y · %H:%M")}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="trust-bar">
    <div class="trust-item"><span class="t-icon">🛡️</span> Procesamiento seguro</div>
    <div class="trust-item"><span class="t-icon">🔒</span> Datos no almacenados</div>
    <div class="trust-item"><span class="t-icon">✅</span> Validación por reglas de ingeniería</div>
    <div class="trust-item"><span class="t-icon">📐</span> Precisión híbrida Vector+Visión</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 16. SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Configuración Industrial")
    perfil_sel = st.selectbox("Perfil de Cliente", list(PERFILES.keys()),
                               format_func=lambda x: PERFILES[x]["display"])
    pf = PERFILES[perfil_sel]
    st.markdown("---")
    st.code(f"Pinza:     {pf['ancho_pinza']}mm\n"
            f"Saneado:   {pf['margen_sandwich']}mm\n"
            f"Kerf:      {pf['kerf_mm']}mm\n"
            f"Canteado:  {'SÍ' if pf['canteado_auto'] else 'NO'}\n"
            f"Cajones:   {'QUBE' if pf['cajon_qube'] else 'NO'}\n"
            f"Backend:   {backend_label}\n"
            f"Modelo:    {GEMINI_MODEL}\n"
            f"Workers:   {MAX_WORKERS}")
    st.markdown("---")
    dpi_sel = st.select_slider("Resolución DPI", [150,200,250,300], value=300)
    mostrar_debug = st.checkbox("Mostrar trazabilidad", value=True)

# ══════════════════════════════════════════════════════════════════════════════
# 17. UPLOAD + EXTRACCIÓN
# ══════════════════════════════════════════════════════════════════════════════
if 'datos_pdf' not in st.session_state:
    st.session_state['datos_pdf'] = []

st.markdown("""
<div class="sec-header"><div class="sec-icon">📁</div>
<div class="sec-text"><div class="sec-title">Importar Proyecto</div>
<div class="sec-sub">PDF con planos técnicos · Extracción dual: Imagen + Texto Vectorial + Tablas</div>
</div></div>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Selecciona PDF", type=["pdf"])

if uploaded_file:
    nombre_base = os.path.splitext(uploaded_file.name)[0]

    if st.session_state.get('_last_file') != uploaded_file.name:
        with st.spinner(f"Extrayendo capas del PDF a {dpi_sel} DPI..."):
            st.session_state['datos_pdf'] = pdf_a_datos(uploaded_file, dpi=dpi_sel)
            st.session_state['_last_file'] = uploaded_file.name
            for k in ['df_final','alertas_final','piezas_obj','meta_pags']:
                st.session_state.pop(k, None)

    datos_pdf = st.session_state['datos_pdf']
    tp = len(datos_pdf)
    pags_texto = sum(1 for d in datos_pdf if d.tiene_texto)
    pags_tablas = sum(1 for d in datos_pdf if d.tiene_tablas)

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card blue">
            <div class="kpi-label">Documento</div>
            <div class="kpi-value" style="font-size:.92rem;word-break:break-all;font-weight:600">{uploaded_file.name}</div>
            <div class="kpi-sub">Perfil: {pf['display']}</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Páginas</div>
            <div class="kpi-value">{tp}</div>
            <div class="kpi-sub">{pags_texto} con texto · {pags_tablas} con tablas</div>
        </div>
        <div class="kpi-card emerald">
            <div class="kpi-label">Texto Vectorial</div>
            <div class="kpi-value">{pags_texto}<span class="kpi-unit">/ {tp}</span></div>
            <div class="kpi-sub">Páginas con datos digitales</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Motor</div>
            <div class="kpi-value" style="font-size:.72rem">{GEMINI_MODEL.replace('-preview-06-05','')}</div>
            <div class="kpi-sub">{backend_label} · {MAX_WORKERS}x hilos</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── SELECCIÓN DE PÁGINAS ──
    st.markdown(f"""
    <div class="sec-header"><div class="sec-icon">📑</div>
    <div class="sec-text"><div class="sec-title">Selección de Páginas</div>
    <div class="sec-sub">📝 = texto vectorial disponible · 🖼️ = solo imagen</div></div>
    <div class="sec-badge">{tp} PÁG</div></div>""", unsafe_allow_html=True)

    for i in range(tp):
        if f"chk_{i}" not in st.session_state:
            st.session_state[f"chk_{i}"] = True

    act = sum(1 for i in range(tp) if st.session_state.get(f"chk_{i}",True))
    todas = act==tp
    c1,c2 = st.columns([5,1])
    with c1: st.markdown(f"**{act}** de **{tp}** seleccionadas")
    with c2:
        if st.button("☐ Ninguna" if todas else "☑ Todas", use_container_width=True):
            for i in range(tp): st.session_state[f"chk_{i}"] = not todas
            st.rerun()

    seleccionadas = []
    cols = st.columns(6)
    for i, dp in enumerate(datos_pdf):
        with cols[i%6]:
            icono = "📝" if dp.tiene_texto else "🖼️"
            tab_tag = " 📊" if dp.tiene_tablas else ""
            m = st.checkbox(f"{icono} Pág {i+1:02d}{tab_tag}", key=f"chk_{i}")
            st.image(dp.imagen, use_container_width=True)
            if m: seleccionadas.append(dp)

    st.markdown("""<div class="section-divider"><div class="line"></div>
    <div class="dot"></div><div class="line"></div></div>""", unsafe_allow_html=True)

    n_sel = len(seleccionadas)
    tiempo_est = max(3, (n_sel*9)//MAX_WORKERS)
    cb,_,ci = st.columns([2,1,3])
    with cb:
        procesar = st.button(f"▶  ANALIZAR HÍBRIDO  ·  {n_sel} PÁGINAS",
                             type="primary", use_container_width=True, disabled=(n_sel==0))
    with ci:
        st.caption(f"~{tiempo_est}s estimado · {MAX_WORKERS} hilos · Pipeline dual")

    # ══════════════════════════════════════════════════════════════════════════
    # 18. PROCESAMIENTO CONCURRENTE
    # ══════════════════════════════════════════════════════════════════════════
    if procesar and n_sel > 0:
        motor = get_motor()
        cerebro = CerebroOperarioV5(perfil_sel)
        piezas_total, alertas_total, meta_pags = [], [], []

        st.markdown("""
        <div class="sec-header"><div class="sec-icon">🔬</div>
        <div class="sec-text"><div class="sec-title">Pipeline Dual Concurrente</div>
        <div class="sec-sub">Vectorial → Gemini Híbrido → Reglas → Validación → Deduplicación</div>
        </div></div>""", unsafe_allow_html=True)

        barra = st.progress(0)
        status = st.empty()
        status.markdown("""<div class="proc-status"><div class="proc-icon">🔄</div>
        <div><span class="proc-text-main">Lanzando análisis concurrente...</span>
        <span class="proc-text-sub">Enviando páginas a workers</span></div></div>""",
        unsafe_allow_html=True)
        barra.progress(5)

        # Lanzar workers (innovación V2)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futuros = {
                executor.submit(_worker_pagina, dp, motor): dp.num
                for dp in seleccionadas
            }
            completados = 0

            for futuro in as_completed(futuros):
                completados += 1
                try:
                    num_pag, datos_raw, origen, estrategia = futuro.result()
                    meta_pags.append(estrategia)

                    status.markdown(f"""<div class="proc-status">
                    <div class="proc-icon">⚡</div>
                    <div><span class="proc-text-main">Página {num_pag} completada</span>
                    <span class="proc-text-sub">({completados}/{n_sel}) · {estrategia}</span></div>
                    </div>""", unsafe_allow_html=True)

                    if isinstance(datos_raw, list) and datos_raw:
                        if isinstance(datos_raw[0], dict) and "error" in datos_raw[0]:
                            alertas_total.append(f"❌ Pág {num_pag}: {datos_raw[0]['error']}")
                        else:
                            # Reglas en main thread (thread-safe)
                            pzs, als = cerebro.procesar(datos_raw, num_pag, origen)
                            piezas_total.extend(pzs)
                            alertas_total.extend(als)

                except Exception as e:
                    alertas_total.append(f"❌ Error en worker: {e}")

                barra.progress(max(5, int((completados/n_sel)*100)))

        status.markdown("""<div class="proc-status" style="border-color:#a7f3d0;background:#ecfdf5">
        <div class="proc-icon" style="background:#d1fae5;border-color:#a7f3d0">✅</div>
        <div><span class="proc-text-main" style="color:#065f46">Procesamiento completado</span>
        <span class="proc-text-sub">Pipeline dual finalizado</span></div></div>""",
        unsafe_allow_html=True)
        barra.progress(100)

        # Ordenar por ID para consistencia
        piezas_total.sort(key=lambda p: p.id)

        if piezas_total:
            rows = [p.to_row_debug() for p in piezas_total] if mostrar_debug else [p.to_csv_row() for p in piezas_total]
            st.session_state['df_final'] = pd.DataFrame(rows)
            st.session_state['alertas_final'] = alertas_total
            st.session_state['piezas_obj'] = piezas_total
            st.session_state['meta_pags'] = meta_pags
            st.session_state['nombre_base'] = nombre_base
        else:
            st.session_state['df_final'] = pd.DataFrame()
            st.session_state['alertas_final'] = alertas_total

        st.rerun()  # Limpiar UI de procesamiento (patrón V2)

# ══════════════════════════════════════════════════════════════════════════════
# 19. RESULTADOS Y EXPORTACIÓN
# ══════════════════════════════════════════════════════════════════════════════
if 'df_final' in st.session_state:
    df = st.session_state['df_final']
    al = st.session_state.get('alertas_final',[])
    po = st.session_state.get('piezas_obj',[])
    nb = st.session_state.get('nombre_base','proyecto')
    meta = st.session_state.get('meta_pags',[])

    if df.empty:
        st.warning("No se extrajeron piezas válidas. Revisa la selección de páginas o el PDF.")
    else:
        st.markdown("""<div class="section-divider"><div class="line"></div>
        <div class="dot"></div><div class="dot" style="margin:0 -4px"></div>
        <div class="dot"></div><div class="line"></div></div>""", unsafe_allow_html=True)

        tpz = int(df['Cantidad'].sum()) if 'Cantidad' in df.columns else len(df)
        tl = len(df)
        mu = df['Material'].nunique() if 'Material' in df.columns else 0
        pv = sum(1 for m in meta if "VECTORIAL" in m)
        pi = sum(1 for m in meta if "GEMINI" in m)

        st.markdown(f"""
        <div class="sec-header"><div class="sec-icon">📋</div>
        <div class="sec-text"><div class="sec-title">Lista de Corte · Exportación Industrial</div>
        <div class="sec-sub">{pv} págs vectoriales + {pi} págs Gemini híbrido</div></div>
        <div class="sec-badge" style="color:#059669;border-color:#a7f3d0;background:#ecfdf5">✓ LISTO</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card emerald"><div class="kpi-label">Líneas</div>
            <div class="kpi-value">{tl}</div><div class="kpi-sub">{pv} det. + {pi} IA</div></div>
            <div class="kpi-card blue"><div class="kpi-label">Piezas</div>
            <div class="kpi-value">{tpz}</div><div class="kpi-sub">Con cantidades</div></div>
            <div class="kpi-card blue"><div class="kpi-label">Materiales</div>
            <div class="kpi-value">{mu}</div><div class="kpi-sub">Tipos</div></div>
            <div class="kpi-card amber"><div class="kpi-label">Alertas</div>
            <div class="kpi-value">{len(al)}</div><div class="kpi-sub">Revisar</div></div>
        </div>""", unsafe_allow_html=True)

        if al:
            with st.expander(f"⚠️ {len(al)} alertas del motor de reglas", expanded=True):
                for a in al:
                    if any(k in a for k in ["🚫","🚨","METAL","KRION","❌"]): st.error(a)
                    elif any(k in a for k in ["🔄","⚠️","sospechoso"]): st.warning(a)
                    else: st.info(a)

        st.markdown("""<div class="table-label"><div class="bar"></div>
        <span>Tabla editable · Doble clic para modificar</span></div>""", unsafe_allow_html=True)

        if mostrar_debug and 'Largo_IA' in df.columns:
            cc = {
                "ID": st.column_config.TextColumn("ID",width="small"),
                "Nombre": st.column_config.TextColumn("Nombre",width="medium"),
                "Largo_IA": st.column_config.NumberColumn("L (IA)",format="%.1f",width="small"),
                "Largo_Corte": st.column_config.NumberColumn("L CORTE",format="%.1f",width="small"),
                "Ancho_IA": st.column_config.NumberColumn("A (IA)",format="%.1f",width="small"),
                "Ancho_Corte": st.column_config.NumberColumn("A CORTE",format="%.1f",width="small"),
                "Espesor": st.column_config.NumberColumn("Esp",format="%.0f",width="small"),
                "Material": st.column_config.TextColumn("Material",width="medium"),
                "Cantidad": st.column_config.NumberColumn("Cant",format="%d",width="small"),
                "Confianza": st.column_config.TextColumn("🔒",width="small"),
                "Regla": st.column_config.TextColumn("Regla",width="large"),
                "Notas": st.column_config.TextColumn("Notas",width="medium"),
            }
        else:
            cc = {
                "Nombre": st.column_config.TextColumn("Nombre",width="medium"),
                "Largo": st.column_config.NumberColumn("Largo",format="%.1f mm",width="small"),
                "Ancho": st.column_config.NumberColumn("Ancho",format="%.1f mm",width="small"),
                "Espesor": st.column_config.NumberColumn("Esp",format="%.0f mm",width="small"),
                "Material": st.column_config.TextColumn("Material",width="medium"),
                "Cantidad": st.column_config.NumberColumn("Cant",format="%d",width="small"),
                "Notas": st.column_config.TextColumn("Notas",width="large"),
            }

        df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True,
                               height=600, column_config=cc)

        st.markdown("""<div class="section-divider"><div class="line"></div>
        <div class="dot"></div><div class="line"></div></div>""", unsafe_allow_html=True)

        csv_l = pd.DataFrame([p.to_csv_row() for p in po]) if po else df_ed
        csv_b = csv_l.to_csv(index=False, sep=";").encode('utf-8')

        c_csv, c_aud, c_inf = st.columns([2,2,3])
        with c_csv:
            st.download_button(f"⬇ CSV · {nb}_corte.csv", data=csv_b,
                               file_name=f"{nb}_corte.csv", mime="text/csv",
                               type="primary", use_container_width=True)
        with c_aud:
            inf = Auditoria.generar(po, al, perfil_sel,
                                    st.session_state.get('_last_file','N/A'))
            st.download_button("📄 AUDITORÍA", data=inf.encode('utf-8'),
                               file_name=f"{nb}_auditoria.txt", mime="text/plain",
                               use_container_width=True)
        with c_inf:
            st.caption(f"CSV: (;) · UTF-8 · Compatible WinCut, CutRite, Ardis\n"
                       f"Auditoría: trazabilidad completa")

# ══════════════════════════════════════════════════════════════════════════════
# 20. FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="corp-footer">
    <div class="footer-logo-text">GABBIANI MASTER AI</div>
    <div class="footer-sub">v6.0 Enterprise · {GEMINI_MODEL} · {backend_label} · Pipeline Dual Concurrente {MAX_WORKERS}x</div>
    <div class="footer-copy">© 2025 · SISTEMA EXPERTO DE OPTIMIZACIÓN DE CORTE INDUSTRIAL</div>
</div>""", unsafe_allow_html=True)
