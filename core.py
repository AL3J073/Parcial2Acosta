import re

def validar_patente(patente):
    patente_limpia = patente.strip().upper().replace(" ", "")
    patron_tradicional = r'^[A-Z]{3}[0-9]{3}$'
    patron_mercosur = r'^[A-Z]{2}[0-9]{3}[A-Z]{2}$'
    
    if re.match(patron_tradicional, patente_limpia) or re.match(patron_mercosur, patente_limpia):
        return patente_limpia
    return None

def calcular_minutos(hora_entrada, hora_salida):
    h_in, m_in = map(int, hora_entrada.split(':'))
    h_out, m_out = map(int, hora_salida.split(':'))
    
    min_in = h_in * 60 + m_in
    min_out = h_out * 60 + m_out
    
    # Desafío Nivel 1: Tratamiento de Medianoche
    if min_out < min_in:
        return (1440 - min_in) + min_out
    return min_out - min_in

def calcular_estacionamiento_recursivo(minutos_restantes, tipo_vehiculo, tarifas_vehiculo):
    if minutos_restantes <= 0:
        return 0
    
    if minutos_restantes > 120:
        excedente = minutos_restantes - 120
        resta = 60 if excedente >= 60 else excedente
        return tarifas_vehiculo["precio_hora_adicional"] + calcular_estacionamiento_recursivo(minutos_restantes - resta, tipo_vehiculo, tarifas_vehiculo)
    else:
        return tarifas_vehiculo["precio_bloque_30min"] + calcular_estacionamiento_recursivo(minutos_restantes - 30, tipo_vehiculo, tarifas_vehiculo)

def liquidar_estadia(minutos_totales, dias, solicito_lavado, tipo_vehiculo, config_tarifas):
    tipo_vehiculo = tipo_vehiculo.strip().lower()
    if tipo_vehiculo not in config_tarifas["tarifas"]:
        raise ValueError(f"Tipo de vehículo desconocido: {tipo_vehiculo}")
        
    tarifas_v = config_tarifas["tarifas"][tipo_vehiculo]
    tope_dia = tarifas_v["tope_dia"]
    precio_lavado = tarifas_v["precio_lavado"]
    
    costo_lavado = precio_lavado if solicito_lavado else 0
    
    if dias > 0:
        return (dias * tope_dia) + costo_lavado
        
    costo_estacionamiento = calcular_estacionamiento_recursivo(minutos_totales, tipo_vehiculo, tarifas_v)
    
    if costo_estacionamiento > tope_dia:
        costo_estacionamiento = tope_dia
        
    if solicito_lavado:
        if minutos_totales <= 120:
            costo_estacionamiento = 0
        else:
            bonificacion = 4 * tarifas_v["precio_bloque_30min"]
            costo_estacionamiento = max(0, costo_estacionamiento - bonificacion)
            
    return costo_estacionamiento + costo_lavado
