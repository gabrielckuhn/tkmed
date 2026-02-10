import streamlit as st
import requests
import json
import base64
import os
import streamlit.components.v1 as components

# Configuração da página Streamlit
st.set_page_config(layout="centered", page_title="Gerador de Relatórios")

# --- FUNÇÕES AUXILIARES ---

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return "" # Retorna vazio se não achar, para não quebrar o script

def fetch_data(report_id):
    # URL de exemplo baseada no seu código
    url = f"https://balancaapi.avanutrionline.com/Relatorio/{report_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Erro ao buscar dados do relatório. Verifique o ID.")
        return None

def extract_id_from_url(input_url):
    if not input_url: return ""
    if "#" in input_url: return input_url.split("#")[-1]
    return input_url

# --- CONFIGURAÇÃO VISUAL ---
COLOR_PRIMARY = "#9e747a"
COLOR_BG = "#f5f1f2"
COLOR_DARK = "#72464e"
COLOR_LIGHT = "#e2d5d7"
COLOR_CHART_FILL = "rgba(158, 116, 122, 0.4)"
COLOR_CHART_STROKE = "rgba(158, 116, 122, 1)"

# Tente carregar as imagens, ou use placeholders transparentes se não existirem
logo_b64 = get_base64_image("logoTKE.png")
corpo_b64 = get_base64_image("corpo.png")

# --- CSS DO RELATÓRIO ---
html_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* --- CONFIGURAÇÃO DE IMPRESSÃO A4 --- */
    @page {{
        size: A4;
        margin: 0;
    }}

    @media print {{
        body, html {{
            width: 210mm;
            height: 297mm;
            margin: 0 !important;
            padding: 0 !important;
            background-color: white !important;
        }}
        #container {{
            width: 100% !important;
            min-height: 100% !important;
            margin: 0 !important;
            box-shadow: none !important;
            border: none !important;
            border-radius: 0 !important;
            transform: scale(1) !important;
        }}
        /* Garante que cores de fundo e imagens apareçam na impressão */
        * {{
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        .barra-corpos {{ display: block !important; }}
    }}

    body {{
        font-family: 'Roboto', Arial, sans-serif;
        margin: 0; padding: 0;
        background-color: #525659;
        display: flex;
        justify-content: center;
        min-height: 100vh;
    }}

    #container {{
        width: 793px; /* Largura pixel perfect para A4 em 96dpi */
        min-height: 1122px;
        margin: 30px auto;
        background-color: {COLOR_BG};
        padding: 0;
        box-sizing: border-box;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        position: relative;
    }}

    /* --- ESTILOS INTERNOS --- */
    .moldura {{ border-radius: 10px; border: 2px solid {COLOR_LIGHT}; overflow: hidden; background-color: {COLOR_BG}; margin: 20px; }}
    .container-padding-lateral {{ padding: 0px 20px; }}
    .rolavel {{ overflow: visible; }}

    h1, h2 {{ color: {COLOR_PRIMARY}; margin-bottom: 4px; margin-top: 5px; }}
    h1 {{ font-size: 20px; }}
    h2 {{ font-size: 15px; }}

    .font-p {{ font-size: 12px; }}
    .font-m {{ font-size: 14px; }}
    .font-g {{ font-size: 16px; }}
    .font-bold {{ font-weight: bold; }}
    .align-center {{ text-align: center; }}
    .align-right {{ text-align: right; }}

    /* CORPO */
    .corpo {{ 
        background-image: url('data:image/png;base64,{corpo_b64}'); 
        background-position: center; 
        background-repeat: no-repeat; 
        background-size: contain; 
        height: 320px; 
        position: relative;
    }}
    /* Ajustes posicionais baseados no seu CSS original */
    .corpo>div:nth-child(1) {{ text-align: right; }}
    .corpo>div:nth-child(2) {{ text-align: center; margin-top: 66px; }}
    
    .lado-corpo {{ font-size: 1.2em; font-weight: bold; color: {COLOR_LIGHT}; }}

    /* GRIDS */
    .grid-container-2c {{ display: grid; grid-template-columns: 1fr 1fr; grid-gap: 10px; }}
    .grid-container-3c {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); grid-gap: 10px; }}
    .grid-container-6c {{ display: grid; grid-template-columns: repeat(11, 1fr); grid-gap: 0; }}
    
    /* Layout específico para normalidades */
    .normalidade-row {{
        display: flex;
        align-items: center;
        margin-bottom: 5px;
        justify-content: space-between;
    }}
    .normalidade-label {{ width: 130px; font-weight: bold; font-size: 12px; color: {COLOR_DARK}; }}
    .normalidade-escala {{ flex-grow: 1; display: flex; justify-content: space-between; font-size: 10px; padding-left: 10px; }}
    .normalidade-escala > div {{ text-align: center; width: 100%; }}
    .normalidade-escala > div > div {{ height: 5px; background-color: {COLOR_LIGHT}; margin-bottom: 2px; border-right: 1px solid #FFF; }}
    
    /* HEADER */
    .header {{ padding: 20px 20px 10px 20px; display: flex; justify-content: space-between; align-items: center; }}
    .logo-cel img {{ max-height: 60px; }}
    .user-cel {{ text-align: right; color: {COLOR_DARK}; }}
    .user-cel .nome {{ font-size: 14pt; font-weight: bold; }}
    
    .dados-paciente {{ background-color: {COLOR_BG}; padding: 10px 20px; border-bottom: 1px solid {COLOR_LIGHT}; border-top: 1px solid {COLOR_LIGHT}; display: flex; justify-content: space-between; flex-wrap: wrap; }}
    .dados-paciente div {{ margin-right: 15px; font-size: 13px; }}
    .dados-paciente .label {{ font-weight: bold; color: {COLOR_DARK}; }}

    /* GRAFICOS */
    #charts {{ width: 100%; border-collapse: separate; border-spacing: 0 5px; margin-top: 20px; }}
    #charts tr td:nth-child(1) {{ width: 110px; background-color: {COLOR_PRIMARY}; font-weight: bold; color: #FFF; padding: 5px; font-size: 11px; vertical-align: middle; border-radius: 4px 0 0 4px; }}
    #charts tr td:nth-child(2) {{ position: relative; height: 70px; border: 1px solid {COLOR_LIGHT}; border-left: none; border-radius: 0 4px 4px 0; }}
    
    .chartPlaceholder {{ width: 100%; height: 100%; }}
    .valor-label {{ font-size: 10px; text-align: center; }}
    .grid-container-6c.datas {{ margin-bottom: 5px; }}
    .grafico-label {{ font-size: 10px; text-align: center; color: {COLOR_DARK}; font-weight: bold; }}

    /* Classes auxiliares */
    .text-primary {{ color: {COLOR_PRIMARY}; }}
    .mt-10 {{ margin-top: 10px; }}
</style>
"""

# --- LÓGICA DO APP (STREAMLIT) ---

st.title("Visualizador de Relatórios A4")

url_input = st.text_input(
    "Link do Relatório", 
    placeholder="Cole aqui o link completo e pressione Enter",
    help="Cole o link (ex: ...#123-abc) e aperte Enter."
)

report_id = extract_id_from_url(url_input)

if report_id:
    with st.spinner('Gerando visualização...'):
        data = fetch_data(report_id)

        if data:
            # Preparação dos dados para injeção no JS
            translations_pt = json.dumps({
                "peso": "Peso (kg)", "percentualGordura_h": "Gordura (%)", 
                "massaGordura_h": "Massa Gorda (kg)", "massaLivreGordura_h": "Massa Livre (kg)",
                "massaMuscularEsqueletica_h": "Músculo Esq. (kg)", "aguaCorporalL_h": "Água Corp. (L)",
                "aguaIntracelularL_h": "Água Intra (L)", "aguaExtracelularL_h": "Água Extra (L)",
                "imc_h": "IMC"
            })
            json_data = json.dumps(data)
            
            # --- JAVASCRIPT ---
            # Reconstruído e completado para funcionar
            js_script = f"""
            <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
            <script>
                const apiData = {json_data};
                const translations = {translations_pt};
                var lang = "pt";
                const sexoTraducoes = {{ pt: {{ male: "Masculino", female: "Feminino" }} }};

                document.addEventListener("DOMContentLoaded", function () {{
                    if (!apiData) return;
                    
                    const data = apiData;
                    
                    // Preencher Header e Paciente
                    popularDadosUsuario(data.user);
                    popularDadosPaciente(data.paciente);

                    const ultimaAvaliacao = data.avaliacoes[data.avaliacoes.length - 1];
                    document.getElementById("data-avaliacao").innerText = formatarData(ultimaAvaliacao.data || new Date());

                    // Preencher Normalidades
                    if(data.normalidades) {{
                        popularNormalidades(ultimaAvaliacao, data.normalidades);
                    }}

                    // Gerar Gráficos
                    criaLabelGrafico(data.avaliacoes);
                    criarGraficos(data);
                }});

                function popularDadosPaciente(pacienteData) {{
                    document.getElementById("paciente-nome").innerText = pacienteData.nome || "";
                    document.getElementById("sexo").innerText = pacienteData.sexo == 70 ? "Feminino" : "Masculino";
                    document.getElementById("estatura").innerText = (pacienteData.estaturaCm / 100).toFixed(2).replace(".", ",") + "m";
                    document.getElementById("idade").innerText = calcularIdade(pacienteData.dataNascimento) + " anos";
                    document.getElementById("email").innerText = pacienteData.email || "";
                }}

                function popularDadosUsuario(userData) {{
                    const nome = userData.clinicaNome || userData.nome;
                    document.getElementById("clinica-nome").innerText = nome;
                    
                    let end = "";
                    if (userData.clinicaEndereco) end = ${{userData.clinicaEndereco}}, ${{userData.clinicaMunicipio}} - ${{userData.clinicaUF}};
                    else if (userData.endereco) end = ${{userData.endereco}}, ${{userData.municipio}} - ${{userData.uf}};
                    
                    document.getElementById("clinica-endereco").innerText = end;
                }}

                function calcularIdade(dataNascimento) {{
                    const dateNascimento = new Date(dataNascimento);
                    const dataAtual = new Date();
                    const diferenca = dataAtual - dateNascimento;
                    return Math.floor(diferenca / (1000 * 60 * 60 * 24 * 365.25));
                }}

                function formatarData(jsonDate) {{
                    const date = new Date(jsonDate);
                    return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', {{hour: '2-digit', minute:'2-digit'}});
                }}

                function formatarNumeroBrasileiro(numero, casas) {{
                    if(numero === null || numero === undefined) return "-";
                    return numero.toLocaleString('pt-BR', {{ minimumFractionDigits: casas || 0, maximumFractionDigits: casas || 1 }});
                }}

                // --- FUNÇÕES DE GRÁFICOS ---
                function criarGraficos(data) {{
                     const graficos = [
                        ["peso", "peso"], 
                        ["dadosCorpo.fmPercentual", "percentualGordura_h"],
                        ["dadosCorpo.fm", "massaGordura_h"], 
                        ["dadosCorpo.ffm", "massaLivreGordura_h"],
                        ["dadosCorpo.bmi", "imc_h"]
                     ];
                     graficos.forEach(g => criarGrafico(data.avaliacoes, g[0], translations[g[1]] || g[1]));
                }}

                function criaLabelGrafico(avaliacoes) {{
                    // Cria a linha de datas no topo dos gráficos se necessário
                    // Simplificado para este exemplo
                }}

                function criarGrafico(avaliacoesData, prop, label) {{
                    // Pega os ultimos 10 ou todos
                    const dadosRecentes = avaliacoesData.slice(-11);
                    const valores = dadosRecentes.map(a => obterValor(a, prop));
                    const datas = dadosRecentes.map(a => new Date(a.data).toLocaleDateString('pt-BR').slice(0,5));

                    const container = document.getElementById("charts");
                    const tr = document.createElement("tr");
                    
                    // Coluna Nome
                    const tdName = document.createElement("td");
                    tdName.innerText = label;
                    tr.appendChild(tdName);

                    // Coluna Gráfico
                    const tdChart = document.createElement("td");
                    const chartDiv = document.createElement("div");
                    chartDiv.className = "chartPlaceholder";
                    tdChart.appendChild(chartDiv);
                    tr.appendChild(tdChart);

                    container.appendChild(tr);

                    var options = {{
                        series: [{{ name: label, data: valores }}],
                        chart: {{ 
                            type: 'area', 
                            height: 70, 
                            sparkline: {{ enabled: true }} 
                        }},
                        stroke: {{ curve: 'smooth', width: 2, colors: ["{COLOR_CHART_STROKE}"] }},
                        fill: {{ type: 'gradient', gradient: {{ shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.3, stops: [0, 90, 100], colorStops: [ {{ offset: 0, color: "{COLOR_CHART_FILL}", opacity: 0.4 }}, {{ offset: 100, color: "{COLOR_CHART_FILL}", opacity: 0.1 }}] }} }},
                        tooltip: {{ x: {{ show: false }}, y: {{ formatter: function(val) {{ return formatarNumeroBrasileiro(val, 1); }} }} }},
                        colors: ["{COLOR_CHART_STROKE}"]
                    }};

                    const chart = new ApexCharts(chartDiv, options);
                    chart.render();
                }}

                function obterValor(obj, path) {{
                    return path.split('.').reduce((o, k) => (o || {{}})[k], obj);
                }}

                // --- FUNÇÕES DE NORMALIDADE (RECONSTRUÍDAS) ---
                function popularNormalidades(avaliacao, norms) {{
                    // Exemplo: Peso, IMC, Gordura
                    criarBarraNormalidade("Peso", avaliacao.peso, norms.peso);
                    criarBarraNormalidade("Gordura %", avaliacao.dadosCorpo.fmPercentual, norms.fmPerc);
                    criarBarraNormalidade("Massa Gorda", avaliacao.dadosCorpo.fm, norms.fmKg);
                    criarBarraNormalidade("IMC", avaliacao.dadosCorpo.bmi, norms.bmi);
                }}

                function criarBarraNormalidade(label, valor, escala) {{
                    if(!escala) return;
                    const container = document.getElementById("normalidades-container");
                    
                    const row = document.createElement("div");
                    row.className = "normalidade-row";

                    const lbl = document.createElement("div");
                    lbl.className = "normalidade-label";
                    lbl.innerHTML = label + ": <span style='color:{COLOR_PRIMARY}'>" + formatarNumeroBrasileiro(valor, 1) + "</span>";
                    
                    const escalaDiv = document.createElement("div");
                    escalaDiv.className = "normalidade-escala";
                    
                    // Gera sequencia visual
                    const nums = gerarSequenciaComDiferencaFixa(escala.minimo, escala.maximo, 10);
                    nums.forEach(n => {{
                        const item = document.createElement("div");
                        item.innerHTML = <div></div><span>${{Math.round(n)}}</span>;
                        escalaDiv.appendChild(item);
                    }});

                    row.appendChild(lbl);
                    row.appendChild(escalaDiv);
                    container.appendChild(row);
                }}

                function gerarSequenciaComDiferencaFixa(min, max, steps) {{
                    let arr = [];
                    let step = (max - min) / (steps - 1);
                    for(let i=0; i<steps; i++) {{
                        arr.push(min + (step * i));
                    }}
                    return arr;
                }}

            </script>
            """

            # --- ESTRUTURA HTML (RECONSTRUÍDA) ---
            html_structure = f"""
            <div id="container">
                <div class="header">
                    <div class="logo-cel">
                        <img src="data:image/png;base64,{logo_b64}" alt="Logo" />
                    </div>
                    <div class="user-cel">
                        <div id="clinica-nome" class="nome">Clínica</div>
                        <div id="clinica-endereco" class="font-p">Endereço</div>
                    </div>
                </div>

                <div class="dados-paciente">
                    <div><span class="label">Nome:</span> <span id="paciente-nome">...</span></div>
                    <div><span class="label">Sexo:</span> <span id="sexo">...</span></div>
                    <div><span class="label">Idade:</span> <span id="idade">...</span></div>
                    <div><span class="label">Estatura:</span> <span id="estatura">...</span></div>
                    <div><span class="label">E-mail:</span> <span id="email">...</span></div>
                    <div><span class="label">Data:</span> <span id="data-avaliacao">...</span></div>
                </div>

                <div class="container-padding-lateral">
                    <h1 class="align-center">Relatório de Composição Corporal</h1>
                    
                    <div class="grid-container-2c mt-10">
                        <div class="corpo">
                            </div>

                        <div class="moldura padding-p">
                            <h2 class="align-center">Análise Global</h2>
                            <div id="normalidades-container" style="padding: 10px;">
                                </div>
                        </div>
                    </div>

                    <div class="mt-10">
                        <h2>Histórico</h2>
                        <table id="charts">
                            </table>
                    </div>
                </div>
            </div>
            """

            # Renderiza o HTML completo
            full_html = f"{html_css}{html_structure}{js_script}"
            components.html(full_html, height=1150, scrolling=True)

        else:
            st.warning("Nenhum dado encontrado para este ID.")
