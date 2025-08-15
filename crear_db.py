import sqlite3

DB_NAME = "padel.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Tabla de usuarios (jugadores)
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nickname TEXT UNIQUE,
    fecha_registro DATE DEFAULT CURRENT_DATE
)
""")

# Tabla de equipos (cada equipo tiene 2 jugadores)
cursor.execute("""
CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT
)
""")

# Relación jugadores-equipos (cada equipo tiene 2 jugadores)
cursor.execute("""
CREATE TABLE IF NOT EXISTS jugadores_equipos (
    equipo_id INTEGER,
    usuario_id INTEGER,
    estado_de_pago BOOLEAN,
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    PRIMARY KEY (equipo_id, usuario_id)
)
""")

# Tabla de partidos (cada partido tiene fecha, lugar y creador)
cursor.execute("""
CREATE TABLE IF NOT EXISTS partidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    cancha TEXT,
    lugar TEXT,
    costo_partido INTEGER,
    partido_con_descuento BOOLEAN,
    creado_por INTEGER,
    equipo_1_id INTEGER NOT NULL,
    equipo_2_id INTEGER NOT NULL,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id),
    FOREIGN KEY (equipo_1_id) REFERENCES equipos(id),
    FOREIGN KEY (equipo_2_id) REFERENCES equipos(id)
)
""")

# Relación equipos-partidos (para marcar el resultado final de cada equipo)
cursor.execute("""
CREATE TABLE IF NOT EXISTS equipos_partidos (
    partido_id INTEGER,
    equipo_id INTEGER,
    resultado TEXT CHECK(resultado IN ('Ganador', 'Perdedor', 'Empate')),
    FOREIGN KEY (partido_id) REFERENCES partidos(id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    PRIMARY KEY (partido_id, equipo_id)
)
""")

# Tabla de sets (resultado detallado por set)
cursor.execute("""
CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partido_id INTEGER NOT NULL,
    numero_set INTEGER NOT NULL,
    equipo_1_puntos INTEGER NOT NULL,
    equipo_2_puntos INTEGER NOT NULL,
    FOREIGN KEY (partido_id) REFERENCES partidos(id)
)
""")

conn.commit()
conn.close()

print("✅ Base de datos actualizada con la columna 'resultado' para manejar empates.")

print("✅ Base de datos actualizada con esquema simplificado.")