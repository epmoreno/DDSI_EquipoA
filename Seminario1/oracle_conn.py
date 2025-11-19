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

def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # Se elimina Detalle_Pedido si existe
        cursor.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = 'DETALLE_PEDIDO'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DROP TABLE Detalle_Pedido PURGE")

        # Se elimina Stock si existe
        cursor.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = 'STOCK'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DROP TABLE Stock PURGE")

        # Se elimina Pedido si existe
        cursor.execute("SELECT COUNT(*) FROM USER_TABLES WHERE TABLE_NAME = 'PEDIDO'")
        if cursor.fetchone()[0] > 0:
            cursor.execute("DROP TABLE Pedido PURGE")

        # Crea la tabla Stock
        cursor.execute("CREATE TABLE Stock (Cproducto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, Cantidad INTEGER)")

        # Crea la tabla Pedido
        cursor.execute("CREATE TABLE Pedido (Cpedido INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, Ccliente INTEGER, Fecha_Pedido DATE)")

        # Crea la tabla Detalle_Pedido
        cursor.execute("""CREATE TABLE Detalle_Pedido (
            Cpedido INTEGER,
            Cproducto INTEGER,
            Cantidad INTEGER,
            PRIMARY KEY (Cpedido, Cproducto),
            FOREIGN KEY (Cpedido) REFERENCES Pedido(Cpedido),
            FOREIGN KEY (Cproducto) REFERENCES Stock(Cproducto)
        )""")
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
    except Exception as e:
        print(f"Error al insertar datos en la tabla Stock: {e}")

def create_Pedido(ccliente, fecha_pedido):
    try:
        while True:
            entrada = input("Ingrese el codigo del cliente: ").strip()
            if not entrada:
                print("Error al introducir el codigo del cliente, no puede estar vacío.")
                continue
            try:
                ccliente = int(entrada)
                if ccliente <= 0:
                    print("Error al introducir el codigo del cliente: Debe ser un entero positivo.")
                    continue
                break
            except Exception as e:
                print(f"Error al introducir el codigo del cliente: No es un entero válido.")
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
    opciones_input_menu = None
    opciones_input = None
    try:
        cursor = create_tables(conn)
        create_tublas_stock(conn, cursor)
        while flag_in_menu == False:
            # Pedir opción del menú principal hasta que sea un entero válido (1-4)
            while True:
                entrada_menu = input("\nINGRESE UNA OPCION: \n  1 - Borrar tablas y crear nuevas tablas \n  2 - Dar de alta nuevo pedido \n  3 - Mostrar contenido de las tablas de la BD \n  4 - Salir del programa y cerrar conexión a BD \n\nRespuesta: ").strip()
                try:
                    opciones_input_menu = int(entrada_menu)
                    if opciones_input_menu in [1, 2, 3, 4]:
                        break
                    else:
                        print("Opción no válida. Intente de nuevo.")
                except ValueError:
                    print("Opción no válida. Intente de nuevo.")
            switcher = {
                1: "Borrar tablas y crear nuevas tablas",
                2: "Dar de alta nuevo pedido",
                3: "Mostrar contenido de las tablas de la BD",
                4: "Salir del programa y cerrar conexión a BD"
            }
            if opciones_input_menu in switcher:
                if opciones_input_menu == 1:
                    ## Informar sobre la creación de las tablas
                    print("Borrando y creando las tablas de nuevo ...")
                    cursor = create_tables(conn)

                    ## Insertar 10 tuplas en la tabla Stock
                    create_tublas_stock(conn, cursor)

                    
                if opciones_input_menu == 2:         
                    # Crear Pedido
                    cursor.execute("SAVEPOINT antes_pedido")
                    id_pedido = create_Pedido(ccliente, fecha_pedido)
                    print(f"ID del nuevo pedido creado: {id_pedido}")
                    flag_in_opcion = False
                            
                    # SAVEPOINT antes de insertar en Detalle_Pedido y OPCIONES de ejecucion
                    cursor.execute("SAVEPOINT antes_detalles_pedidos")
                    if conn and cursor:
                        try:
                            while flag_in_opcion == False:
                                # Pedir opción del submenú hasta que sea un entero válido (1-4)
                                while True:
                                    entrada_sub = input("\nINGRESE UNA OPCION: \n  1 - Añadir detalle de producto \n  2 - Eliminar detalles de producto \n  3 - Cancelar Pedido \n  4 - Finalizar Pedido \n\nRespuesta: ").strip()
                                    try:
                                        opciones_input = int(entrada_sub)
                                        if opciones_input in [1, 2, 3, 4]:
                                            break
                                        else:
                                            print("Opción no válida. Intente de nuevo.")
                                    except ValueError:
                                        print("Opción no válida. Intente de nuevo.")
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
                                            while True:
                                                articulo = input("Ingrese el código del producto a añadir: ").strip()
                                                if not articulo:
                                                    print("El código del producto no puede estar vacío. Intente de nuevo.")
                                                    continue
                                                try:
                                                    articulo = int(articulo)
                                                    if articulo <= 0:
                                                        print("Error: El código del producto debe ser un entero positivo. Intente de nuevo.")
                                                        continue
                                                    break
                                                except ValueError:
                                                    print("Error: El código del producto debe ser un entero válido. Intente de nuevo.")
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
                                            while True:
                                                cantidad_solicitada = input("Ingrese la cantidad a añadir: ").strip()
                                                if not cantidad_solicitada:
                                                    print("La cantidad no puede estar vacía. Intente de nuevo.")
                                                    continue
                                                try:
                                                    cantidad_solicitada = int(cantidad_solicitada)
                                                    if cantidad_solicitada <= 0:
                                                        print("Error: La cantidad debe ser un entero positivo. Intente de nuevo.")
                                                        continue
                                                    break
                                                except ValueError:
                                                    print("Error: La cantidad debe ser un entero válido. Intente de nuevo.")

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
                                            #Eliminar Detalles de pedido en Detalle_Pedido a traves de rollback
                                            cursor.execute("ROLLBACK TO antes_detalles_pedidos")
                                            print("Detalles de pedido eliminados exitosamente")
                                        except Exception as e:
                                            print(f"Error al eliminar detalle de pedido: {e}")
                                    # Opciones 3 y 4 que salen del bucle y regresan al menú principal
                                    if opciones_input == 3:
                                        #Cancelar el pedido usando rollback
                                        cursor.execute("ROLLBACK TO antes_pedido")
                                        print("Pedido cancelado mediante ROLLBACK al savepoint.")
                                        flag_in_opcion = True  
                                    if opciones_input == 4:
                                        conn.commit()
                                        print("Pedido finalizado y cambios guardados.")
                                        flag_in_opcion = True
                                        opciones_input = None
                        except Exception as e:
                            print(f"Error al crear el savepoint: {e}")
                if opciones_input_menu == 3:
                    try:
                        print("\nMostrando el contenido de las tablas de la BD...\n")
                        check_tables()
                    except Exception as e:
                            print(f"Error al mostrar las tablas: {e}")
                if opciones_input_menu == 4:
                    try:
                        conn.commit()
                        print("\n[Cambios guardados.]")
                        print("\nFinalizando conexión . . . .")
                        # Cerrar el cursor y Conexion:
                        if disconnect_cursor(cursor) and disconnect_from_db(conn):
                            print("Conexion cerrada exitosamente")
                        break
                    except Exception as e:
                        print(f"Error al guardar los cambios y finalizar el programa: {e}")
    except Exception as e:
        print(f"Error en el menu principal: {e}")