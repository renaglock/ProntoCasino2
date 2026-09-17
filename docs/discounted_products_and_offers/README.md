# Feature: Productos por Vencer a Precio Rebajado y Apartado de Ofertas

- **Fecha**: 2026-09-17
- **Estado**: En Desarrollo / Revisión HITL
- **Autor / Agente**: Antigravity Punto Casino Engineer
- **Referencia Requerimientos**: docs/requerimientos.md (Secciones 1.1, 4, 5 y 6)

---

## 1. Descripción y Objetivo

Permitir al Administrador del casino marcar o crear platos con fecha de consumo próximo (*"Por vencer"*) a un precio rebajado especial contra el desperdicio de comida (*Zero Waste Cafeteria*), y habilitar un apartado de **"Ofertas"** de alta visibilidad para Estudiantes e Invitados en el catálogo, mostrando el precio original tachado, el precio oferta con descuento y el distintivo de ahorro.

---

## 2. Tecnicismos y Arquitectura

### 2.1 Módulos y Capas Afectadas

1. **Modelo de Dominio (`punto_casino/models/product.py`)**:
   - Campos extendidos en `Product`:
     - `is_offer: bool = False`: Indica si el plato está en liquidación.
     - `original_price: Optional[int] = None`: Precio normal anterior.
     - `offer_label: str = ""`: Motivo (ej: *"Consumo antes de las 16:00"*, *"50% Descuento"*).

2. **Repositorio de Productos (`punto_casino/repositories/product_repository.py`)**:
   - `get_offers() -> List[Product]`: Retorna exclusivamente platos en oferta activos con stock.
   - `set_offer(product_id: str, offer_price: int, offer_label: str) -> bool`.

3. **Panel de Administración (`punto_casino/views/screens/admin_screen.py`)**:
   - Formulario de creación/edición con casilla *"Marcar como Oferta / Por Vencer"*, campo de precio rebajado y etiqueta de vencimiento.
   - Badge distintivo *"🔥 Oferta"* en la lista de gestión.

4. **Catálogo de Clientes (`punto_casino/views/screens/catalog_screen.py`)**:
   - Nueva categoría/pestaña destacada **"🔥 Ofertas"**.
   - Banner de liquidación en la parte superior del menú.
   - Tarjetas con visualización de precio anterior tachado (`[s]$4.800[/s]`) y precio rebajado en rojo/naranja de oferta (`$2.500`).

---

## 3. Casos Borde y Manejo de Errores

1. **Stock en Cero**: Los productos por vencer agotados muestran el badge *"Agotado"* y se deshabilitan para compra inmediata.
2. **Precio de Oferta Inválido**: Se valida que el precio con descuento sea estrictamente mayor a 0 y menor al precio original.
3. **Cancelación de Oferta**: Si el cliente cancela un pedido con plato en oferta, el stock regresa al inventario de oferta.

---

## 4. Pruebas y Verificación

```powershell
.\kivy_env\Scripts\python.exe main.py
```

