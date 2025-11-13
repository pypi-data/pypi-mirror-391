import pandas as pd
import os
from pathlib import Path
import glob

def merge_excel_files(folder_path, output_filename="merged_excel.xlsx", sheet_name_prefix="Sheet"):
    """
    Mergea todos los archivos Excel (.xlsx, .xls) de una carpeta en un único archivo.
    
    Args:
        folder_path (str): Ruta de la carpeta que contiene los archivos Excel
        output_filename (str): Nombre del archivo de salida
        sheet_name_prefix (str): Prefijo para los nombres de las hojas en el archivo final
    """
    
    # Verificar que la carpeta existe
    if not os.path.exists(folder_path):
        print(f"Error: La carpeta '{folder_path}' no existe.")
        return
    
    # Buscar todos los archivos Excel en la carpeta
    excel_extensions = ['*.xlsx', '*.xls']
    excel_files = []
    
    for extension in excel_extensions:
        pattern = os.path.join(folder_path, extension)
        excel_files.extend(glob.glob(pattern))
    
    if not excel_files:
        print(f"No se encontraron archivos Excel en la carpeta '{folder_path}'.")
        return
    
    print(f"Encontrados {len(excel_files)} archivos Excel:")
    for file in excel_files:
        print(f"  - {os.path.basename(file)}")
    
    # Crear el archivo Excel de salida
    output_path = os.path.join(folder_path, output_filename)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        sheet_counter = 1
        
        for excel_file in excel_files:
            try:
                # Leer el archivo Excel
                file_name = os.path.splitext(os.path.basename(excel_file))[0]
                
                # Verificar si el archivo tiene múltiples hojas
                excel_data = pd.ExcelFile(excel_file)
                
                for sheet_name in excel_data.sheet_names:
                    # Leer cada hoja
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    
                    # Crear nombre único para la hoja en el archivo final
                    if len(excel_data.sheet_names) == 1:
                        # Si solo tiene una hoja, usar el nombre del archivo
                        final_sheet_name = file_name[:31]  # Excel limita a 31 caracteres
                    else:
                        # Si tiene múltiples hojas, incluir el nombre de la hoja original
                        final_sheet_name = f"{file_name}_{sheet_name}"[:31]
                    
                    # Asegurar que el nombre de la hoja sea único
                    original_name = final_sheet_name
                    counter = 1
                    while final_sheet_name in writer.sheets:
                        final_sheet_name = f"{original_name}_{counter}"[:31]
                        counter += 1
                    
                    # Escribir la hoja al archivo final
                    df.to_excel(writer, sheet_name=final_sheet_name, index=False)
                    print(f"  ✓ Procesado: {os.path.basename(excel_file)} -> {final_sheet_name}")
                
            except Exception as e:
                print(f"  ✗ Error procesando {os.path.basename(excel_file)}: {str(e)}")
                continue
    
    print(f"\n¡Proceso completado! Archivo guardado como: {output_path}")

def merge_excel_files_single_sheet(folder_path, output_filename="merged_excel.xlsx"):
    """
    Mergea todos los archivos Excel de una carpeta en una sola hoja (concatenando filas).
    Útil cuando todos los archivos tienen la misma estructura.
    
    Args:
        folder_path (str): Ruta de la carpeta que contiene los archivos Excel
        output_filename (str): Nombre del archivo de salida
    """
    
    # Verificar que la carpeta existe
    if not os.path.exists(folder_path):
        print(f"Error: La carpeta '{folder_path}' no existe.")
        return
    
    # Buscar todos los archivos Excel en la carpeta
    excel_extensions = ['*.xlsx', '*.xls']
    excel_files = []
    
    for extension in excel_extensions:
        pattern = os.path.join(folder_path, extension)
        excel_files.extend(glob.glob(pattern))
    
    if not excel_files:
        print(f"No se encontraron archivos Excel en la carpeta '{folder_path}'.")
        return
    
    print(f"Encontrados {len(excel_files)} archivos Excel para concatenar:")
    
    # Lista para almacenar todos los DataFrames
    all_dataframes = []
    
    for excel_file in excel_files:
        try:
            # Leer solo la primera hoja de cada archivo
            df = pd.read_excel(excel_file, sheet_name=0)
            
            # Agregar una columna con el nombre del archivo fuente
            df['archivo_fuente'] = os.path.basename(excel_file)
            
            all_dataframes.append(df)
            print(f"  ✓ Leído: {os.path.basename(excel_file)} ({len(df)} filas)")
            
        except Exception as e:
            print(f"  ✗ Error leyendo {os.path.basename(excel_file)}: {str(e)}")
            continue
    
    if not all_dataframes:
        print("No se pudieron leer archivos Excel válidos.")
        return
    
    # Concatenar todos los DataFrames
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Guardar el archivo final
    output_path = os.path.join(folder_path, output_filename)
    merged_df.to_excel(output_path, index=False)
    
    print(f"\n¡Proceso completado!")
    print(f"Archivo guardado como: {output_path}")
    print(f"Total de filas en el archivo final: {len(merged_df)}")

if __name__ == "__main__":
    print("=== MERGER DE ARCHIVOS EXCEL ===\n")
    
    # Solicitar la ruta de la carpeta
    folder_path = input("Ingresa la ruta de la carpeta con los archivos Excel: ").strip()
    
    if not folder_path:
        print("Usando carpeta actual...")
        folder_path = "."
    
    # Preguntar el tipo de merge
    print("\nSelecciona el tipo de merge:")
    print("1. Cada archivo Excel como hoja separada")
    print("2. Todos los archivos concatenados en una sola hoja")
    
    choice = input("Elige una opción (1 o 2): ").strip()
    
    # Solicitar nombre del archivo de salida
    output_name = input("Nombre del archivo de salida (presiona Enter para usar 'merged_excel.xlsx'): ").strip()
    if not output_name:
        output_name = "merged_excel.xlsx"
    
    if not output_name.endswith('.xlsx'):
        output_name += '.xlsx'
    
    print("\nIniciando proceso de merge...\n")
    
    if choice == "2":
        merge_excel_files_single_sheet(folder_path, output_name)
    else:
        merge_excel_files(folder_path, output_name)