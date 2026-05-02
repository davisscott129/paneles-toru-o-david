from pulp import *

# ─── Datos base de los paneles ─────────────────────────────────────────────
PANELES = {
    'A': {'costo': 190, 'area': 1.9, 'potencia': 400},
    'B': {'costo': 205, 'area': 2.1, 'potencia': 450},
    'C': {'costo': 255, 'area': 2.5, 'potencia': 550},
}

HSP          = 4.5    # Horas Solares Pico diarias
VIDA_UTIL    = 20     # años
DEGRADACION  = 0.005  # 0.5% anual de degradación

# Tipo de cambio de referencia (CRC por USD) — ajustable por el usuario en la UI
TC_DEFAULT   = 520.0  # colones por dólar


def resolver(
    area_disponible: float,
    demanda_diaria: float,
    max_inversion: float | None = None,
):
    """
    Resuelve el modelo PLE para cualquier combinación de área y demanda.

    Variables de decisión
    ─────────────────────
      Xa : cantidad de paneles tipo A (400 W, $190, 1.9 m²)
      Xb : cantidad de paneles tipo B (450 W, $205, 2.1 m²)
      Xc : cantidad de paneles tipo C (550 W, $255, 2.5 m²)

    Función objetivo
    ─────────────────
      Min Z = 190·Xa + 205·Xb + 255·Xc

    Restricciones
    ─────────────
      R1 Energía : (Xa·400 + Xb·450 + Xc·550)·HSP/1000 ≥ D
      R2 Área    : 1.9·Xa + 2.1·Xb + 2.5·Xc ≤ A
      R3 Opcional: 190·Xa + 205·Xb + 255·Xc ≤ max_inversion
      R4          : Xa, Xb, Xc ∈ ℤ≥0
    """
    modelo = LpProblem('Paneles_Solares', LpMinimize)

    xa = LpVariable('Xa', lowBound=0, cat='Integer')
    xb = LpVariable('Xb', lowBound=0, cat='Integer')
    xc = LpVariable('Xc', lowBound=0, cat='Integer')

    modelo += 190*xa + 205*xb + 255*xc, 'Inversion_total'
    modelo += (400*xa + 450*xb + 550*xc) * HSP / 1000 >= demanda_diaria, 'Energia'
    modelo += 1.9*xa + 2.1*xb + 2.5*xc <= area_disponible, 'Area'

    if max_inversion is not None:
        modelo += 190*xa + 205*xb + 255*xc <= max_inversion, 'Max_inversion'

    modelo.solve(PULP_CBC_CMD(msg=0))

    es_optimo = LpStatus[modelo.status] == 'Optimal'
    xa_val = int(xa.varValue or 0)
    xb_val = int(xb.varValue or 0)
    xc_val = int(xc.varValue or 0)
    inversion  = value(modelo.objective) or 0
    gen_diaria = (xa_val*400 + xb_val*450 + xc_val*550) * HSP / 1000

    return {
        'xa': xa_val,
        'xb': xb_val,
        'xc': xc_val,
        'inversion': inversion,
        'generacion_diaria': gen_diaria,
        'demanda_diaria': demanda_diaria,
        'superavit_diario': gen_diaria - demanda_diaria,
        'es_optimo': es_optimo,
        'status': LpStatus[modelo.status],
    }


def analizar_viabilidad(
    inversion: float,
    consumo_mensual_kwh: float,
    tarifa_kwh_usd: float,
    vida_util: int = VIDA_UTIL,
    degradacion_anual: float = DEGRADACION,
):
    """
    Viabilidad financiera a N años sin VPN ni flujos descontados.

    Retorna dict con:
      ahorro_mensual_inicial, ahorro_acumulado, inversion_recuperada,
      anio_recuperacion, rentabilidad_neta
    """
    ahorro_mensual_inicial = consumo_mensual_kwh * tarifa_kwh_usd
    ahorro_acum   = 0.0
    anio_recup    = None

    for anio in range(1, vida_util + 1):
        factor = (1 - degradacion_anual) ** (anio - 1)
        ahorro_acum += ahorro_mensual_inicial * 12 * factor
        if anio_recup is None and ahorro_acum >= inversion:
            anio_recup = anio

    return {
        'ahorro_mensual_inicial':   ahorro_mensual_inicial,
        'ahorro_acumulado_20_anios': ahorro_acum,
        'inversion_recuperada':     anio_recup is not None,
        'anio_recuperacion':        anio_recup,
        'rentabilidad_neta':        ahorro_acum - inversion,
    }
