import json
import csv
import os
from core import validar_patente, calcular_minutos, liquidar_estadia

def procesar_lotes():
    try:
        with open('tarifas.json', 'r', encoding='utf-8') as f:
            config_tarifas = json.load(f)
        with open('movimientos.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        print(f"Error al leer archivos JSON: {e}")
        return

    procesados = []
    rechazados = []
    recaudacion_total = 0

    for mov in datos.get("movimientos", []):
        patente = validar_patente(mov.get("patente", ""))
        if not patente:
            mov["motivo_rechazo"] = "Patente inválida"
            rechazados.append(mov)
            continue
            
        tipo_vehiculo = mov.get("tipo_vehiculo", "").strip().lower()
        if tipo_vehiculo not in config_tarifas["tarifas"]:
            mov["motivo_rechazo"] = "Tipo de vehículo inválido"
            rechazados.append(mov)
            continue

        try:
            minutos = calcular_minutos(mov["entrada"], mov["salida"])
            total = liquidar_estadia(minutos, 0, mov["solicito_lavado"], tipo_vehiculo, config_tarifas)
            mov["patente"] = patente
            mov["tipo_vehiculo"] = tipo_vehiculo
            mov["minutos_totales"] = minutos
            mov["total_cobrado"] = total
            procesados.append(mov)
            recaudacion_total += total
        except Exception as e:
            mov["motivo_rechazo"] = str(e)
            rechazados.append(mov)

    # Exportar a CSV
    if procesados:
        with open('liquidacion.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "patente", "tipo_vehiculo", "entrada", "salida", "solicito_lavado", "minutos_totales", "total_cobrado"])
            writer.writeheader()
            for p in procesados:
                writer.writerow({k: p[k] for k in writer.fieldnames})
                
    if rechazados:
        with open('rechazados.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "patente", "tipo_vehiculo", "entrada", "salida", "solicito_lavado", "motivo_rechazo"])
            writer.writeheader()
            for r in rechazados:
                writer.writerow({k: r.get(k, "") for k in writer.fieldnames})

    print("\n--- RESUMEN DE PROCESAMIENTO POR LOTE ---")
    print(f"Procesados con éxito: {len(procesados)}")
    print(f"Rechazados por errores: {len(rechazados)}")
    print(f"Recaudación total del lote: ${recaudacion_total}")
    print("Se generaron los archivos 'liquidacion.csv' y 'rechazados.csv'")
    print("-------------------------------------------\n")
