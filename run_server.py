# -*- coding: utf-8 -*-
"""
Script de Python para iniciar un servidor web local.
Incluye: Calculadora GEI, Gráficos con Chart.js y Modo Reporte de Impresión.
"""
import http.server
import socketserver
import webbrowser
import os

# --- Contenido del archivo HTML actualizado ---
html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Huella de Carbono (GEI)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f0fdf4; }
        
        /* ESTILOS PARA IMPRESIÓN (Reporte Limpio) */
        @media print {
            @page { margin: 1.5cm; size: auto; }
            body { background-color: white; -webkit-print-color-adjust: exact; }
            .no-print { display: none !important; } /* Ocultar selectores y botones */
            .print-only { display: block !important; }
            #app { box-shadow: none; border: none; max-width: 100%; padding: 0; }
            h1 { color: #166534 !important; } /* Verde oscuro forzado */
            .page-break { page-break-before: always; }
        }
    </style>
</head>
<body class="p-4 sm:p-8 text-gray-800">

    <div id="app" class="max-w-5xl mx-auto bg-white shadow-2xl rounded-2xl overflow-hidden p-8 border border-green-100">
        
        <header class="mb-8 border-b border-green-200 pb-6 flex justify-between items-center">
            <div>
                <h1 class="text-3xl sm:text-4xl font-extrabold text-green-800 flex items-center gap-3">
                    <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Reporte de Emisiones GEI
                </h1>
                <p class="text-gray-500 mt-2 font-medium">Cálculo de Huella de Carbono para Proyectos de Infraestructura</p>
                <p id="project-subtitle" class="text-green-600 text-sm font-bold mt-1 uppercase tracking-wide">PROYECTO: LOGROÑO</p>
            </div>
            <button onclick="window.print()" class="no-print bg-gray-800 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg flex items-center gap-2 transition shadow-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                Imprimir / PDF
            </button>
        </header>

        <div class="no-print mb-8 bg-green-50 p-6 rounded-xl border border-green-200">
            <h3 class="text-green-800 font-bold mb-3 uppercase text-sm tracking-wider">Configuración del Proyecto</h3>
            <label for="project-selector" class="block text-sm font-medium text-gray-700 mb-2">Seleccione Ubicación:</label>
            <select id="project-selector" class="w-full p-3 border border-green-300 rounded-lg bg-white focus:ring-green-500 focus:border-green-500">
                <option value="logroño" selected>Logroño (Datos Presupuesto)</option>
                <option value="rumiñahui">Rumiñahui (Agua Potable)</option>
                <option value="mera">Mera (Saneamiento)</option>
            </select>
            <p class="text-xs text-gray-500 mt-2 italic">Modifique los valores abajo y presione Imprimir para generar el reporte.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            <div class="space-y-6">
                <h2 class="text-xl font-bold text-gray-800 border-l-4 border-green-500 pl-3">1. Desglose de Emisiones</h2>
                
                <div id="results-list" class="space-y-0 divide-y divide-gray-100 border rounded-lg overflow-hidden">
                    </div>

                <div class="bg-green-600 text-white p-5 rounded-xl shadow-lg flex justify-between items-center mt-6">
                    <div>
                        <p class="text-sm font-medium text-green-100 uppercase">Huella Total Estimada</p>
                        <p id="total-emissions" class="text-3xl font-extrabold">0.00 tCO₂e</p>
                    </div>
                    <svg class="w-12 h-12 text-green-200 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                </div>

                <div class="no-print mt-8 pt-6 border-t">
                    <h3 class="text-gray-600 font-bold mb-4 text-sm">EDITAR CANTIDADES (APU):</h3>
                    <form id="calculation-form" class="grid grid-cols-1 gap-4 bg-gray-50 p-4 rounded-lg">
                        </form>
                </div>
            </div>

            <div class="flex flex-col justify-start">
                <h2 class="text-xl font-bold text-gray-800 border-l-4 border-blue-500 pl-3 mb-4">2. Análisis Gráfico</h2>
                <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-inner relative" style="height: 400px;">
                    <canvas id="emissionsChart"></canvas>
                </div>
                <p class="text-xs text-gray-400 text-center mt-4">Gráfico generado automáticamente con Chart.js</p>
                
                <div class="mt-8 pt-4 border-t">
                    <h3 class="text-sm font-bold text-gray-500 mb-2 uppercase">Factores de Emisión Utilizados</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full text-xs text-gray-600">
                            <thead class="bg-gray-100">
                                <tr><th class="px-2 py-1 text-left">Rubro</th><th class="px-2 py-1 text-right">FE (tCO₂e/u)</th></tr>
                            </thead>
                            <tbody id="fe-summary-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <footer class="mt-12 border-t pt-6 text-center text-xs text-gray-400">
            <p>Generado el: <span id="current-date"></span> | Consultoría Ambiental y Cartográfica</p>
        </footer>

    </div>

    <script>
        // --- CONFIGURACIÓN DE DATOS ---
        const factors = {
            logroño: {
                'Hormigón y Mortero': { unit: 'm³', fe: 0.40, key: 'hormigon_mortero', color: '#10b981' }, 
                'Tubería PVC': { unit: 't', fe: 3.10, key: 'pvc_tuberia', color: '#3b82f6' },
                'Acero de Refuerzo': { unit: 't', fe: 1.85, key: 'acero_refuerzo', color: '#6366f1' },
                'Diésel (Maquinaria)': { unit: 'L', fe: 0.00267, key: 'diesel_obra', color: '#f59e0b' }, 
                'Diésel (Generador)': { unit: 'L', fe: 0.00267, key: 'diesel_respaldo', color: '#f97316' }, 
                'Transporte Excavado': { unit: 't·km', fe: 0.00012, key: 'transporte_excavado', color: '#ef4444' } 
            },
            rumiñahui: {
                'Hormigón y Mortero': { unit: 'm³', fe: 0.40, key: 'hormigon_mortero', color: '#10b981' },
                'Tubería PVC': { unit: 't', fe: 3.10, key: 'pvc_tuberia', color: '#3b82f6' },
                'Acero Refuerzo': { unit: 't', fe: 1.85, key: 'acero_refuerzo', color: '#6366f1' },
                'Mezcla Asfáltica': { unit: 't', fe: 0.08, key: 'asfalto', color: '#1f2937' },
                'Diésel Maquinaria': { unit: 'L', fe: 0.00267, key: 'diesel_obra', color: '#f59e0b' },
                'Insumos Químicos': { unit: 't', fe: 1.00, key: 'quimicos_operacion', color: '#06b6d4' },
            },
            mera: {
                'Hormigón': { unit: 'm³', fe: 0.40, key: 'hormigon_mortero', color: '#10b981' }, 
                'Tubería PVC': { unit: 't', fe: 3.10, key: 'pvc_tuberia', color: '#3b82f6' },
                'Acero Refuerzo': { unit: 't', fe: 1.85, key: 'acero_refuerzo', color: '#6366f1' },
                'Diésel Maquinaria': { unit: 'L', fe: 0.00267, key: 'diesel_obra', color: '#f59e0b' },
                'Diésel Generador': { unit: 'L', fe: 0.00267, key: 'diesel_respaldo', color: '#f97316' },
                'Transp. Excavado': { unit: 't·km', fe: 0.00012, key: 'transporte_excavado', color: '#ef4444' },
                'Trat. Biológico': { unit: 'm³', fe: 0.0003, key: 'tratamiento_biologico', color: '#8b5cf6' } 
            }
        };

        const initial_apus = {
            logroño: { 'hormigon_mortero': 333.73, 'pvc_tuberia': 233.96, 'acero_refuerzo': 10.63, 'diesel_obra': 22085.20, 'diesel_respaldo': 2000, 'transporte_excavado': 249228 },
            rumiñahui: { 'hormigon_mortero': 2111.18, 'pvc_tuberia': 133.13, 'acero_refuerzo': 84.28, 'asfalto': 1111.87, 'diesel_obra': 39218.36, 'quimicos_operacion': 5.45 },
            mera: { 'hormigon_mortero': 1665.24, 'pvc_tuberia': 179.59, 'acero_refuerzo': 104.25, 'diesel_obra': 54121.12, 'diesel_respaldo': 2000, 'transporte_excavado': 219546.83, 'tratamiento_biologico': 746985 }
        };

        // --- VARIABLES GLOBALES ---
        let myChart = null;
        const projectSelector = document.getElementById('project-selector');
        const form = document.getElementById('calculation-form');
        const resultsList = document.getElementById('results-list');
        const feSummaryBody = document.getElementById('fe-summary-body');
        const totalEmissionsElement = document.getElementById('total-emissions');
        const projectSubtitle = document.getElementById('project-subtitle');
        const dateSpan = document.getElementById('current-date');

        dateSpan.innerText = new Date().toLocaleDateString('es-EC', { year: 'numeric', month: 'long', day: 'numeric' });

        // --- FUNCIONES ---

        function initializeApp() {
            const selected = projectSelector.value;
            projectSubtitle.innerText = "PROYECTO: " + selected.toUpperCase();
            renderInputs(selected);
            calculateAndChart();
        }

        function renderInputs(project) {
            form.innerHTML = '';
            feSummaryBody.innerHTML = '';
            const currentFactors = factors[project];
            const currentApus = initial_apus[project] || {};
            const savedData = JSON.parse(localStorage.getItem(`apu_data_${project}`) || '{}');

            for (const [name, data] of Object.entries(currentFactors)) {
                let val = savedData[data.key] !== undefined ? savedData[data.key] : (currentApus[data.key] || 0);
                
                // Input en formulario
                const div = document.createElement('div');
                div.innerHTML = `
                    <label class="block text-xs font-bold text-gray-500 uppercase">${name} (${data.unit})</label>
                    <input type="number" step="any" id="${data.key}" value="${val}" 
                        class="w-full p-2 border rounded text-sm focus:border-green-500 focus:outline-none">
                `;
                form.appendChild(div);

                // Fila en tabla de resumen FE
                const tr = document.createElement('tr');
                tr.className = "border-b border-gray-50";
                tr.innerHTML = `<td class="px-2 py-1">${name}</td><td class="px-2 py-1 text-right font-mono">${data.fe}</td>`;
                feSummaryBody.appendChild(tr);
            }
            
            // Listeners
            form.querySelectorAll('input').forEach(inp => inp.addEventListener('input', calculateAndChart));
        }

        function calculateAndChart() {
            const project = projectSelector.value;
            const currentFactors = factors[project];
            
            let total = 0;
            let labels = [];
            let dataValues = [];
            let bgColors = [];
            let resultsHTML = '';

            for (const [name, data] of Object.entries(currentFactors)) {
                const inp = document.getElementById(data.key);
                const cant = parseFloat(inp.value) || 0;
                const emision = cant * data.fe;
                
                total += emision;
                
                // Data para gráfico
                labels.push(name);
                dataValues.push(emision);
                bgColors.push(data.color || '#ccc');

                // HTML de lista de resultados
                resultsHTML += `
                    <div class="flex justify-between items-center p-3 bg-white">
                        <div class="flex items-center gap-2">
                            <span class="w-3 h-3 rounded-full" style="background-color: ${data.color}"></span>
                            <span class="text-sm text-gray-700 font-medium">${name}</span>
                        </div>
                        <span class="text-sm font-bold text-gray-900">${emision.toFixed(2)} <span class="text-xs text-gray-500 font-normal">tCO₂e</span></span>
                    </div>
                `;
            }

            resultsList.innerHTML = resultsHTML;
            totalEmissionsElement.innerText = total.toFixed(2) + " tCO₂e";

            updateChart(labels, dataValues, bgColors);
            saveLocal(project);
        }

        function updateChart(labels, data, colors) {
            const ctx = document.getElementById('emissionsChart').getContext('2d');
            
            if (myChart) {
                myChart.destroy();
            }

            myChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 12 } },
                        title: { display: true, text: 'Distribución de Emisiones (tCO₂e)' }
                    },
                    layout: { padding: 10 }
                }
            });
        }

        function saveLocal(project) {
            const currentFactors = factors[project];
            const values = {};
            for (const data of Object.values(currentFactors)) {
                const inp = document.getElementById(data.key);
                values[data.key] = parseFloat(inp.value) || 0;
            }
            localStorage.setItem(`apu_data_${project}`, JSON.stringify(values));
        }

        projectSelector.addEventListener('change', initializeApp);
        window.onload = initializeApp;

    </script>
</body>
</html>
"""

# Puerto para el servidor
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler
HTML_FILE = "index.html"

# --- Guardar el contenido HTML ---
try:
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Archivo '{HTML_FILE}' actualizado con gráficos y modo reporte.")
except IOError as e:
    print(f"❌ Error al escribir: {e}")
    exit()

# --- Iniciar Servidor ---
try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        server_url = f"http://localhost:{PORT}/{HTML_FILE}"
        print("\n" + "="*60)
        print(f"🚀 CALCULADORA GEI MEJORADA (Versión Gráfica)")
        print(f"👉 Abre aquí: {server_url}")
        print("="*60 + "\n")
        webbrowser.open_new_tab(server_url)
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido. ¡Buen trabajo!")
except Exception as e:
    print(f"\n⚠️ Error: {e}")