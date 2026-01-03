import os
import yaml

def load_yaml(ruta_archivo):
    # Verificamos que el archivo exista para evitar errores
    if not os.path.exists(ruta_archivo):
        print(f"Error: No se encontró el archivo en {ruta_archivo}")
        return None

    with open(ruta_archivo, 'r') as file:
        try:
            # yaml.safe_load es la forma segura de convertir el archivo a datos de Python
            contenido = yaml.safe_load(file)
            print("--- Archivo YAML cargado exitosamente ---")
            return contenido
        except yaml.YAMLError as exc:
            print(f"Error leyendo YAML: {exc}")
            return None
