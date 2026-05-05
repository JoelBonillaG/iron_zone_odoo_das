# Módulo Training Plans - Interfaz de Empleados

## Descripción General

El módulo `training_plans` proporciona una interfaz dedicada para que los **empleados (instructores)** de Iron Zone puedan:
- Ver **solo los eventos asignados** para ellos
- Gestionar detalles de sus eventos
- Ver la lista de participantes registrados
- Actualizar el estado de eventos

## Cómo Funciona

### 1. **Filtrado de Eventos por Usuario**

Cuando un empleado inicia sesión en Odoo, la interfaz automaticamente filtra los eventos usando:

```python
# Domain: solo eventos donde user_id == usuario_actual
[("user_id", "=", uid)]
```

Esto se aplica en:
- **Acción**: `action_event_employee_view` 
- **Regla de Seguridad**: `ir_rule_event_employee_own` (nivel de base de datos)

### 2. **Puntos de Acceso**

Los empleados pueden acceder a "Mis Eventos" desde el menú:

```
Recursos Humanos → Mis Eventos
```

Allí verán múltiples vistas:

#### **Kanban (por defecto)**
- Columnas por etapa: Nuevo, Reservado, Anunciado
- Tarjetas mostrando: nombre, fecha, registros/capacidad
- Arrastrar eventos entre etapas

#### **Lista (Tree)**
- Tabla con: nombre, fechas, capacidad, etapa, estado
- Orden filtrable y editable directamente

#### **Formulario (Detalle)**
- Vista completa con:
  - Nombre y descripción
  - Fechas de inicio/fin (datetime)
  - Capacidad (máximo y disponible)
  - Etapa y estado
  - Botones: Confirmar, Completar, Cancelar
  - Número de registrados
  - Información de la compañía

#### **Calendario**
- Vista cronológica
- Coloreado por etapa
- Muestra nombre y registrados

### 3. **Gestión de Registros**

Los empleados pueden ver quién se registró en sus eventos:

```
Vista de Evento → Botón "Registros" → Lista de participantes
```

Información disponible:
- Nombre del participante
- Email y teléfono
- Fecha de registro
- Estado del registro

### 4. **Reglas de Seguridad**

Se aplican dos niveles de control:

#### **A nivel de Base de Datos** (`ir.rule`)
```
Regla: "Empleado ve solo sus eventos"
Grupo: HR User
Domain: [("user_id", "=", user.id)]
Permisos: Lectura ✓, Escritura ✓, Crear ✗, Eliminar ✗
```

Esto garantiza que **incluso en reportes o API** un empleado no pueda acceder a eventos de otros.

#### **A nivel de Vista** (XML domain)
```xml
<field name="domain">[("user_id", "=", uid)]</field>
```

### 5. **Flujo Típico de un Entrenador**

1. **Inicia sesión** en Odoo con su usuario (creado automáticamente en `06_event_classes.py`)
2. **Va a Recursos Humanos → Mis Eventos**
3. **Ve en Kanban** todos sus eventos organizados por etapa
4. **Hace clic en un evento** para ver detalles completos
5. **Consulta participantes** registrados
6. **Actualiza el estado** (Confirmar → Completar)
7. **Puede mover eventos** entre etapas (drag & drop en Kanban)

## Configuración Requerida

### **Paso 1: Crear usuarios para empleados**

El seed `06_event_classes.py` automáticamente:
- Busca empleados en `hr.employee`
- Crea un usuario (`res.users`) si no existe
- Vincula el usuario al empleado
- Asigna el usuario al evento como `user_id`

### **Paso 2: Asignar grupo de HR**

Asegúrate que cada empleado tenga el grupo **"HR User"**:

```
Odoo → Configuración → Usuarios
→ Selecciona empleado
→ Pestaña "Acceso"
→ Marca "HR User"
```

O automáticamente si usas seeds, el usuario obtiene el grupo al ser creado.

### **Paso 3: Instalar el módulo**

```bash
# Desde Odoo UI
Aplicaciones → Training Plans → Instalar

# O desde terminal
bash scripts/install_apps.sh
```

## Tabla de Modelos y Accesos

| Modelo | Descripción | Permiso |
|--------|-------------|---------|
| `event.event` | Evento/Clase | Lectura ✓, Escritura ✓ |
| `event.registration` | Registro a evento | Lectura ✓, Escritura ✓ |
| `event.stage` | Etapa (Nuevo, Reservado, Anunciado) | Lectura ✓ |

## Ejemplo de Vista en Kanban

```
┌─ NUEVO ────────────────────┐
│                            │
│ ┌──────────────────────┐   │
│ │ CrossFit AM          │   │
│ │ Fecha: 2025-05-15    │   │
│ │ Registros: 18/20     │   │
│ └──────────────────────┘   │
│                            │
│ ┌──────────────────────┐   │
│ │ HIIT Entrenamiento   │   │
│ │ Fecha: 2025-05-16    │   │
│ │ Registros: 15/20     │   │
│ └──────────────────────┘   │
└────────────────────────────┘

┌─ RESERVADO ────────────────┐
│                            │
│ ┌──────────────────────┐   │
│ │ Yoga Avanzado        │   │
│ │ Fecha: 2025-05-17    │   │
│ │ Registros: 12/15     │   │
│ └──────────────────────┘   │
└────────────────────────────┘

┌─ ANUNCIADO ────────────────┐
│                            │
│ ┌──────────────────────┐   │
│ │ Musculación Personal │   │
│ │ Fecha: 2025-05-18    │   │
│ │ Registros: 7/8       │   │
│ └──────────────────────┘   │
└────────────────────────────┘
```

## Campos del Evento

Cada evento tiene:

- **name** (Nombre): CrossFit AM, Yoga Principiantes, etc.
- **date_begin** (Inicio): Fecha y hora del evento
- **date_end** (Fin): Fecha y hora de cierre
- **user_id** (Instructor): Usuario del empleado asignado
- **seats_max** (Capacidad máxima): 20, 15, etc.
- **seats_available** (Disponibles): Actualiza automáticamente
- **stage_id** (Etapa): Nuevo / Reservado / Anunciado
- **state** (Estado): draft / running / done / cancel
- **description** (Descripción): Detalles adicionales

## Permisos por Rol

| Rol | Mis Eventos | Crear | Editar | Eliminar |
|-----|-------------|-------|--------|----------|
| Entrenador (HR User) | ✓ Solo propios | ✗ | ✓ | ✗ |
| Administrador | ✓ Todos | ✓ | ✓ | ✓ |
| Recepcionista (HR User) | ✓ Solo propios | ✗ | ✓ | ✗ |

## Troubleshooting

### **"No tengo acceso a Mis Eventos"**
- Verifica que tu usuario tiene el grupo "HR User"
- Verifica que hay un evento con `user_id` = tu usuario

### **"Veo todos los eventos, no solo los míos"**
- Posiblemente eres Administrador (acceso global)
- Como admin, puedes usar el filtro manual o ir a: Recursos Humanos → Eventos (vista admin)

### **"Quiero ver también los eventos de otros"**
- Solicita al administrador cambiar tu grupo a administrador
- O usa Recursos Humanos → Eventos (requiere permisos adicionales)

## Extensiones Futuras

Podrías agregar:
- **Portal para empleados**: Vista web pública (similar a website)
- **Notificaciones**: Alertas cuando hay nuevos registros
- **Reportes**: Asistencia, ingresos, participación
- **Chat en vivo**: Comunicación durante clases
- **QR check-in**: Validar asistencia con móvil
