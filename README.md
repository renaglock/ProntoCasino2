# Pronto Casino Universidad 🍽️📱

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![KivyMD](https://img.shields.io/badge/KivyMD-2.0.0%20(M3)-29B6F6?logo=kivy&logoColor=white)](https://kivymd.readthedocs.io/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%7C%20Multi--Tenant-4CAF50)](#-arquitectura-del-sistema)
[![Security](https://img.shields.io/badge/Security-PBKDF2--HMAC--SHA256%20%7C%20OWASP-E91E63)](#-seguridad-y-persistencia)
[![License](https://img.shields.io/badge/License-Proprietary-gray)](#-autoría-y-licencia)

> **Plataforma móvil empresarial para la gestión integral de menús, comandas y retiros rápidos en casinos de educación superior.**  
> Diseñada para erradicar las largas filas en recintos universitarios, sincronizando en tiempo real a estudiantes, personal de cocina, cajeros y administradores a través de una experiencia móvil táctil basada en **Material Design 3** y arquitectura desacoplada de grado comercial.

---

## 📌 Tabla de Contenidos
- [Propósito y Contexto Institucional](#-propósito-y-contexto-institucional)
- [Matriz de Roles y Capacidades](#-matriz-de-roles-y-capacidades)
- [Características Principales de la Plataforma](#-características-principales-de-la-plataforma)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Seguridad y Persistencia](#-seguridad-y-persistencia)
- [Cuentas de Prueba Preconfiguradas](#-cuentas-de-prueba-preconfiguradas)
- [Instalación y Puesta en Marcha](#-instalación-y-puesta-en-marcha)
- [Pruebas Automatizadas](#-pruebas-automatizadas)
- [Estructura del Proyecto y Documentación](#-estructura-del-proyecto-y-documentación)
- [Roadmap de Expansión Universitaria en Chile](#-roadmap-de-expansión-universitaria-en-chile)
- [Autoría y Licencia](#-autoría-y-licencia)

---

## 🎯 Propósito y Contexto Institucional

El flujo tradicional de compra y retiro en los casinos universitarios sufre habitualmente de:
1. **Aglomeraciones masivas en horarios punta** (12:30 a 14:30 hrs).
2. **Pérdida innecesaria de tiempo** de estudiantes y docentes en filas de pago y espera.
3. **Descoordinación entre caja y mesón de despacho**, con errores de cuadratura manual.
4. **Desperdicio de alimentos preparados** por falta de previsión en la demanda diaria.

**Pronto Casino** resuelve esta problemática permitiendo a los usuarios reservar su almuerzo con antelación desde su teléfono inteligente, recibir una comanda secuencial con código de retiro digital en memoria, y recoger su comida en caja mediante un trámite express de menos de 10 segundos.

---

## 👥 Matriz de Roles y Capacidades

| Rol | Identificador | Capacidades del Sistema | Ámbito Universitario |
| :--- | :--- | :--- | :--- |
| **Estudiante / Funcionario** | `client` | Catálogo clasificado, carrito reactivo, comanda digital con código QR en memoria, historial de pedidos y cancelación con devolución de stock. | Alumnos, docentes y funcionarios con correo institucional |
| **Invitado** | `guest` | Navegación de menú y pedidos directos en mesón sin registro previo. | Visitas al campus y público general |
| **Cajero** | `cashier` | Cola en vivo de cocina, confirmación y despacho en 1-toque, cobro de comanda en mesón, escáner de códigos QR físicos/simulados y auditoría de turno. | Operadores de concesión y cajeros |
| **Administrador** | `admin` | Todas las facultades de cajero más: gestión de catálogo y precios, creación de ofertas/promociones con etiquetas personalizadas, herramientas gráficas contables (KPIs, distribución de ingresos, balance de pedidos y ranking de consumo) y auditoría histórica. | Concesionario y administradores de sede |
| **SuperAdmin** | `superadmin` | Gestión multi-tenant de instituciones, configuración de pasarelas de federación (SSO) y administración de sedes. | Administrador de plataforma SaaS |

---

## ✨ Características Principales de la Plataforma

### 1. Experiencia de Usuario Móvil de Alta Fidelidad (Material Design 3)
- **Viewport Nativo Vertical**: Optimizado estrictamente para smartphones (`380 x 720 dp`, adaptable desde `360 x 640 dp`).
- **Navegación Táctil M3 (`M3NavItem`)**: Barra de pestañas con captura táctil en el 100% de la superficie de cada celda, eliminando artefactos visuales de tipo interruptor (*switch*) y proporcionando un indicador superior de acento corporativo de 3 dp (`#0A3871`).
- **Paleta de Identidad Visual Institucional**:
  - Azul Marino Corporativo (`#0A3871`): Títulos principales, estado activo y botones primarios.
  - Azul Cielo (`#0288D1`): Acciones complementarias y acentos informativos.
  - Verde Esmeralda (`#2EC76E`): Promociones, ofertas destacadas y confirmación de cobro.
  - Gris Pizarra (`#64748B` / `#475569`): Tipografía secundaria, metadatos y descripciones legibles.
  - Blanco Puro (`#FFFFFF`) y Gris Suave (`#F8FAFC`): Superficies limpias tipo tarjeta con bordes contorneados (`style="outlined"`, `elevation=0`) que previenen defectos gráficos en entornos OpenGL por software.

### 2. Catálogo Interactivo y Carrito Reactivo
- **Filtrado por Categorías Oficiales**: Menú Normal, Menú Ejecutivo, Menú Hipocalórico, Menú Vegetariano, Comidas Rápidas, Bebidas y sección especial de **Ofertas**.
- **Control de Inventario en Vivo**: Desactivación preventiva y control de stock unitario por plato.
- **Transiciones Instantáneas (0 ms)**: Mecanismo de control de estado sucio (*dirty check*) que evita la reconstrucción innecesaria del árbol de widgets al navegar entre vistas.

### 3. Sistema de Comandas y Código QR Segregado por Rol
- **Comandas Numeradas Secuenciales**: Identificador diario unívoco para cocina y caja (`#101`, `#102`, etc.).
- **Código QR en Memoria (Estudiantes / Invitados)**: Generado directamente como textura OpenGL (`generate_qr_texture`), sin escribir archivos temporales en disco ni saturar el almacenamiento del dispositivo.
- **Ficha Ejecutiva de Comanda (Cajeros / Administradores)**: Cuando un cajero o administrador consulta una comanda, la plataforma muestra la ficha de auditoría contable (datos del cliente, rol, hora de creación, desglose de platos y montos), ocultando el código QR redundante y eliminando espacios vacíos.

### 4. Módulo de Operación de Caja y Cocina
- **Cola de Comandas Activas**: Visualización de pedidos en estado `Pendiente`, `Confirmado` y `Listo en Cocina`.
- **Despacho Rápido en 1-Toque**: Botón directo *"Cobrar y Entregar"* para liquidar pedidos en mesón sin forzar lectura óptica obligatoria.
- **Escáner QR Integrado**: Soporte para lectura en vivo mediante cámara web física (OpenCV) y modo de prueba simulado.

### 5. Panel de Gestión y Analítica Contable
- **Gestión Simplificada de Platos**: Formulario con selector interactivo de categorías (`cat_select_card`) e insignias institucionales de ID (`MENU-010`).
- **Motor de Ofertas y Descuentos**: Activación de precios rebajados con distintivos visuales (*"Promo Alumnos"*, *"Por Vencer"*, *"30% OFF"*).
- **Herramientas Gráficas de Inteligencia de Negocio**:
  - *KPI Cards*: Recaudación total en CLP, ticket promedio, tasa de despacho y volumen de productos entregados.
  - *Distribución de Ingresos*: Barras horizontales relativas con porcentaje de facturación por categoría.
  - *Balance Operativo de Pedidos*: Barra segmentada continua (Entregados, En Cocina, Cancelados).
  - *Ranking de Platos Más Vendidos*: Top de productos con métricas de demanda.

---

## 🏛️ Arquitectura del Sistema

El proyecto implementa los principios de **Clean Architecture** y separación estricta de responsabilidades:

```text
                               ┌─────────────────────────┐
                               │   Vistas / UI (KivyMD)  │
                               │  Screens & Components   │
                               └────────────┬────────────┘
                                            │ Dispatches UI events
                                            ▼
                               ┌─────────────────────────┐
                               │     Capa de Servicios   │
                               │  Auth, Order, Cashier   │
                               └────────────┬────────────┘
                                            │ Encapsulates business logic
                                            ▼
                               ┌─────────────────────────┐
                               │  Capa de Repositorios   │
                               │  Users, Products, Orders│
                               └────────────┬────────────┘
                                            │ Executes SQL queries
                                            ▼
                               ┌─────────────────────────┐
                               │   Base de Datos SQLite  │
                               │   (WAL Mode + Pragmas)  │
                               └─────────────────────────┘
```

---

## 🔐 Seguridad y Persistencia

1. **Persistencia SQLite WAL**:
   - Concurrencia optimizada mediante Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
   - Integridad referencial reforzada con `PRAGMA foreign_keys = ON;`.
2. **Criptografía de Credenciales**:
   - Algoritmo **PBKDF2-HMAC-SHA256 con 600.000 iteraciones**.
   - Sal criptográfica aleatoria de 32 bytes (`os.urandom(32)`) única por usuario.
   - Comparación en tiempo constante con `secrets.compare_digest` para neutralizar ataques de temporización (*timing attacks*).
3. **Defensa contra Inyecciones SQL**:
   - Todas las consultas a nivel repositorio se encuentran 100% parametrizadas (`?`, tuplas de valores). Cero concatenación de cadenas SQL.
4. **Control de Acceso Basado en Roles (RBAC)**:
   - Validación de permisos en cada servicio de dominio antes de ejecutar acciones de administración, cobro o inventario.

---

## 🔑 Cuentas de Prueba Preconfiguradas

La base de datos se inicializa automáticamente con los siguientes usuarios de demostración:

| Rol | Correo Electrónico | Contraseña | Perfil y Propósito |
| :--- | :--- | :--- | :--- |
| **Estudiante** | `renato@uct.cl` | `Renato2026!` | Flujo completo de compra, reserva de comanda y visualización de QR |
| **Cajero** | `cristian@uct.cl` | `Cristian2026!` | Operación de cola activa en cocina, cobro directo y escaneo QR |
| **Administrador** | `admin@uct.cl` | `Admin2026!` | Creación de platos, activación de ofertas, métricas y auditoría |
| **Invitado** | `invitado@uct.cl` | `Invitado2026!` | Pedido directo sin credenciales |

---

## 🚀 Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.10 o superior (compatible con Python 3.11, 3.12 y 3.13).
- Sistema Operativo: Linux (Debian/Ubuntu, Fedora, Arch), macOS o Windows.
- Dependencias de sistema para Kivy (librerías SDL2, OpenGL).

### 1. Clonar el Repositorio
```bash
git clone https://github.com/renaglock/ProntoCasino2.git
cd ProntoCasino2
```

### 2. Configurar el Entorno Virtual
```bash
python3 -m venv kivy_env
source kivy_env/bin/activate    # En Linux / macOS
# kivy_env\Scripts\activate     # En Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar la Aplicación
```bash
python main.py
```

---

## 🧪 Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración de dominio:

```bash
# Ejecución completa de la suite de pruebas
./kivy_env/bin/python -m unittest discover -s tests -p "test_*.py"

# Verificación de compilación y análisis estático
./kivy_env/bin/python -m py_compile main.py punto_casino/views/screens/*.py
```

---

## 📁 Estructura del Proyecto y Documentación

```text
.
├── main.py                                      # Punto de entrada principal y gestor de pantallas
├── requirements.txt                             # Especificación de dependencias del proyecto
├── .gitignore                                   # Filtros de exclusión de git
├── punto_casino/                                # Paquete principal de la plataforma
│   ├── core/                                    # Configuraciones globales y eventos de bus
│   │   ├── config.py
│   │   └── events.py
│   ├── models/                                  # Entidades de dominio y esquemas
│   │   ├── order.py                             # Modelos de comandas, estados y colores
│   │   ├── product.py                           # Modelos de platos e inventario
│   │   └── user.py                              # Modelos de usuario y roles
│   ├── repositories/                            # Capa de persistencia SQLite
│   │   ├── database.py                          # Gestor de conexión WAL y migraciones
│   │   ├── order_repository.py
│   │   ├── product_repository.py
│   │   └── user_repository.py
│   ├── services/                                # Capa de lógica de negocio y seguridad
│   │   ├── auth_service.py                      # Sesión, autenticación y RBAC
│   │   ├── cashier_service.py                   # Operaciones de cocina y escáner
│   │   ├── order_service.py                     # Carrito, comandas y reportería contable
│   │   └── security.py                          # Hashing PBKDF2-HMAC-SHA256
│   ├── utils/                                   # Utilidades generales
│   │   ├── formatters.py                        # Formato de moneda chilena (CLP)
│   │   └── qr_generator.py                      # Renderizado QR en texturas OpenGL
│   └── views/                                   # Capa de interfaz de usuario
│       ├── styles.kv                            # Reglas de estilo Kivy declarativo
│       ├── components/                          # Componentes reutilizables M3
│       │   └── ui_elements.py                   # Botones, tabs de navegación e insignias
│       └── screens/                             # Pantallas principales
│           ├── admin_screen.py                  # Administración de catálogo y contabilidad
│           ├── cashier_screen.py                # Caja, cocina y lector QR
│           ├── catalog_screen.py                # Menú del día y carrito
│           ├── login_screen.py                  # Autenticación y teclado
│           └── reservations_screen.py           # Reservas, ficha de comanda y código QR
├── tests/                                       # Suite de pruebas automatizadas
│   └── test_domain.py                           # Pruebas de dominio, servicios y seguridad
└── docs/                                        # Documentación técnica y arquitectura
    ├── requerimientos.md                        # Requerimientos funcionales y no funcionales
    ├── TEMPLATE_FEATURE.md                      # Plantilla estándar para nuevas funcionalidades
    └── plan_expansion_universidades_chile/      # Estrategia de expansión SaaS universitaria
        └── README.md                            # Blueprint multi-tenant para universidades de Chile
```

---

## 🗺️ Roadmap de Expansión Universitaria en Chile

El plan estratégico de internacionalización y escalamiento nacional de la plataforma se detalla en [`docs/plan_expansion_universidades_chile/README.md`](docs/plan_expansion_universidades_chile/README.md) y contempla:

1. **Federación Institucional de Identidades**:
   - Integración con proveedores de identidad universitarios vía **OAuth2 / OpenID Connect (OIDC)** y **SAML2 / Shibboleth** (red COFIDE / REUNA).
   - Acceso con credenciales institucionales reales (`@uct.cl`, `@udec.cl`, `@uchile.cl`, `@usach.cl`, `@puc.cl`, etc.).
2. **Arquitectura Multi-Tenant Aislada**:
   - Segregación lógica de datos por universidad, campus y concesionario de alimentación.
3. **Integración con Becas y Medios de Pago Chilenos**:
   - Compatibilidad con tarjeta BAES / Junaeb (Sodexo / Edenred), Webpay Plus (Transbank) y billeteras digitales.
4. **Notificaciones Push y Pantalla de Cocina (KDS)**:
   - Notificaciones móviles inmediatas cuando la comanda cambia a estado *"Listo para retirar"*.

---

## 📜 Autoría y Licencia

Desarrollado bajo estándares empresariales para la **Universidad Católica de Temuco (UCT)** y el ecosistema de instituciones de educación superior en Chile.  
Todos los derechos reservados © 2026.
