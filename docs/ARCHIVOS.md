# Descripción de Archivos

## Archivos Principales

### `__init__.py`
Punto de entrada del módulo. Registra el modelo `PrescriptionLine` en el Pool de Tryton.

```python
def register():
    Pool.register(
        health_prescription_audit.PrescriptionLine,
        module='health_prescription_audit_v2', type_='model')
```

### `health_prescription_audit.py`
Contiene la clase `PrescriptionLine` que extiende `gnuhealth.prescription.line`.

#### Campos Agregados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `audit_state` | Selection | Estado de auditoría: pending, aprobada, rechazada |
| `audit_notes` | Text | Notas sobre la decisión de auditoría |
| `audit_date` | DateTime | Fecha y hora de la auditoría |
| `audit_user` | Many2One (res.user) | Usuario que realizó la auditoría |
| `patient` | Function (Many2One) | Paciente (obtenido de la prescripción padre) |
| `prescription_date` | Function (Date) | Fecha de la prescripción padre |

#### Métodos Principales

- `get_prescription_context()`: Función que obtiene datos de la prescripción padre
- `approve_line()`: Botón para aprobar la línea de medicamento
- `reject_line()`: Botón para rechazar la línea de medicamento
- `reset_line()`: Botón para resetear el estado a pendiente

### `tryton.cfg`
Archivo de configuración del módulo Tryton que define:
- Versión del módulo (4.2.0)
- Dependencias (`ir`, `health`)
- Archivos XML incluídos

### `setup.py`
Configuración de setuptools para la distribución del paquete.

## Archivos de Vistas

### `view/medication_audit_list.xml`
Vista de lista (tree) que muestra:
- `name`: Identificador de la línea
- `prescription_date`: Fecha de prescripción
- `audit_state`: Estado de auditoría

### `view/medication_audit_form.xml`
Vista de formulario con secciones:
- **Grupo Prescripción**: Datos del paciente y fecha
- **Grupo Medicamento**: Medicamento prescrito
- **Estado de Auditoría**: Campos de auditoría
- **Acciones de Auditoría**: Botones approve/reject/reset
- **Notas**: Campo audit_notes

## Archivo de Definiciones XML

### `health_prescription_audit_view.xml`
Contiene todas las definiciones XML del módulo:

- **Grupo de seguridad**: `group_prescription_auditor`
- **Vistas**: `view_medication_audit_list`, `view_medication_audit_form`
- **Acción de ventana**: `act_medication_audit`
- **Menú**: Acceso desde `health.gnuhealth_menu`
- **Accesos de modelo**: Permisos para el grupo de auditores
- **Accesos de campos**: Permisos específicos por campo
- **Botones**: Definiciones y reglas de `approve_line`, `reject_line`, `reset_line`
