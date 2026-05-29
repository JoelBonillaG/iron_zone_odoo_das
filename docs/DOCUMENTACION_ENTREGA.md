# Documentacion de entrega - Iron Zone Odoo

## Herramienta seleccionada

La herramienta seleccionada para la documentacion principal es Notion. La documentacion fue generada previamente en archivos Markdown dentro de la carpeta `docs_notion/`, para luego ser importada o copiada a Notion.

## Justificacion

Notion permite organizar la documentacion en paginas jerarquicas, incluir capturas de pantalla, tablas, bloques de codigo y enlaces. Esta herramienta es adecuada para documentar una aplicacion Odoo completa porque combina manual de usuario, documentacion tecnica, rutas internas, capturas y recomendaciones en un solo espacio navegable.

## Estructura generada

```text
docs_notion/
  IRON_ZONE.md
  01_contexto_general.md
  02_documentacion_usuario.md
  03_documentacion_tecnica.md
  04_documentacion_desarrolladores.md
  05_evidencias_visuales.md
  06_importacion_notion.md
  assets/capturas/
```

## Requisitos del taller cubiertos

| Requisito | Evidencia |
| --- | --- |
| Uso de herramienta de documentacion | Notion, con contenido generado en Markdown. |
| Indice y flujo narrativo principal | `docs_notion/IRON_ZONE.md` |
| Contexto general del sistema | `docs_notion/01_contexto_general.md` |
| Documentacion de usuario | `docs_notion/02_documentacion_usuario.md` |
| Capturas de pantalla | `docs_notion/assets/capturas/` |
| Documentacion tecnica, rutas, controladores y servicios internos | `docs_notion/03_documentacion_tecnica.md` |
| Documentacion para desarrolladores | `docs_notion/04_documentacion_desarrolladores.md`, `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` |
| Evidencias visuales | `docs_notion/05_evidencias_visuales.md` |
| Guia de importacion a Notion | `docs_notion/06_importacion_notion.md` |

## Archivos complementarios agregados

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `docs/DOCUMENTACION_ENTREGA.md`

## Nota sobre Swagger o Scalar

No se selecciono Swagger o Scalar como herramienta principal porque el proyecto no expone una API REST formal basada en OpenAPI. La aplicacion usa principalmente vistas web, modelos internos, controladores HTML, portal y procesos de negocio de Odoo. Por eso, las rutas y servicios internos se documentan dentro de Notion mediante tablas y bloques de codigo.

La documentacion de rutas incluye no solo el modulo de guias, sino tambien sitio web, tienda, eventos, portal, cuenta de usuario, suscripciones, backend administrativo, ventas, inventario, facturacion, correo, pagos y servicios XML-RPC usados por los seeds.
