import streamlit as st
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório Clínica", page_icon="🏥", layout="wide")

# --- NOME DO ARQUIVO DE LOGO ---
LOGO_FILENAME = "logoTKE.png"

# --- PALETA DE CORES PERSONALIZADA ---
COLORS = {
    "verde_substituto": "#9e747a",  # Rosa Queimado
    "fundo": "#f5f1f2",             # Rosa/Cinza Claríssimo
    "escuro": "#72464e",            # Marrom/Roxo Escuro
    "claro": "#e2d5d7"              # Rosa Pálido
}

# --- FUNÇÕES AUXILIARES ---

def get_base64_logo():
    """Lê a imagem local e converte para base64 para embutir no HTML"""
    try:
        with open(LOGO_FILENAME, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

def formatar_numero(valor, decimais=1):
    if valor is None: return "-"
    try: return f"{float(valor):.{decimais}f}".replace('.', ',')
    except: return str(valor)

def calcular_idade(data_nascimento_str):
    if not data_nascimento_str: return "-"
    try:
        nasc = datetime.fromisoformat(data_nascimento_str)
        hoje = datetime.now()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except: return "-"

def obter_dados_api(url_relatorio):
    try:
        if "#" not in url_relatorio: return None
        report_id = url_relatorio.split("#")[1]
        # URL da API
        url_api = f"https://balancaapi.avanutrionline.com/Relatorio/{report_id}"
        
        # Headers para simular navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url_api, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- GERAÇÃO DO HTML ---
def gerar_html_relatorio(dados, logo_b64):
    if not dados: return "<h1>Erro ao processar dados.</h1>"
    
    paciente = dados.get('paciente', {})
    av = dados.get('avaliacoes', [])[-1]
    corpo = av.get('dadosCorpo', {})
    membros = av.get('dadosMembros', []) 
    freqs = av.get('dadosFrequencia', [])
    
    # Helper para Impedância
    def get_imp(khz, membro_key):
        item = next((f for f in freqs if f.get('frequency') == khz), {})
        return formatar_numero(item.get(membro_key), 0)

    # Helper para Membros
    def get_membro(idx, campo):
        if idx < len(membros):
            return formatar_numero(membros[idx].get('composicaoCorporal', {}).get(campo))
        return "-"

    # Tratamento da Logo no HTML
    html_logo = ""
    if logo_b64:
        html_logo = f'<img src="data:image/png;base64,{logo_b64}" alt="Logo" />'
    else:
        # Se a imagem falhar, mostra o nome em texto
        html_logo = f'<div style="font-size:24px; font-weight:bold; color:{COLORS["escuro"]}">{dados.get("user", {}).get("clinicaNome", "Clínica")}</div>'

    # CSS INJETADO
    css_style = f"""
    <style>
        :root {{
            --cor-principal: {COLORS['verde_substituto']};
            --cor-fundo: {COLORS['fundo']};
            --cor-texto: {COLORS['escuro']};
            --cor-secundaria: {COLORS['claro']};
        }}
        
        body {{
            font-family: 'Segoe UI', sans-serif;
            background-color: var(--cor-fundo);
            color: var(--cor-texto);
            margin: 0; padding: 20px;
        }}
        
        .grid-container-2c {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .grid-container-3c-paciente {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }}
        .grid-container-normalidades {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 5px; align-items: center; }}
        .grid-container-3c-corpo {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center; }}
        .grid-container-impedancias {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 2px; }}
        
        .header {{ margin-bottom: 20px; border-bottom: 2px solid var(--cor-principal); padding-bottom: 10px; }}
        .logo-cel img {{ max-height: 80px; }}
        .user-cel {{ text-align: right; font-weight: bold; color: var(--cor-texto); }}
        
        .moldura {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            max-width: 1000px;
            margin: 0 auto;
        }}

        h1, h2 {{ color: var(--cor-texto); text-transform: uppercase; font-size: 1.2rem; border-bottom: 1px solid var(--cor-secundaria); padding-bottom: 5px; margin-top: 20px; }}
        .label {{ font-weight: bold; color: var(--cor-principal); display: inline-block; margin-right: 5px; }}
        
        .cel-verde {{ background-color: var(--cor-principal); color: white; padding: 5px; border-radius: 4px; text-align: center; }}
        .cel-cinza {{ background-color: var(--cor-secundaria); color: var(--cor-texto); padding: 5px; border-radius: 4px; }}
        .cel-header {{ font-weight: bold; text-align: center; margin-bottom: 5px; }}
        
        .lado-corpo {{ font-weight: bold; margin-bottom: 10px; display: block; color: var(--cor-principal); }}
        .display-centro-corpo-k {{ font-size: 2rem; font-weight: bold; color: var(--cor-texto); margin-top: 20px; }}
        
        .barra-baixo {{ border-bottom: 1px dashed var(--cor-secundaria); padding-bottom: 15px; margin-bottom: 15px; }}
        .grid-container-impedancias > div {{ font-size: 0.85rem; }}
        .font-bold {{ font-weight: bold; }}
    </style>
    """

    # HTML COMPLETO
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8">{css_style}</head>
    <body>
        <div class="moldura">
            <div class="header grid-container-2c">
                <div class="logo-cel">{html_logo}</div>
                <div class="user-cel">
                    <div class="nome">{dados.get('user', {}).get('clinicaNome') or 'Minha Clínica'}</div>
                    <div class="endereco">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
                </div>
            </div>
        
            <div class="dados-paciente barra-baixo">
                <div class="grid-container-3c-paciente">
                    <div><span class="label">Nome:</span>{paciente.get('nome')}</div>
                    <div><span class="label">Estatura:</span>{formatar_numero(paciente.get('estaturaCm',0)/100, 2)}m</div>
                    <div><span class="label">Data:</span>{datetime.fromisoformat(av.get('data')).strftime('%d/%m/%Y')}</div>
                    <div><span class="label">Email:</span>{paciente.get('email')}</div>
                    <div><span class="label">Sexo:</span>{'F' if paciente.get('sexo')==70 else 'M'}</div>
                    <div><span class="label">Idade:</span>{calcular_idade(paciente.get('dataNascimento'))}</div>
                </div>
            </div>

            <h1>Análise Global Resumida</h1>
            <div class="grid-container-normalidades">
                <div class="cel-cinza cel-header">Indicador</div> <div class="cel-verde cel-header">Valor</div> <div class="cel-cinza cel-header">Mín</div> <div class="cel-verde cel-header">Máx</div>

                <div class="cel-cinza">Peso</div> <div class="cel-verde">{formatar_numero(av.get('peso'))} kg</div> <div class="cel-cinza">{formatar_numero(corpo.get('pesoMin'))}</div> <div class="cel-verde">{formatar_numero(corpo.get('pesoMax'))}</div>
                <div class="cel-cinza">IMC</div> <div class="cel-verde">{formatar_numero(corpo.get('bmi'))}</div> <div class="cel-cinza">18,5</div> <div class="cel-verde">24,9</div>
                <div class="cel-cinza">% Gordura</div> <div class="cel-verde">{formatar_numero(corpo.get('fmPercentual'))}%</div> <div class="cel-cinza">{formatar_numero(corpo.get('fmMinPercentual'))}</div> <div class="cel-verde">{formatar_numero(corpo.get('fmMaxPercentual'))}</div>
                <div class="cel-cinza">Massa Muscular</div> <div class="cel-verde">{formatar_numero(corpo.get('ssm'))} kg</div> <div class="cel-cinza">{formatar_numero(corpo.get('ssmMin'))}</div> <div class="cel-verde">{formatar_numero(corpo.get('ssmMax'))}</div>
                <div class="cel-cinza">Água Total</div> <div class="cel-verde">{formatar_numero(corpo.get('tbw'))} L</div> <div class="cel-cinza">{formatar_numero(corpo.get('tbwMin'))}</div> <div class="cel-verde">{formatar_numero(corpo.get('tbwMax'))}</div>
            </div>

            <h1>Análise de Massa Magra (kg)</h1>
            <div class="grid-container-3c-corpo">
                <div><div class="lado-corpo">Direito</div><div><b>Braço:</b> {get_membro(0, 'ffm')}</div><div><b>Tronco:</b> {get_membro(2, 'ffm')}</div><div><b>Perna:</b> {get_membro(3, 'ffm')}</div></div>
                <div><div class="display-centro-corpo-k">{formatar_numero(corpo.get('ffm'))} kg</div><div>Massa Livre de Gordura Total</div></div>
                <div><div class="lado-corpo">Esquerdo</div><div><b>Braço:</b> {get_membro(1, 'ffm')}</div><div><b>Tronco:</b> -</div><div><b>Perna:</b> {get_membro(4, 'ffm')}</div></div>
            </div>

            <h1>Análise de Gordura (kg)</h1>
            <div class="grid-container-3c-corpo">
                <div><div class="lado-corpo">Direito</div><div><b>Braço:</b> {get_membro(0, 'fm')}</div><div><b>Tronco:</b> {get_membro(2, 'fm')}</div><div><b>Perna:</b> {get_membro(3, 'fm')}</div></div>
                <div><div class="display-centro-corpo-k">{formatar_numero(corpo.get('fm'))} kg</div><div>Massa Gorda Total</div></div>
                <div><div class="lado-corpo">Esquerdo</div><div><b>Braço:</b> {get_membro(1, 'fm')}</div><div><b>Tronco:</b> -</div><div><b>Perna:</b> {get_membro(4, 'fm')}</div></div>
            </div>

            <div class="grid-container-2c" style="margin-top: 30px;">
                <div>
                    <h2>Metabolismo</h2>
                    <div class="grid-container-2c">
                        <div class="cel-cinza">Taxa Metabólica Basal</div><div class="cel-verde font-bold">{formatar_numero(av.get('taxaMetabolicaBasal'), 0)} kcal</div>
                        <div class="cel-cinza">Idade Metabólica</div><div class="cel-verde font-bold">{av.get('idadeMetabolica')} anos</div>
                        <div class="cel-cinza">Gordura Visceral</div><div class="cel-verde font-bold">Nível {corpo.get('vfl')}</div>
                    </div>
                </div>
                <div>
                    <h2>Impedâncias (Ω)</h2>
                    <div class="grid-container-impedancias">
                        <div class="cel-cinza">Freq</div> <div class="cel-cinza">BD</div> <div class="cel-cinza">BE</div> <div class="cel-cinza">TR</div> <div class="cel-cinza">PD</div> <div class="cel-cinza">PE</div>
                        <div class="cel-verde">5k</div> <div>{get_imp(5, 'impedanceRightArm')}</div> <div>{get_imp(5, 'impedanceLeftArm')}</div> <div>{get_imp(5, 'impedanceTrunk')}</div> <div>{get_imp(5, 'impedanceRightLeg')}</div> <div>{get_imp(5, 'impedanceLeftLeg')}</div>
                        <div class="cel-verde">50k</div> <div>{get_imp(50, 'impedanceRightArm')}</div> <div>{get_imp(50, 'impedanceLeftArm')}</div> <div>{get_imp(50, 'impedanceTrunk')}</div> <div>{get_imp(50, 'impedanceRightLeg')}</div> <div>{get_imp(50, 'impedanceLeftLeg')}</div>
                        <div class="cel-verde">250k</div> <div>{get_imp(250, 'impedanceRightArm')}</div> <div>{get_imp(250, 'impedanceLeftArm')}</div> <div>{get_imp(250, 'impedanceTrunk')}</div> <div>{get_imp(250, 'impedanceRightLeg')}</div> <div>{get_imp(250, 'impedanceLeftLeg')}</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# --- INTERFACE STREAMLIT ---

st.title("🏥 Visualizador de Relatório Personalizado")
st.markdown("Cole o link completo do relatório Avanutri abaixo para gerar a versão com sua identidade visual.")

url_input = st.text_input("Link do Relatório:", placeholder="https://d196bwsv53491l.cloudfront.net/relatorios/...")

if st.button("Gerar Relatório"):
    if url_input:
        with st.spinner("Processando dados e gerando layout..."):
            dados = obter_dados_api(url_input)
            
            if dados:
                # Carrega logo (Tenta ler arquivo local)
                logo_b64 = get_base64_logo()
                
                # Gera HTML
                html_final = gerar_html_relatorio(dados, logo_b64)
                
                # Renderiza
                st.components.v1.html(html_final, height=1200, scrolling=True)
                
                # Botão Download
                st.download_button(
                    label="📥 Baixar HTML para Imprimir/Salvar",
                    data=html_final,
                    file_name=f"Relatorio_{dados['paciente']['nome']}.html",
                    mime="text/html"
                )
            else:
                st.error("Erro: Link inválido ou falha na conexão com Avanutri.")
    else:
        st.warning("Cole o link antes de clicar.")
