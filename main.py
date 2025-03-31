import flet as ft

def main(page: ft.Page):
    page.title = "Punto de Venta - Tienda de Abarrotes"
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configuración de seguridad
    ADMIN_PASSWORD = "admin123"
    is_admin = False
    
    productos = [
        {"id": "001", "nombre": "Arroz", "precio": 20.0, "cantidad": 10},
        {"id": "002", "nombre": "Frijoles", "precio": 25.0, "cantidad": 15},
        {"id": "003", "nombre": "Aceite", "precio": 50.0, "cantidad": 8},
    ]
    carrito = {}

    # Diálogo de contraseña
    password_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Acceso de administrador"),
        content=ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_password_dialog()),
            ft.TextButton("Aceptar", on_click=lambda e: verificar_password(password_dialog.content.value))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )


    def verificar_password(password):
        nonlocal is_admin
        if password == ADMIN_PASSWORD:
            is_admin = True
            page.snack_bar = ft.SnackBar(ft.Text("Acceso concedido"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            cerrar_password_dialog()
            # Forzar la actualización de la vista actual
            content.content = inventario_view()  # Esto recargará la vista
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Contraseña incorrecta"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()

    def abrir_password_dialog():
        password_dialog.content.value = ""  
        password_dialog.open = True  
        page.overlay.append(password_dialog)  # Agregar a overlay
        page.update()  






    def cerrar_password_dialog():
        password_dialog.open = False
        page.update()

    # Barra de navegación (siempre habilitada)
    navigation = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_CART, label="Ventas"),
            ft.NavigationRailDestination(icon=ft.Icons.INVENTORY, label="Inventario"),
            ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Reportes"),
        ],
        selected_index=0,
    )  
    # Payment Dialog
    pago_dialog = ft.AlertDialog(
        title=ft.Text("¡Venta exitosa!", text_align=ft.TextAlign.CENTER),
        content=ft.Text("Gracias por su compra", text_align=ft.TextAlign.CENTER),
    )
    
    # Payment Section
    forma_pago = ft.Dropdown(
        label="Forma de pago",
        options=[
            ft.dropdown.Option("Efectivo"),
            ft.dropdown.Option("Tarjeta")
        ],
        width=300,
        on_change=lambda e: actualizar_forma_pago()
    )
    
    cantidad_recibida = ft.TextField(
        label="Cantidad recibida", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        width=300,
        on_change=lambda e: actualizar_cambio()
    )
    
    cambio_text = ft.Text("Cambio: $0.00", size=18)
    total_text = ft.Text("Total: $0.00", size=18)
    
    pago_section = ft.Container(
        content=ft.Column([
            ft.Container(width=1, height=1),  # Espacio para centrar el contenido
            forma_pago,
            cantidad_recibida,
            cambio_text,
            total_text,
            ft.Row([
                ft.ElevatedButton(
                    "Cancelar venta", 
                    icon=ft.Icons.CANCEL, 
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: cancelar_venta(),
                    icon_color=ft.Colors.WHITE
                ),
                ft.ElevatedButton(
                    "Finalizar venta", 
                    icon=ft.Icons.CHECK, 
                    bgcolor=ft.Colors.GREEN, 
                    color=ft.Colors.WHITE,
                    on_click=lambda e: finalizar_venta(),
                    icon_color=ft.Colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False,
        padding=20,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=10,
    )
    
    search_field = ft.TextField(label="Buscar producto", prefix_icon=ft.Icons.SEARCH)
    product_list = ft.ListView(expand=True, spacing=10)
    carrito_list = ft.ListView(expand=True, spacing=10)
    
    def actualizar_forma_pago():
        if forma_pago.value == "Tarjeta":
            cantidad_recibida.visible = False
            cambio_text.value = "Cambio: N/A"
        else:
            cantidad_recibida.visible = True
            cambio_text.value = "Cambio: $0.00"
        page.update()
    
    def actualizar_cambio():
        if forma_pago.value == "Efectivo" and cantidad_recibida.value:
            try:
                recibido = float(cantidad_recibida.value)
                total = sum(info["precio"] * info["cantidad"] for info in carrito.values())
                cambio = recibido - total
                cambio_text.value = f"Cambio: ${cambio:.2f}" if cambio >= 0 else "Cantidad insuficiente"
            except ValueError:
                cambio_text.value = "Cantidad inválida"
        page.update()
    
    def actualizar_lista():
        product_list.controls.clear()
        busqueda = search_field.value.lower()

        for p in productos:
            if busqueda in p["nombre"].lower() or busqueda in p["id"]:
                product_list.controls.append(ft.ListTile(
                    title=ft.Text(f"{p['id']} - {p['nombre']} - ${p['precio']:.2f}"),
                    subtitle=ft.Text(f"Disponibles: {p['cantidad']}"),
                    trailing=ft.IconButton(ft.Icons.ADD, on_click=lambda e, p=p: agregar_al_carrito(p))
                ))
        page.update()
    
    def agregar_al_carrito(producto):
        if producto["nombre"] in carrito:
            carrito[producto["nombre"]]["cantidad"] += 1
        else:
            carrito[producto["nombre"]] = {"precio": producto["precio"], "cantidad": 1}
        actualizar_carrito()
    
    def quitar_del_carrito(producto):
        if producto in carrito:
            if carrito[producto]["cantidad"] > 1:
                carrito[producto]["cantidad"] -= 1
            else:
                del carrito[producto]
        actualizar_carrito()
    
    def actualizar_carrito():
        carrito_list.controls.clear()
        for nombre, info in carrito.items():
            carrito_list.controls.append(ft.ListTile(
                title=ft.Row([
                    ft.Text(f"{nombre} - ${info['precio']:.2f}"),
                    ft.Container(expand=True),
                    ft.Text(f"{info['cantidad']}")
                ]),
                trailing=ft.IconButton(ft.Icons.REMOVE, on_click=lambda e, n=nombre: quitar_del_carrito(n))
            ))
        
        vaciar_carrito_btn.visible = len(carrito) > 0
        proceder_al_pago_btn.visible = len(carrito) > 0
        
        actualizar_total()
        page.update()
    
    def actualizar_total():
        total = sum(info["precio"] * info["cantidad"] for info in carrito.values())
        total_text.value = f"Total: ${total:.2f}"
        actualizar_cambio()
        page.update()
    
    def vaciar_carrito():
        carrito.clear()
        actualizar_carrito()
        page.update()
    
    def proceder_al_pago():
        if carrito:
            pago_section.visible = True
            vaciar_carrito_btn.visible = False
            proceder_al_pago_btn.visible = False
            total = sum(info["precio"] * info["cantidad"] for info in carrito.values())
            total_text.value = f"Total: ${total:.2f}"
            page.update()
    
    def cancelar_venta():
        pago_section.visible = False
        vaciar_carrito_btn.visible = len(carrito) > 0
        proceder_al_pago_btn.visible = len(carrito) > 0
        cantidad_recibida.value = ""
        forma_pago.value = None
        cambio_text.value = "Cambio: $0.00"
        page.update()
    
    def finalizar_venta():
        page.dialog = pago_dialog
        pago_dialog.open = True
        
        carrito.clear()
        pago_section.visible = False
        actualizar_carrito()
        cantidad_recibida.value = ""
        forma_pago.value = None
        cambio_text.value = "Cambio: $0.00"
        
        page.update()
    
    def ventas_view():
        global vaciar_carrito_btn, proceder_al_pago_btn
        
        vaciar_carrito_btn = ft.ElevatedButton(
            "Vaciar carrito",
            icon=ft.Icons.DELETE, 
            bgcolor=ft.Colors.RED, 
            color=ft.Colors.WHITE,
            on_click=lambda e: vaciar_carrito(),
            visible=False,
            icon_color=ft.Colors.WHITE
        )
        
        proceder_al_pago_btn = ft.ElevatedButton(
            "Proceder al pago", 
            icon=ft.Icons.PAYMENT, 
            bgcolor=ft.Colors.GREEN, 
            color=ft.Colors.WHITE,
            on_click=lambda e: proceder_al_pago(),
            visible=False,
            icon_color=ft.Colors.WHITE
        )
        
        return ft.Column([
            ft.Text("Ventas", size=24, weight=ft.FontWeight.BOLD),
            search_field,
            ft.ElevatedButton("Buscar", on_click=lambda e: actualizar_lista()),
            product_list,
            ft.Text("Carrito de compras", size=20, weight=ft.FontWeight.BOLD),
            carrito_list,
            ft.Row([
                vaciar_carrito_btn,
                proceder_al_pago_btn
            ], alignment=ft.MainAxisAlignment.CENTER),
            pago_section
        ])

    def inventario_view():
        if not is_admin:
            return ft.Column([
                ft.Text("Acceso restringido", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Debes ingresar como administrador para acceder a esta sección"),
                ft.ElevatedButton(
                    "Ingresar contraseña",
                    on_click=lambda e: abrir_password_dialog(),
                    icon=ft.Icons.LOCK_OPEN
                )

            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
        
        # Definir las columnas
        table_columns = [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Precio")),
            ft.DataColumn(ft.Text("En existencia")),
        ]
        
        # Crea la tabla con las columnas
        inventario_table = ft.DataTable(columns=table_columns, rows=[])

        table_columns = [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Precio")),
            ft.DataColumn(ft.Text("En existencia")),
        ]
        ft.ElevatedButton(
            "Bloquear inventario",
            icon=ft.icons.LOCK,
            on_click=lambda e: abrir_password_dialog()  # Reabre el diálogo de contraseña
        )


        inventario_table = ft.DataTable(columns=table_columns, rows=[])

        def actualizar_tabla():
            inventario_table.rows.clear()
            for p in productos:
                inventario_table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p["id"])),
                    ft.DataCell(ft.Text(p["nombre"])),
                    ft.DataCell(ft.Text(f"${p['precio']:.2f}")),
                    ft.DataCell(ft.Text(str(p["cantidad"]))),
                ]))
            page.update()

        actualizar_tabla()

        new_product_id = ft.TextField(label="ID del producto")
        new_product_name = ft.TextField(label="Nombre del producto")
        new_product_price = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
        new_product_quantity = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)

        def agregar_producto(e):
            if all([new_product_id.value, new_product_name.value, new_product_price.value, new_product_quantity.value]):
                productos.append({
                    "id": new_product_id.value,
                    "nombre": new_product_name.value,
                    "precio": float(new_product_price.value),
                    "cantidad": int(new_product_quantity.value)
                })
                new_product_id.value = ""
                new_product_name.value = ""
                new_product_price.value = ""
                new_product_quantity.value = ""
                actualizar_tabla()

        return ft.Column([
            ft.Row([
                new_product_id,
                new_product_name,
                new_product_price,
                new_product_quantity,
                ft.ElevatedButton("Agregar Producto", icon=ft.Icons.ADD, on_click=agregar_producto),
                #ft.ElevatedButton("Bloquear inventario", icon=ft.Icons.LOCK, on_click=lambda e: abrir_password_dialog())
            ]),
            ft.Text("Gestión de Inventario", size=24, weight=ft.FontWeight.BOLD),
            inventario_table,
        ])

    def reportes_view():
        return ft.Column([
            ft.Text("Reportes de Ventas", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Exportar a PDF", icon=ft.Icons.PICTURE_AS_PDF),
            ft.ElevatedButton("Exportar a Excel", icon=ft.Icons.TABLE_CHART),
        ])

    content = ft.Container(expand=True)

    def change_view(e):
        index = navigation.selected_index if e is None else e.control.selected_index
        if index == 0:
            content.content = ventas_view()
        elif index == 1:
            content.content = inventario_view()
            if not is_admin:
                abrir_password_dialog()
        elif index == 2:
            content.content = reportes_view()
        page.update()

    navigation.on_change = change_view
    layout = ft.Row([navigation, ft.VerticalDivider(width=1), content], expand=True)
    
    page.add(layout)
    change_view(None)  # Inicializar con la vista de ventas
    actualizar_lista()

ft.app(target=main)