# Documentación Completa del Módulo: health_prescription_audit_v2

## 📋 Descripción General del Módulo

El módulo **health_prescription_audit_v2** es una extensión para GNU Health (integrada en Tryton) que proporciona capacidades de auditoría a nivel medicamento para líneas de prescripción. Permite auditar, aprobar, rechazar y resetear el estado de medicamentos individuales dentro de una prescripción médica.

---

## 📁 Estructura de Archivos del Módulo

```
health_prescription_audit_v2/
├── __init__.py                          # Inicialización del módulo
├── health_prescription_audit.py         # Lógica principal del módulo
├── health_prescription_audit_view.xml   # Configuración de interfaz (vistas, menús)
├── setup.py                             # Configuración de instalación
├── tryton.cfg                           # Configuración de Tryton
```

---

## 📄 Descripción Detallada de Archivos

### 1. **`__init__.py`**

**Propósito:** Archivo de inicialización del paquete Python que registra los modelos y magos (wizards) del módulo en el Pool de Tryton.

**Contenido y Bloques:**

```python
from trytond.pool import Pool
from . import health_prescription_audit

def register():
    Pool.register(
        health_prescription_audit.PrescriptionLine,
        health_prescription_audit.ExportResult,
        module='health_prescription_audit_v2', type_='model')
    Pool.register(
        health_prescription_audit.PrescriptionAuditExport,
        module='health_prescription_audit_v2', type_='wizard')
```

- **Bloque de Importaciones:** Importa `Pool` de Tryton y el módulo principal
- **Función `register()`:** Registra los componentes del módulo:
  - `PrescriptionLine`: Modelo que extiende las líneas de prescripción
  - `ExportResult`: Modelo para resultados de exportación
  - `PrescriptionAuditExport`: Wizard (asistente) para exportar a CSV

---

### 2. **`health_prescription_audit.py`**

**Propósito:** Archivo principal que contiene la lógica de auditoría, modelos de datos y funcionalidad de exportación.

#### **Clase 1: `PrescriptionLine` (Metaclase PoolMeta)**

**Propósito:** Extiende el modelo `gnuhealth.prescription.line` para agregar campos y métodos de auditoría.

##### **Campos Definidos:**

1. **`audit_state`** - Campo de Selección
   - Propósito: Almacena el estado de auditoría del medicamento
   - Valores: `pending` (Pendiente), `aprobada` (Aprobada), `rechazada` (Rechazada)
   - Características: Solo lectura, estado por defecto es 'pending'

2. **`audit_notes`** - Campo de Texto
   - Propósito: Notas sobre la decisión de auditoría
   - Características: Editable solo cuando `audit_state` es 'pending'

3. **`audit_date`** - Campo DateTime
   - Propósito: Fecha y hora cuando se auditó el medicamento
   - Características: Solo lectura, se establece automáticamente

4. **`audit_user`** - Campo Many2One (Relación con usuario)
   - Propósito: Usuario que realizó la auditoría
   - Características: Solo lectura, se establece automáticamente

5. **`patient`** - Campo Function (Campo calculado/virtual)
   - Propósito: Obtiene el paciente de la prescripción padre (solo lectura)
   - Consulta a través del método `get_prescription_context`

6. **`prescription_date`** - Campo Function (Campo calculado/virtual)
   - Propósito: Obtiene la fecha de prescripción (solo lectura)

##### **Métodos de la Clase:**

**`get_prescription_context(cls, lines, name)` - @classmethod**
- Propósito: Obtiene datos del contexto de la prescripción de forma eficiente (batch)
- Proceso:
  1. Realiza una consulta única para todas las líneas
  2. Lee los datos de la prescripción de una sola vez (optimización)
  3. Maneja excepciones si el campo no existe
- Retorna: Diccionario con los valores del campo solicitado para cada línea

**`default_audit_state()` - @staticmethod**
- Propósito: Establece el valor por defecto del campo `audit_state`
- Retorna: El valor `'pending'`

**`__setup__(cls)` - @classmethod**
- Propósito: Configura los botones del modelo y su visibilidad
- Botones configurados:
  - `approve_line`: Visible solo cuando el estado es 'pending'
  - `reject_line`: Visible solo cuando el estado es 'pending'
  - `reset_line`: Visible cuando el estado NO es 'pending'

**`approve_line(cls, lines)` - @classmethod, @ModelView.button**
- Propósito: Aprueba una o más líneas de medicamento
- Acciones:
  1. Obtiene el usuario actual
  2. Actualiza el estado a `'aprobada'`
  3. Registra la fecha y hora actual
  4. Registra el usuario auditor
  5. Registra la acción en el log

**`reject_line(cls, lines)` - @classmethod, @ModelView.button**
- Propósito: Rechaza una o más líneas de medicamento
- Acciones: Similar a `approve_line`, pero con estado `'rechazada'`

**`reset_line(cls, lines)` - @classmethod, @ModelView.button**
- Propósito: Reinicia la auditoría de líneas a estado 'pending'
- Acciones:
  1. Cambia el estado a `'pending'`
  2. Limpia la fecha de auditoría
  3. Limpia el usuario auditor

---

#### **Clase 2: `ExportResult` (ModelView)**

**Propósito:** Modelo simple que define la interfaz para mostrar el resultado de la exportación CSV.

**Campos:**

- **`csv_file`** - Campo Binary (archivo binario)
  - Propósito: Almacena el contenido del archivo CSV generado
  - **`filename`**: Atributo que especifica el nombre del archivo

- **`filename`** - Campo Char (texto)
  - Propósito: Nombre del archivo CSV
  - Características: Solo lectura

---

#### **Clase 3: `PrescriptionAuditExport` (Wizard)**

**Propósito:** Asistente que genera un archivo CSV con la auditoría de medicamentos seleccionados.

**Atributos:**

- **`__name__`**: Identificador único del wizard: `'gnuhealth.prescription.audit.export'`
- **`start_state`**: Estado inicial del wizard: `'result'`

**Estados del Wizard:**

**`result` - StateView**
- Propósito: Pantalla de resultado del wizard
- Vista asociada: `'health_prescription_audit_v2.view_audit_export_result'`
- Botón: "Cerrar" (cierra el wizard)

**Métodos:**

**`default_result(self, fields_names)` - Método**
- Propósito: Genera el contenido del CSV con los datos de auditoría
- Proceso:
  1. Obtiene las líneas de prescripción seleccionadas (o todas si ninguna está seleccionada)
  2. Crea un StringIO para contener el CSV
  3. Escribe encabezados: ID Receta, Paciente, Medicamento, Estado, Fecha, Auditor, Notas
  4. Itera sobre cada línea y:
     - Extrae información del medicamento, paciente, etc.
     - Maneja excepciones si los datos no existen
     - Traduce los estados de auditoría usando `_STATE_LABELS`
  5. Convierte el CSV a bytes UTF-8 con BOM para compatibilidad con Excel
- Retorna: Diccionario con `csv_file` (contenido) y `filename` (nombre de archivo)

**`_STATE_LABELS` - Diccionario de clase**
- Propósito: Mapeo de códigos de estado a etiquetas en español
- Valores:
  - `'pending'` → `'Pendiente'`
  - `'aprobada'` → `'Aprobada'`
  - `'rechazada'` → `'Rechazada'`

---

### 3. **`health_prescription_audit_view.xml`**

**Propósito:** Archivo de configuración de la interfaz de usuario en Tryton que define vistas, menús, permisos y reglas de acceso.

#### **Bloques Principales:**

##### **A. BLOQUE DE GRUPO (Líneas 12-15)**

```xml
<record model="res.group" id="group_prescription_auditor">
    <field name="name">Prescription Auditor v2</field>
</record>
```

**Propósito:** Define un grupo de usuarios con rol específico "Auditor de Prescripciones v2"
- Este grupo será asignado a los usuarios que pueden auditar prescripciones
- Se usa para controlar permisos a nivel de fila y campo

---

##### **B. BLOQUE DE VISTAS (Líneas 24-32)**

```xml
<record model="ir.ui.view" id="view_medication_audit_list">
    <field name="model">gnuhealth.prescription.line</field>
    <field name="name">medication_audit_list</field>
    <field name="type">tree</field>
</record>

<record model="ir.ui.view" id="view_medication_audit_form">
    <field name="model">gnuhealth.prescription.line</field>
    <field name="name">medication_audit_form</field>
    <field name="type">form</field>
</record>
```

**Propósito:** Define dos vistas para el modelo `gnuhealth.prescription.line`
- **Vista tipo "tree" (lista)**: `view_medication_audit_list`
  - Propósito: Mostrar líneas de prescripción en formato de tabla/árbol
  - Archivo de diseño: `view/medication_audit_list.xml`

- **Vista tipo "form" (formulario)**: `view_medication_audit_form`
  - Propósito: Mostrar detalles de una línea individual
  - Archivo de diseño: `view/medication_audit_form.xml`

---

##### **C. BLOQUE DE VENTANA DE ACCIÓN (Líneas 37-56)**

```xml
<record model="ir.action.act_window" id="act_medication_audit">
    <field name="name">Medication Audit</field>
    <field name="res_model">gnuhealth.prescription.line</field>
</record>

<record model="ir.action.act_window.view" id="act_medication_audit_view_list">
    <field name="sequence" eval="10"/>
    <field name="view" ref="view_medication_audit_list"/>
    <field name="act_window" ref="act_medication_audit"/>
</record>

<record model="ir.action.act_window.view" id="act_medication_audit_view_form">
    <field name="sequence" eval="20"/>
    <field name="view" ref="view_medication_audit_form"/>
    <field name="act_window" ref="act_medication_audit"/>
</record>
```

**Propósito:** Define la acción de ventana que abre la interfaz de auditoría
- **`act_medication_audit`**: Acción principal que abre el modelo de auditoría
- **`act_medication_audit_view_list`**: Asocia la vista de lista (orden 10 = aparece primero)
- **`act_medication_audit_view_form`**: Asocia la vista de formulario (orden 20 = aparece segundo)

---

##### **D. BLOQUE DE MENÚ (Líneas 61-71)**

```xml
<menuitem name="Prescription Audit"
          parent="health.gnuhealth_menu"
          id="menu_prescription_audit"
          sequence="50"
          action="act_medication_audit"/>

<record model="ir.ui.menu-res.group" id="menu_prescription_audit_group_access">
    <field name="menu" ref="menu_prescription_audit"/>
    <field name="group" ref="group_prescription_auditor"/>
</record>
```

**Propósito:** Crea una entrada de menú en la interfaz
- **`menuitem`**: Crea el menú "Prescription Audit" bajo el menú principal de GNU Health
  - `sequence="50"`: Posición en el menú (50 = después de elementos con secuencia menor)
  - `action`: Vincula a la acción `act_medication_audit`

- **Restricción de acceso al menú**: Solo visible para usuarios del grupo `group_prescription_auditor`

---

##### **E. BLOQUE DE ACCESO A MODELS (Líneas 76-92)**

```xml
<record model="ir.model.access" id="access_prescription_line_auditor">
    <field name="model" search="[('model', '=', 'gnuhealth.prescription.line')]"/>
    <field name="group" ref="group_prescription_auditor"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_delete" eval="False"/>
</record>

<record model="ir.model.access" id="access_audit_export_result_auditor">
    <field name="model" search="[('model', '=', 'gnuhealth.prescription.audit.export.result')]"/>
    <field name="group" ref="group_prescription_auditor"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_delete" eval="False"/>
</record>
```

**Propósito:** Define permisos de acceso a nivel de modelo
- **`access_prescription_line_auditor`**: Permisos para leer/escribir líneas de prescripción
  - ✅ Lectura y escritura permitidas
  - ❌ No puede crear ni eliminar líneas

- **`access_audit_export_result_auditor`**: Permisos para el resultado de exportación
  - ✅ Lectura, escritura y creación permitidas
  - ❌ No puede eliminar

---

##### **F. BLOQUE DE ACCESO A CAMPOS (Líneas 97-125)**

```xml
<record model="ir.model.field.access" id="access_audit_state_auditor">
    <field name="field" search="[('model.model', '=', 'gnuhealth.prescription.line'), ('name', '=', 'audit_state')]"/>
    <field name="group" ref="group_prescription_auditor"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
</record>

<!-- Similar para: audit_notes, audit_date, audit_user -->
```

**Propósito:** Define permisos específicos por campo
- Controla quién puede leer/escribir campos individuales
- **Campos protegidos:**
  - `audit_state`: Leer y escribir
  - `audit_notes`: Leer y escribir
  - `audit_date`: Leer y escribir
  - `audit_user`: Leer y escribir

---

##### **G. BLOQUE DE WIZARD DE EXPORTACIÓN (Líneas 130-172)**

```xml
<record model="ir.ui.view" id="view_audit_export_result">
    <field name="model">gnuhealth.prescription.audit.export.result</field>
    <field name="name">medication_audit_export</field>
    <field name="type">form</field>
</record>

<record model="ir.action.wizard" id="act_export_audit_wizard">
    <field name="name">Exportar a CSV</field>
    <field name="wiz_name">gnuhealth.prescription.audit.export</field>
</record>

<record model="ir.action.keyword" id="keyword_export_audit">
    <field name="keyword">form_action</field>
    <field name="action" ref="act_export_audit_wizard"/>
    <field name="model">gnuhealth.prescription.line,-1</field>
</record>

<menuitem name="Exportar a CSV"
          parent="menu_prescription_audit"
          id="menu_export_audit_csv"
          sequence="60"
          action="act_export_audit_wizard"/>
```

**Propósito:** Define el asistente de exportación a CSV
- **Vista de resultado**: Formulario para mostrar el archivo CSV generado
- **Acción del wizard**: Ejecuta el wizard `gnuhealth.prescription.audit.export`
- **Palabra clave**: Permite ejecutar el wizard como acción desde el formulario
- **Menú**: Crea entrada de menú "Exportar a CSV" bajo "Prescription Audit"

---

##### **H. BLOQUE DE REGLAS DE BOTONES (Líneas 177-197)**

```xml
<record model="ir.model.button" id="button_approve_line">
    <field name="name">approve_line</field>
    <field name="model" search="[('model', '=', 'gnuhealth.prescription.line')]"/>
</record>
<record model="ir.model.button.rule" id="rule_approve_line">
    <field name="button" ref="button_approve_line"/>
    <field name="group" ref="group_prescription_auditor"/>
</record>

<!-- Similar para: reject_line, reset_line -->
```

**Propósito:** Define qué botones puede ejecutar cada grupo de usuarios
- **Botón `approve_line`**: Solo grupo auditor puede aprobar
- **Botón `reject_line`**: Solo grupo auditor puede rechazar
- **Botón `reset_line`**: Solo grupo auditor puede resetear

---

### 4. **`setup.py`**

**Propósito:** Archivo de configuración de instalación del paquete Python (setuptools).

**Campos Principales:**

- **`name`**: `'gnuhealth_prescription_audit_v2'` - Nombre del paquete
- **`version`**: `'0.1'` - Versión del módulo
- **`description`**: Descripción breve del módulo
- **`author` / `author_email` / `url`**: Información de contacto
- **`packages`**: `find_packages()` - Encuentra automáticamente paquetes Python
- **`install_requires`**: Dependencias necesarias (`gnuhealth`, `trytond`)
- **`entry_points`**: Registra el módulo como componente de Tryton
- **`classifiers`**: Metadatos sobre el proyecto (licencia, estado, audience)

---

### 5. **`tryton.cfg`**

**Propósito:** Archivo de configuración específica de Tryton para el módulo.

**Contenido típico:**
- Definición de versión de Tryton soportada
- Dependencias de módulos de Tryton
- Información de configuración del módulo

---

## 🔄 Flujo de Trabajo del Módulo

```
Usuario abre "Prescription Audit"
        ↓
Ver lista/forma de líneas de prescripción
        ↓
Selecciona una línea (estado = 'pending')
        ↓
    ┌─────────────────────────┐
    │  Elige una acción:      │
    ├─────────────────────────┤
    │ 1. Aprobar (approve)    │
    │ 2. Rechazar (reject)    │
    │ 3. Resetear (reset)     │
    └─────────────────────────┘
        ↓
Sistema registra:
- Estado nuevo
- Fecha/hora
- Usuario auditor
        ↓
Exportar a CSV:
- Ejecuta wizard de exportación
- Genera archivo CSV
- Usuario descarga el archivo
```

---

## 📊 Relación entre Componentes

```
PrescriptionLine (Modelo)
    ├── Campos de auditoría (audit_state, audit_notes, etc.)
    ├── Botones (approve_line, reject_line, reset_line)
    └── Métodos de acción

ExportResult (Modelo)
    └── Contiene el archivo CSV generado

PrescriptionAuditExport (Wizard)
    ├── Lee datos de PrescriptionLine
    └── Genera ExportResult

Views (XML)
    ├── Configuran cómo se muestran los datos
    ├── Define permisos de acceso
    ├── Enable/disable funcionalidades
    └── Crea menús y botones
```

---

## 🔐 Modelo de Seguridad

| Grupo | Lectura | Escritura | Crear | Eliminar | Acciones |
|-------|---------|-----------|-------|----------|----------|
| Auditor | ✅ | ✅ | ❌ | ❌ | Aprobar, Rechazar, Resetear, Exportar |
| Otros | ❌ | ❌ | ❌ | ❌ | Sin acceso |

---

## 🚀 Características Principales

1. **Auditoría por Medicamento**: Registra estado de cada medicamento en una prescripción
2. **Tres Estados**: Pendiente, Aprobada, Rechazada
3. **Rastreo Completo**: Registra fecha, hora y usuario auditor
4. **Exportación CSV**: Genera reportes exportables a Excel
5. **Control de Acceso**: Basado en grupos de usuarios
6. **Interfaz Intuitiva**: Botones visibles según el estado actual

---

## 📝 Notas Técnicas

- **Metaclase PoolMeta**: Extiende modelo existente sin reemplazarlo
- **Optimización Batch**: El método `get_prescription_context` optimiza lecturas de BD
- **Manejo de Excepciones**: La exportación CSV maneja datos faltantes gracefully
- **UTF-8 con BOM**: El CSV incluye BOM para compatibilidad con Excel en diferentes idiomas
- **Logging**: Las acciones se registran para auditoría del sistema

---

**Versión del Documento**: 1.0  
**Fecha**: 2024  
**Licencia**: GPL-3.0-or-later
