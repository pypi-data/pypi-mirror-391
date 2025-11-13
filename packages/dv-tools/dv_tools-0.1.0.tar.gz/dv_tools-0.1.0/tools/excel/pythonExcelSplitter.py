import pandas as pd
import math
import os


def dividir_excel(archivo_origen, filas_por_archivo=3000, carpeta_destino="excels_divididos"):
    """
    Divide un archivo Excel en varios archivos más pequeños

    Parámetros:
    - archivo_origen: ruta del archivo Excel original
    - filas_por_archivo: número de filas por cada archivo nuevo
    - carpeta_destino: carpeta donde guardar los archivos divididos
    """

    # Crear carpeta de destino si no existe
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Leer el archivo Excel
    print(f"Leyendo archivo: {archivo_origen}")
    df = pd.read_excel(archivo_origen)

    total_filas = len(df)
    num_archivos = math.ceil(total_filas / filas_por_archivo)

    print(f"Total de filas: {total_filas}")
    print(f"Se crearán {num_archivos} archivos con máximo {filas_por_archivo} filas cada uno")

    # Obtener el nombre base del archivo
    nombre_base = os.path.splitext(os.path.basename(archivo_origen))[0]

    # Dividir y guardar
    for i in range(num_archivos):
        inicio = i * filas_por_archivo
        fin = min((i + 1) * filas_por_archivo, total_filas)

        # Extraer chunk de datos
        chunk = df.iloc[inicio:fin]

        # Nombre del archivo nuevo
        nombre_archivo = f"{nombre_base}_parte_{i + 1:03d}.xlsx"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        # Guardar chunk
        chunk.to_excel(ruta_completa, index=False)

        print(f"Guardado: {nombre_archivo} (filas {inicio + 1} a {fin})")

    print(f"\n¡Proceso completado! Archivos guardados en: {carpeta_destino}")


# Ejemplo de uso
if __name__ == "__main__":
    # Cambia estos valores según tus necesidades
    archivo_original = "clientes_instalaciones.xlsx"  # Cambia por tu archivo
    filas_por_archivo = 1000  # Ajusta según necesites

    dividir_excel(archivo_original, filas_por_archivo)

    # También puedes especificar una carpeta diferente:
    # dividir_excel(archivo_original, filas_por_archivo, "mi_carpeta_custom")