# Feature: Arquitectura de Base de Datos SQLite WAL, Criptografía OWASP y Diseño UI UCT

- **Fecha**: 2026-09-15
- **Estado**: Completada
- **Autor / Responsable**: Antigravity Punto Casino Engineer
- **Referencia a Requerimientos**: [docs/requerimientos.md](../requerimientos.md) y [docs/PRONTO CASINO.pdf](../PRONTO%20CASINO.pdf) (Seguridad, cifrado de datos, autenticación, no saturación de UI y diseño institucional UCT)

---

## 1. Descripción y Objetivo
Esta feature eleva la plataforma a un nivel de acabado profesional de alta fidelidad:
1. **Estética y UI Responsive UCT**: Rediseño completo de las tarjetas de platos y pedidos en Kivy Language ([punto_casino/views/styles.kv](../../punto_casino/views/styles.kv)) para evitar la saturación de texto en pantallas móviles (380x720), aplicando la paleta de la Universidad Católica de Temuco (azul marino UCT `#0A3871`, azul cielo `#00A3E0`, blanco inmaculado `#FFFFFF` y fondos `#F0F7FD`).
2. **Base de Datos Relacional SQLite (Modo WAL)**: Motor de persistencia ACID transaccional local (`punto_casino.db`) configurado con *Write-Ahead Logging* para alta concurrencia y consultas 100% preparadas contra inyecciones SQL.
3. **Seguridad Criptográfica Grado Bancario**: Hashing de contraseñas con `PBKDF2-HMAC-SHA256` utilizando **600.000 iteraciones** (estándar NIST SP 800-63B y OWASP Password Storage Cheat Sheet), sales criptográficas independientes de 32 bytes y comparación en tiempo constante (`secrets.compare_digest`).

---

## 2. Tecnicismos y Mecánica de Funcionamiento

### 2.1 Arquitectura Criptográfica (`SecurityService`)
- **Algoritmo**: `hashlib.pbkdf2_hmac("sha256", password, salt, 600000)`
- **Sal Aleatoria**: `secrets.token_bytes(32)` generada por hardware.
- **Formato de Almacenamiento**: `hash_hex$salt_hex`.
- **Prevención de Ataques de Tiempo**: `secrets.compare_digest(computed_hash, stored_hash)` evita la fuga de información por micro-variaciones de tiempo en la CPU.

### 2.2 Esquema de Base de Datos Relacional (`DatabaseManager`)
```sql
CREATE TABLE IF NOT EXISTS users (
    id_usuario TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL,
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id_producto TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    category TEXT NOT NULL,
    ingredients TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS orders (
    id_pedido TEXT PRIMARY KEY,
    comanda_number INTEGER NOT NULL,
    customer_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    total INTEGER NOT NULL,
    status TEXT NOT NULL,
    pickup_qr TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES users(id_usuario)
);
```

### 2.3 Diseño Visual Responsive (Evitar Saturación de Texto)
- En un viewport angosto (380px), las cadenas largas como listas de 5 ingredientes rompían la estructura.
- **Solución implementada**:
  - `shorten: True` con `shorten_from: "right"` en el texto de ingredientes.
  - Distribución en tarjetas estilizadas (`UCTCard`) con badges compactos de categoría (*Normal*, *Ejecutivo*, etc.).
  - Separación armónica entre el título del plato, su precio destacado en azul y el botón de acción con esquinas redondeadas.

### 2.4 Pantalla de Login Institucional, UX Amigable y Seguridad Sin Jerga Técnica
- **Encabezado sin tarjeta ni efecto hover**: Título institucional directo en `MDBoxLayout` con tipografía de alto contraste (Azul UCT `#0A3871` y Celeste `#0288D1` sobre fondo limpio `#F4F8FC`).
- **Formulario Espacioso y Cómodo (Sin Textos Superpuestos)**: Tarjeta de credenciales con altura de 300dp y márgenes ergonómicos. Se eliminaron los textos de ejemplo auxiliares que colisionaban con el borde superior de la contraseña, dejando los campos de texto `MDTextField` limpios, independientes y con espacio visual armónico.
- **Eliminación Total de Atajos y Directorio**: Se eliminaron los botones de atajo rápido y el directorio de cuentas en pantalla, otorgando un aspecto minimalista, profesional y enfocado al flujo real.
- **Seguridad Institucional Amigable**: Se reemplazaron los nombres técnicos criptográficos por una insignia de confianza institucional: *"Conexión Institucional Segura • Acceso protegido por la plataforma central de la UCT"* (sin glifos emoji rotos). La protección con PBKDF2-HMAC-SHA256 y SQLite WAL continúa activa a nivel de arquitectura.
- **Eliminación de Beca Ficticia**: Se retiró el saldo artificial de $15.000 CLP de la cuenta de estudiante. Los pedidos y comandas se generan de forma libre para retiro en casino con pago en caja.

---

## 3. Pruebas y Verificación

### Comando de ejecución
```bash
./kivy_env/bin/python main.py
```

### Checklist Funcional
- [x] Título institucional sin comportamiento de tarjeta ni hover, con contraste óptimo.
- [x] Formulario de login responsive sin helper texts superpuestos ni colisiones.
- [x] Eliminación total del inicio rápido (demo) y del directorio de prueba; autenticación obligatoria.
- [x] Insignia de seguridad institucional amigable y sin glifos unicode corruptos.
- [x] Eliminación de la beca de $15.000 CLP; comandas generadas sin restricción de saldo prepagado.
- [x] La base de datos `punto_casino.db` inicializa tablas y valida contraseñas encriptadas.
- [x] Tarjetas de platos renderizan de forma limpia sin colisión ni saturación de texto.
- [x] Colores fieles a la identidad institucional UCT.

