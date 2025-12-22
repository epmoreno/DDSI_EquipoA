from nicegui import ui

from datetime import datetime
from os import getenv
from dotenv import load_dotenv
import oracledb
import sys
load_dotenv()

# BACKEND
conn  = None
cursor = None
def connect_to_db(conn):
    try:
        # Configuración de la conexión
        username = getenv("DB_USER")
        password = getenv("DB_PASSWORD")
        dsn = getenv("DB_DSN")
        
        if not all([username, password, dsn]):
            raise ValueError("Faltan variables de entorno necesarias (DB_USER, DB_PASSWORD, DB_DSN)")
        
        # Establecer la conexión
        conn = oracledb.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        print("\nConexión establecida exitosamente")
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        sys.exit(1)

def disconnect_from_db(conn):
    try:
        if conn:
            conn.close()
            return True
    except Exception as e:
        print(f"Error al desconectar de la base de datos: {e}")
        return False

def disconnect_cursor(cursor):
    try:
        if cursor:
            cursor.close()
            return True
    except Exception as e:
        print(f"Error al cerrar el cursor: {e}")
        return False

conn = connect_to_db(conn)
try:
    cursor = conn.cursor()
    print("Cursor creado exitosamente")
except Exception as e:
    print(f"Error al crear el cursor: {e}")
    disconnect_from_db(conn)
    sys.exit(1)

disconnect_from_db(conn)
disconnect_cursor(cursor)
# FRONTEND

ui.label('AMAXON')
with ui.card():
    ui.button('button A')
    ui.label('label A')

ui.run()
