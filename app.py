"""
☀️  Optimizador de Paneles Solares — UCR Modelos de Optimización Industrial
David Alfredo Valdivia Williams - C4L974
Roger Alejandro Toruño Gutierrez - C4K365
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modelo import (
    resolver_casa, analizar_viabilidad,
    CASAS, PANELES, HSP, VIDA_UTIL,
)

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(
    page_title='Solar Optimizer · UCR',
    page_icon='☀️',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ─── CSS personalizado ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3, h4, .stMetric label {
    font-family: 'Syne', sans-serif !important;
}

/* Fondo principal */
.stApp {
    background: linear-gradient(135deg, #0d0d0d 0%, #111827 60%, #0d1f0f 100%);
    color: #f0f0f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}

/* Header principal */
.hero-header {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
    padding: 2.5rem 2rem;
    border-radius: 18px;
    margin-bottom: 2rem;
    border: 1px solid rgba(16, 185, 129, 0.3);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '☀️';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.15;
}
.hero-header h1 {
    color: #ecfdf5 !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin: 0 0 0.4rem 0;
}
.hero-header p {
    color: #a7f3d0;
    margin: 0;
    font-size: 0.95rem;
    font-weight: 300;
}

/* Cards métricas */
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: rgba(16,185,129,0.5); }
.metric-card .label {
    font-size: 0.75rem;
    color: #6ee7b7;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'Syne', sans-serif;
    color: #ecfdf5;
    line-height: 1;
}
.metric-card .unit {
    font-size: 0.85rem;
    color: #6ee7b7;
    margin-top: 0.3rem;
}

/* Sección bloques */
.section-block {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #a7f3d0;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Badge viable/no viable */
.badge-viable {
    background: rgba(16,185,129,0.15);
    color: #6ee7b7;
    border: 1px solid rgba(16,185,129,0.4);
    padding: 0.3rem 0.9rem;
    border-radius: 99px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
    display: inline-block;
}
.badge-noviable {
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.4);
    padding: 0.3rem 0.9rem;
    border-radius: 99px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
    display: inline-block;
}

/* Tabla de restricciones */
.restrict-row {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 0.7rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.88rem;
}
.restrict-label {
    background: rgba(16,185,129,0.1);
    color: #6ee7b7;
    border: 1px solid rgba(16,185,129,0.25);
    padding: 0.15rem 0.6rem;
    border-radius: 6px;
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    white-space: nowrap;
    min-width: 60px;
    text-align: center;
}

/* Fórmula */
.formula-box {
    background: rgba(16,185,129,0.06);
    border-left: 3px solid #10b981;
    padding: 0.8rem 1.2rem;
    border-radius: 0 10px 10px 0;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: #d1fae5;
    margin: 0.5rem 0;
}

/* Sliders labels */
[data-testid="stSidebar"] label {
    color: #a7f3d0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* Botón principal */
.stButton>button {
    background: linear-gradient(135deg, #065f46, #047857) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton>button:hover { opacity: 0.85 !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    color: #6ee7b7 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #10b981 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] select, .stSelectbox {
    background: rgba(255,255,255,0.04) !important;
}

/* Success / warning / error */
.stAlert {
    border-radius: 10px !important;
}

div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    color: #ecfdf5 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <h1>Optimizador de Paneles Solares</h1>
  <p>Universidad de Costa Rica · Modelos de Optimización Industrial · I Ciclo 2026</p>
  <p style="margin-top:0.4rem; font-size:0.82rem; color:#6ee7b7;">
    David Alfredo Valdivia Williams C4L974 · Roger Alejandro Toruño Gutierrez C4K365
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Parámetros del Modelo")
    st.markdown("---")

    casa_id = st.selectbox(
        "🏠 Seleccionar Casa",
        options=[1, 2, 3],
        format_func=lambda x: f"Casa {x} — {CASAS[x]['area']} m²  |  {CASAS[x]['consumo_mensual']} kWh/mes",
    )

    st.markdown("**Personalizar parámetros:**")
    area_custom = st.slider(
        "📐 Área del techo disponible (m²)",
        min_value=20, max_value=300,
        value=int(CASAS[casa_id]['area']),
        step=5,
    )
    consumo_mensual = st.slider(
        "⚡ Consumo mensual (kWh)",
        min_value=50, max_value=600,
        value=int(CASAS[casa_id]['consumo_mensual']),
        step=5,
    )
    tarifa = st.slider(
        "💵 Tarifa eléctrica (USD/kWh)",
        min_value=0.05, max_value=0.30,
        value=0.115, step=0.005, format="%.3f",
    )
    max_inv = st.checkbox("💰 Limitar inversión máxima")
    inversion_max = None
    if max_inv:
        inversion_max = st.slider("Inversión máxima (USD)", 200, 10000, 2000, step=100)

    st.markdown("---")
    run = st.button("🚀 Optimizar")

# ─── Datos derivados ─────────────────────────────────────────────────────────
consumo_diario = round(consumo_mensual / 30.44, 2)

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Modelo Matemático",
    "⚡ Solución Óptima",
    "📈 Viabilidad Financiera",
    "📊 Comparativo de Casas",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — MODELO MATEMÁTICO
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 📐 Formulación del Modelo")

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        # Variables de decisión
        st.markdown('<div class="section-block">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔢 Variables de Decisión</div>', unsafe_allow_html=True)
        vd = pd.DataFrame({
            "Variable": ["Xₐ", "X_b", "X_c"],
            "Descripción": [
                "Cantidad de paneles tipo A (400 W)",
                "Cantidad de paneles tipo B (450 W)",
                "Cantidad de paneles tipo C (550 W)",
            ],
            "Dominio": ["ℤ ≥ 0", "ℤ ≥ 0", "ℤ ≥ 0"],
        })
        st.dataframe(vd, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Datos de los paneles
        st.markdown('<div class="section-block">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔆 Características de Paneles</div>', unsafe_allow_html=True)
        dp = pd.DataFrame({
            "Tipo": ["A", "B", "C"],
            "Potencia (W)": [400, 450, 550],
            "Área (m²)": [1.9, 2.1, 2.5],
            "Costo (USD)": [190, 205, 255],
            "Gen. diaria (kWh)*": [
                round(400 * HSP / 1000, 3),
                round(450 * HSP / 1000, 3),
                round(550 * HSP / 1000, 3),
            ],
        })
        st.dataframe(dp, hide_index=True, use_container_width=True)
        st.caption(f"* Con {HSP}h HSP (Horas Solares Pico)")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        # Función objetivo
        st.markdown('<div class="section-block">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Función Objetivo</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="formula-box">Min Z = 190·Xₐ + 205·X_b + 255·X_c</div>',
            unsafe_allow_html=True,
        )
        st.caption("Minimizar la inversión inicial total en USD.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Restricciones
        st.markdown('<div class="section-block">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📏 Restricciones del Modelo</div>', unsafe_allow_html=True)

        restr = [
            ("R1 Energía",
             f"(400·Xₐ + 450·X_b + 550·X_c) · {HSP}/1000  ≥  D",
             f"D = {consumo_diario} kWh/día (consumo diario requerido)"),
            ("R2 Área",
             f"1.9·Xₐ + 2.1·X_b + 2.5·X_c  ≤  A",
             f"A = {area_custom} m² (área disponible del techo)"),
            ("R3 Integridad",
             "Xₐ, X_b, X_c  ∈  ℤ",
             "Los paneles son unidades enteras"),
            ("R4 No-neg.",
             "Xₐ, X_b, X_c  ≥  0",
             "No se instalan cantidades negativas"),
        ]
        if inversion_max:
            restr.append(("R5 Inversión",
                          f"190·Xₐ + 205·X_b + 255·X_c  ≤  {inversion_max}",
                          "Presupuesto máximo definido"))

        for lbl, formula, desc in restr:
            st.markdown(
                f'<div class="restrict-row">'
                f'<span class="restrict-label">{lbl}</span>'
                f'<div><div class="formula-box" style="margin:0">{formula}</div>'
                f'<div style="color:#9ca3af;font-size:0.78rem;margin-top:0.3rem">{desc}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Premisas
    st.markdown("---")
    st.markdown("### 📋 Premisas del Modelo")
    premisas = [
        ("☀️ Radiación constante", f"Se asumen {HSP} HSP diarias fijas, sin variaciones estacionales ni días nublados."),
        ("🏠 Techo ideal", "El área del techo es totalmente aprovechable: sin chimeneas, obstáculos ni sombras externas."),
        ("⚡ Demanda estacionaria", "El consumo diario es constante a lo largo del periodo de análisis."),
        ("🔢 Integralidad", "Solo se instalan paneles completos (variables enteras); no se admiten fracciones."),
        ("📉 Degradación", "Para el análisis financiero se aplica una degradación anual del 0.5% en la generación."),
    ]
    cols = st.columns(len(premisas))
    for col, (titulo, desc) in zip(cols, premisas):
        with col:
            st.markdown(
                f'<div class="section-block" style="height:100%">'
                f'<div style="font-family:Syne,sans-serif;font-weight:700;'
                f'font-size:0.9rem;color:#6ee7b7;margin-bottom:0.4rem">{titulo}</div>'
                f'<div style="font-size:0.82rem;color:#9ca3af">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — SOLUCIÓN ÓPTIMA
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    if not run:
        st.info("👈 Ajusta los parámetros en el panel izquierdo y presiona **🚀 Optimizar**.")
    else:
        res = resolver_casa(
            casa_id,
            area_disponible=area_custom,
            demanda_diaria=consumo_diario,
            max_inversion=inversion_max,
        )

        if not res['es_optimo']:
            st.error(
                f"⚠️ No se encontró una solución óptima (status: {res['status']}). "
                "Ajusta el área disponible, la demanda o el presupuesto máximo."
            )
        else:
            st.success(f"✅ Solución óptima encontrada | Status: {res['status']}")

            # KPIs principales
            c1, c2, c3, c4 = st.columns(4)
            def metric_html(label, value, unit):
                return (
                    f'<div class="metric-card">'
                    f'<div class="label">{label}</div>'
                    f'<div class="value">{value}</div>'
                    f'<div class="unit">{unit}</div>'
                    f'</div>'
                )
            c1.markdown(metric_html("Inversión Mínima", f"${res['inversion']:,.0f}", "USD"), unsafe_allow_html=True)
            c2.markdown(metric_html("Paneles Tipo A", res['xa'], "unidades"), unsafe_allow_html=True)
            c3.markdown(metric_html("Paneles Tipo B", res['xb'], "unidades"), unsafe_allow_html=True)
            c4.markdown(metric_html("Paneles Tipo C", res['xc'], "unidades"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c5, c6, c7, c8 = st.columns(4)
            total_paneles = res['xa'] + res['xb'] + res['xc']
            area_usada = res['xa']*1.9 + res['xb']*2.1 + res['xc']*2.5
            c5.markdown(metric_html("Total Paneles", total_paneles, "unidades"), unsafe_allow_html=True)
            c6.markdown(metric_html("Área Utilizada", f"{area_usada:.1f}", f"de {area_custom} m²"), unsafe_allow_html=True)
            c7.markdown(metric_html("Generación Diaria", f"{res['generacion_diaria']:.2f}", "kWh/día"), unsafe_allow_html=True)
            c8.markdown(metric_html("Superávit Diario", f"{res['superavit_diario']:+.2f}", "kWh/día"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_chart, col_interp = st.columns([1, 1], gap="large")

            with col_chart:
                # Gráfico de distribución de paneles
                tipos = ['Panel A\n(400W)', 'Panel B\n(450W)', 'Panel C\n(550W)']
                cantidades = [res['xa'], res['xb'], res['xc']]
                fig = go.Figure(go.Bar(
                    x=tipos,
                    y=cantidades,
                    marker=dict(
                        color=['#065f46', '#059669', '#34d399'],
                        line=dict(color='rgba(255,255,255,0.1)', width=1),
                    ),
                    text=cantidades,
                    textposition='outside',
                    textfont=dict(color='#ecfdf5', family='Syne', size=14),
                ))
                fig.update_layout(
                    title=dict(text='Distribución de Paneles', font=dict(family='Syne', color='#a7f3d0')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(255,255,255,0.03)',
                    font=dict(color='#9ca3af', family='DM Sans'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', title='Cantidad'),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.06)'),
                    margin=dict(t=50, b=20, l=20, r=20),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_interp:
                # Interpretación gerencial
                st.markdown('<div class="section-block" style="height:100%">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🧑‍💼 Interpretación Gerencial</div>', unsafe_allow_html=True)

                superavit = res['superavit_diario']
                st.markdown(f"""
La solución óptima para la **Casa {casa_id}** asigna:
- **{res['xa']} paneles tipo A** (400 W, $190 c/u)
- **{res['xb']} paneles tipo B** (450 W, $205 c/u)
- **{res['xc']} paneles tipo C** (550 W, $255 c/u)

Con una **inversión mínima de USD ${res['inversion']:,.0f}**, el sistema genera
**{res['generacion_diaria']:.2f} kWh/día**, cubriendo la demanda de
**{res['demanda_diaria']:.2f} kWh/día** y dejando un
**{"superávit" if superavit>=0 else "déficit"} de {abs(superavit):.2f} kWh/día**.

El modelo utiliza únicamente **{area_usada:.1f} m²** de los **{area_custom} m²** disponibles,
dejando margen para expansión futura.
                """)

                viab = analizar_viabilidad(
                    inversion=res['inversion'],
                    consumo_mensual_kwh=consumo_mensual,
                    tarifa_kwh=tarifa,
                )
                if viab['inversion_recuperada']:
                    st.markdown(
                        f'<span class="badge-viable">✅ FINANCIERAMENTE VIABLE — recuperación en ~{viab["anio_recuperacion"]} años</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<span class="badge-noviable">⚠️ No se recupera la inversión en 20 años</span>',
                        unsafe_allow_html=True,
                    )
                st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — VIABILIDAD FINANCIERA
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    if not run:
        st.info("👈 Primero ejecuta la optimización.")
    else:
        if res.get('es_optimo'):
            viab = analizar_viabilidad(
                inversion=res['inversion'],
                consumo_mensual_kwh=consumo_mensual,
                tarifa_kwh=tarifa,
            )

            # KPIs financieros
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(
                metric_html("Inversión Inicial", f"${res['inversion']:,.0f}", "USD"),
                unsafe_allow_html=True,
            )
            c2.markdown(
                metric_html("Ahorro Mensual Inicial", f"${viab['ahorro_mensual_inicial']:.1f}", "USD/mes"),
                unsafe_allow_html=True,
            )
            c3.markdown(
                metric_html("Ahorro Acumulado 20 años", f"${viab['ahorro_acumulado_20_anios']:,.0f}", "USD"),
                unsafe_allow_html=True,
            )
            rentab = viab['rentabilidad_neta']
            c4.markdown(
                metric_html(
                    "Rentabilidad Neta",
                    f"{'+'if rentab>=0 else ''}${rentab:,.0f}",
                    "USD en 20 años",
                ),
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Gráfico de recuperación acumulada
            from modelo import DEGRADACION
            años = list(range(0, VIDA_UTIL + 1))
            acum = [0.0]
            ahorro_inicial = viab['ahorro_mensual_inicial'] * 12
            for a in range(1, VIDA_UTIL + 1):
                factor = (1 - DEGRADACION) ** (a - 1)
                acum.append(acum[-1] + ahorro_inicial * factor)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=años, y=acum,
                mode='lines+markers',
                name='Ahorro acumulado',
                line=dict(color='#10b981', width=3),
                marker=dict(size=6, color='#10b981'),
                fill='tozeroy',
                fillcolor='rgba(16,185,129,0.08)',
            ))
            fig2.add_hline(
                y=res['inversion'],
                line_dash='dash',
                line_color='#f59e0b',
                annotation_text=f"Inversión USD ${res['inversion']:,.0f}",
                annotation_font_color='#f59e0b',
            )
            if viab['anio_recuperacion']:
                fig2.add_vline(
                    x=viab['anio_recuperacion'],
                    line_dash='dot',
                    line_color='#34d399',
                    annotation_text=f"Recuperación: año {viab['anio_recuperacion']}",
                    annotation_font_color='#34d399',
                )

            fig2.update_layout(
                title=dict(
                    text=f'Ahorro Acumulado vs. Inversión — Casa {casa_id}',
                    font=dict(family='Syne', color='#a7f3d0'),
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.03)',
                font=dict(color='#9ca3af', family='DM Sans'),
                xaxis=dict(title='Año', gridcolor='rgba(255,255,255,0.06)'),
                yaxis=dict(title='USD', gridcolor='rgba(255,255,255,0.06)'),
                legend=dict(bgcolor='rgba(0,0,0,0)'),
                margin=dict(t=50, b=40, l=60, r=20),
                height=420,
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Conclusión financiera
            st.markdown('<div class="section-block">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📌 Conclusión de Viabilidad Financiera</div>', unsafe_allow_html=True)

            if viab['inversion_recuperada']:
                st.markdown(f"""
**✅ El proyecto ES financieramente viable.**

Con una inversión de **USD ${res['inversion']:,.0f}** y un ahorro mensual inicial de
**USD ${viab['ahorro_mensual_inicial']:.1f}**, el sistema se paga a sí mismo en aproximadamente
**{viab['anio_recuperacion']} años**, dejando una rentabilidad neta de
**USD ${viab['rentabilidad_neta']:,.0f}** al cabo de los 20 años de vida útil.

> **Nota:** Este análisis NO considera VPN, tasa de descuento ni flujos de caja descontados.
> El cálculo refleja el ahorro bruto acumulado aplicando únicamente una degradación
> anual del 0.5% en la generación de los paneles.
                """)
            else:
                st.markdown(f"""
**⚠️ El proyecto NO recupera la inversión en el horizonte de 20 años.**

Con los parámetros actuales, el ahorro acumulado en 20 años (**USD ${viab['ahorro_acumulado_20_anios']:,.0f}**)
no alcanza la inversión inicial (**USD ${res['inversion']:,.0f}**).
Considera reducir la inversión máxima, usar una tarifa eléctrica mayor o revisar el consumo.

> **Nota:** Este análisis NO considera VPN, tasa de descuento ni flujos de caja descontados.
                """)
            st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — COMPARATIVO DE CASAS
# ═══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📊 Solución Óptima para las 3 Casas (datos originales)")
    st.caption("Usando los datos exactos del enunciado de la tarea. Tarifa: USD 0.115/kWh.")

    rows = []
    for cid, cdata in CASAS.items():
        r = resolver_casa(cid)
        v = analizar_viabilidad(
            inversion=r['inversion'],
            consumo_mensual_kwh=cdata['consumo_mensual'],
            tarifa_kwh=0.115,
        )
        rows.append({
            "Casa": f"Casa {cid}",
            "Área (m²)": cdata['area'],
            "Demanda (kWh/día)": cdata['consumo_diario'],
            "Paneles A": r['xa'],
            "Paneles B": r['xb'],
            "Paneles C": r['xc'],
            "Total paneles": r['xa']+r['xb']+r['xc'],
            "Inversión (USD)": f"${r['inversion']:,.0f}",
            "Gen. diaria (kWh)": round(r['generacion_diaria'], 3),
            "Ahorro 20 años (USD)": f"${v['ahorro_acumulado_20_anios']:,.0f}",
            "Recuperación (año)": v['anio_recuperacion'] or "No",
            "Viable": "✅" if v['inversion_recuperada'] else "⚠️",
        })

    df_comp = pd.DataFrame(rows)
    st.dataframe(df_comp, hide_index=True, use_container_width=True)

    # Gráfico comparativo de inversiones
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        inversiones = [
            resolver_casa(cid)['inversion']
            for cid in CASAS
        ]
        fig3 = go.Figure(go.Bar(
            x=[f"Casa {cid}" for cid in CASAS],
            y=inversiones,
            marker=dict(color=['#065f46', '#059669', '#34d399']),
            text=[f"${v:,.0f}" for v in inversiones],
            textposition='outside',
            textfont=dict(color='#ecfdf5', family='Syne'),
        ))
        fig3.update_layout(
            title=dict(text="Inversión Óptima por Casa", font=dict(family='Syne', color='#a7f3d0')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.03)',
            font=dict(color='#9ca3af'),
            yaxis=dict(title='USD', gridcolor='rgba(255,255,255,0.06)'),
            margin=dict(t=50, b=20, l=60, r=20),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        generaciones = [
            resolver_casa(cid)['generacion_diaria']
            for cid in CASAS
        ]
        demandas = [CASAS[cid]['consumo_diario'] for cid in CASAS]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            name='Generación', x=[f"Casa {cid}" for cid in CASAS],
            y=generaciones, marker_color='#10b981',
            text=[f"{v:.2f}" for v in generaciones], textposition='outside',
            textfont=dict(color='#ecfdf5', family='Syne'),
        ))
        fig4.add_trace(go.Bar(
            name='Demanda', x=[f"Casa {cid}" for cid in CASAS],
            y=demandas, marker_color='rgba(245,158,11,0.6)',
            text=[f"{v:.2f}" for v in demandas], textposition='outside',
            textfont=dict(color='#ecfdf5', family='Syne'),
        ))
        fig4.update_layout(
            title=dict(text="Generación vs Demanda Diaria (kWh)", font=dict(family='Syne', color='#a7f3d0')),
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.03)',
            font=dict(color='#9ca3af'),
            yaxis=dict(title='kWh/día', gridcolor='rgba(255,255,255,0.06)'),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=50, b=20, l=60, r=20),
        )
        st.plotly_chart(fig4, use_container_width=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#374151;font-size:0.78rem;font-family:DM Sans,sans-serif">'
    'Universidad de Costa Rica · Modelos de Optimización Industrial · I Ciclo 2026 · '
    'David Alfredo Valdivia Williams C4L974 · Roger Alejandro Toruño Gutierrez C4K365'
    '</div>',
    unsafe_allow_html=True,
)
