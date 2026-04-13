# Conceptos Clave sobre Creación de Módulos Tryton

## Arquitectura de un Módulo Tryton

Un módulo Tryton es un paquete Python que extiende la funcionalidad del sistema base.

### Estructura Básica

```
mi_modulo/
├── __init__.py       # Registro del módulo
├── model.py          # Modelos de datos
├── view.xml          # Vistas y acciones
├── tryton.cfg        # Configuración
└── setup.py          # Distribución
```

## Archivo `tryton.cfg`

Define metadatos del módulo:
```ini
[tryton]
version=4.2.0
depends:
    ir
    health
xml:
    mi_vista.xml
```

## Registro de Modelos (`__init__.py`)

```python
from trytond.pool import Pool

def register():
    Pool.register(
        MiModelo,
        module='mi_modulo', type_='model')
```

## Metaclase `PoolMeta`

Los modelos que extienden otros modelos usan `PoolMeta`:

```python
from trytond.pool import PoolMeta

class MiModelo(metaclass=PoolMeta):
    __name__ = 'nombre.del.modelo'
```

## Campos (Fields)

### Tipos Comunes
- `fields.Char()`: Texto corto
- `fields.Text()`: Texto largo
- `fields.Integer()`: Entero
- `fields.Float()`: Número decimal
- `fields.Boolean()`: Booleano
- `fields.Date()`: Fecha
- `fields.DateTime()`: Fecha y hora
- `fields.Many2One()`: Relación uno a muchos
- `fields.Function()`: Campo calculado
- `fields.Selection()`: Lista de opciones

### Estados y Dependencias
```python
fields.Char('Nombre',
    states={'readonly': True},
    depends=['campo_dependiente'])
```

## Campos Función (Function Fields)

Permiten obtener datos de relaciones:

```python
campo = fields.Function(
    fields.Tipo('Descripción'),
    'getter_method')

@classmethod
def getter_method(cls, records, name):
    # Lógica para obtener el valor
    return result_dict
```

## Botones y Acciones

### Definición de Botones en `__setup__`
```python
cls._buttons.update({
    'mi_boton': {
        'invisible': Eval('estado') != 'pendiente',
    }
})
```

### Decorador `@ModelView.button`
```python
@classmethod
@ModelView.button
def mi_boton(cls, records):
    # Lógica del botón
    pass
```

## Vistas XML

### Vista Lista (Tree)
```xml
<tree>
    <field name="campo1"/>
    <field name="campo2"/>
</tree>
```

### Vista Formulario
```xml
<form>
    <group string="Título" colspan="4" col="2">
        <field name="campo1"/>
    </group>
    <button name="mi_boton"/>
</form>
```

### Elementos de Grupo
- `colspan`: Columnas que ocupa
- `col`: Número de columnas
- `string`: Etiqueta del grupo

## Menús y Acciones

```xml
<record model="ir.action.act_window" id="mi_accion">
    <field name="name">Mi Acción</field>
    <field name="res_model">mi.modelo</field>
</record>

<menuitem name="Mi Menú"
          parent="parent.menu"
          id="menu_id"
          action="mi_accion"/>
```

## Control de Acceso

### Grupos de Seguridad
```xml
<record model="res.group" id="mi_grupo">
    <field name="name">Mi Grupo</field>
</record>
```

### Permisos de Modelo
```xml
<record model="ir.model.access" id="access_mi_modelo">
    <field name="model" search="[...]"/>
    <field name="group" ref="mi_grupo"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
</record>
```

### Permisos de Campo
```xml
<record model="ir.model.field.access" id="access_campo">
    <field name="field" search="[...]"/>
    <field name="group" ref="mi_grupo"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
</record>
```

## Reglas de Botones

```xml
<record model="ir.model.button" id="button_accion">
    <field name="name">accion</field>
    <field name="model" search="[...]"/>
</record>
<record model="ir.model.button.rule" id="rule_accion">
    <field name="button" ref="button_accion"/>
    <field name="group" ref="mi_grupo"/>
</record>
```

## Transacciones y Usuario Actual

```python
from trytond.transaction import Transaction
from trytond.pool import Pool

user_id = Transaction().user
```

## Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info('Mensaje de información')
logger.warning('Mensaje de advertencia')
logger.error('Mensaje de error')
```

## Mejores Prácticas

1. **Siempre usar metaclase `PoolMeta`** al extender modelos existentes
2. ** batch-read** con `cls.read()` para eficiencia
3. **Manejar excepciones** en campos función
4. **Definir estados de campos** apropiadamente
5. **Usar valores por defecto** con métodos estáticos
6. **Registrar cambios** en `__setup__()`
7. **Documentar** campos con `help`
