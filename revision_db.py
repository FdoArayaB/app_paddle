import sqlite3
import pandas as pd

# Nombre de tu base de datos
DB_NAME = "padel.db"

def revisar_tabla(nombre_tabla):
    """
    Conecta a la base de datos y muestra todo el contenido de una tabla.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        
        # Lee la tabla completa en un DataFrame de pandas
        df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla};", conn)
        
        if df.empty:
            print(f"📋 La tabla '{nombre_tabla}' está vacía.")
        else:
            print(f"📋 Contenido de la tabla '{nombre_tabla}':")
            print("-" * 50)
            print(df)
            print("-" * 50)
            
    except pd.io.sql.DatabaseError as e:
        print(f"⚠️ Error: La tabla '{nombre_tabla}' no existe o ha ocurrido un error al leerla.")
        print(f"Detalles: {e}")
    except sqlite3.Error as e:
        print(f"⚠️ Error en la base de datos: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("✅ Conexión cerrada.")

if __name__ == "__main__":
    # --- Usa esta función para revisar tus tablas ---
    # Revisa la tabla de usuarios
    revisar_tabla("usuarios")
    
    # Revisa la tabla de equipos
    revisar_tabla("equipos")
    
    # Revisa la tabla de jugadores_equipos
    revisar_tabla("jugadores_equipos")
    
    # Revisa la tabla de partidos
    revisar_tabla("partidos")
    
    # Revisa la tabla de equipos_partidos
    revisar_tabla("equipos_partidos")
    
    # Revisa la tabla de sets
    revisar_tabla("sets")