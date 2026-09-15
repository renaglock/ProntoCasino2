# Feature: Resolución Móvil, Hoja de Estilos UCT (styles.kv) y Pantalla de Login

- **Fecha**: 2026-09-15
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) y [docs/PRONTO CASINO.pdf](../PRONTO%20CASINO.pdf) (Diseño de interfaz móvil UCT, colores institucionales y autenticación limpia)

---

## 1. Descripción y Objetivo
Esta feature adapta la aplicación móvil a los estándares ergonómicos y estéticos de un smartphone real:
1. **Resolución de Smartphone**: Se establece el viewport a dimensiones verticales de smartphone (`380 x 720 px`), garantizando una experiencia idéntica a la ejecución nativa en dispositivos Android 10+ e iOS 14+.
2. **Hoja de Estilos UCT (`punto_casino/views/styles.kv`)**: Implementación del equivalente de CSS en Kivy mediante Kivy Language (`.kv`), aplicando la paleta institucional de la Universidad Católica de Temuco: fondos blancos inmaculados (`#FFFFFF`), azul cielo claro (`#E1F5FE` / `#0288D1`) y azul UCT (`#0A3871`).
3. **Pantalla de Login Dedicada (`LoginScreen`)**: Se remueve el selector provisional de roles de la pantalla principal para mantener el diseño prístino. El usuario inicia sesión formalmente en una pantalla de bienvenida antes de acceder al sistema.

---

## 2. Tecnicismos y Mecánica de Funcionamiento

### 2.1 Arquitectura y Módulos
- **`main.py`**:
  - Configura `Window.size = (380, 720)` y fija dimensiones mínimas para simular un smartphone.
  - Carga la hoja de estilos `punto_casino/views/styles.kv` mediante `Builder.load_file`.
  - Establece `LoginScreen` como pantalla inicial en el `MDScreenManager`.
- **`punto_casino/views/styles.kv`**:
  - Define reglas globales para tarjetas estilizadas con fondo blanco puro y sombras sutiles (`radius: [14, 14, 14, 14]`).
  - Barras superiores con gradiente/color azul UCT y botones redondeados en tonos celestes y blancos.
- **`punto_casino/views/screens/login_screen.py` (`LoginScreen`)**:
  - Pantalla con tarjeta de acceso centralizada.
  - Opciones de acceso con un solo toque para cada perfil:
    - 🎓 **Estudiante**: Renato Escárate (Saldo: $15.000 CLP).
    - 🧑‍🍳 **Cajero**: Cristian (Sabor Único).
    - ⚙️ **Administrador**: Gestión General.
    - 👤 **Invitado**: Pedido Rápido.
  - Navegación automática hacia la pantalla respectiva tras autenticarse con éxito.
- **Barra Superior Prístina**:
  - Muestra el nombre del usuario activo y un botón minimalista de "Salir / Cerrar Sesión" que reinicia la sesión hacia `LoginScreen`.

---

## 3. Casos Borde y Manejo de Errores
- **Cierre de Sesión Seguro**: Al presionar "Salir", se restablece el usuario activo a estado no autenticado y se limpia el carrito de compras.
- **Redimensionamiento de Ventana**: La ventana respeta la relación de aspecto móvil sin distorsionar los botones ni el scrollview.
- **Contraste y Accesibilidad**: Tipografías oscuras sobre fondos blancos y textos blancos sobre fondos azules profundos, asegurando cumplimiento WCAG de contraste visual.

---

## 4. Pruebas y Verificación

### Comando de ejecución local
```bash
./kivy_env/bin/python main.py
```

### Checklist de Verificación Funcional
- [x] La ventana abre en formato vertical de smartphone (380x720).
- [x] El flujo inicia en la pantalla de Login con estética blanca y azul claro UCT.
- [x] Al seleccionar un perfil, ingresa con los permisos correspondientes.
- [x] El botón "Salir" regresa a la pantalla de Login y permite alternar de usuario de forma limpia.

