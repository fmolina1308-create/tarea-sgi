import streamlit as st
from config.conexion import obtener_conexion


def cargar_productos():
    conexion = obtener_conexion()
    if conexion is None:
        return [], []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT Id_Producto, Nombre, Precio, Stock "
            "FROM PRODUCTOS ORDER BY Id_Producto DESC"
        )
        filas = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]
        return filas, columnas
    except Exception as error:
        st.error(f"Error al consultar los productos: {error}")
        return [], []
    finally:
        if cursor is not None:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


def guardar_producto(nombre, precio, stock):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion is None:
            return
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO PRODUCTOS (Nombre, Precio, Stock) "
            "VALUES (%s, %s, %s)",
            (nombre, float(precio), int(stock))
        )
        conexion.commit()
        st.success("Producto registrado correctamente.")
    except Exception as error:
        if conexion is not None:
            conexion.rollback()
        st.error(f"Error al registrar el producto: {error}")
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()


def mostrar_productos():
    st.header("Productos")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre del producto")
        precio = st.number_input("Precio", min_value=0.01, step=0.01)
        stock = st.number_input("Stock", min_value=0, step=1)
        guardar = st.form_submit_button("Guardar producto")

        if guardar:
            if nombre.strip() == "":
                st.warning("Debe ingresar el nombre del producto.")
            else:
                guardar_producto(nombre, precio, stock)

    st.subheader("Listado de productos")
    filas, columnas = cargar_productos()
    if filas:
        st.dataframe(
            [dict(zip(columnas, fila)) for fila in filas],
            use_container_width=True
        )
    else:
        st.info("Aún no hay productos registrados.")
