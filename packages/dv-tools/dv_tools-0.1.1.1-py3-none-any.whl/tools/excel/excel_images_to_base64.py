import pandas as pd
from openpyxl import load_workbook
import base64

def convertir_imagenes_excel_a_base64(ruta_excel, ruta_salida=None):
    """
    Lee un Excel, reemplaza las imágenes por su representación en base64
    y guarda una copia del archivo.

    Args:
        ruta_excel (str): Ruta al archivo Excel original
        ruta_salida (str): Ruta del archivo de salida (opcional)

    Returns:
        DataFrame: DataFrame con las imágenes convertidas a base64
    """
    # Si no se especifica ruta de salida, crear una automáticamente
    if ruta_salida is None:
        nombre_base = ruta_excel.rsplit('.', 1)[0]
        ruta_salida = f"{nombre_base}_base64.xlsx"

    # Cargar el workbook con openpyxl para extraer imágenes
    wb = load_workbook(ruta_excel)
    ws = wb.active

    # Diccionario para mapear posiciones a base64
    imagenes_por_posicion = {}

    # Extraer imágenes y sus posiciones
    if hasattr(ws, '_images'):
        for img in ws._images:
            try:
                # Obtener datos de la imagen
                img_data = img._data()

                # Convertir a base64
                img_base64 = base64.b64encode(img_data).decode('utf-8')

                # Detectar el formato de imagen
                formato = img.format if hasattr(img, 'format') else 'png'

                # Agregar prefijo data URI para Odoo
                if formato.lower() in ['jpg', 'jpeg']:
                    img_base64 = f"data:image/jpeg;base64,{img_base64}"
                elif formato.lower() == 'png':
                    img_base64 = f"data:image/png;base64,{img_base64}"
                elif formato.lower() == 'gif':
                    img_base64 = f"data:image/gif;base64,{img_base64}"
                else:
                    img_base64 = f"data:image/{formato.lower()};base64,{img_base64}"

                # Obtener posición (columna y fila)
                col = img.anchor._from.col
                row = img.anchor._from.row

                # Guardar en diccionario
                imagenes_por_posicion[(row, col)] = img_base64

            except Exception as e:
                print(f"Error al procesar una imagen: {e}")

    # Leer el Excel con pandas
    df = pd.read_excel(ruta_excel)

    # Crear una copia del DataFrame y convertir todas las columnas a object
    df_nuevo = df.copy()
    df_nuevo = df_nuevo.astype(object)

    # Reemplazar imágenes por base64 en las posiciones correspondientes
    for (row, col), base64_str in imagenes_por_posicion.items():
        if row < len(df_nuevo) and col < len(df_nuevo.columns):
            df_nuevo.iloc[row, col] = base64_str

    # Guardar el nuevo archivo
    df_nuevo.to_excel(ruta_salida, index=False)

    print(f"Archivo guardado en: {ruta_salida}")
    print(f"Imágenes convertidas: {len(imagenes_por_posicion)}")

    return df_nuevo

# Ejemplo de uso
if __name__ == "__main__":
    ruta_archivo = "piezas.xlsx"

    try:
        df_resultado = convertir_imagenes_excel_a_base64(ruta_archivo)
        print("\nProceso completado exitosamente")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'")
    except Exception as e:
        print(f"Error: {e}")
