from datetime import date
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
import oracledb
import sys
load_dotenv()

conn = None
cursor = None
flag_in_menu = False
flag_in_opcion = False
ccliente = None
fecha_pedido = None

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
            print("Conexión cerrada exitosamente")
    except Exception as e:
        print(f"Error al desconectar de la base de datos: {e}")

def disconnect_cursor(cursor):
    try:
        if cursor:
            cursor.close()
            print("Cursor cerrado exitosamente")
    except Exception as e:
        print(f"Error al cerrar el cursor: {e}")

def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # Se elimina Detalle_Pedido si existe
        cursor.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = 'DETALLE_PEDIDO'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DROP TABLE Detalle_Pedido PURGE")
            print("Tabla 'Detalle_Pedido' eliminada")

        # Se elimina Stock si existe
        cursor.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = 'STOCK'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DROP TABLE Stock PURGE")
            print("Tabla 'Stock' eliminada")

        # Se elimina Pedido si existe
        cursor.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = 'PEDIDO'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DROP TABLE Pedido PURGE")
            print("Tabla 'Pedido' eliminada")

        # Crea la tabla Stock
        cursor.execute("CREATE TABLE Stock (Cproducto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, Cantidad INTEGER)")
        print("Tabla 'Stock' creada exitosamente")

        # Crea la tabla Pedido
        cursor.execute("CREATE TABLE Pedido (Cpedido INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, Ccliente INTEGER, Fecha_Pedido DATE)")
        print("Tabla 'Pedido' creada exitosamente")

        # Crea la tabla Detalle_Pedido
        cursor.execute("""CREATE TABLE Detalle_Pedido (
            Cpedido INTEGER,
            Cproducto INTEGER,
            Cantidad INTEGER,
            PRIMARY KEY (Cpedido, Cproducto),
            FOREIGN KEY (Cpedido) REFERENCES Pedido(Cpedido),
            FOREIGN KEY (Cproducto) REFERENCES Stock(Cproducto)
        )""")
        print("Tabla 'Detalle_Pedido' creada exitosamente")
        # Devolver el cursor para uso posterior
        return cursor
    except oracledb.DatabaseError as e:
        print(f"Error en la operación de la base de datos: {e}")
        return None

def create_tublas_stock(conn, cursor):
    try:
        for i in range(10):
            cantidad = (i+1)*10
            cursor.execute("INSERT INTO Stock (Cantidad) VALUES (:1)", [cantidad])
        conn.commit()
        print("10 tuplas insertadas en la tabla Stock exitosamente")
    except Exception as e:
        print(f"Error al insertar datos en la tabla Stock: {e}")

def create_Pedido(ccliente, fecha_pedido):
    try:
        ccliente = int(input("Ingrese el código del cliente: "))
        fecha_pedido = datetime.now()
        id_var = cursor.var(int)
        sql = "INSERT INTO Pedido (Ccliente, Fecha_Pedido) VALUES (:ccliente, :fecha_pedido) RETURNING Cpedido INTO :id_var"
        cursor.execute(sql, ccliente=ccliente, fecha_pedido=fecha_pedido, id_var=id_var)
        print("Nuevo pedido creado exitosamente")
        return id_var.getvalue()[0]
    except Exception as e:
        print(f"Error al crear un nuevo pedido: {e}")
        return None

def check_tables():
    print("\n| \tCproducto          |       Cantidad        \t\t|\n")
    if cursor:
        cursor.execute("SELECT * FROM Stock")
        productos = cursor.fetchall()
        for producto in productos:
            print(f"|  \t- Cproducto: {producto[0]}     |       Cantidad disponible: {producto[1]}\t|")
    
        print("")
    else:
        print("No se pudo mostrar las tablas debido a problemas de cursor.")

    print("\n| \tCpedido\t\t|       Ccliente\t|       Fecha_Pedido\t\t\t\t|\n")
    if cursor:
        cursor.execute("SELECT * FROM Pedido")
        pedidos = cursor.fetchall()
        for pedido in pedidos:
            print(f"|  \t- Cpedido: {pedido[0]}\t|       Ccliente: {pedido[1]}\t|       Fecha_Pedido: {pedido[2]}\t|")
        print("")
    else:
        print("No se pudo mostrar las tablas debido a problemas de cursor.")

    print("\n| \tCpedido\t\t|       Cproducto\t|       Cantidad\t|\n")
    if cursor:
        cursor.execute("SELECT * FROM Detalle_Pedido")
        detalles = cursor.fetchall()
        for detalle in detalles:
            print(f"|  \t- Cpedido: {detalle[0]}\t|       Cproducto: {detalle[1]}\t|       Cantidad: {detalle[2]}\t|")
        print("")
    else:
        print("No se pudo mostrar las tablas debido a problemas de cursor.")

    return None

## Conectandose a la base de datos
conn = connect_to_db(conn)

if conn:
    cursor = conn.cursor()
    cursor.execute("SAVEPOINT principal")
    opciones_input = None
    try:
        while flag_in_menu == False:
            opciones_input = int(input("\nINGRESE UNA OPCION: \n  1 - Borrar tablas y crear nuevas tablas \n  2 - Dar de alta nuevo pedido \n  3 - Mostrar contenido de las tablas de la BD \n  4 - Salir del programa y cerrar conexión a BD \n\nRespuesta: "))
            while opciones_input not in [1, 2, 3, 4]:
                print("Opción no válida. Intente de nuevo.")
                opciones_input = int(input("\nINGRESE UNA OPCION: \n  1 - Borrar tablas y crear nuevas tablas \n  2 - Dar de alta nuevo pedido \n  3 - Mostrar contenido de las tablas de la BD \n  4 - Salir del programa y cerrar conexión a BD \n\nRespuesta: "))
            switcher = {
                1: "Borrar tablas y crear nuevas tablas",
                2: "Dar de alta nuevo pedido",
                3: "Mostrar contenido de las tablas de la BD",
                4: "Salir del programa y cerrar conexión a BD"
            }
            if opciones_input in switcher:
                if opciones_input == 1:
                    ## Informar sobre la creación de las tablas
                    cursor = create_tables(conn)

                    ## Insertar 10 tuplas en la tabla Stock
                    create_tublas_stock(conn, cursor)
                    
                if opciones_input == 2:         
                    # Crear Pedido
                    cursor.execute("SAVEPOINT antes_pedido")
                    id_pedido = create_Pedido(ccliente, fecha_pedido)
                    print(f"ID del nuevo pedido creado: {id_pedido}")
                    flag_in_opcion = False
                            
                    # SAVEPOINT antes de insertar en Detalle_Pedido y OPCIONES de ejecucion
                    if conn and cursor:
                        try:
                            while flag_in_opcion == False:
                                opciones_input = int(input("\nINGRESE UNA OPCION: \n  1 - Añadir detalle de producto \n  2 - Eliminar detalles de producto \n  3 - Cancelar Pedido \n  4 - Finalizar Pedido \n\nRespuesta: "))
                                while opciones_input not in [1, 2, 3, 4]:
                                    print("Opción no válida. Intente de nuevo.")
                                    opciones_input = int(input("\nINGRESE UNA OPCION: \n  1 - Añadir detalle de producto \n  2 - Eliminar detalles de producto \n  3 - Cancelar Pedido \n  4 - Finalizar Pedido \n\nRespuesta: "))
                                switcher = {
                                    1: "Añadir detalle de producto",
                                    2: "Eliminar detalles de producto",
                                    3: "Cancelar Pedido",
                                    4: "Finalizar Pedido"
                                }
                                if opciones_input in switcher:
                                    print(f"Ejecutando la opción: {switcher[opciones_input]}")
                                    if opciones_input == 1:
                                        # Visualizar los productos disponibles en Stock
                                        try:
                                            print("\nProductos disponibles en Stock:")
                                            cursor.execute("SELECT Cproducto, Cantidad FROM Stock")
                                            productos = cursor.fetchall()
                                            for producto in productos:
                                                print(f"|  \t- Cproducto: {producto[0]}\t|       Cantidad disponible: {producto[1]}\t|")
                                        
                                            print("")

                                            # Introducir y Verificar si el producto existe
                                            articulo = int(input("Ingrese el código del producto a añadir: "))
                                            cursor.execute("SELECT COUNT(*) FROM Stock WHERE Cproducto = :1", [articulo])
                                            if cursor.fetchone()[0] == 0:
                                                while True:
                                                    print("El producto no existe. Seleccione otro producto.")
                                                    articulo = int(input("Ingrese el código del producto a añadir: "))
                                                    cursor.execute("SELECT COUNT(*) FROM Stock WHERE Cproducto = :1", [articulo])
                                                    if cursor.fetchone()[0] > 0:
                                                        break
                                            else:
                                                print("Producto encontrado en Stock.")
                                            
                                            # Introducir y Verificar si hay suficiente stock
                                            cantidad_solicitada = int(input("Ingrese la cantidad a añadir: "))
                                            cursor.execute("SELECT Cantidad FROM Stock WHERE Cproducto = :1", [articulo])
                                            resultado = cursor.fetchone()
                                            if resultado[0] < cantidad_solicitada:
                                                while resultado[0] < cantidad_solicitada:
                                                    print("No hay suficiente stock para este producto, Seleccione otra cantidad o producto.")
                                                    cantidad_solicitada = int(input("Ingrese la cantidad a añadir: "))
                                            else:
                                                print("Cantidad disponible en stock.")

                                            # Verifica si el producto ya está en Detalle_Pedido (por pedido y producto)
                                            cursor.execute("SELECT COUNT(*) FROM Detalle_Pedido WHERE Cpedido = :1 AND Cproducto = :2", [id_pedido, articulo])
                                            if cursor.fetchone()[0] > 0:
                                                # Actualizar Cantidad en Detalle_Pedido
                                                print(f"Actualizando cantidad del detalle de pedido...{id_pedido}, {articulo}, {cantidad_solicitada}")
                                                cursor.execute("UPDATE Detalle_Pedido SET Cantidad = Cantidad + :1 WHERE Cpedido = :2 AND Cproducto = :3", [cantidad_solicitada, id_pedido, articulo])
                                                print("Cantidad actualizada en Detalle_Pedido.")
                                                # Actualizar Stock
                                                cursor.execute("UPDATE Stock SET Cantidad = Cantidad - :1 WHERE Cproducto = :2", [cantidad_solicitada, articulo])
                                                print("Detalle de pedido añadido exitosamente.")
                                            else:
                                                # Insertar en Detalle_Pedido
                                                print(f"Insertando nuevo detalle de pedido...{id_pedido}, {articulo}, {cantidad_solicitada}")
                                                cursor.execute("INSERT INTO Detalle_Pedido (Cpedido, Cproducto, Cantidad) VALUES (:1, :2, :3)", [id_pedido, articulo, cantidad_solicitada])
                                                # Actualizar Stock
                                                cursor.execute("UPDATE Stock SET Cantidad = Cantidad - :1 WHERE Cproducto = :2", [cantidad_solicitada, articulo])
                                                print("Detalle de pedido añadido exitosamente.")
                                        except Exception as e:
                                            print(f"Error al recuperar productos de Stock: {e}")
                                    if opciones_input == 2:
                                        try:
                                            #Eliminar Detalles de pedido en Detalle_Pedido
                                            cursor.execute("DELETE FROM Detalle_Pedido WHERE Cpedido = :1", [id_pedido])
                                            print("Detalles de pedido eliminados exitosamente")
                                        except Exception as e:
                                            print(f"Error al eliminar detalle de pedido: {e}")
                                    # Opciones 3 y 4 que salen del bucle y regresan al menú principal
                                    if opciones_input == 3:
                                        cursor.execute("ROLLBACK TO antes_pedido")
                                        conn.rollback()
                                        print("Pedido cancelado mediante ROLLBACK al savepoint.")
                                        flag_in_opcion = True  
                                    if opciones_input == 4:
                                        conn.commit()
                                        print("Pedido finalizado y cambios guardados mediante COMMIT.")
                                        flag_in_opcion = True
                                        opciones_input = None
                        except Exception as e:
                            print(f"Error al crear el savepoint: {e}")
                if opciones_input == 3:
                    try:
                        print("\nMostrando el contenido de las tablas de la BD...\n")
                        check_tables()
                    except Exception as e:
                            print(f"Error al mostrar las tablas: {e}")
                if opciones_input == 4:
                    try:
                        conn.commit()
                        print("\nCambios guardados mediante COMMIT. Fin de la conexión.")
                        # Cerrar el cursor y Conexion:
                        disconnect_cursor(cursor)
                        disconnect_from_db(conn)
                        break
                    except Exception as e:
                        print(f"Error al guardar los cambios y finalizar el programa: {e}")
    except Exception as e:
        print(f"Error en el menu principal: {e}")