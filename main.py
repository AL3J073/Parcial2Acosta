import os
import csv
import json
from core import validar_patente, calcular_minutos, liquidar_estadia
from batch import procesar_lotes

def cargar_tarifas():
    with open('tarifas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def cobro_manual():
    try:
        config_tarifas = cargar_tarifas()
    except Exception:
        print("Error: No se encontró el archivo 'tarifas.json'. Asegúrese de que esté en la misma carpeta.")
        return

    print("\n--- COBRO MANUAL EN VENTANILLA ---")
    patente = input("Ingrese la patente: ")
    patente_valida = validar_patente(patente)
    while not patente_valida:
        print("Patente inválida. Formatos admitidos: AAA123 o AA123BB")
        patente = input("Ingrese la patente: ")
        patente_valida = validar_patente(patente)

    tipo = input("Tipo de vehículo (moto, auto, camioneta): ").strip().lower()
    while tipo not in config_tarifas["tarifas"]:
        print("Tipo inválido. Opciones válidas: moto, auto, camioneta.")
        tipo = input("Tipo de vehículo (moto, auto, camioneta): ").strip().lower()

    try:
        dias = int(input("¿Cuántos días pasaron? (0 si se retira hoy): "))
    except ValueError:
        dias = 0

    minutos = 0
    entrada, salida = "", ""
    if dias == 0:
        entrada = input("Hora de entrada (HH:MM): ")
        salida = input("Hora de salida (HH:MM): ")
        minutos = calcular_minutos(entrada, salida)
    else:
        print("Liquidando por días completos a costo fijo (no se requiere hora de salida).")

    lavado_input = input("¿Solicitó lavado? (S/N): ").strip().upper()
    lavado = lavado_input == 'S'

    total = liquidar_estadia(minutos, dias, lavado, tipo, config_tarifas)

    print("\n--- DESGLOSE CONTABLE ---")
    print(f"Patente: {patente_valida}")
    if dias == 0:
        print(f"Tiempo: {minutos} minutos")
    else:
        print(f"Tiempo: {dias} días completos")
    print(f"Lavado: {'Sí' if lavado else 'No'}")
    print(f"TOTAL A PAGAR: ${total}")
    print("-------------------------\n")

    archivo_csv = 'liquidacion-manual.csv'
    existe = os.path.exists(archivo_csv)
    with open(archivo_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["patente", "tipo_vehiculo", "dias", "minutos", "lavado", "entrada", "salida", "total"])
        writer.writerow([patente_valida, tipo, dias, minutos, lavado, entrada, salida, total])
    print("Registro manual guardado en 'liquidacion-manual.csv'.")

def menu():
    while True:
        print("==================================================")
        print("   SISTEMA DE GESTIÓN DE ESTACIONAMIENTO AUTOPARK")
        print("==================================================")
        print("1. Registrar / Consultar cobro manual")
        print("2. Procesar lote de movimientos (JSON -> CSV)")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            cobro_manual()
        elif opcion == '2':
            procesar_lotes()
        elif opcion == '3':
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    menu()
