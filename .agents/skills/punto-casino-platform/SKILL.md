---
name: punto-casino-platform
description: >-
  Use when designing, implementing, debugging, reviewing, or testing Python and KivyMD code for the Punto
  Casino Universidad platform, strictly aligning with docs/requerimientos.md and docs/plan_expansion_universidades_chile/README.md,
  enforcing enterprise Material Design 3 guidelines, a rigorous Human-in-the-Loop (HITL) verification protocol,
  OWASP Mobile security standards, and per-feature technical documentation conforming to docs/TEMPLATE_FEATURE.md.
---

# Punto Casino Platform Engineering Skill (Enterprise Standard)

This skill provides the comprehensive engineering blueprint, domain rules, architectural standards, and operational procedures for building the **Punto Casino Universidad** platform — a mobile ordering, reservation, and cashier pickup solution designed for Chilean higher education institutions (universities, professional institutes, and technical training centers) using **Python 3.10+** and **KivyMD 2.0**, based on [`docs/requerimientos.md`](file:///home/renato/Dev/DesarrolloMovil/docs/requerimientos.md) and [`docs/plan_expansion_universidades_chile/README.md`](file:///home/renato/Dev/DesarrolloMovil/docs/plan_expansion_universidades_chile/README.md).

---

## 1. Enterprise Domain Overview & Requirements Matrix

The platform eliminates severe cafeteria crowding, long queues, and cashier reconciliation errors by orchestrating a synchronized, multi-role mobile pipeline between students, guests, kitchen staff, cashiers, and store managers.

### 1.1 User Roles & Permissions Matrix
| Role | Identifier | Permissions & System Capabilities | Chilean University Scope |
| :--- | :--- | :--- | :--- |
| **Client** | `client` | Account registration, browse catalog, place orders, make payments, receive pickup QR, view personal order history | Authenticated student, faculty, or staff |
| **Guest** | `guest` | Browse menu, immediate cart ordering with upfront payment checkout, no account required | Campus visitor or non-registered student |
| **Cashier** | `cashier` | Live comanda queue reception, accept/confirm or reject orders, toggle item stock, process meson charge | Cafeteria operator |
| **Admin** | `admin` | Full cashier capabilities, catalog and pricing management, special discount / offer activation, executive accounting KPI charts, order history audit | Cafeteria manager |
| **SuperAdmin** | `superadmin` | Multi-tenant university administration, campus and concession management, identity federation configs | Platform SaaS administrator |

### 1.2 Core Data Entities & Chilean Context
- **`Product`**:
  - `id_producto`: str (e.g., `"EMPA-01"`, `"MENU-010"`) — auto-assigned or managed by catalog.
  - `name`: str (e.g., `"Empanada de Pino"`, `"Menú Ejecutivo"`)
  - `category`: str (e.g., `"Menú Normal"`, `"Menú Ejecutivo"`, `"Menú Hipocalórico"`, `"Comidas Rápidas"`, `"Bebidas"`)
  - `price`: int (CLP currency, Chilean pesos rounded without decimals as per SII rules)
  - `stock`: int (available inventory count)
  - `is_active`: bool (can be toggled by cashier/admin)
  - `is_offer`: bool (special discount / promotional pricing)
  - `offer_label`: Optional[str] (e.g., `"30% OFF"`, `"Promo Alumnos"`, `"Por Vencer"`)
- **`Order`**:
  - `id_pedido`: str (unique UUID or transaction ID)
  - `comanda_number`: int (human-friendly daily queue number, e.g., `#101`, `#102`)
  - `customer_name`: str
  - `customer_role`: str (e.g., `"Estudiante"`, `"Docente"`, `"Funcionario"`, `"Invitado"`)
  - `items`: List of order line items (`id_producto`, `name`, `quantity`, `unit_price`, `subtotal`)
  - `total`: int (CLP)
  - `status`: Enum (`PENDING`, `CONFIRMED`, `REJECTED`, `READY`, `DELIVERED`, `CANCELLED`)
  - `pickup_qr`: Optional[str] (encoded payload for pickup validation)
  - `created_at`: datetime
- **`User`**:
  - `id_usuario`: str (UUID)
  - `rut`: Optional[str] (Chilean national ID formatted as `XX.XXX.XXX-X` with valid modulo 11)
  - `name`: str
  - `email`: str (institutional email e.g. `@uct.cl`, `@udec.cl`, `@uchile.cl`)
  - `tenant_id`: str (university identifier e.g., `"uct"`, `"udec"`, `"ufro"`)
  - `role`: UserRole Enum (`CLIENT`, `CASHIER`, `ADMIN`, `GUEST`)

---

## 2. Material Design 3 (M3) & KivyMD 2.0 Engineering Guidelines

To guarantee a modern, executive user experience that meets commercial B2B standards:

### 2.1 Viewport & Responsive Bounds
- **Standard Resolution**: 380 x 720 dp (standard modern Android/iOS smartphone viewport).
- **Minimum Supported**: 360 x 640 dp.
- Layouts must adapt gracefully using `size_hint_x`, `size_hint_y=None`, `minimum_height`, and `ScrollView` wrappers to avoid rendering overflows.

### 2.2 Navigation Bar Architecture (Full Touch Surface & Zero Switch Appearance)
- **Mandatory Full-Surface Touch Capture**: Never embed an inner `MDCard` inside navigation items (causes touch events to be intercepted by the card, forcing users to click only the label, and produces an off-center toggle switch illusion).
- Use `M3NavItem` (`create_nav_item(text, icon, on_release)`):
  - **Full-Tab Click Area**: Intercepts `on_touch_down` and `on_touch_up` using `self.collide_point(*touch.pos)`, ensuring the entire tab height and width responds instantly to finger taps.
  - **Top Accent Indicator Line**: A sleek 3dp top accent bar (`#0A3871` when active, transparent when inactive) replaces bulky pill shapes.
  - **Centered Icon & Label**: 24dp `MDIcon` vertically centered with complete unabbreviated `MDLabel` below.
  - **Color States**: Active uses UCT Navy (`#0A3871`) with bold typography; inactive uses Slate Gray (`#64748B`).

### 2.3 Screen Hierarchy & Zero-Shadow Outlined Card Standard
1. **Fixed Top View Descriptions**:
   - In every screen view (`AdminScreen`, `CatalogScreen`, `CashierScreen`, `ReservationsScreen`), the view description / status label must remain permanently anchored at the very top of the screen layout (directly beneath the title or campus banner), never submerged within scrollable containers or displaced below tab bars.
2. **Zero-Shadow Outlined Cards (Software OpenGL Resilience)**:
   - Never use `style="elevated"` with `elevation > 0` (causes opaque black shadow polygon artifacts under Linux Mesa / SDL2 software rendering).
   - Always enforce `style="outlined"` with `elevation=0`, `line_color=[0.88, 0.92, 0.96, 1]` (`#DFEAF2`), and `theme_bg_color="Custom"` with crisp white background `[1, 1, 1, 1]`.
3. **Unified Select Cards (`cat_select_card`)**:
   - Never place an `MDTextField` and an `MDButton` side-by-side for dropdowns (causes height, radius, and baseline misalignment).
   - Use an outlined `MDCard` (height 54dp) containing the category icon (`tag-outline`), descriptive floating caption, bold selected value, and chevron dropdown icon (`menu-down`). Clicking anywhere on the card opens the interactive selection modal.
4. **Institutional Metadata Badges (`id_badge`)**:
   - Auto-generated system IDs (e.g., `MENU-010`) must be displayed as a clean metadata pill card with a barcode icon (`barcode-scan`), rather than a disabled editable text field.
5. **KivyMD 2.0 Button Sizing**:
   - When supplying `size_hint` or explicit dimensions to `MDButton`, always pass `theme_width="Custom"` and `theme_height="Custom"`. Otherwise, KivyMD 2.0 internal KV rules will force `size_hint_x: None`.

### 2.4 Performance & UI Thread Decoupling
- **Never block the main UI thread**: Heavy I/O, SQLite bulk writes, or network requests must run in background threads.
- UI mutations must be dispatched via `from kivy.clock import Clock; Clock.schedule_once(callback)`.

---

## 3. Security, Persistence & OWASP Mobile Compliance

1. **SQLite 3 WAL Mode**:
   - Use Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) for high-concurrency read/write operations.
   - Always enforce foreign keys: `PRAGMA foreign_keys = ON;`.
2. **Parameterized Queries**:
   - Zero string interpolation in SQL. Every query must use parameterized placeholders (`?`, params tuple).
3. **Authentication & Session**:
   - Password hashes must use PBKDF2/bcrypt with unique per-user salts.
   - Clear session state on logout; sanitize all input fields against XSS/injection.

---

## 4. Mandatory Human-in-the-Loop (HITL) Verification Protocol

**Every single code change, architectural refinement, or system action must pass through the Human-in-the-Loop checkpoint before application**.

### 4.1 The Standard HITL Checkpoint Template
When proposing changes, format the proposal using the following structure:

```markdown
### 🛡️ Human-in-the-Loop (HITL) Code Verification Checkpoint

#### 1. Target Metadata
- **Target File**: `path/to/module.py`
- **Action**: `[NEW]` | `[MODIFY]` | `[DELETE]`
- **Layer**: `Presentation (KivyMD)` | `Domain / Service` | `Data / Repository` | `Security / Config`
- **Requirement Reference**: `docs/requerimientos.md` (Section X.X) & `docs/plan_expansion_universidades_chile/README.md`

#### 2. Architectural Rationale & Impact
- **Why**: Explains why this specific solution satisfies the functional requirement.
- **Impact**: Details dependencies, potential side effects, state interactions, and UI responsiveness.

#### 3. Proposed Code / Diff
```python
# Full, clean, type-annotated code snippet or precise unified diff
```

#### 4. Human Verification Checklist
- [ ] **Requirements Compliance**: Fulfills the domain criteria in `docs/requerimientos.md`.
- [ ] **Typings & Docstrings**: Complete Python type hints and Google-style docstrings.
- [ ] **Material Design 3 Ergonomics**: Zero text clipping, touch targets >= 48dp, unified select components.
- [ ] **Safe Execution & Threading**: No long-running tasks on the Kivy UI loop; dispatches via `Clock.schedule_once`.
- [ ] **Security & OWASP**: Parameterized queries, role access enforced, no sensitive data exposed.
- [ ] **Feature Documentation**: Specification created/updated under `docs/<feature_name>/README.md` adhering to `docs/TEMPLATE_FEATURE.md`.

#### 5. Verification Commands
```bash
./kivy_env/bin/python -m unittest discover -s tests -p "test_*.py"
./kivy_env/bin/python main.py
```
```

---

## 5. Mandatory Feature Documentation Protocol (`docs/<feature_name>/`)

Every feature must maintain comprehensive technical documentation inside `docs/<feature_name>/README.md`, strictly following the structure established in [`docs/TEMPLATE_FEATURE.md`](file:///home/renato/Dev/DesarrolloMovil/docs/TEMPLATE_FEATURE.md):

```text
docs/
├── requerimientos.md                          # Foundational specifications
├── TEMPLATE_FEATURE.md                        # Master RFC / Technical Feature Template
├── plan_expansion_universidades_chile/        # Multi-university Chilean SaaS expansion plan
└── <feature_name>/                            # e.g., docs/ui_ux_m3_nav_and_admin_form/
    └── README.md                              # Complete specification adhering to TEMPLATE_FEATURE.md
```

---

## 6. Git Discipline & Safety Guidelines

In strict accordance with Section 7 of [`docs/requerimientos.md`](file:///home/renato/Dev/DesarrolloMovil/docs/requerimientos.md):
- **Branch Target**: Work on feature branches or `develop`. Never push broken states directly to `main`.
- **Commit Messages**: Conventional commits format (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `perf:`).
- **Pristine Environment**: Keep `.gitignore` updated to exclude `kivy_env/`, `*.pyc`, `__pycache__/`, `.buildozer/`, and `.DS_Store`.
