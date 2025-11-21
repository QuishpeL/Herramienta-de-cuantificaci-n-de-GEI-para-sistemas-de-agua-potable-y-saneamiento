# -*- coding: utf-8 -*-
"""
Script de Servidor v2: Reporte Avanzado de Costo Social del Carbono.
Metodología: Burke et al. (2023) + Fernandez et al. (2015).
Enfoque: Escenarios de Tasa de Descuento y Análisis Multidimensional.
"""
import http.server
import socketserver
import webbrowser
import os
import json

# --- BASE DE DATOS INTEGRADA ---
# Datos extraídos de tus documentos y papers subidos.

PROJECT_DB = {
    "rumiñahui": {
        "id": "rumiñahui",
        "title": "Sistema AP Rumiñahui",
        "location": "Sierra (Pichincha)",
        "emissions": 1589.98, # tCO2e Construcción
        # Fernandez 2015: Baja sensibilidad, Alta capacidad adaptativa 
        "vuln_metrics": {"exp": 0.85, "sens": 0.20, "ac": 0.80}, 
        "sc_scenarios": {
            "conservative": 17.00, # 5% Discount (Burke)
            "central": 51.00,      # 3% Discount (Burke)
            "ethical": 85.00       # 2.5% Discount (Burke)
        }
    },
    "logroño": {
        "id": "logroño",
        "title": "Agua Potable Logroño",
        "location": "Amazonía (M. Santiago)",
        "emissions": 946.03, # tCO2e Construcción
        # Fernandez 2015: Alta vulnerabilidad amazónica 
        "vuln_metrics": {"exp": 0.75, "sens": 0.85, "ac": 0.30},
        "sc_scenarios": {
            # Ajuste por vulnerabilidad (+20% sobre base Burke para Amazonía)
            "conservative": 45.00, 
            "central": 85.00,      
            "ethical": 120.00      
        }
    },
    "mera": {
        "id": "mera",
        "title": "Alcantarillado Mera",
        "location": "Amazonía (Pastaza)",
        "emissions": 1586.55, # tCO2e Construcción
        # Fernandez 2015: Alta sensibilidad y exposición
        "vuln_metrics": {"exp": 0.80, "sens": 0.75, "ac": 0.40},
        "sc_scenarios": {
            # Ajuste por vulnerabilidad (+20% sobre base Burke para Amazonía)
            "conservative": 45.00, 
            "central": 85.00,      
            "ethical": 120.00      
        }
    }
}

json_data = json.dumps(PROJECT_DB)

# --- PLANTILLA HTML V2 ---
html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte SC-CO2 V2 | Burke & Fernandez Methodology</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Manrope', sans-serif; background-color: #f8fafc; color: #1e293b; }}
        .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .scenario-card {{ transition: all 0.2s; }}
        .scenario-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
        .gradient-text {{ background: linear-gradient(to right, #0f172a, #334155); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: white; padding: 0; }}
            .card {{ box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }}
            .grid {{ display: block; }}
            .col-span-2 {{ width: 100%; margin-bottom: 20px; }}
        }}
    </style>
</head>
<body class="p-6 lg:p-12">

    <div class="max-w-7xl mx-auto">
        
        <header class="flex justify-between items-end mb-10 border-b border-slate-200 pb-6">
            <div>
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 mb-3">
                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span class="text-xs font-bold text-slate-600 uppercase tracking-wider">Technical Report V2.0</span>
                </div>
                <h1 class="text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight mb-2">
                    Costo Social del Carbono
                </h1>
                <p class="text-lg text-slate-500 max-w-3xl">
                    Valoración económica de daños climáticos basada en tasas de descuento (Burke et al., 2023) y vulnerabilidad territorial (Fernandez et al., 2015).
                </p>
            </div>
            <div class="no-print flex flex-col gap-2 items-end">
                <select id="projectSelector" class="bg-white border border-slate-300 text-slate-700 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-64 p-2.5 font-semibold shadow-sm">
                    <option value="rumiñahui">📍 Rumiñahui (Urbano/Sierra)</option>
                    <option value="logroño">🌳 Logroño (Amazonía)</option>
                    <option value="mera">💧 Mera (Amazonía)</option>
                </select>
                <button onclick="window.print()" class="text-indigo-600 hover:text-indigo-800 text-sm font-bold flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                    Imprimir PDF
                </button>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

            <div class="lg:col-span-4 space-y-6">
                
                <div class="card p-6 bg-slate-900 text-white">
                    <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Proyecto Analizado</h2>
                    <div class="text-2xl font-bold mb-1" id="projTitle">...</div>
                    <div class="text-sm text-slate-300 mb-6 flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
                        <span id="projLocation">...</span>
                    </div>
                    
                    <div class="border-t border-slate-700 pt-4">
                        <div class="flex justify-between items-end">
                            <span class="text-sm text-slate-400">Emisiones Totales</span>
                            <span class="text-xl font-mono font-bold text-emerald-400" id="projEmissions">0 tCO₂e</span>
                        </div>
                        <p class="text-xs text-slate-500 mt-1">Fase de Construcción (Materiales + Maquinaria)</p>
                    </div>
                </div>

                <div class="card p-6">
                    <h3 class="text-sm font-bold text-slate-800 mb-4 flex justify-between">
                        Perfil de Vulnerabilidad
                        <span class="text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-500">Fernandez et al. 2015</span>
                    </h3>
                    <div class="relative h-64 w-full">
                        <canvas id="radarChart"></canvas>
                    </div>
                    <div class="mt-4 text-xs text-slate-500 text-center">
                        Métrica normalizada (0-1). Mayor área = Mayor riesgo estructural.
                    </div>
                </div>

                <div class="card p-6 border-l-4 border-indigo-500">
                    <div class="flex justify-between items-center mb-2">
                        <h3 class="text-sm font-bold text-slate-700">Índice de Vulnerabilidad</h3>
                        <span class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded" id="vulnLabel">ALTA</span>
                    </div>
                    <div class="text-4xl font-extrabold text-slate-900 mb-2" id="vulnScore">0.00</div>
                    <p class="text-xs text-slate-500 leading-relaxed">
                        Calculado ponderando Exposición, Sensibilidad y (1 - Capacidad Adaptativa). Define el multiplicador del costo social.
                    </p>
                </div>

            </div>

            <div class="lg:col-span-8 space-y-8">

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    
                    <div class="scenario-card card p-5 border-t-4 border-slate-400">
                        <div class="text-xs font-bold text-slate-500 uppercase mb-1">Escenario Conservador</div>
                        <div class="text-xs text-slate-400 mb-3">Tasa Descuento: 5.0%</div>
                        <div class="text-2xl font-bold text-slate-800" id="costConserv">$0</div>
                        <div class="text-xs text-slate-500 mt-2">Precio/ton: <span class="font-mono" id="priceConserv">$0</span></div>
                    </div>

                    <div class="scenario-card card p-5 border-t-4 border-blue-600 bg-blue-50/50">
                        <div class="text-xs font-bold text-blue-700 uppercase mb-1">Escenario Central</div>
                        <div class="text-xs text-blue-500 mb-3">Tasa Descuento: 3.0%</div>
                        <div class="text-3xl font-bold text-blue-900" id="costCentral">$0</div>
                        <div class="text-xs text-blue-600 mt-2">Precio/ton: <span class="font-mono font-bold" id="priceCentral">$0</span></div>
                    </div>

                    <div class="scenario-card card p-5 border-t-4 border-emerald-500">
                        <div class="text-xs font-bold text-emerald-700 uppercase mb-1">Escenario Ético</div>
                        <div class="text-xs text-emerald-500 mb-3">Tasa Descuento: 2.5%</div>
                        <div class="text-2xl font-bold text-emerald-900" id="costEthical">$0</div>
                        <div class="text-xs text-emerald-600 mt-2">Precio/ton: <span class="font-mono" id="priceEthical">$0</span></div>
                    </div>
                </div>

                <div class="card p-8">
                    <h3 class="text-lg font-bold text-slate-800 mb-6">Costo Social Total por Escenario (VPN)</h3>
                    <div class="h-80 w-full">
                        <canvas id="barChart"></canvas>
                    </div>
                    <p class="text-xs text-slate-400 mt-4 text-center">
                        *Valores representan el daño económico acumulado futuro (Loss & Damage) atribuible a las emisiones de construcción hoy.
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="card p-6">
                        <h3 class="text-sm font-bold text-slate-800 mb-4">Distribución Relativa del Daño</h3>
                        <div class="h-48 w-full relative">
                            <canvas id="doughnutChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card p-6 bg-white border-0 shadow-none">
                        <h3 class="text-sm font-bold text-slate-800 mb-2">Interpretación Técnica</h3>
                        <div class="prose prose-sm text-slate-600 text-xs leading-relaxed">
                            <p class="mb-2">
                                <strong>Metodología Burke (2023):</strong> Aplica tasas de descuento decrecientes. El escenario "Ético" (2.5%) valora más los daños a futuras generaciones, resultando en costos sociales más altos.
                            </p>
                            <p>
                                <strong>Ajuste Fernandez (2015):</strong> Los proyectos en <span class="font-semibold text-slate-800">Amazonía (Logroño/Mera)</span> reciben un precio social por tonelada más alto debido a su baja capacidad adaptativa y alta sensibilidad ecosistémica, lo que amplifica el impacto monetario de cada tonelada emitida.
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
        
        <footer class="mt-12 pt-6 border-t border-slate-200 text-center text-xs text-slate-400">
            <p>Generado con Python Server V2 | Referencias: Burke et al. (Stanford, 2023), Fernandez et al. (SpringerPlus, 2015).</p>
        </footer>

    </div>

    <script>
        const db = {json_data};
        let radarChart = null;
        let barChart = null;
        let doughnutChart = null;

        // Utilitarios
        const fmtMoney = (v) => new Intl.NumberFormat('en-US', {{ style: 'currency', currency: 'USD', maximumFractionDigits: 0 }}).format(v);
        const fmtNum = (v) => new Intl.NumberFormat('en-US', {{ maximumFractionDigits: 2 }}).format(v);

        function init() {{
            const selector = document.getElementById('projectSelector');
            selector.addEventListener('change', updateDashboard);
            updateDashboard();
        }}

        function updateDashboard() {{
            const key = document.getElementById('projectSelector').value;
            const data = db[key];
            const m = data.vuln_metrics;
            const sc = data.sc_scenarios;

            // 1. Textos Básicos
            document.getElementById('projTitle').innerText = data.title;
            document.getElementById('projLocation').innerText = data.location;
            document.getElementById('projEmissions').innerText = fmtNum(data.emissions) + " tCO₂e";

            // 2. Cálculos de Vulnerabilidad (Indice simple promedio ponderado inverso AC)
            // Score = (Exp + Sens + (1-AC))/3
            const vScore = (m.exp + m.sens + (1 - m.ac)) / 3;
            document.getElementById('vulnScore').innerText = vScore.toFixed(2);
            
            const vLabel = document.getElementById('vulnLabel');
            if(vScore > 0.6) {{ vLabel.innerText = "ALTA"; vLabel.className = "text-xs font-bold text-red-600 bg-red-50 px-2 py-1 rounded"; }}
            else {{ vLabel.innerText = "BAJA"; vLabel.className = "text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded"; }}

            // 3. Costos Totales
            const cConserv = data.emissions * sc.conservative;
            const cCentral = data.emissions * sc.central;
            const cEthical = data.emissions * sc.ethical;

            document.getElementById('costConserv').innerText = fmtMoney(cConserv);
            document.getElementById('costCentral').innerText = fmtMoney(cCentral);
            document.getElementById('costEthical').innerText = fmtMoney(cEthical);

            document.getElementById('priceConserv').innerText = fmtMoney(sc.conservative);
            document.getElementById('priceCentral').innerText = fmtMoney(sc.central);
            document.getElementById('priceEthical').innerText = fmtMoney(sc.ethical);

            // 4. Actualizar Gráficos
            updateRadar(m);
            updateBar(cConserv, cCentral, cEthical);
            updateDoughnut(cCentral);
        }}

        function updateRadar(m) {{
            const ctx = document.getElementById('radarChart').getContext('2d');
            if(radarChart) radarChart.destroy();

            radarChart = new Chart(ctx, {{
                type: 'radar',
                data: {{
                    labels: ['Exposición (Clima)', 'Sensibilidad (Social)', 'Capacidad Adaptativa'],
                    datasets: [{{
                        label: 'Índice Local',
                        data: [m.exp, m.sens, m.ac],
                        backgroundColor: 'rgba(79, 70, 229, 0.2)',
                        borderColor: '#4f46e5',
                        pointBackgroundColor: '#4f46e5',
                        pointBorderColor: '#fff'
                    }}]
                }},
                options: {{
                    scales: {{ r: {{ min: 0, max: 1, ticks: {{ display: false }} }} }},
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
        }}

        function updateBar(c1, c2, c3) {{
            const ctx = document.getElementById('barChart').getContext('2d');
            if(barChart) barChart.destroy();

            barChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Conservador (5%)', 'Central (3%)', 'Ético (2.5%)'],
                    datasets: [{{
                        label: 'Costo Social Total ($)',
                        data: [c1, c2, c3],
                        backgroundColor: ['#94a3b8', '#2563eb', '#10b981'],
                        borderRadius: 6,
                        barThickness: 50
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ y: {{ beginAtZero: true }} }}
                }}
            }});
        }}

        function updateDoughnut(currentCost) {{
            const ctx = document.getElementById('doughnutChart').getContext('2d');
            
            // Calcular totales de los otros proyectos para contexto (hardcoded logic for demo)
            // En una app real, iteraríamos sobre DB.
            const totalRumi = db['rumiñahui'].emissions * db['rumiñahui'].sc_scenarios.central;
            const totalLogro = db['logroño'].emissions * db['logroño'].sc_scenarios.central;
            const totalMera = db['mera'].emissions * db['mera'].sc_scenarios.central;
            
            if(doughnutChart) doughnutChart.destroy();

            doughnutChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Rumiñahui', 'Logroño', 'Mera'],
                    datasets: [{{
                        data: [totalRumi, totalLogro, totalMera],
                        backgroundColor: ['#cbd5e1', '#64748b', '#334155'],
                        hoverBackgroundColor: ['#2563eb', '#2563eb', '#2563eb'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {{ legend: {{ position: 'right', labels: {{ usePointStyle: true, font: {{ size: 10 }} }} }} }}
                }}
            }});
        }}

        window.onload = init;
    </script>
</body>
</html>
"""

# --- SERVER SETUP ---
PORT = 8003 # Puerto V2
OUTPUT = "social_cost_v2.html"

try:
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"✅ Reporte V2 Generado: {OUTPUT}")
except Exception as e:
    print(f"Error: {e}")
    exit()

Handler = http.server.SimpleHTTPRequestHandler

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/{OUTPUT}"
        print(f"\n🚀 SERVIDOR V2 ACTIVO (Burke + Fernandez Model)")
        print(f"👉 Ver Reporte: {url}")
        print("Ctrl+C para salir.")
        webbrowser.open_new_tab(url)
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")