import streamlit as st
import requests
import json
import base64
import os
import re

# Configuração da página Streamlit
st.set_page_config(layout="centered", page_title="Gerador de Relatórios")

# --- FUNÇÕES AUXILIARES ---

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def fetch_data(report_id):
    url = f"https://balancaapi.avanutrionline.com/Relatorio/{report_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
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

logo_b64 = get_base64_image("logoTKE.png")
corpo_b64 = get_base64_image("corpo.png")

# --- CSS DO RELATÓRIO (HTML DA NOVA ABA) ---
html_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    body {{
        font-family: 'Roboto', Arial, sans-serif;
        margin: 0; padding: 0;
        background-color: #525659; /* Fundo cinza escuro para destacar a folha */
        display: flex;
        justify-content: center;
        min-height: 100vh;
    }}

    #container {{
        width: 793px; /* Largura A4 */
        min-height: 1122px; /* Altura A4 */
        margin: 30px auto;
        background-color: {COLOR_BG};
        padding: 0;
        box-sizing: border-box;
        box-shadow: 0 0 20px rgba(0,0,0,0.5); /* Sombra estilo documento */
    }}

    /* --- ESTILOS INTERNOS DO RELATÓRIO --- */
    .moldura {{ border-radius: 10px; border: 2px solid {COLOR_LIGHT}; overflow: hidden; background-color: {COLOR_BG}; margin: 20px; }}
    .container-padding-lateral {{ padding: 0px 20px; }}
    .rolavel {{ overflow: visible; }}

    h1, h2 {{ color: {COLOR_PRIMARY}; margin-bottom: 4px; }}
    h1 {{ font-size: 20px; }}
    h2 {{ font-size: 15px; }}

    .font-p {{ font-size: 12px; }}
    .font-m {{ font-size: 14px; }}
    .font-g {{ font-size: 16px; }}
    .font-bold {{ font-weight: bold; }}
    .align-center {{ text-align: center; }}
    .align-right {{ text-align: right; }}

    /* CORPO */
    .corpo {{ background-image: url('data:image/png;base64,{corpo_b64}'); background-position: center; background-repeat: no-repeat; background-size: contain; height: 320px; }}
    .corpo>div:nth-child(1) {{ text-align: right; }}
    .corpo>div:nth-child(1)>div:nth-child(2) {{ margin-top: 10px; }}
    .corpo>div:nth-child(1)>div:nth-child(3) {{ margin-top: 30px; }}
    .corpo>div:nth-child(1)>div:nth-child(4) {{ margin-top: 63px; }}
    .corpo>div:nth-child(2) {{ text-align: center; margin-top: 66px; }}
    .corpo>div:nth-child(3)>div:nth-child(2) {{ margin-top: 10px; }}
    .corpo>div:nth-child(3)>div:nth-child(3) {{ margin-top: 140px; }}
    .lado-corpo {{ font-size: 1.2em; font-weight: bold; color: {COLOR_LIGHT}; }}

    /* GRIDS */
    .grid-container-2c {{ display: grid; grid-template-columns: 1fr 1fr; grid-gap: 10px; }}
    .grid-container-3c {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); grid-gap: 10px; }}
    .grid-container-3c-p {{ display: grid; grid-template-columns: 1fr 1fr 1fr; grid-gap: 10px; }}
    .grid-container-6c {{ display: grid; grid-template-columns: repeat(11, 1fr); grid-gap: 0; }}
    .grid-container-3c-paciente {{ display: grid; grid-template-columns: 2fr 0.8fr 0.8fr; grid-gap: 10px; }}
    .grid-container-3c-corpo {{ display: grid; grid-template-columns: 1fr 150px 1fr; grid-gap: 10px; }}
    .grid-container-normalidades {{ display: grid; grid-template-columns: 130px 2.3fr 1.8fr 6fr; grid-gap: 3px; }}
    .grid-container-impedancias {{ display: grid; grid-template-columns: 55px 1fr 1fr 1fr 1fr 1fr; grid-gap: 3px; }}
    .grid-container-3c-dados-adicionais {{ display: grid; grid-template-columns: 1fr 1fr; grid-gap: 10px; }}
    .grid-container-dados-adicionais {{ display: grid; grid-template-columns: 106px 1fr; grid-gap: 4px; }}
    .padding-p {{ padding: 2px 5px; }}

    /* TABELAS E CORES */
    .cel-cinza, .cel-verde {{ font-weight: bold; color: #FFF; align-items: center; display: grid; }}
    .cel-cinza {{ background-color: {COLOR_LIGHT}; color: {COLOR_DARK}; }}
    .cel-verde {{ background-color: {COLOR_PRIMARY}; }}
    .cel-header {{ color: {COLOR_DARK}; font-size: 16px; font-weight: bold; text-align: center; padding: 4px; }}
    .cel-verde.cel-header {{ color: #FFF; }}
    .cel-label {{ color: #FFF; font-size: 13px; font-weight: bold; padding: 4px 5px; height: 41px; display: flex; align-items: center; }}
    .cel-grafico {{ grid-column: span 3; border-top: {COLOR_DARK} 3px solid; border-left: {COLOR_DARK} 3px solid; }}
    #valor-idade-metabolica {{ display: inline-flex; align-items: center; justify-content: center; width: 100%; }}

    /* HEADER */
    .header {{ margin-bottom: 10px; padding: 0 20px; }}
    .logo-cel img {{ max-height: 80px; }}
    .user-cel {{ text-align: right; color: {COLOR_DARK}; }}
    .user-cel .nome {{ font-size: 12pt; font-weight: bold; }}
    
    .dados-paciente {{ background-color: {COLOR_BG}; padding: 10px 20px; border-bottom: 1px solid {COLOR_LIGHT}; }}
    .dados-paciente .label {{ font-weight: bold; color: {COLOR_DARK}; display: inline; }}
    .barra-baixo {{ border-bottom: 5px solid {COLOR_PRIMARY}; padding-bottom: 12px; }}
    .barra-corpos {{ width: 5px; background-color: {COLOR_PRIMARY}; height: 334px; position: absolute; left: calc(50% - 2.5px); margin-top: 15px; }}

    /* GRAFICOS */
    .grafico-valores {{ display: grid; grid-template-columns: repeat(11, 1fr); grid-gap: 2px; }}
    .grafico-valores>div {{ text-align: center; }}
    .grafico-valores>div>div {{ background-color: {COLOR_DARK}; width: 2px; height: 5px; display: block; margin-left: calc(50% - 1px); }}
    .barra-grafico-container {{ font-size: 18px; font-weight: bold; margin-top: 2px; }}
    .barra-grafico {{ background-color: {COLOR_DARK}; height: 15px; display: inline-block; margin-right: 10px; max-width: calc(100% - 70px); }}
    .cel-grafico-p {{ border-top: {COLOR_DARK} 1px solid; border-left: {COLOR_DARK} 1px solid; }}
    .barra-grafico-p-container {{ font-size: 12px; font-weight: bold; margin-top: 3px; }}
    .barra-grafico-p {{ background-color: {COLOR_DARK}; height: 7px; display: inline-block; margin-right: 10px; }}

    #charts {{ width: 100%; border-collapse: separate; border-spacing: 5px; }}
    #charts tr td:nth-child(1) {{ width: 110px; background-color: {COLOR_PRIMARY}; font-weight: bold; color: #FFF; padding: 8px; min-height: 32px; font-size: 12px; }}
    .chartPlaceholder {{ position: absolute; width: calc(81.5% + 30px); height: 56px; overflow: hidden; left: calc(8.33% - 5px); }}
    .graficos-tr {{ height: 38px; }}
    .valor-label {{ border-right: dashed 2px {COLOR_LIGHT}; height: 56px; font-size: 11px; padding: 0 5px; z-index: 1000; color: {COLOR_DARK}; }}
    .grafico-label {{ text-align: center; font-weight: bold; font-size: 11px; color: {COLOR_DARK}; background-color: {COLOR_LIGHT}; padding: 3px; }}
    .datas {{ grid-gap: 3px; height: 20px; }}
    .quebra-de-pagina {{ page-break-before: always; }}

    @media (max-width: 800px) {{
        #container {{ width: 100%; transform: scale(0.9); transform-origin: top left; }}
        .barra-corpos {{ display: none; }}
    }}
    
    /* REMOVER TUDO NA IMPRESSÃO */
    @media print {
        body { background-color: white; }
        #container { margin: 0; box-shadow: none; width: 100%; }
    }
</style>
"""

# --- LÓGICA DO APP (STREAMLIT) ---

st.title("Visualizador de Relatórios")

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
            nome_paciente = data.get('paciente', {}).get('nome', 'Paciente')
            
            # JSONs para JS
            translations_pt = json.dumps({
                "titulo": "Relatório de Avaliações", "nome": "Nome: ", "estatura": "Estatura: ", "data": "Data: ",
                "email": "E-mail: ", "sexo": "Sexo: ", "idade": "Idade: ", "analiseGlobalResumida_titulo": "Análise Global Resumida",
                "abaixo": "Abaixo", "normal": "Normal", "acima": "Acima", "peso": "Peso", "percentualGordura": "Percentual de Gordura",
                "massaGordura": "Massa de Gordura", "massaLivreGordura": "Massa Livre de Gordura", "aguaCorporal": "Água Corporal",
                "imc": "IMC", "analiseMassaMagra_titulo": "Análise de Massa Magra", "analiseGordura_titulo": "Análise de Gordura",
                "direito": "Direito", "esquerdo": "Esquerdo", "braco": "Braço", "tronco": "Tronco", "perna": "Perna",
                "dadosAdicionais": "Dados Adicionais", "tmb": "Taxa Metabólica Basal", "ia": "Índice Apendicular",
                "idade_metabolica": "Idade Metabólica ", "nivelGorduraVisceral": "Nível de Gordura Visceral",
                "dadosAdicionais_impedancias": "Impedâncias Z(Ω)", "BD": "BD", "BE": "BE", "TR": "TR", "PD": "PD", "PE": "PE",
                "historicoComposicaoCorporal": "Histórico da composição Corporal", "anos": "anos",
                "peso_h": "Peso (kg)", "percentualGordura_h": "Percentual de Gordura (%)", "massaGordura_h": "Massa de Gordura (kg)",
                "massaLivreGordura_h": "Massa Livre de Gordura (kg)", "massaMuscularEsqueletica_h": "Massa Muscular Esquelética (kg)",
                "aguaCorporalL_h": "Água Corporal (L)", "aguaIntracelularL_h": "Água Intracelular (L)", "aguaExtracelularL_h": "Água Extracelular (L)",
                "imc_h": "IMC", "areaOuNivelGorduraVisceral_h": "Área/Nível Gordura Visceral", "proteina_h": "Proteína", "minerais_h": "Minerais",
                "massaMagraBracoDireito_h": "Massa Magra Braço Dir.", "massaMagraBracoEsquerdo_h": "Massa Magra Braço Esq.",
                "massaMagraTronco_h": "Massa Magra Tronco", "massaMagraPernaDireita_h": "Massa Magra Perna Dir.", "massaMagraPernaEsquerda_h": "Massa Magra Perna Esq.",
                "gorduraBracoDireito_h": "Gordura Braço Dir.", "gorduraBracoEsquerdo_h": "Gordura Braço Esq.", "gorduraTronco_h": "Gordura Tronco",
                "gorduraPernaDireita_h": "Gordura Perna Dir.", "gorduraPernaEsquerda_h": "Gordura Perna Esq."
            })
            json_data = json.dumps(data)
            
            # Script JS (Sem html2pdf, apenas renderização)
            js_script = f"""
            <script>
                const apiData = {json_data};
                const translations = {translations_pt};
                var lang = "pt";
                const sexoTraducoes = {{ pt: {{ male: "Masculino", female: "Feminino" }} }};

                document.addEventListener("DOMContentLoaded", function () {{
                    const data = apiData;
                    aplicarTraducoes();
                    popularDadosUsuario(data.user);
                    popularDadosPaciente(data.paciente);
                    const ultimaAvaliacao = data.avaliacoes[data.avaliacoes.length - 1];
                    document.getElementById("data").innerText = formatarData(ultimaAvaliacao.data || new Date());
                    popularNormalidades(ultimaAvaliacao, data.normalidades);
                    popularDadosMembros(ultimaAvaliacao.dadosMembros, ultimaAvaliacao);
                    popularDadosAdicionais(ultimaAvaliacao);
                    criaLabelGrafico(data.avaliacoes);
                    criarGraficos(data);
                }});

                // --- FUNÇÕES DE PREENCHIMENTO (Compactadas) ---
                function aplicarTraducoes() {{ document.querySelectorAll("[data-translate]").forEach(el => {{ const key = el.getAttribute("data-translate"); el.innerText = translations[key] || key; }}); }}
                function criarGraficos(data) {{
                     const config = {{ chart: {{ animations: {{ enabled: false }} }} }};
                     const graficos = [
                        ["peso", "peso_h"], ["dadosCorpo.fmPercentual", "percentualGordura_h"],
                        ["dadosCorpo.fm", "massaGordura_h"], ["dadosCorpo.ffm", "massaLivreGordura_h"],
                        ["dadosCorpo.ssm", "massaMuscularEsqueletica_h"], ["dadosCorpo.tbw", "aguaCorporalL_h"],
                        ["dadosCorpo.icw", "aguaIntracelularL_h"], ["dadosCorpo.ecw", "aguaExtracelularL_h"],
                        ["dadosCorpo.bmi", "imc_h"]
                     ];
                     graficos.forEach(g => criarGrafico(data.avaliacoes, g[0], translations[g[1]], g[1]));
                }}
                function criaLabelGrafico(avaliacoes) {{
                    const labels = avaliacoes.map(avaliacao => formatarData(avaliacao.data));
                    while (labels.length < 6) {{ labels.push(null); }}
                    const container = document.getElementById("charts"); const tr = document.createElement("tr"); tr.className = "graficos-tr"; container.appendChild(tr); const td1 = document.createElement("td"); tr.appendChild(td1); const td2 = document.createElement("td"); tr.appendChild(td2); const valoresLabel = document.createElement('div'); valoresLabel.className = "grid-container-6c datas";
                    labels.forEach(l => {{ const label = document.createElement("div"); label.className = "grafico-label"; label.innerText = l; valoresLabel.appendChild(label); }}); td2.appendChild(valoresLabel);
                }}
                function criarGrafico(avaliacoesData, prop, label, translationKey, utilizarFormaDecimalPadrao = true) {{
                    const valores = avaliacoesData.map(avaliacao => obterValor(avaliacao, prop));
                    while (valores.length < 6) {{ valores.push(null); }}
                    const container = document.getElementById("charts"); const tr = document.createElement("tr"); tr.className = "graficos-tr"; container.appendChild(tr); const td1 = document.createElement("td"); tr.appendChild(td1); const labelElement = document.createElement('label'); labelElement.innerText = label; td1.appendChild(labelElement); const td2 = document.createElement("td"); tr.appendChild(td2); const chartPlaceholder = document.createElement('div'); chartPlaceholder.className = "chartPlaceholder"; td2.appendChild(chartPlaceholder); const valoresLabel = document.createElement('div'); valoresLabel.className = "grid-container-6c";
                    valores.forEach(v => {{ const valorLabel = document.createElement("div"); valorLabel.className = "valor-label"; if (v) valorLabel.innerText = utilizarFormaDecimalPadrao ? formatarNumeroDecimalBrasileiro(v) : formatarNumeroBrasileiro(v); valoresLabel.appendChild(valorLabel); }});
                    td2.appendChild(valoresLabel);
                    var options = {{ series: [{{ data: valores }}], chart: {{ height: 90, type: 'area', zoom: {{ enabled: false }}, animations: {{ enabled: false }}, toolbar: {{ show: false }}, offsetX: -7, offsetY: -25 }}, dataLabels: {{ enabled: false }}, stroke: {{ curve: 'straight', width: 2, colors: ["{COLOR_CHART_STROKE}"] }}, fill: {{ colors: ["{COLOR_CHART_FILL}"] }}, xaxis: {{ labels: {{ show: false }} }}, yaxis: {{ show: false }}, grid: {{ show: false }}, markers: {{ size: 4, colors: ["#fff"], strokeColors: ["{COLOR_CHART_STROKE}"], strokeWidth: 2, hover: {{ size: 7 }} }} }};
                    const chart = new ApexCharts(chartPlaceholder, options); chart.render();
                }}
                function obterValor(objeto, referencia) {{ var partes = referencia.split("."); var valor = objeto; for (var i = 0; i < partes.length; i++) {{ var parte = partes[i]; if (isNaN(parte)) {{ valor = valor[parte]; }} else {{ valor = valor[Number(parte)]; }} }} return valor; }}
                function formatarData(jsonDate) {{ return formatarDataBrasileira(jsonDate); }}
                function popularDadosPaciente(pacienteData) {{ document.getElementById("paciente-nome").innerText = pacienteData.nome; document.getElementById("sexo").innerText = pacienteData.sexo == 70 ? sexoTraducoes[lang]["female"] : sexoTraducoes[lang]["male"]; document.getElementById("estatura").innerText = (pacienteData.estaturaCm / 100).toString().replace(".", ",") + "m"; document.getElementById("idade").innerText = calcularIdade(pacienteData.dataNascimento); document.getElementById("email").innerText = pacienteData.email; }}
                function popularDadosUsuario(userData) {{ if (userData.clinicaNome) {{ document.getElementById("nome").innerText = userData.clinicaNome; document.getElementById("endereco").innerHTML = `${{userData.clinicaEndereco ?? ""}} ${{userData.clinicaComplemento ?? ""}}<br />${{userData.clinicaCEP ?? ""}} - ${{userData.clinicaMunicipio ?? ""}} - ${{userData.clinicaUF ?? ""}}`; }} else {{ document.getElementById("nome").innerText = userData.nome; document.getElementById("endereco").innerHTML = `${{userData.endereco ?? ""}} ${{userData.complemento ?? ""}}<br />${{userData.cep ?? ""}} - ${{userData.municipio ?? ""}} - ${{userData.uf ?? ""}}`; }} }}
                function formatarDataBrasileira(jsonDate) {{ const date = new Date(jsonDate); const dia = date.getDate().toString().padStart(2, "0"); const mes = (date.getMonth() + 1).toString().padStart(2, "0"); const ano = date.getFullYear(); const horas = date.getHours().toString().padStart(2, "0"); const minutos = date.getMinutes().toString().padStart(2, "0"); return `${{dia}}/${{mes}}/${{ano}} ${{horas}}:${{minutos}}`; }}
                function calcularIdade(dataNascimento) {{ const dateNascimento = new Date(dataNascimento); const dataAtual = new Date(); const diferenca = dataAtual - dateNascimento; return Math.floor(diferenca / (1000 * 60 * 60 * 24 * 365.25)); }}
                function formatarNumeroBrasileiro(numero, casasDecimais) {{ return numero.toLocaleString('pt-BR', {{ minimumFractionDigits: 0, maximumFractionDigits: casasDecimais == undefined ? 1 : casasDecimais }}); }}
                function formatarNumeroDecimalBrasileiro(numero) {{ return numero.toLocaleString('pt-BR', {{ minimumFractionDigits: 1, maximumFractionDigits: 1 }}); }}
                function popularNormalidades(avaliacaoData, normalidades) {{ popularNormalidade(normalidades.peso, "normalidadePeso", avaliacaoData.peso, "", 1); popularNormalidade(normalidades.fmPerc, "normalidadeFMPerc", avaliacaoData.dadosCorpo.fmPercentual, "", 1); popularNormalidade(normalidades.fmKg, "normalidadeFM", avaliacaoData.dadosCorpo.fm, "", 1); popularNormalidade(normalidades.ffmKg, "normalidadeFFM", avaliacaoData.dadosCorpo.ffm, "", 1); popularNormalidade(normalidades.tbw, "normalidadeTBW", avaliacaoData.dadosCorpo.tbw, "", 1); popularNormalidade(normalidades.bmi, "normalidadeBMI", avaliacaoData.dadosCorpo.bmi, "", 1); }}
                function popularNormalidade(normalidade, idElemento, valor, unidade, casasDecimaisEscala) {{ casasDecimaisEscala = casasDecimaisEscala == undefined ? 0 : casasDecimaisEscala; let numerosEscala = gerarSequenciaComDiferencaFixa(normalidade.minimo, normalidade.maximo, 11); let html = ""; numerosEscala.forEach(n => {{ html += `<div><div></div><label>${{formatarNumeroBrasileiro(n, casasDecimaisEscala)}}</label></div>` }}); document.getElementById(idElemento).querySelector(".grafico-valores").innerHTML = html; document.getElementById(idElemento).querySelector(".barra-grafico-container label").innerHTML = (casasDecimaisEscala == 1 ? formatarNumeroDecimalBrasileiro(valor) : formatarNumeroBrasileiro(valor, casasDecimaisEscala)) + unidade; let percentual = converterValorParaPercentualGrafico(valor, normalidade.minimo, normalidade.maximo); document.getElementById(idElemento).querySelector(".barra-grafico").style.width = Math.round(percentual) + "%"; }}
                function converterValorParaPercentualGrafico(valor, minimoNormal, maximoNormal) {{ const valorEscalaA = (valor - minimoNormal) * (41 - 23) / (maximoNormal - minimoNormal) + 23; return valorEscalaA; }}
                function gerarSequenciaComDiferencaFixa(terceiro, quinto, quantidade) {{ const diferenca = (quinto - terceiro) / 2; const sequencia = Array.from({{ length: quantidade }}, (_, index) => terceiro + (index - 2) * diferenca); return sequencia; }}
                function popularDadosMembros(dadosMembro, avaliacao) {{ document.getElementById("mm-bd-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[0].composicaoCorporal.ffm) + "kg"; document.getElementById("mm-bd-p").innerText = formatarNumeroBrasileiro(dadosMembro[0].composicaoCorporal.ffm / avaliacao.peso * 100) + "%"; document.getElementById("mm-be-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[1].composicaoCorporal.ffm) + "kg"; document.getElementById("mm-be-p").innerText = formatarNumeroBrasileiro(dadosMembro[1].composicaoCorporal.ffm / avaliacao.peso * 100) + "%"; document.getElementById("mm-t-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[2].composicaoCorporal.ffm) + "kg"; document.getElementById("mm-t-p").innerText = formatarNumeroBrasileiro(dadosMembro[2].composicaoCorporal.ffm / avaliacao.peso * 100) + "%"; document.getElementById("mm-pd-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[3].composicaoCorporal.ffm) + "kg"; document.getElementById("mm-pd-p").innerText = formatarNumeroBrasileiro(dadosMembro[3].composicaoCorporal.ffm / avaliacao.peso * 100) + "%"; document.getElementById("mm-pe-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[4].composicaoCorporal.ffm) + "kg"; document.getElementById("mm-pe-p").innerText = formatarNumeroBrasileiro(dadosMembro[4].composicaoCorporal.ffm / avaliacao.peso * 100) + "%"; document.getElementById("mm-c-k").innerText = formatarNumeroDecimalBrasileiro(avaliacao.dadosCorpo.ffm) + "kg"; document.getElementById("mm-c-p").innerText = formatarNumeroBrasileiro(avaliacao.dadosCorpo.ffm / avaliacao.peso * 100) + "%"; document.getElementById("g-bd-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[0].composicaoCorporal.fm) + "kg"; document.getElementById("g-bd-p").innerText = formatarNumeroBrasileiro(dadosMembro[0].composicaoCorporal.fm / avaliacao.peso * 100) + "%"; document.getElementById("g-be-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[1].composicaoCorporal.fm) + "kg"; document.getElementById("g-be-p").innerText = formatarNumeroBrasileiro(dadosMembro[1].composicaoCorporal.fm / avaliacao.peso * 100) + "%"; document.getElementById("g-t-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[2].composicaoCorporal.fm) + "kg"; document.getElementById("g-t-p").innerText = formatarNumeroBrasileiro(dadosMembro[2].composicaoCorporal.fm / avaliacao.peso * 100) + "%"; document.getElementById("g-pd-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[3].composicaoCorporal.fm) + "kg"; document.getElementById("g-pd-p").innerText = formatarNumeroBrasileiro(dadosMembro[3].composicaoCorporal.fm / avaliacao.peso * 100) + "%"; document.getElementById("g-pe-k").innerText = formatarNumeroDecimalBrasileiro(dadosMembro[4].composicaoCorporal.fm) + "kg"; document.getElementById("g-pe-p").innerText = formatarNumeroBrasileiro(dadosMembro[4].composicaoCorporal.fm / avaliacao.peso * 100) + "%"; document.getElementById("g-c-k").innerText = formatarNumeroDecimalBrasileiro(avaliacao.dadosCorpo.fm) + "kg"; document.getElementById("g-c-p").innerText = formatarNumeroBrasileiro(avaliacao.dadosCorpo.fm / avaliacao.peso * 100) + "%"; }}
                function popularDadosAdicionais(avaliacao) {{ document.getElementById("valor-taxa-metabolica-basal").innerText = formatarNumeroBrasileiro(avaliacao.taxaMetabolicaBasal, 0) + " kcal"; document.getElementById("valor-indice-apendicular").innerText = formatarNumeroBrasileiro(avaliacao.dadosCorpo.indiceApendicular, 2) + " kg/m²"; document.getElementById("valor-idade-metabolica").innerHTML = avaliacao.idadeMetabolica + '&nbsp;<span>anos</span>'; document.getElementById("valor-vfl").innerText = "Nível " + formatarNumeroBrasileiro(avaliacao.dadosCorpo.vfl, 0); document.getElementById("grafico-gordura-veisceral").style.width = Math.min(Math.round((avaliacao.dadosCorpo.vfl / 20) * 100), 100) + "%"; }}
            </script>
            """

            # CONSTRUÇÃO DO HTML COMPLETO
            html_content = f"""
            <!DOCTYPE html>
            <html lang="pt">
            <head>
                <meta charset="UTF-8">
                <title>Relatório - {nome_paciente}</title>
                <script src="https://cdn.jsdelivr.net/npm/apexcharts@3.27.0/dist/apexcharts.min.js"></script>
                {html_css}
            </head>
            <body>
                <div id="container">
                    <div class="header grid-container-2c">
                        <div class="logo-cel"><img src="data:image/png;base64,{logo_b64}" /></div>
                        <div class="user-cel">
                            <div class="nome" id="nome">---</div>
                            <div class="endereco" id="endereco">---<br />---</div>
                        </div>
                    </div>
                    
                    <div class="moldura">
                        <div class="dados-paciente barra-baixo">
                            <div class="grid-container-3c-paciente">
                                <div><div data-translate="nome" class="label">Nome: </div><label id="paciente-nome">---</label></div>
                                <div><div data-translate="estatura"class="label">Estatura: </div><label id="estatura">---m</label></div>
                                <div><div data-translate="data" class="label">Data: </div><label id="data">--/--/----</label></div>
                                <div><div data-translate="email" class="label">E-mail: </div><label id="email">---</label></div>
                                <div><div data-translate="sexo" class="label">Sexo: </div><label id="sexo">---</label></div>
                                <div><div data-translate="idade" class="label">Idade: </div><label id="idade">---</label></div>
                            </div>
                        </div>

                        <div class="container-padding-lateral rolavel barra-baixo">
                            <h1 data-translate="analiseGlobalResumida_titulo">Análise Global Resumida</h1>
                            <div class="grid-container-normalidades">
                                <div class="cel-cinza cel-header"></div>
                                <div data-translate="abaixo" class="cel-verde cel-header">Abaixo</div>
                                <div data-translate="normal" class="cel-cinza cel-header">Normal</div>
                                <div data-translate="acima" class="cel-verde cel-header">Acima</div>

                                <div data-translate="peso" class="cel-verde cel-label">Peso</div>
                                <div class="cel-grafico" id="normalidadePeso">
                                    <div class="grafico-valores"></div>
                                    <div class="barra-grafico-container"><div class="barra-grafico"></div><label>--</label></div>
                                </div>
                                <div data-translate="percentualGordura" class="cel-verde cel-label">Percentual de Gordura</div>
                                <div class="cel-grafico" id="normalidadeFMPerc">
                                    <div class="grafico-valores"></div>
                                    <div class="barra-grafico-container"><div class="barra-grafico"></div><label>--</label></div>
                                </div>
                                
                                <div data-translate="massaGordura" class="cel-verde cel-label">Massa de Gordura</div>
                                <div class="cel-grafico" id="normalidadeFM">
                                    <div class="grafico-valores"></div>
                                    <div class="barra-grafico-container"><div class="barra-grafico"></div><label>--</label></div>
                                </div>
                                <div data-translate="massaLivreGordura" class="cel-verde cel-label">Massa Livre de Gordura</div>
                                <div class="cel-grafico" id="normalidadeFFM">
                                    <div class="grafico-valores"></div>
                                    <div class="barra-grafico-container"><div class="barra-grafico"></div><label>--</label></div>
                                </div>
                                <div data-translate="aguaCorporal" class="cel-verde cel-label">Agua Corporal</div>
                                <div class="cel-grafico" id="normalidadeTBW">
                                    <div class="grafico-valores"></div>
                                    <div class="barra-grafico-container"><div class="barra-grafico"></div><label>--</label></div>
                                </div>
                                <div data-translate="imc" class="cel-verde cel-label">IMC</div>
                                <div class="cel-grafico" id="normalidadeBMI">
                                    <div class="grafico-valores"></div>
                                    <div class="barra-grafico-container"><div class="barra-grafico"></div><label>--</label></div>
                                </div>
                            </div>
                        </div>

                        <div class="barra-corpos"></div>
                        
                        <div class="membros grid-container-2c barra-baixo">
                            <div>
                                <h1 data-translate="analiseMassaMagra_titulo">Análise de Massa Magra</h1>
                                <div class="grid-container-3c-corpo corpo">
                                    <div>
                                        <div data-translate="direito" class="lado-corpo">Direito</div>
                                        <div><b data-translate="braco">Braço</b><div id="mm-bd-k">-</div><div id="mm-bd-p">-</div></div>
                                        <div><b data-translate="tronco">Tronco</b><div id="mm-t-k">-</div><div id="mm-t-p">-</div></div>
                                        <div><b data-translate="perna">Perna</b><div id="mm-pd-k">-</div><div id="mm-pd-p">-</div></div>
                                    </div>
                                    <div>
                                        <div class="display-centro-corpo-k" id="mm-c-k">kg</div>
                                        <div class="display-centro-corpo-p" id="mm-c-p">%</div>
                                    </div>
                                    <div>
                                        <div data-translate="esquerdo" class="lado-corpo">Esquerdo</div>
                                        <div><b data-translate="braco">Braço</b><div id="mm-be-k">-</div><div id="mm-be-p">-</div></div>
                                        <div><b data-translate="perna">Perna</b><div id="mm-pe-k">-</div><div id="mm-pe-p">-</div></div>
                                    </div>
                                </div>
                            </div>
                            <div>
                                <h1 data-translate="analiseGordura_titulo">Análise de Gordura</h1>
                                <div class="grid-container-3c-corpo corpo">
                                    <div>
                                        <div data-translate="direito" class="lado-corpo">Direito</div>
                                        <div><b data-translate="braco">Braço</b><div id="g-bd-k">-</div><div id="g-bd-p">-</div></div>
                                        <div><b data-translate="tronco">Tronco</b><div id="g-t-k">-</div><div id="g-t-p">-</div></div>
                                        <div><b data-translate="perna">Perna</b><div id="g-pd-k">-</div><div id="g-pd-p">-</div></div>
                                    </div>
                                    <div>
                                        <div class="display-centro-corpo-k" id="g-c-k">kg</div>
                                        <div class="display-centro-corpo-p" id="g-c-p">%</div>
                                    </div>
                                    <div>
                                        <div data-translate="esquerdo" class="lado-corpo">Esquerdo</div>
                                        <div><b data-translate="braco">Braço</b><div id="g-be-k">-</div><div id="g-be-p">-</div></div>
                                        <div><b data-translate="perna">Perna</b><div id="g-pe-k">-</div><div id="g-pe-p">-</div></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="container-padding-lateral">
                             <div class="grid-container-3c-dados-adicionais">
                                <div>
                                    <h2 data-translate="dadosAdicionais">Dados Adicionais</h2>
                                    <div class="grid-container-dados-adicionais">
                                        <div data-translate="tmb" class="cel-cinza font-p padding-p">Taxa Metabólica Basal</div>
                                        <div class="cel-verde align-center font-g" id="valor-taxa-metabolica-basal">--- kcal</div>
                                        <div data-translate="ia" class="cel-cinza font-p padding-p">Índice Apendicular</div>
                                        <div class="cel-verde align-center font-g" id="valor-indice-apendicular">---</div>
                                        <div data-translate="idade_metabolica" class="cel-cinza font-p padding-p">Idade Metabólica</div>
                                        <div class="cel-verde align-center font-g" id="valor-idade-metabolica">---</div>
                                    </div>
                                </div>
                                <div>
                                    <h2 data-translate="nivelGorduraVisceral">Nível de Gordura Visceral</h2>
                                    <div class="cel-cinza padding-p align-center" id="valor-vfl">Nível</div>
                                    <div class="grid-container-3c-p">
                                        <div data-translate="abaixo" class="font-p">Abaixo</div>
                                        <div class="align-center font-bold font-m">10</div>
                                        <div data-translate="acima" class="align-right font-p">Acima</div>
                                    </div>
                                    <div class="cel-grafico-p">
                                        <div class="barra-grafico-p-container">
                                            <div class="barra-grafico-p" id="grafico-gordura-veisceral"></div>
                                        </div>
                                    </div>
                                </div>
                             </div>
                        </div>
                        
                        <div class="graficos rolavel quebra-de-pagina">
                            <h1 data-translate="historicoComposicaoCorporal">Histórico da composição Corporal</h1>
                            <table id="charts"></table>
                        </div>

                    </div>
                </div>
                {js_script}
            </body>
            </html>
            """
            
            # --- CRIAÇÃO DO LINK E LÓGICA DE ABERTURA ---
            b64_html = base64.b64encode(html_content.encode()).decode()
            data_url = f"data:text/html;base64,{b64_html}"

            st.success(f"Relatório de **{nome_paciente}** preparado!")
            
            # Exibe um BOTÃO LINK GRANDE para abrir a aba
            st.markdown(f"""
                <div style="display: flex; justify-content: center; margin-top: 20px;">
                    <a href="{data_url}" target="_blank" style="
                        background-color: {COLOR_PRIMARY};
                        color: white;
                        padding: 15px 30px;
                        text-align: center;
                        text-decoration: none;
                        font-size: 18px;
                        font-weight: bold;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        font-family: sans-serif;
                    ">
                        📄 ABRIR RELATÓRIO EM NOVA ABA
                    </a>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error("Dados não encontrados. Verifique o link ou ID.")
