# Pronto Casino UCT 🍽️📱

Plataforma móvil oficial para la gestión de reservas, comandas y retiros rápidos en el casino de la **Universidad Católica de Temuco (UCT)**. Diseñada bajo resolución de smartphone (380x720 px), con interfaz Material Design 3 (KivyMD 2.0), persistencia SQLite WAL de alto rendimiento y seguridad criptográfica de grado bancario.

---

## 🚀 Características Principales

1. **Resolución y Ergonomía Móvil (Smartphone UX)**:
   - Formato móvil vertical optimizado (`Window.size = (380, 720)`).
   - Paleta institucional UCT: Azul Marino (`#0A3871`), Celeste (`#0288D1`), Verde Claro para promociones (`#2EC76E`) y fondos limpios.
   - Tarjetas responsivas con truncamiento inteligente anti-saturación de texto para pantallas compactas.

2. **Acceso Seguro y Accesibilidad**:
   - Navegación completa por teclado físico (`Tab`, `Shift+Tab`, `Enter`, flechas de dirección).
   - Campo de contraseña con botón interactivo de revelación (`eye` / `eye-off`).
   - Hashing con **PBKDF2-HMAC-SHA256 (600.000 iteraciones)** y sal criptográfica de 32 bytes por usuario.
   - Protección contra *timing attacks* mediante `secrets.compare_digest`.

3. **Catálogo y Reservas sin Filas**:
   - Menú del día organizado por categorías oficiales (*Menú Normal*, *Menú Ejecutivo*, *Menú Hipocalórico*, *Menú Vegetariano*, *Comidas Rápidas*, *Bebidas* y *Postres y Snacks*).
   - Control de inventario y stock en tiempo real.
   - Carrito dinámico con resumen de ítems y cálculo automático de totales.

4. **Comandas Numeradas y Código QR de Retiro**:
   - Generación de comandas secuenciales (`#101`, `#102`, etc.).
   - Estado explícito **"Pendiente por pagar"** en color ámbar institucional.
   - Modal interactivo con desglose de platos, total a pagar en casino y **código QR visual generado en memoria** (OpenGL Texture).
   - Cancelación de comanda por el estudiante con devolución atómica de stock e importe.

5. **Módulo de Caja y Cocina Omnipresente**:
   - Cola activa de comandas para preparación y entrega (`PENDING`, `CONFIRMED`, `READY`).
   - Botón directo de 1 toque **"Cobrar y Entregar"** para liquidar comandas sin forzar escaneo físico.
   - Botón **"Cobrar en Caja"** accesible para cajeros y administradores directamente desde el detalle de la comanda en **Reservas**.
   - Escáner y decodificador de códigos QR con soporte de cámara web física (OpenCV) y simulación instantánea.
   - Historial de turno para auditoría de comandas entregadas, rechazadas y canceladas.

6. **Panel de Administración y Gestión de Ofertas**:
   - CRUD completo de productos con confirmación de seguridad para evitar eliminaciones accidentales.
   - **Selector guiado de categorías (`select`)** con las 7 categorías oficiales del casino universitario.
   - **Gestión integral de ofertas y promociones**: activación de descuentos especiales con motivos personalizados (*Promo 2x1, Menú del día, 30% OFF, Por vencer*) destacados en verde claro.
   - Métricas contables en tiempo real: total recaudado, volumen de ventas y balance de comandas.

---

## 👥 Cuentas de Acceso Preconfiguradas

| Rol | Correo Electrónico | Contraseña | Capacidades |
| :--- | :--- | :--- | :--- |
| **Estudiante** | `renato@uct.cl` | `Renato2026!` | Catálogo, pedidos, comanda QR y cancelación |
| **Cajero** | `cristian@uct.cl` | `Cristian2026!` | Cola de cocina, confirmación, cobro directo y escáner QR |
| **Administrador** | `admin@uct.cl` | `Admin2026!` | Gestión CRUD, selector de categorías, ofertas y métricas |
| **Invitado** | `invitado@uct.cl` | `Invitado2026!` | Compra directa sin registro previo |

---

## 📦 Instalación y Ejecución Local

### Prerrequisitos
- Python 3.10 o superior (compatible con Python 3.11, 3.12 y 3.13)
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
│       ├── components/
│       │   └── ui_elements.py     # Botones, insignias y paleta de colores UCT
│       └── screens/
│           ├── admin_screen.py    # Panel de administración CRUD y selector de categorías
│           ├── cashier_screen.py  # Dashboard de caja, cobro y escáner QR
│           ├── catalog_screen.py  # Menú del día y carrito
│           ├── login_screen.py    # Autenticación institucional y teclado interactivo
│           └── reservations_screen.py # Reservas, detalle y QR de comanda
└── docs/                          # Documentación técnica por funcionalidad
    ├── requerimientos.md          # Especificación formal del sistema
    ├── cashier_charge_markup_and_admin_category_selector/
    ├── crud_and_user_roles/
    ├── login_keyboard_ux_and_green_offers/
    ├── mobile_ui_and_auth/
    ├── mvp_ui_screens/
    ├── project_structure/
    ├── qr_pickup_and_reservations/
    └── security_and_database/
```

---

## 📜 Licencia y Autoría
Desarrollado para la **Universidad Católica de Temuco (UCT)**.
