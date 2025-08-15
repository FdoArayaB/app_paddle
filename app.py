import streamlit as st
import pandas as pd
import psycopg2
import os
from database import init_db

# --- Lógica de la Conexión a la Base de Datos con Caching ---

# Esta función solo se ejecutará una vez
# Streamlit la guarda en caché y reutiliza la conexión en cada rerun
@st.cache_resource
def get_db_connection():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            # En la nube, esta variable se carga desde los "Secrets"
            st.error("Error: La variable de entorno DATABASE_URL no está configurada.")
            st.stop()
        
        # Conexión a la base de datos de PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        st.stop()

# --- Lógica Principal de la Aplicación ---

# Inicializa las tablas de la base de datos si no existen.
# Solo ejecuta esto una vez desde tu terminal:
# `export DATABASE_URL="..." && python -c "from database import init_db; init_db()"`
# Una vez que las tablas están creadas, no es necesario volver a ejecutar esta función.
# init_db()

# Obtén la conexión a la base de datos
conn = get_db_connection()
cursor = conn.cursor()


st.title("🎾 Registro de Partidos de Pádel")

# Pestañas para organizar la interfaz
tab1, tab2, tab3 = st.tabs(["Registro de Jugadores", "Registro de Equipos", "Registro de Partidos"])

# -----------------
# Pestaña 1: Registro de Jugadores
# -----------------
with tab1:
    st.header("👥 Jugadores")
    with st.form("form_jugador"):
        nombre = st.text_input("Nombre del jugador")
        nickname = st.text_input("Apodo")
        submit_jugador = st.form_submit_button("Registrar Jugador")

        if submit_jugador:
            try:
                # Se usa %s para PostgreSQL
                cursor.execute("INSERT INTO usuarios (nombre, nickname) VALUES (%s, %s)", (nombre, nickname))
                conn.commit()
                st.success(f"✅ Jugador '{nombre}' registrado correctamente.")
            except psycopg2.errors.UniqueViolation:
                # Se usa psycopg2.errors.UniqueViolation para PostgreSQL
                st.error("❌ Ese apodo ya está registrado.")
                conn.rollback() # Es buena práctica hacer rollback en caso de error
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                conn.rollback()

    st.subheader("📋 Jugadores Registrados")
    df_jugadores = pd.read_sql_query("SELECT nombre, nickname, fecha_registro FROM usuarios", conn)
    st.dataframe(df_jugadores)

# -----------------
# Pestaña 2: Registro de Equipos
# -----------------
with tab2:
    st.header("🤝 Equipos")
    st.write("Crea un equipo y asigna dos jugadores.")

    jugadores = pd.read_sql_query("SELECT id, nombre FROM usuarios", conn)
    jugadores_dict = dict(zip(jugadores['id'], jugadores['nombre']))

    with st.form("form_equipo"):
        # Verificación para evitar errores si no hay suficientes jugadores
        if jugadores.empty or len(jugadores) < 2:
            st.warning("⚠️ Debes registrar al menos 2 jugadores para poder crear un equipo.")
        else:
            nombre_equipo = st.text_input("Nombre del equipo")
            jugador1_id = st.selectbox("Jugador 1", options=jugadores_dict.keys(), format_func=lambda x: jugadores_dict[x])
            jugador2_id = st.selectbox("Jugador 2", options=jugadores_dict.keys(), format_func=lambda x: jugadores_dict[x])
            submit_equipo = st.form_submit_button("Crear Equipo")

            if submit_equipo:
                if jugador1_id == jugador2_id:
                    st.error("❌ Un equipo debe tener dos jugadores diferentes.")
                else:
                    try:
                        cursor.execute("INSERT INTO equipos (nombre) VALUES (%s) RETURNING id", (nombre_equipo,))
                        equipo_id = cursor.fetchone()[0]
                        
                        cursor.execute("INSERT INTO jugadores_equipos (equipo_id, usuario_id) VALUES (%s, %s)", (equipo_id, jugador1_id))
                        cursor.execute("INSERT INTO jugadores_equipos (equipo_id, usuario_id) VALUES (%s, %s)", (equipo_id, jugador2_id))
                        conn.commit()
                        st.success(f"✅ Equipo '{nombre_equipo}' creado y jugadores asignados.")
                    except Exception as e:
                        st.error(f"⚠️ Error: {e}")
                        conn.rollback()

    st.subheader("📋 Equipos Creados")
    df_equipos = pd.read_sql_query("""
        SELECT e.nombre,
               j1.nombre AS jugador1,
               j2.nombre AS jugador2
        FROM equipos e
        JOIN jugadores_equipos je1 ON e.id = je1.equipo_id
        JOIN jugadores_equipos je2 ON e.id = je2.equipo_id AND je1.usuario_id < je2.usuario_id
        JOIN usuarios j1 ON je1.usuario_id = j1.id
        JOIN usuarios j2 ON je2.usuario_id = j2.id
    """, conn)
    st.dataframe(df_equipos)

# -----------------
# Pestaña 3: Registro de Partidos y Resultados
# -----------------
with tab3:
    st.header("🗓️ Partidos")
    
    equipos = pd.read_sql_query("SELECT id, nombre FROM equipos", conn)
    
    # Verificación para evitar errores si no hay suficientes equipos
    if equipos.empty or len(equipos) < 2:
        st.warning("⚠️ Debes crear al menos dos equipos en la pestaña 'Registro de Equipos' para registrar un partido.")
    else:
        equipos_dict = dict(zip(equipos['id'], equipos['nombre']))
        
        with st.form("form_partido"):
            st.subheader("Datos del Partido")
            fecha = st.date_input("Fecha del partido")
            lugar = st.text_input("Lugar del partido")
            equipo_1_id = st.selectbox("Equipo 1", options=equipos_dict.keys(), format_func=lambda x: equipos_dict[x])
            equipo_2_id = st.selectbox("Equipo 2", options=equipos_dict.keys(), format_func=lambda x: equipos_dict[x])
            
            st.subheader("Resultados por Set")
            sets = []
            for i in range(1, 4):
                col1, col2 = st.columns(2)
                with col1:
                    # Añadimos la clave única para cada widget
                    puntos_e1 = st.number_input(f"Puntos {equipos_dict[equipo_1_id]} - Set {i}", min_value=0, step=1, key=f"puntos_e1_set_{i}")
                with col2:
                    # Añadimos la clave única para cada widget
                    puntos_e2 = st.number_input(f"Puntos {equipos_dict[equipo_2_id]} - Set {i}", min_value=0, step=1, key=f"puntos_e2_set_{i}")
                sets.append((puntos_e1, puntos_e2))
            
            submit_partido = st.form_submit_button("Registrar Partido")
            
            if submit_partido:
                if equipo_1_id == equipo_2_id:
                    st.error("❌ Los equipos no pueden ser iguales.")
                else:
                    try:
                        cursor.execute("INSERT INTO partidos (fecha, lugar, equipo_1_id, equipo_2_id) VALUES (%s, %s, %s, %s) RETURNING id",
                                   (fecha, lugar, equipo_1_id, equipo_2_id))
                        partido_id = cursor.fetchone()[0]
                        
                        for i, (puntos_e1, puntos_e2) in enumerate(sets):
                            cursor.execute("INSERT INTO sets (partido_id, numero_set, equipo_1_puntos, equipo_2_puntos) VALUES (%s, %s, %s, %s)",
                                       (partido_id, i + 1, puntos_e1, puntos_e2))

                        ganador_sets_e1 = sum(1 for p1, p2 in sets if p1 > p2)
                        ganador_sets_e2 = sum(1 for p1, p2 in sets if p2 > p1)

                        resultado_e1 = "Empate"
                        resultado_e2 = "Empate"
                        if ganador_sets_e1 > ganador_sets_e2:
                            resultado_e1 = "Ganador"
                            resultado_e2 = "Perdedor"
                        elif ganador_sets_e2 > ganador_sets_e1:
                            resultado_e1 = "Perdedor"
                            resultado_e2 = "Ganador"

                        cursor.execute("INSERT INTO equipos_partidos (partido_id, equipo_id, resultado) VALUES (%s, %s, %s)",
                                   (partido_id, equipo_1_id, resultado_e1))
                        cursor.execute("INSERT INTO equipos_partidos (partido_id, equipo_id, resultado) VALUES (%s, %s, %s)",
                                   (partido_id, equipo_2_id, resultado_e2))
                        
                        conn.commit()
                        st.success("✅ Partido y resultados registrados correctamente.")
                    except Exception as e:
                        st.error(f"⚠️ Error: {e}")
                        conn.rollback()

    st.subheader("📋 Partidos Registrados")
    df_partidos = pd.read_sql_query("""
        SELECT p.id, p.fecha, p.lugar, e1.nombre as equipo1, e2.nombre as equipo2, ep1.resultado as resultado_e1, ep2.resultado as resultado_e2
        FROM partidos p
        JOIN equipos e1 ON p.equipo_1_id = e1.id
        JOIN equipos e2 ON p.equipo_2_id = e2.id
        LEFT JOIN equipos_partidos ep1 ON p.id = ep1.partido_id AND p.equipo_1_id = ep1.equipo_id
        LEFT JOIN equipos_partidos ep2 ON p.id = ep2.partido_id AND p.equipo_2_id = ep2.equipo_id
    """, conn)
    st.dataframe(df_partidos)

conn.close()