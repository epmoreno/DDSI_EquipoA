from nicegui import ui, app
from database import OracleDBConn


# --- Estado de la aplicacion ---
db = OracleDBConn()
estado = {
    'pedido_actual_id' : None,
    'en_proceso' : False
}
try:
    db.conectar()
    ui.notify('Conectado a la base de datos Oracle', type='positive')
except Exception as e:
    ui.notify(f'Error al conectar a la base de datos: {e}', type='negative')

# --- Lógica de la aplicacion ---
def reiniciar_bd():
    try:    
        db.reset_tablas()
        refrescar_tablas_visuales.refresh()
        seccion_detalles.refresh()
        ui.notify('Tablas reiniciadas exitosamente', type='positive')
    except Exception as e:
        ui.notify(f'Error al reiniciar las tablas: {e}', type='negative')

def iniciar_pedido():
    cliente = input_cliente.value
    if not cliente or not cliente.isdigit() or int(cliente) <= 0:
        ui.notify('ID de cliente inválido', type='warning')
        return
    try:
        # Crear nueva cabecera de pedido
        pedido_id = db.crear_pedido_cabecera(int(cliente))
        estado['pedido_actual_id'] = pedido_id
        estado['en_proceso'] = True
        # Actualizar UI
        ui.notify(f'Pedido {pedido_id} iniciado. Añade Productos', type='info')
        seccion_detalles.refresh()
        input_cliente.value = ''
    except Exception as e:
        ui.notify(f'Error al crear pedido: {e}', type='negative')

def agregar_linea():
    prod_id = selector_producto.value
    cant = input_cantidad.value

    if not prod_id or not cant or not cant.isdigit() or int(cant) <= 0:
        ui.notify('Selecciona producto y cantidad válidos', type='warning')
        return
    try:
        db.agregar_detalle_pedido(estado['pedido_actual_id'], int(prod_id), int(cant))
        ui.notify('Producto agregado exitosamente', type='positive')
        tabla_carrito.refresh()
        seccion_detalles.refresh()
    except ValueError as ve:
        ui.notify(str(ve), type='warning')
    except Exception as e:
        ui.notify(f'Error BD: {e}', type='negative')

def finalizar_pedido():
    try:
        db.confirmar_transaccion()
        ui.notify('Pedido Finalizado y Guardado', type='positive')
        resetear_estado_pedido()
    except Exception as e:
        ui.notify(f'Error al commit: {e}', type='negative')

def cancelar_pedido():
    try:
        db.cancelar_transaccion()
        ui.notify('Pedido Cancelado (Rollback)', type='warning')
        resetear_estado_pedido()
    except Exception as e:
        ui.notify(f'Error al rollback: {e}', type='negative')

def resetear_estado_pedido():
    estado['pedido_actual_id'] = None
    estado['en_proceso'] = False
    seccion_detalles.refresh() # Oculta controles de añadir productos
    refrescar_tablas_visuales.refresh() # Muestra los datos actualizados en la pestaña "Ver Datos"

def obtener_opciones_productos():
    try:
        lista = db.obtener_stock()
        return {
            p['CPRODUCTO']: f"Producto {p['CPRODUCTO']} (Stock: {p['CANTIDAD']})" 
            for p in lista
        }
    except Exception as e:
        print(f"Error cargando productos: {e}") # Añade print para ver errores si pasan
        return {}

# --- Diseño de la Interfaz (UI) ---
ui.dark_mode().enable()

with ui.tabs().classes('w-full') as tabs:
    tab_nuevo = ui.tab('Nuevo Pedido', icon ='add_shopping_cart')
    tab_datos = ui.tab('Ver Datos', icon ='storage')
    tab_admin = ui.tab('Administración', icon ='settings')

def al_cambiar_pestana(e):
    # e.value contiene el objeto ui.tab seleccionado
    if e.value == tab_datos:
        refrescar_tablas_visuales.refresh()

with ui.tab_panels(tabs, value=tab_nuevo, on_change=al_cambiar_pestana).classes('w-full p-4'):
    # Panel 1: Nuevo Pedido
    with ui.tab_panel(tab_nuevo):
        ui.label('Crear Nuevo Pedido').classes('text-2xl font-bold self-center q-mb-md')
        # Cabecera Pedido
        with ui.row().classes('items-end gap-4'):
            input_cliente = ui.input('ID Cliente', placeholder='Ej: 1').classes('w-32')
            btn_crear = ui.button('Iniciar Pedido', on_click=iniciar_pedido)
            # Binding: Si ya hay un pedido en proceso, deshabilitamos el botón de crear
            btn_crear.bind_enabled_from(estado, 'en_proceso', backward=lambda x: not x)
        
        ui.separator().classes('q-my-lg')
        # Detalles Pedido (Solo si hay un pedido en proceso)
        @ui.refreshable
        def seccion_detalles():
            if not estado['en_proceso']:
                ui.label('Inicia el pedido arriba para añadir productos.').classes('text-gray-500 italic')
                return
            with ui.card().classes('w-full bg-gray-900'):
                ui.label(f'Editando Pedido {estado["pedido_actual_id"]}').classes('text-lg font-bold text-green-400')

                with ui.row().classes('items-center w-full'):
                    # Selector Producto
                    global selector_producto
                    opciones_actuales = obtener_opciones_productos()
                    
                    selector_producto = ui.select(
                        options=opciones_actuales, 
                        label='Seleccionar Producto'
                    ).classes('w-64')
                    global input_cantidad
                    input_cantidad = ui.input(label='Cantidad').classes('w-32')
                    ui.button('Añadir', icon = 'add',on_click = agregar_linea).classes('q-ml-sm')
                
                # Tabla Carrito
                tabla_carrito()

                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('Cancelar Todo', color='red', on_click=cancelar_pedido).props('flat')
                    ui.button('Finalizar Pedido', color='green', on_click=finalizar_pedido)

        @ui.refreshable
        def tabla_carrito():
            if not estado['pedido_actual_id']: return
            detalles = db.obtener_detalles_pedido(estado['pedido_actual_id'])
            if detalles:
                ui.table(columns=[
                    {'name': 'Cproducto', 'label': 'Producto ID', 'field': 'CPRODUCTO'},
                    {'name': 'Cantidad_Solicitada', 'label': 'Cantidad Solicitada', 'field': 'CANTIDAD_SOLICITADA'},
                    {'name': 'Cantidad_Disponible', 'label': 'Cantidad Disponible', 'field': 'CANTIDAD_DISPONIBLE'},
                ], rows=detalles).classes('w-full')
        seccion_detalles()
        
    with ui.tab_panel(tab_datos):
        ui.label('Datos de la Base de Datos').classes('text-2xl font-bold self-center q-mb-md')
        @ui.refreshable
        def refrescar_tablas_visuales():
            with ui.row().classes('w-full gap-4'):
                # Tabla Stock
                with ui.column().classes('flex-1'):
                    ui.label('Stock Actual').classes('font-bold text-xl')
                    try:
                        rows = db.obtener_todo_stock()
                        ui.table(columns=[
                            {'name': 'Cproductos', 'label': 'ID', 'field': 'CPRODUCTO'},
                            {'name': 'Cantidad', 'label': 'Cant', 'field': 'CANTIDAD'},
                        ], rows=rows).classes('h-64')
                    except : ui.label('Sin datos')
                # Tabla Pedidos
                with ui.column().classes('flex-1'):
                    ui.label('Historial De Pedidos').classes('font-bold text-xl')
                    try:
                        rows = db.obtener_todo_pedidos()
                        ui.table(columns=[
                            {'name': 'Cpedido', 'label': 'ID Pedido', 'field': 'CPEDIDO'},
                            {'name': 'Ccliente', 'label': 'ID Cliente', 'field': 'CCLIENTE'},
                            {'name': 'Fecha_Pedido', 'label': 'Fecha Pedido', 'field': 'FECHA_PEDIDO'},
                        ], rows=rows).classes('h-64')
                    except : ui.label('Sin datos')
        refrescar_tablas_visuales()
    with ui.tab_panel(tab_admin):
        ui.label('Zona de Peligro').classes('text-red font-bold')
        ui.button('Borrar y Reiniciar Base de Datos', color='red', on_click=reiniciar_bd)

app.on_shutdown(db.desconectar)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Mi App de Tareas', native = True)