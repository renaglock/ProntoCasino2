# Plantilla Estándar de Especificación Técnica: Estandarización de Colores de Herramientas del Administrador y Títulos de Categorías

```yaml
id_feature: "PC-FEAT-021"
nombre: "Estandarización de Colores para Herramientas del Administrador y Títulos de Categorías"
version: "1.0.0"
fecha: "2026-11-02"
estado: "Implementada"
autor: "Antigravity Punto Casino Principal Architect"
aprobador_hitl: "Operador / Arquitecto Líder"
impacto: "Menor (UI/UX y Coherencia Institucional M3)"
referencia_requerimientos: "docs/requerimientos.md (Sección 1.1, 1.2, 2.2, 5.1)"
referencia_expansion_saas: "docs/plan_expansion_universidades_chile/README.md (Hito UI M3)"
```

---

## 1. Resumen Ejecutivo y Valor de Negocio

### 1.1 Declaración del Problema
Previamente, la plataforma presentaba dispersión cromática y falta de uniformidad visual en dos puntos neurálgicos:
1. **Herramientas del Administrador**: Las tarjetas de analítica contable y filtros de auditoría utilizaban bordes y colores arbitrarios (ej. borde azul translúcido en resumen contable frente a bordes gris suave en el resto de tarjetas; colores púrpuras `#7C3AED` e inconsistencias de badges en ranking).
2. **Títulos de Categorías de Platos**:
   - En el catálogo de usuario (`CatalogScreen`), las tarjetas de platos renderizaban el nombre de la categoría como texto sin contenedor (*raw label*), mientras que en administración (`AdminScreen`) se utilizaba un componente de píldora estilizado (`create_category_pill`).
   - Las pestañas de filtrado de categoría no reflejaban visualmente el color institucional de la categoría al estar activas.
   - No existía una cabecera (*category title header*) estandarizada que introdujera de manera elegante la sección de platos en el catálogo ni en la vista administrativa.
   - En el selector de categorías del formulario administrativo, el icono y el texto no adoptaban el color ni el icono distintivo de la categoría seleccionada.

### 1.2 Valor Aportado y Métrica de Éxito
- **Coherencia Visual al 100%**: Unificación estricta bajo los lineamientos corporativos UCT y Material Design 3.
- **Dimensionamiento Proporcional y Centrado Óptico**: La caja (`MDCard`) de la píldora de categoría ahora calcula su ancho (`width`) de forma dinámica y estrictamente proporcional a la longitud del texto renderizado (`texture_size[0] + padding`), eliminando espacios vacíos desproporcionados a la derecha y asegurando un centrado perfecto del texto horizontal y verticalmente.
- **Identificación Instantánea por Color**: Reducción de la carga cognitiva de estudiantes, cajeros y administradores al asociar cada categoría de menú (Normal, Ejecutivo, Hipocalórico, Vegetariano, Rápidas, Bebidas, Ofertas) a su paleta canónica.
- **Resiliencia de Renderizado**: Tarjetas con estilo `outlined` y elevación 0 (`elevation=0`), garantizando cero artefactos poligonales en entornos OpenGL por software.

---

## 2. Especificación Técnica y Arquitectura de Software

### 2.1 Módulos Involucrados

```text
punto_casino/
├── core/
│   └── config.py                  # CATEGORY_PALETTE expandida y ADMIN_TOOLS_PALETTE canónica
├── views/
│   ├── components/
│   │   └── ui_elements.py         # Componente create_category_title_header() y píldoras
│   └── screens/
│       ├── admin_screen.py        # Herramientas contables, ranking, filtros y picker sincronizados
│       └── catalog_screen.py      # Píldoras estandarizadas, tabs coloreadas y cabecera de categoría
└── tests/
    └── test_domain.py             # Pruebas de coherencia de paletas y asilamiento de repositorios
```

### 2.2 Paleta Estandarizada de Categorías (`CATEGORY_PALETTE`)

| Categoría | Hex | Color Institucional | Icono Vectorial |
| :--- | :--- | :--- | :--- |
| **Menú Normal** | `#0A3871` | Azul Marino UCT | `food` |
| **Menú Ejecutivo** | `#0288D1` | Azul Cielo Brillante | `star` |
| **Menú Hipocalórico** | `#16A34A` | Verde Esmeralda | `leaf` |
| **Menú Vegetariano** | `#059669` | Verde Bosque | `sprout` |
| **Comidas Rápidas** | `#D97706` | Ámbar Cálido | `hamburger` |
| **Bebidas** | `#0D9488` | Turquesa / Teal | `cup` |
| **Postres y Snacks** | `#9333EA` | Púrpura | `cake-variant` |
| **Ofertas** | `#2EC76E` | Verde Lima Fresco | `sale` |
| **Todos** | `#0A3871` | Azul Marino UCT | `silverware-fork-knife` |

### 2.3 Paleta Estandarizada de Herramientas de Administración (`ADMIN_TOOLS_PALETTE`)

- **Bordes y Superficies**: Bordes idénticos `[0.88, 0.92, 0.96, 1.0]` (`#DFEAF2`) en todas las tarjetas de herramientas.
- **Métricas KPI**:
  - Recaudación Neta: `#10B981` (Verde Éxito)
  - Ticket Promedio: `#0288D1` (Azul UCT)
  - Tasa de Despacho: `#10B981`
  - Unidades Despachadas: `#0A3871`
  - Mediana (NumPy): `#0288D1`
  - Desviación Estándar (NumPy): `#D97706`
  - perf_counter() I/O: `#0D9488`
- **Balance Operativo**: Entregadas (`#10B981`), En Cocina (`#D97706`), Canceladas (`#DC2626`).
- **Chips de Auditoría**:
  - `Todos`: Azul Marino (`#0A3871`)
  - `Entregados`: Verde Esmeralda (`#10B981`)
  - `Cocina`: Ámbar (`#D97706`)
  - `Cancelados`: Carmesí (`#DC2626`)
- **Ranking Top Platos**: #1 Oro/Ámbar (`#D97706`), #2 Plata/Pizarra (`#64748B`), #3 Bronce/Azul (`#0A3871`), #4+ Muted (`#94A3B8`).

---

## 3. Pruebas y Verificación

### 3.1 Comandos de Ejecución
```bash
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile main.py punto_casino/views/screens/*.py
```

### 3.2 Resultados
- **13/13 pruebas unitarias aprobadas**.
- **0 errores de compilación o importación**.

