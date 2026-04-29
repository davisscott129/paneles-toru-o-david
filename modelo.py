from pulp import *

# ─── Datos base del proyecto ───────────────────────────────────────────────
PANELES = {
    'A': {'costo': 190, 'area': 1.9, 'potencia': 400},
    'B': {'costo': 205, 'area': 2.1, 'potencia': 450},
    'C': {'costo': 255, 'area': 2.5, 'potencia': 550},
}

CASAS = {
    1: {'area': 156,  'consumo_mensual': 280.0,  'consumo_diario': 9.03},
    2: {'area': 238,  'consumo_mensual': 128.5,  'consumo_diario': 4.15},
    3: {'area': 120,  'consumo_mensual': 284.5,  'consumo_diario': 9.17},
}

HSP = 4.5          # Horas Solares Pico diarias
TARIFA_KWH = 0.115  # USD por kWh (tarifa ICE residencial aprox.)
VIDA_UTIL = 20     # años
DEGRADACION = 0.005 # 0.5% anual de degradación de los paneles


def resolver_casa(
    casa_id: int,
    area_disponible: float | None = None,
    demanda_diaria: float | None = None,
    max_inversion: float | None = None,
):
    """
    Resuelve el modelo de Programación Lineal Entera (PLE) para una casa.

    Variables de decisión
    ─────────────────────
      Xa : cantidad de paneles tipo A (400 W, $190, 1.9 m²)
      Xb : cantidad de paneles tipo B (450 W, $205, 2.1 m²)
      Xc : cantidad de paneles tipo C (550 W, $255, 2.5 m²)

    Función objetivo
    ─────────────────
      Min Z = 190·Xa + 205·Xb + 255·Xc   (minimizar inversión inicial)

    Restricciones
    ─────────────
      1. Energía:  (Xa·400 + Xb·450 + Xc·550)·HSP/1000 ≥ D  [kWh/día]
      2. Área:      1.9·Xa + 2.1·Xb + 2.5·Xc ≤ A            [m²]
      3. Inversión:  190·Xa + 205·Xb + 255·Xc ≤ max_inversion (opcional)
      4. No negatividad + integralidad: Xa, Xb, Xc ∈ ℤ≥0

    Retorna
    ───────
      dict con xa, xb, xc, inversion, generacion_diaria, es_optimo
    """
    casa = CASAS[casa_id]
    A = area_disponible if area_disponible is not None else casa['area']
    D = demanda_diaria  if demanda_diaria  is not None else casa['consumo_diario']

    modelo = LpProblem(f'Paneles_Casa_{casa_id}', LpMinimize)

    xa = LpVariable('Xa', lowBound=0, cat='Integer')
    xb = LpVariable('Xb', lowBound=0, cat='Integer')
    xc = LpVariable('Xc', lowBound=0, cat='Integer')

    # Función objetivo
    modelo += 190*xa + 205*xb + 255*xc, 'Inversion_total'

    # Restricción 1: energía mínima (kWh/día)
    modelo += (400*xa + 450*xb + 550*xc) * HSP / 1000 >= D, 'Energia'

    # Restricción 2: área disponible
    modelo += 1.9*xa + 2.1*xb + 2.5*xc <= A, 'Area'

    # Restricción 3: inversión máxima (opcional)
    if max_inversion is not None:
        modelo += 190*xa + 205*xb + 255*xc <= max_inversion, 'Max_inversion'

    modelo.solve(PULP_CBC_CMD(msg=0))

    es_optimo = LpStatus[modelo.status] == 'Optimal'

    xa_val = int(xa.varValue or 0)
    xb_val = int(xb.varValue or 0)
    xc_val = int(xc.varValue or 0)
    inversion = value(modelo.objective) or 0
    gen_diaria = (xa_val*400 + xb_val*450 + xc_val*550) * HSP / 1000

    return {
        'xa': xa_val,
        'xb': xb_val,
        'xc': xc_val,
        'inversion': inversion,
        'generacion_diaria': gen_diaria,
        'demanda_diaria': D,
        'superavit_diario': gen_diaria - D,
        'es_optimo': es_optimo,
        'status': LpStatus[modelo.status],
    }


def analizar_viabilidad(
    inversion: float,
    consumo_mensual_kwh: float,
    tarifa_kwh: float = TARIFA_KWH,
    vida_util: int = VIDA_UTIL,
    degradacion_anual: float = DEGRADACION,
):
    """
    Analiza la viabilidad financiera a 20 años SIN calcular VPN ni flujos de caja.

    Retorna
    ───────
      dict con:
        - ahorro_mensual_inicial   : USD/mes en el año 1
        - ahorro_acumulado_20_anios: USD ahorrados al final del periodo
        - inversion_recuperada     : bool — ¿se recupera la inversión?
        - anio_recuperacion        : int o None
        - rentabilidad_neta        : ahorro acumulado - inversión (USD)
    """
    ahorro_acum = 0.0
    ahorro_mensual_inicial = consumo_mensual_kwh * tarifa_kwh
    anio_recuperacion = None

    for anio in range(1, vida_util + 1):
        factor = (1 - degradacion_anual) ** (anio - 1)
        ahorro_anual = ahorro_mensual_inicial * 12 * factor
        ahorro_acum += ahorro_anual
        if anio_recuperacion is None and ahorro_acum >= inversion:
            anio_recuperacion = anio

    return {
        'ahorro_mensual_inicial': ahorro_mensual_inicial,
        'ahorro_acumulado_20_anios': ahorro_acum,
        'inversion_recuperada': anio_recuperacion is not None,
        'anio_recuperacion': anio_recuperacion,
        'rentabilidad_neta': ahorro_acum - inversion,
    }
