import pandas as pd
import sys
import os
from typing import Optional


def compare_excel_files(
    file1_path: str,
    file2_path: str,
    column1_name: str,
    column2_name: str,
    output_path: Optional[str] = None,
    sheet1_name: str = 0,
    sheet2_name: str = 0
) -> pd.DataFrame:
    """
    Compara dos archivos Excel por columnas específicas y elimina las filas del segundo
    archivo que no tengan valores coincidentes en el primero.
    
    Args:
        file1_path (str): Ruta del primer archivo Excel (archivo de referencia)
        file2_path (str): Ruta del segundo archivo Excel (archivo a filtrar)
        column1_name (str): Nombre de la columna en el primer archivo
        column2_name (str): Nombre de la columna en el segundo archivo
        output_path (str, optional): Ruta donde guardar el resultado. Si no se especifica,
                                   se guarda como 'filtered_' + nombre del segundo archivo
        sheet1_name (str/int): Nombre o índice de la hoja del primer archivo (default: 0)
        sheet2_name (str/int): Nombre o índice de la hoja del segundo archivo (default: 0)
    
    Returns:
        pd.DataFrame: DataFrame filtrado con solo las filas que tienen valores coincidentes
    """
    
    try:
        # Leer los archivos Excel
        print(f"Leyendo archivo de referencia: {file1_path}")
        df1 = pd.read_excel(file1_path, sheet_name=sheet1_name)
        
        print(f"Leyendo archivo a filtrar: {file2_path}")
        df2 = pd.read_excel(file2_path, sheet_name=sheet2_name)
        
        # Verificar que las columnas existen
        if column1_name not in df1.columns:
            raise ValueError(f"La columna '{column1_name}' no existe en el primer archivo")
        
        if column2_name not in df2.columns:
            raise ValueError(f"La columna '{column2_name}' no existe en el segundo archivo")
        
        # Obtener los valores únicos de la columna del primer archivo
        reference_values = set(df1[column1_name].dropna())
        
        print(f"Valores únicos en '{column1_name}' del archivo de referencia: {len(reference_values)}")
        print(f"Filas totales en el segundo archivo: {len(df2)}")
        
        # Filtrar el segundo DataFrame manteniendo solo las filas con valores coincidentes
        filtered_df2 = df2[df2[column2_name].isin(reference_values)]
        
        print(f"Filas después del filtrado: {len(filtered_df2)}")
        print(f"Filas eliminadas: {len(df2) - len(filtered_df2)}")
        
        # Guardar el resultado
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(file2_path))[0]
            output_path = f"filtered_{base_name}.xlsx"
        
        filtered_df2.to_excel(output_path, index=False)
        print(f"Archivo filtrado guardado como: {output_path}")
        
        return filtered_df2
        
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar el archivo: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """
    Función principal para ejecutar el script desde línea de comandos
    """
    if len(sys.argv) < 5:
        print("Uso: python python_field_comparer.py <archivo1> <archivo2> <columna1> <columna2> [archivo_salida]")
        print("\nEjemplo:")
        print("python python_field_comparer.py referencia.xlsx datos.xlsx ID ID_CLIENTE")
        print("python python_field_comparer.py referencia.xlsx datos.xlsx ID ID_CLIENTE resultado.xlsx")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    column1_name = sys.argv[3]
    column2_name = sys.argv[4]
    output_path = sys.argv[5] if len(sys.argv) > 5 else None
    
    # Verificar que los archivos existen
    if not os.path.exists(file1_path):
        print(f"Error: El archivo {file1_path} no existe")
        sys.exit(1)
    
    if not os.path.exists(file2_path):
        print(f"Error: El archivo {file2_path} no existe")
        sys.exit(1)
    
    # Ejecutar la comparación
    result_df = compare_excel_files(
        file1_path, 
        file2_path, 
        column1_name, 
        column2_name, 
        output_path
    )
    
    print("\n¡Proceso completado exitosamente!")
    print(f"Resumen del archivo filtrado:")
    print(f"- Filas: {len(result_df)}")
    print(f"- Columnas: {len(result_df.columns)}")


if __name__ == "__main__":
    # Ejemplo de uso directo (descomenta para usar)
    result = compare_excel_files(
        file2_path="contactos_eaac.xlsx",
        file1_path="contactos_incomp_eaac.xlsx",
        column1_name="name",
        column2_name="name",
        output_path="resultado_filtrado.xlsx"
    )

    # Ejecutar desde línea de comandos
    # main()