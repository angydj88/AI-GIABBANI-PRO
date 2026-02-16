import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import io

# --- 1. CONFIGURACIÓN Y SECRETOS ---
st.set_page_config(page_title="Corte Gabbiani AI - Pro", layout="wide", page_icon="🪚")

# Gestión segura de la API Key para la nube
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Fallback para local si tienes un archivo .env o quieres probar rápido (no recomendado para prod)
    # API_KEY = "TU_CLAVE_AQUI_SOLO_PARA_LOCAL"
    st.error("⚠️ No se ha detectado la API Key. Configúrala en los 'Secrets' de Streamlit Cloud.")
    st.stop()

# --- 2. EL CEREBRO DEL OPERARIO (LÓGICA PYTHON) ---
class CerebroOperario:
    def __init__(self):
        # Configuración de tu máquina (Gabbiani Galaxy)
        self.ANCHO_MINIMO_PINZA = 70   # mm (Por debajo de esto, es peligroso)
        self.ANCHO_SEGURIDAD = 130     # mm (Medida a la que forzamos el corte)
        self.MARGEN_SANEADO = 60       # mm (Para piezas pegadas/sándwich)
        self.MARGEN_CNC = 10           # mm (Para piezas curvas)

    def normalizar_material(self, texto_material):
        """Traduce lo que lee la IA a códigos de WinCut"""
        mat = str(texto_material).upper()
        if "BLANCO" in mat or "CAOLIN" in mat: return "W980"
        if "ELEGANCE" in mat or "M6317" in mat: return "M6317"
        if "FONDO" in mat or "OCULTO" in mat: return "16 B"
        return texto_material # Si no sabe, devuelve lo original

    def procesar_lista(self, datos_crudos):
        lista_final = []
        alertas = []

        for pieza in datos_crudos:
            # Copiamos datos base
            p = {
                "ID": pieza.get("id", "??"),
                "Nombre": pieza.get("nombre", "Sin Nombre"),
                "Largo": float(pieza.get("largo", 0)),
                "Ancho": float(pieza.get("ancho", 0)),
                "Espesor": float(pieza.get("espesor", 19)),
                "Material": self.normalizar_material(pieza.get("material", "")),
                "Cantidad": int(pieza.get("cantidad", 1)),
                "Notas": pieza.get("notas", "")
            }

            # --- REGLA 1: CAJONES QUBE (Ingeniería Inversa) ---
            # Si la IA detecta que es un fondo de cajón Qube, corregimos la medida
            if "QUBE" in p['Notas'].upper() or "QUBE" in p['Nombre'].upper():
                if "FONDO" in p['Nombre'].upper():
                    # La IA suele leer el largo nominal (ej: 300). 
                    # Python sabe que el corte real es Nominal - 20mm.
                    if p['Ancho'] == 300: p['Ancho'] = 280
                    if p['Ancho'] == 500: p['Ancho'] = 480
                    p['Notas'] += " | CORTE QUBE (Nominal-20)"
                    alertas.append(f"🔧 {p['Nombre']}: Ajustado fondo cajón Qube.")

            # --- REGLA 2: SÁNDWICH (Pegado) ---
            if "PEGAR" in p['Notas'].upper() or "DOBLE" in p['Notas'].upper() or "+" in str(p['Espesor']):
                p['Largo'] += self.MARGEN_SANEADO
                p['Ancho'] += self.MARGEN_SANEADO
                p['Notas'] += f" | SANEADO +{self.MARGEN_SANEADO}mm"
                alertas.append(f"🥪 {p['Nombre']}: Añadido margen de pegado.")

            # --- REGLA 3: FORMAS IRREGULARES (CNC) ---
            if "CURVA" in p['Notas'].upper() or "CNC" in p['Notas'].upper():
                p['Largo'] += self.MARGEN_CNC
                p['Ancho'] += self.MARGEN_CNC
                p['Notas'] += f" | MARGEN CNC +{self.MARGEN_CNC}mm"

            # --- REGLA 4: SEGURIDAD PINZAS (La más importante) ---
            # Se aplica al final, sobre las medidas ya corregidas
            if p['Ancho'] < self.ANCHO_MINIMO_PINZA:
                medida_original = p['Ancho']
                p['Ancho'] = self.ANCHO_SEGURIDAD
                p['Notas'] += f" | RECORTAR A {medida_original} MANUAL"
                alertas.append(f"🚨 {p['Nombre']}: PINZAS! Ancho {medida_original} -> {self.ANCHO_SEGURIDAD}")
            
            # A veces la máquina coge por el largo si es muy corto
            elif p['Largo'] < self.ANCHO_MINIMO_PINZA:
                medida_original = p['Largo']
                p['Largo'] = self.ANCHO_SEGURIDAD
                p['Notas'] += f" | RECORTAR A {medida_original} MANUAL"
                alertas.append(f"🚨 {p['Nombre']}: PINZAS! Largo {medida_original} -> {self.ANCHO_SEGURIDAD}")

            lista_final.append(p)

        return lista_final, alertas

# --- 3. EL OJO DE LA IA (GEMINI) ---
def analizar_imagen_con_ia(imagen):
    genai.configure(api_key=API_KEY)
    # Usamos Flash para velocidad, o Pro para mayor razonamiento si falla
    model = genai.GenerativeModel('gemini-1.5-flash') 

    prompt_maestro = """
    Eres un experto lector de planos técnicos OCR.
    Tu misión: Extraer una lista JSON con las piezas que aparecen en la imagen.
    
    REGLAS DE EXTRACCIÓN:
    1. Extrae ID, Nombre, Largo (medida mayor), Ancho (medida menor), Espesor, Material, Cantidad.
    2. Si ves notas como "Pegar", "Qube", "Curva", añádelas al campo "notas".
    3. NO calcules márgenes. NO cambies medidas. Solo copia lo que ves escrito.
    4. Si ves un mueble "Cajón", intenta extraer el Frente, la Trasera y el Fondo por separado si están listados.
    
    FORMATO JSON ESTRICTO:
    [
        {"id": "P13_01", "nombre": "Costado", "largo": 600, "ancho": 300, "espesor": 19, "material": "Blanco", "cantidad": 2, "notas": ""},
        ...
    ]
    """
    
    try:
        response = model.generate_content([prompt_maestro, imagen])
        # Limpieza quirúrgica del JSON (Gemini a veces mete markdown)
        texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except Exception as e:
        st.error(f"Error de lectura IA: {e}")
        return []

# --- 4. INTERFAZ DE USUARIO (FRONTEND) ---
st.title("🏭 Sistema de Corte Gabbiani (IA + Python)")
st.markdown("Suba el plano (JPG/PNG). La IA leerá los datos y **Python aplicará las reglas de seguridad**.")

uploaded_file = st.file_uploader("Arrastra aquí tu plano", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Layout de dos columnas
    col_img, col_data = st.columns([1, 1.5])

    with col_img:
        st.image(uploaded_file, caption="Plano Original", use_column_width=True)
        btn_procesar = st.button("⚡ ANALIZAR Y APLICAR REGLAS", type="primary", use_container_width=True)

    if btn_procesar:
        with st.spinner("🤖 La IA está leyendo... 🧠 Python está calculando..."):
            # 1. Cargar
            img = Image.open(uploaded_file)
            # 2. IA
            datos_ia = analizar_imagen_con_ia(img)
            
            if datos_ia:
                # 3. Python (Cerebro)
                cerebro = CerebroOperario()
                datos_finales, alertas = cerebro.procesar_lista(datos_ia)
                
                # Guardar en estado para que no desaparezca
                st.session_state['df_resultado'] = pd.DataFrame(datos_finales)
                st.session_state['alertas'] = alertas
            else:
                st.error("La IA no pudo encontrar piezas legibles en esta imagen.")

    # Mostrar resultados si existen
    if 'df_resultado' in st.session_state:
        with col_data:
            st.subheader("✅ Lista de Corte Optimizada")
            
            # Panel de Alertas
            if st.session_state['alertas']:
                with st.expander(f"⚠️ {len(st.session_state['alertas'])} REGLAS APLICADAS (Revisar)", expanded=True):
                    for a in st.session_state['alertas']:
                        if "PINZAS" in a: st.error(a) # Rojo para pinzas
                        elif "SÁNDWICH" in a: st.warning(a) # Amarillo para pegados
                        else: st.info(a) # Azul para info

            # Tabla Editable
            df_editado = st.data_editor(
                st.session_state['df_resultado'],
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Largo": st.column_config.NumberColumn(format="%d mm"),
                    "Ancho": st.column_config.NumberColumn(format="%d mm"),
                }
            )

            # Exportación
            csv_buffer = io.StringIO()
            # WinCut suele usar punto y coma (;)
            df_editado.to_csv(csv_buffer, index=False, sep=";")
            
            st.download_button(
                label="💾 DESCARGAR CSV PARA WINCUT",
                data=csv_buffer.getvalue().encode('utf-8'),
                file_name="corte_gabbiani.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )