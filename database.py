import psycopg2
import os

def init_db():
    """
    Conecta a la base de datos de PostgreSQL y crea todas las tablas si no existen.
    """
    conn = None
    try:
        # Obtiene la cadena de conexión de la variable de entorno
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                nickname TEXT UNIQUE NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla de equipos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipos (
                id SERIAL PRIMARY KEY,
                nombre TEXT UNIQUE NOT NULL
            );
        """)
        
        # Tabla de jugadores_equipos (relación muchos a muchos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jugadores_equipos (
                equipo_id INTEGER,
                usuario_id INTEGER,
                FOREIGN KEY (equipo_id) REFERENCES equipos(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                UNIQUE (equipo_id, usuario_id)
            );
        """)
        
        # Tabla de partidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidos (
                id SERIAL PRIMARY KEY,
                fecha DATE,
                lugar TEXT,
                equipo_1_id INTEGER,
                equipo_2_id INTEGER,
                FOREIGN KEY (equipo_1_id) REFERENCES equipos(id),
                FOREIGN KEY (equipo_2_id) REFERENCES equipos(id)
            );
        """)
        
        # Tabla de sets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sets (
                id SERIAL PRIMARY KEY,
                partido_id INTEGER,
                numero_set INTEGER,
                equipo_1_puntos INTEGER,
                equipo_2_puntos INTEGER,
                FOREIGN KEY (partido_id) REFERENCES partidos(id)
            );
        """)
        
        # Tabla de equipos_partidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipos_partidos (
                partido_id INTEGER,
                equipo_id INTEGER,
                resultado TEXT,
                FOREIGN KEY (partido_id) REFERENCES partidos(id),
                FOREIGN KEY (equipo_id) REFERENCES equipos(id),
                UNIQUE (partido_id, equipo_id)
            );
        """)
        
        # ¡Este es el paso que faltaba! Confirma los cambios en la base de datos
        conn.commit()
        
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    finally:
        if conn:
            conn.close()