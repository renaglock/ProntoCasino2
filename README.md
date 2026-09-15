# Pronto Casino UCT 🍽️📱

Plataforma móvil oficial para la gestión de reservas, comandas y retiros rápidos en el casino de la **Universidad Católica de Temuco (UCT)**. Diseñada bajo la resolución de smartphone (380x720 px), con interfaz Material Design 3 (KivyMD 2.0), persistencia SQLite WAL de alto rendimiento y seguridad criptográfica OWASP.

---

## 🚀 Características Principales

1. **Resolución y Diseño Móvil (Smartphone UX)**:
   - Formato móvil optimizado (`Window.size = (380, 720)`).
   - Estilizado institucional con colores de la UCT (Azul Marino `#0A3871`, Celeste `#0288D1` y fondos limpios).
   - Tarjetas responsivas anti-saturación de texto para visualización ergonómica en pantallas compactas.

2. **Catálogo y Reservas sin Filas**:
   - Menú del día (Menú Normal, Ejecutivo, Hipocalórico, Vegetariano, Comidas Rápidas y Bebidas).
   - Control en tiempo real del stock disponible en cocina.
   - Carrito de compras con cálculo automático de totales.

3. **Comandas Numeradas y Código QR de Retiro**:
   - Generación de comandas secuenciales (`#101`, `#102`, etc.).
   - Estado explícito **"Pendiente por pagar"** en color ámbar (`#D97706`).
   - Modal interactivo con desglose plato por plato, total a pagar en casino y **código QR visual generado en memoria** (OpenGL Texture).
   - Cancelación de comanda por el cliente con restitución atómica de stock a cocina.

4. **Módulo de Caja y Cocina (Sabor Único)**:
   - Cola de comandas en preparación.
   - Escáner/lector de códigos QR para validar pedidos.
   - Previsualización del cliente, platos y total a cobrar.
   - Flujo de cobro y entrega en meson (**"Cobrar y Entregar"**).

5. **Panel de Administración General**:
   - CRUD completo de productos (Crear, Ver, Editar, Eliminar platos y precios).
   - Confirmación de acciones críticas para evitar borrados accidentales.

6. **Seguridad y Persistencia de Nivel Bancario**:
   - Base de datos local SQLite configurada en modo **WAL (Write-Ahead Logging)** para máxima concurrencia y fluidez a 60 FPS.
   - Hashing de contraseñas con **PBKDF2-HMAC-SHA256 (600.000 iteraciones)** y sal criptográfica de 32 bytes por usuario.
   - Validación segura contra ataques de temporización (*timing attacks*) mediante `secrets.compare_digest`.

---

## 👥 Cuentas de Acceso Preconfiguradas

| Rol | Correo Electrónico | Contraseña | Capacidades |
| :--- | :--- | :--- | :--- |
| **Estudiante** | `renato@uct.cl` | `Renato2026!` | Catálogo, pedidos, comanda QR y cancelación |
| **Cajero** | `cristian@uct.cl` | `Cristian2026!` | Cola de cocina, confirmación y escáner/cobro QR |
| **Administrador** | `admin@uct.cl` | `Admin2026!` | Gestión CRUD de platos, inventario y precios |
| **Invitado** | `invitado@uct.cl` | `Invitado2026!` | Compra directa sin registro previo |

---

## 📦 Instalación y Ejecución Local

### Prerrequisitos
- Python 3.10 o superior (compatible con Python 3.13)
- Sistema operativo Linux / macOS / Windows

### 1. Clonar el repositorio
```bash
git clone https://github.com/renaglock/ProntoCasino2.git
cd ProntoCasino2
```

### 2. Crear y activar entorno virtual
```bash
python3 -m venv kivy_env
source kivy_env/bin/activate   # En Linux/macOS
# kivy_env\Scripts\activate    # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar la aplicación
```bash
python main.py
```

---

## 📁 Estructura del Proyecto

```text
.
├── main.py                        # Punto de entrada y orquestador KivyMD
├── requirements.txt               # Dependencias del proyecto
├── punto_casino/
│   ├── core/
│   │   ├── config.py              # Configuración y temas institucionales
│   │   └── events.py              # Eventos del sistema
│   ├── models/
│   │   ├── order.py               # Modelo de comandas, estados y colores
│   │   ├── product.py             # Modelo de platos e inventario
│   │   └── user.py                # Modelo de usuarios y roles
│   ├── repositories/
│   │   ├── database.py            # SQLite WAL Manager y seeding inicial
│   │   ├── order_repository.py    # Persistencia de comandas
│   │   ├── product_repository.py  # Persistencia y catálogo de platos
│   │   └── user_repository.py     # Repositorio seguro de credenciales
│   ├── services/
│   │   ├── auth_service.py        # Lógica de autenticación y sesiones
│   │   ├── cashier_service.py     # Gestión de cocina, cobro y escaneo QR
│   │   ├── order_service.py       # Carrito, checkout y cancelación
│   │   └── security.py            # Criptografía PBKDF2-HMAC-SHA256
│   ├── utils/
│   │   ├── formatters.py          # Formateo monetario en CLP
│   │   └── qr_generator.py        # Generación de códigos QR en memoria
│   └── views/
│       ├── styles.kv              # Hoja de estilos Kivy (CSS responsive UCT)
│       └── screens/
│           ├── admin_screen.py    # Panel de administración CRUD
│           ├── cashier_screen.py  # Dashboard de caja y escáner QR
│           ├── catalog_screen.py  # Menú del día y carrito
│           ├── login_screen.py    # Autenticación institucional UCT
│           └── reservations_screen.py # Reservas, detalle y QR de comanda
└── docs/                          # Documentación técnica por feature
    ├── requerimientos.md          # Especificación formal del sistema
    ├── crud_and_user_roles/
    ├── mobile_ui_and_auth/
    ├── mvp_ui_screens/
    ├── project_structure/
    ├── qr_pickup_and_reservations/
    └── security_and_database/
```

---

## 📜 Licencia y Autoría
Desarrollado para la **Universidad Católica de Temuco (UCT)**.
