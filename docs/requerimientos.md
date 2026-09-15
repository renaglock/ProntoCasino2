# TOMA DE REQUERIMIENTOS SIMPLE DE PUNTO CASINO UNIVERSIDAD

## 1. Contexto de la situación

En un casino universitario donde los estudiantes van a comer, a menudo se forman largas filas para ser atendidos.
Esto genera congestión, molestias y pérdida de tiempo tanto para los clientes como para el personal del local.

En este documento presentamos una **solución tecnológica** al problema: una **aplicación móvil (APP)** que permita la **interacción entre el cliente y el encargado de la caja**, facilitando la **reserva, compra y retiro de pedidos sin necesidad de hacer fila**.
De esta manera, los clientes podrán **realizar sus pedidos con anticipación**, reduciendo el flujo de personas en el local y mejorando la experiencia general.

---

## 2. Lista de usuarios del sistema

Los usuarios que van a utilizar la aplicación son:

* Clientes (Acceso a la app para comprar un pedido de la tienda).
* Cajero (Recepciona el pedido desde su propia APP, confirma el pedido o rechaza el pedido).
* Administrador (Jefe del local que pueda tener acceso y tener vista de información de alto nivel).
* Invitados (No necesitan registrarse en la APP, pueden pedir mientras hagan el pago del producto).

## 3. Tipos de usuario o roles

Roles de usuario que permite la APP:

* Cliente normal (Necesita registrarse mediante su correo, contraseña y un nombre. Tiene acceso a los productos de la tienda para comprar y pagar).
* Usuario Cajero (Tiene un perfil más alto para poder confirmar los pedidos y también puede cancelar los pedidos si se necesita. También puede tener acceso al inventario donde puede agregar o quitar productos).
* Administrador (Tiene acceso al panel de administración de la tienda, donde puede otorgar permisos. También puede tener acceso a información con privilegios, como por ejemplo: estadísticas de venta, y tiene acceso a todos los permisos del cajero).

## 4. Datos básicos que va a guardar la base de datos

La base de datos de la app va a almacenar los datos del usuario cliente, los datos del usuario cajero, productos y datos del administrador.

**Productos** (El producto que se tiene dentro de la tienda):

* id_producto (La ID del producto, EMPA-01).
* Nombre del producto (Empanada).
* Precio del producto ($2.000 pesos).
* Stock (Esto si hay inventario).

**Pedido** (El pedido que hace el cliente):

* id_pedido (ID del pedido del cliente).
* nombre_cliente (Nombre de la persona que compra).
* id_producto (Los productos que pide el cliente).
* Nombre (Nombre del producto).
* Cantidad (Cantidad de artículos que lleva el cliente).
* Precio (Precio de los artículos).
* Total de la venta (El total a pagar).

**Usuarios** (Personal de la tienda):

* id_usuario (La ID de la persona que trabaja en la tienda).
* Nombre (Nombre de la persona).
* Rol (Puede ser rol como: Administrador o Cajero).

## 5. Lista de requisitos funcionales y no funcionales

**Funcionales**

* El sistema debe registrar un pedido hecho por el cliente.
* El sistema debe mostrar una lista de productos disponibles.
* El cajero puede confirmar un pedido en su app.
* Incluye sistema de inventario básico.

**No funcionales**

* Función donde el cajero pueda dar de baja un producto por falta de stock o por algún otro motivo.
* Reservar producto.
* Interfaz amigable y clara.

## 6. Definición del MVP (qué incluye / qué queda para futuras versiones)

**Qué incluye:**

* Que el cliente pueda buscar un producto y reservarlo desde su terminal (Puede ser un cliente o un invitado).
* Que el cajero pueda dar el visto bueno y confirmar el pedido para posteriormente ser entregado.

**Qué queda para futuras versiones:**

* Incluir un menú de registro (Sign in).
* Menú colación diaria.
* Notificaciones de promociones. Ejemplo: (Promo completo + bebida 20%).
* Sistema de inventarios.
* Producto del día o de la semana.
* Uso de la APP desde una computadora (uso desde un navegador).
* Estadisticas de venta (Métrica)



## 7. Prueba de que funciona git.

* Todo se debe subir a una branch develop antes que la main.
* Se debe ingresar un commit referencial y simple.
* Despues de cada jornada se debe hacer push de las features trabajadas.
* Se debe mantener el entorno lo mas simple y pristino posible.

## 8. Plazo deseado 

* Fase de analsis y diseño: 2 semanas.
* Desarrollo de pruebas: 6 semanas.
* Prueba piloto: 2 semanas.
* Entrega final: 10 semanas desde el inicio del proyecto.

## 9. Flujo principal del sistema 

* inicio de sesion/registro 
* visualizacion del menu 
* seleccion del pedido 
* pago
* confirmacion 
* generacion qr
* notificacion para retiro 

## Requisitos no funcionales 

* Seguridad: cifrado de datos y autificacion 
* Usabilidad: interfaz intuitiva y accesible 
* compatibilidad: soporte para dispositivos Android 10+ e IOS 14+ 
* Mantenibilidad: codigo modular y documentado
* Escalabilidad: soporte para minimo 800 usuarios simultaneos  
