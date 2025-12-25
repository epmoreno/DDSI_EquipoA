import oracledb
from os import getenv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class OracleDBConn:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def conectar(self):
        try:
            self.conn = oracledb.connect(
                user=getenv("DB_USER"),
                password=getenv("DB_PASSWORD"),
                dsn=getenv("DB_DSN")
            )
            self.cursor = self.conn.cursor()
            print("\nConexión establecida exitosamente")
        except Exception as e:
            print(f"Error en la conexión: {e}")

    def desconectar(self):
        self.cursor.close()
        self.conn.close()
    
    def reset_tablas(self):
        try:
            # Eliminacion
            tablas = ['DETALLE_PEDIDO', 'STOCK', 'PEDIDO']
            for tabla in tablas:
                try:
                    self.cursor.execute(f"DROP TABLE {tabla} PURGE")
                except oracledb.DatabaseError:
                    pass
            
            # Creacion
            self.cursor.execute("""CREATE TABLE Stock (
                Cproducto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                Cantidad INTEGER
            )""")
            self.cursor.execute("""CREATE TABLE Pedido (
                Cpedido INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                Ccliente INTEGER, 
                Fecha_Pedido DATE
            )""")
            self.cursor.execute("""CREATE TABLE Detalle_Pedido (
                Cpedido INTEGER,
                Cproducto INTEGER,
                Cantidad INTEGER,
                PRIMARY KEY (Cpedido, Cproducto),
                FOREIGN KEY (Cpedido) REFERENCES Pedido(Cpedido),
                FOREIGN KEY (Cproducto) REFERENCES Stock(Cproducto)
            )""")

            # Elementos Basicos
            for i in range(10):
                cantidad = (i+1)*10
                self.cursor.execute("""INSERT INTO Stock (Cantidad)
                                    VALUES (:1)""", [cantidad])
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al resetear las tablas: {e}")
            self.conn.rollback()
            raise e
    
    def crear_pedido_cabecera(self, ccliente):
        fecha_pedido = datetime.now()
        id_var = self.cursor.var(int)
        sql = """INSERT INTO Pedido (Ccliente, Fecha_Pedido) 
                VALUES (:ccliente, :fecha_pedido) 
                RETURNING Cpedido INTO :id_var"""
        self.cursor.execute(sql, ccliente=ccliente, fecha_pedido=fecha_pedido, id_var=id_var)
        return id_var.getvalue()[0]
        
    def obtener_stock(self):
        try:
            self.cursor.execute("SELECT Cproducto, Cantidad FROM Stock ORDER BY Cproducto")
            return self.row_to_dict(self.cursor)
        except Exception as e:
            print(f"Error al obtener stock: {e}")
            return []
        
    def agregar_detalle_pedido(self, cpedido, cproducto, cantidad):
        # Verifica el stock
        self.cursor.execute("""SELECT Cantidad 
                            FROM Stock 
                            WHERE Cproducto = :1""", [cproducto])
        res = self.cursor.fetchone()
        if not res:
            raise ValueError("No existe el producto.")
        stock_disponible = res[0]

        if stock_disponible < cantidad:
            raise ValueError("No hay suficiente stock.")

        # Insertar o Actualizar Detalles
        self.cursor.execute("""SELECT COUNT(*) FROM Detalle_Pedido
                            WHERE Cpedido = :1 AND Cproducto = :2""", [cpedido, cproducto])
        existe = self.cursor.fetchone()[0] > 0
        if existe:
            self.cursor.execute("""UPDATE Detalle_Pedido 
                                SET Cantidad = Cantidad + :1 
                                WHERE Cpedido = :2 AND Cproducto = :3""", 
                                [cantidad, cpedido, cproducto])
        else:
            self.cursor.execute("""INSERT INTO Detalle_Pedido (Cpedido, Cproducto, Cantidad)
                                VALUES (:1, :2, :3)""", 
                                [cpedido, cproducto, cantidad])
        # Actualizar Stock
        self.cursor.execute("""UPDATE Stock 
                            SET Cantidad = Cantidad - :1 
                            WHERE Cproducto = :2""", 
                            [cantidad, cproducto])
        
    def obtener_detalles_pedido(self, cpedido):
        try:
            sql = """SELECT d.Cproducto, d.Cantidad as CANTIDAD_SOLICITADA, s.Cantidad as CANTIDAD_DISPONIBLE
                    FROM Detalle_Pedido d
                    JOIN Stock s ON d.Cproducto = s.Cproducto
                    WHERE d.Cpedido = :1"""
            self.cursor.execute(sql, [cpedido])
            return self.row_to_dict(self.cursor)
        except Exception as e:
            print(f"Error al obtener detalles del pedido: {e}")
            return []

    def obtener_todo_stock(self):
        try:
            self.cursor.execute("SELECT * FROM Stock ORDER BY Cproducto")
            return self.row_to_dict(self.cursor)
        except Exception as e:
            print(f"Error al obtener todo el stock: {e}")
            return []
        
    def obtener_todo_pedidos(self):
        try:
            sql = """SELECT Cpedido, Ccliente, 
                    TO_CHAR(Fecha_Pedido, 'DD/MM/YYYY HH24:MI:SS') as FECHA_PEDIDO 
                FROM Pedido 
                ORDER BY Cpedido DESC"""
            self.cursor.execute(sql)
            return self.row_to_dict(self.cursor)
        except Exception as e:
            print(f"Error al obtener todos los pedidos: {e}")
            return []
    
    def confirmar_transaccion(self):
        self.conn.commit()

    def cancelar_transaccion(self):
        self.conn.rollback()
    
    def row_to_dict(self, cursor):
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]