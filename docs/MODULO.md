# Módulo health_prescription_audit_v2

## Descripción General

Este módulo extiende el modelo `gnuhealth.prescription.line` de GNU Health para agregar funcionalidad de auditoría a nivel de medicamento en recetas médicas.

Permite a los auditores revisar, aprobar o rechazar líneas individuales de medicamentos dentro de una receta, manteniendo un registro completo de las decisiones de auditoría.

## Dependencias

- `ir` (módulo base de Tryton)
- `health` (módulo base de GNU Health)
- Tryton version 4.2.0

## Estructura del Módulo

```
health_prescription_audit_v2/
├── __init__.py                    # Punto de entrada del módulo
├── health_prescription_audit.py   # Lógica principal del modelo
├── health_prescription_audit_view.xml  # Definiciones de XML (vistas, acciones, menús)
├── tryton.cfg                     # Configuración del módulo
├── setup.py                       # Configuración de setuptools
└── view/
    ├── medication_audit_list.xml  # Vista de lista (tree)
    └── medication_audit_form.xml   # Vista de formulario (form)
```
