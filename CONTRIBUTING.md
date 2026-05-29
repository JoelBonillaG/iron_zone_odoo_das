# Guia de contribucion - Iron Zone Odoo

## Objetivo

Este documento define reglas basicas para colaborar en el proyecto Iron Zone, desarrollado sobre Odoo 18 para la gestion de un gimnasio y centro deportivo.

## Flujo de trabajo recomendado

1. Actualizar la rama principal antes de iniciar cambios.
2. Crear una rama nueva para cada funcionalidad o correccion.
3. Realizar cambios pequenos y relacionados entre si.
4. Probar el sistema localmente con Docker.
5. Documentar cambios funcionales o tecnicos.
6. Crear un pull request para revision del equipo.

## Nombres de ramas

Usar nombres descriptivos:

```text
feature/guias-ejercicios
fix/menu-website-duplicado
docs/manual-usuario
seed/datos-prueba-guias
```

## Commits

Usar mensajes claros:

```text
feat: agregar filtros por maquina en guias
fix: evitar duplicado de menu en website
docs: documentar instalacion del proyecto
seed: actualizar datos de prueba de entrenadores
```

## Reglas antes de enviar cambios

- Verificar que Odoo levante correctamente.
- Ejecutar `bash scripts/install_apps.sh` si se modificaron manifests, vistas, seguridad o datos XML.
- Ejecutar `bash seeds/run_seeds.sh` si se actualizaron datos de prueba.
- Revisar que no se suba `.env`.
- No subir archivos temporales, cache o capturas duplicadas.
- No modificar directamente modulos nativos de Odoo.
- Preferir cambios dentro de `addons/` personalizados.

## Documentacion

Cada cambio funcional debe actualizar, cuando corresponda:

- `README.md`
- `docs/`
- `docs_notion/`
- Capturas de pantalla de evidencia.

## Pull requests

Cada pull request debe incluir:

- Resumen del cambio.
- Modulos afectados.
- Pasos de prueba.
- Capturas si cambia la interfaz.
- Riesgos o notas pendientes.

## Convencion para datos de prueba

Los seeds deben ser idempotentes siempre que sea posible:

- Si el registro existe, se actualiza.
- Si no existe, se crea.
- Se evita duplicar usuarios, productos, guias, maquinas o planes.

