import streamlit as st
import requests
import base64
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÕES E CORES (TKE)
# =============================================================================
st.set_page_config(page_title="Relatório Avanutri TKE", layout="wide")

# Definição da Paleta de Cores TKE
COR_PRIMARIA = "#9e747a"       # Substitui o #00ada8 (Verde Teal)
COR_SECUNDARIA = "#b09ca0"     # Substitui o #929da7 (Cinza azulado)
COR_TEXTO = "#5e4b4f"          # Substitui o texto padrão
COR_FUNDO_CINZA = "#f2eff0"    # Fundo claro para áreas cinzas

# Nome do arquivo de logo (deve estar na mesma pasta)
ARQUIVO_LOGO = "logo.png" 

# =============================================================================
# 2. IMAGEM DO CORPO (SVG EMBUTIDO)
# =============================================================================
# Isso substitui o arquivo 'corpo.svg' para o código não quebrar
SVG_CORPO = """
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 600">
<g fill="none" stroke="#e0e0e0" stroke-width="2">
  <path d="M150,50 C170,50 180,70 180,90 C180,105 170,120 150,120 C130,120 120,105 120,90 C120,70 130,50 150,50 Z" />
  <path d="M120,120 L80,140 L70,280 L50,350" /> 
  <path d="M180,120 L220,140 L230,280 L250,350" />
  <path d="M120,120 L120,300 L110,550" />
  <path d="M180,120 L180,300 L190,550" />
  <path d="M120,300 L180,300" />
</g>
</svg>
"""
B64_CORPO = base64.b64encode(SVG_CORPO.encode('utf-8')).decode("utf-8")

# =============================================================================
# 3. CSS (ADAPTADO COM SUAS CORES)
# =============================================================================
# Aqui eu peguei o CSS que você mandou e troquei as cores hardcoded pelas variáveis
CSS_TEMPLATE = f"""
<style>
    /* BASE STYLES */
    #container {{ width: 800px; margin: auto; background: white; padding: 20px; }}
    @media (max-width: 700px) {{ #container {{ width: 100%; margin: 0; }} }}
    .moldura {{ border-radius: 10px; border: 2px solid #AAA; overflow: hidden; }}
    .container-padding-lateral {{ padding: 0px 20px; }}
    .rolavel {{ overflow: auto; }}
    
    h1 {{ color: {COR_PRIMARIA}; font-size: 20px; margin-bottom: 4px; border-bottom: 1px solid #ddd; }}
    h2 {{ color: {COR_PRIMARIA}; font-size: 15px; margin-bottom: 4px; }}
    
    .font-p {{ font-size: 12px; }}
    .font-m {{ font-size: 14px; }}
    .font-g {{ font-size: 16px; }}
    .align-center {{ text-align: center; }}
    .align-right {{ text-align: right; }}
    .font-bold {{ font-weight: bold; }}

    /* CORPO CSS */
    .corpo {{
        background-image: url('data:image/svg+xml;base64,{B64_CORPO}');
        background-position: center;
        background-repeat: no-repeat;
        height: 320px;
    }}
    /* Posicionamentos do corpo (mantidos do seu CSS original) */
    .corpo>div:nth-child(1) {{ text-align: right; }}
    .corpo>div:nth-child(1)>div:nth-child(2) {{ margin-top: 10px; }}
    .corpo>div:nth-child(1)>div:nth-child(3) {{ margin-top: 30px; }}
    .corpo>div:nth-child(1)>div:nth-child(4) {{ margin-top: 63px; }}
    .corpo>div:nth-child(2) {{ text-align: center; margin-top: 66px; }}
    .corpo>div:nth-child(3)>div:nth-child(2) {{ margin-top: 10px; }}
    .corpo>div:nth-child(3)>div:nth-child(3) {{ margin-top: 140px; }}
    .lado-corpo {{ font-size: 1.2em; font-weight: bold; color: {COR_SECUNDARIA}; }}

    /* GRID CSS */
    .grid-container-2c {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); grid-gap: 10px; }}
    .grid-container-3c-paciente {{ display: grid; grid-template-columns: minmax(310px, 1fr) minmax(110px, 0.4fr) minmax(110px, 0.4fr); grid-gap: 10px; }}
    .grid-container-3c-corpo {{ display: grid; grid-template-columns: 1fr 150px 1fr; grid-gap: 10px; }}
    .grid-container-normalidades {{ display: grid; grid-template-columns: 150px 2.3fr 1.8fr 6fr; grid-gap: 3px; min-width: 570px; }}
    .grid-container-impedancias {{ display: grid; grid-template-columns: 55px 1fr 1fr 1fr 1fr 1fr; grid-gap: 3px; }}
    .grid-container-dados-adicionais {{ display: grid; grid-template-columns: 106px 1fr; grid-gap: 4px; }}
    .grid-container-3c-dados-adicionais {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); grid-gap: 10px; }}

    .cel-cinza, .cel-verde {{ font-weight: bold; color: #FFF; align-items: center; display: grid; padding: 4px; border-radius: 4px; }}
    .cel-cinza {{ background-color: {COR_SECUNDARIA}; }}
    .cel-verde {{ background-color: {COR_PRIMARIA}; }}
    .cel-header {{ color: #FFF; font-size: 14px; font-weight: bold; text-align: center; padding: 4px; }}
    .cel-label {{ color: #FFF; font-size: 14px; font-weight: bold; padding: 4px 10px; height: 41px; display: flex; align-items: center; }}
    
    /* GERAL */
    body {{ font-family: Arial, sans-serif; margin: 0; color: {COR_TEXTO}; font-size: 10pt; }}
    .header {{ margin-bottom: 10px; }}
    .logo-cel img {{ max-height: 80px; }}
    .user-cel {{ text-align: right; }}
    .dados-paciente {{ background-color: {COR_FUNDO_CINZA}; padding: 10px 20px; }}
    .dados-paciente .label {{ font-weight: bold; color: {COR_PRIMARIA}; display: inline; }}
    .barra-baixo {{ border-bottom: 5px solid {COR_PRIMARIA}; padding-bottom: 12px; }}
    
    /* Barras gráficas (Simulação Visual) */
    .barra-grafico-container {{ background: #eee; height: 15px; margin-top: 5px; width: 100%; border-radius: 3px; }}
    .barra-grafico {{ background-color: {COR_PRIMARIA}; height: 100%; display: block; border-radius: 3px; }}
</style>
"""

# =============================================================================
# 4. FUNÇÕES LÓGICAS
# =============================================================================

def get_base64_logo():
    try:
        with open(ARQUIVO_LOGO, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except FileNotFoundError:
        return "" 

def fmt(valor, decimais=1):
    if valor is None: return "-"
    try: return f"{float(valor):.{decimais}f}".replace('.', ',')
    except: return str(valor)

def calc_idade(nasc_str):
    try:
        nasc = datetime.fromisoformat(nasc_str)
        hoje = datetime.now()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except: return "-"

def calc_width(val, min_v, max_v):
    # Calcula largura da barra (0 a 100%) baseado no min/max
    try:
        v, mn, mx = float(val), float(min_v), float(max_v)
        # Lógica simples: Min é 20%, Max é 80% da barra visual
        range_val = mx - mn
        if range_val == 0: return "50%"
        pos = 20 + ((v - mn) / range_val) * 60 
        pos = max(5, min(100, pos)) # Limita entre 5% e 100%
        return f"{pos}%"
    except: return "0%"

def obter_dados(url):
    try:
        if "#" not in url: return None
        rid = url.split("#")[1]
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(f"https://balancaapi.avanutrionline.com/Relatorio/{rid}", headers=headers)
        return resp.json() if resp.status_code == 200 else
