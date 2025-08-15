import sqlite3

def init_db():
    """
    Conecta a la base de datos y crea todas las tablas si no existen.
    """
    conn = sqlite3.connect("padel.db")
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            nickname TEXT UNIQUE NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de equipos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY,
            nombre TEXT UNIQUE NOT NULL
        )
    """)
    
    # Tabla de jugadores_equipos (relación muchos a muchos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jugadores_equipos (
            equipo_id INTEGER,
            usuario_id INTEGER,
            FOREIGN KEY (equipo_id) REFERENCES equipos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE (equipo_id, usuario_id)
        )
    """)
    
    # Tabla de partidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY,
            fecha DATE,
            lugar TEXT,
            equipo_1_id INTEGER,
            equipo_2_id INTEGER,
            FOREIGN KEY (equipo_1_id) REFERENCES equipos(id),
            FOREIGN KEY (equipo_2_id) REFERENCES equipos(id)
        )
    """)
    
    # Tabla de sets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY,
            partido_id INTEGER,
            numero_set INTEGER,
            equipo_1_puntos INTEGER,
            equipo_2_puntos INTEGER,
            FOREIGN KEY (partido_id) REFERENCES partidos(id)
        )
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
        )
    """)
    
    conn.commit()
    conn.close()