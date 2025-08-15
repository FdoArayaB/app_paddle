import sqlite3

# Nombre de tu base de datos
DB_NAME = "padel.db"

# Conexión a la base de datos
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Consulta SQL para borrar todos los registros de la tabla equipos_partidos
query = "DELETE FROM equipos_partidos;"
query = "DELETE FROM partidos;"

try:
    # 1. Ejecutar la consulta de eliminación
    cursor.execute(query)

    # 2. Confirmar los cambios en la base de datos
    conn.commit()
    print("✅ Todos los registros de la tabla 'equipos_partidos' han sido eliminados.")
except sqlite3.Error as e:
    print(f"⚠️ Ha ocurrido un error: {e}")
finally:
    # 3. Cerrar la conexión
    conn.close()
    print("✅ Conexión cerrada.")