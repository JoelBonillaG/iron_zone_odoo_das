# Politica de seguridad - Iron Zone Odoo

## Alcance

Este proyecto es academico y se ejecuta en ambiente local o de pruebas. Aun asi, se documentan practicas basicas de seguridad para proteger credenciales, datos de prueba y configuraciones sensibles.

## Credenciales

- No subir el archivo `.env` al repositorio.
- Usar `.env.example` como plantilla.
- No publicar claves reales de SMTP, Stripe u otros servicios.
- Usar credenciales ficticias o de sandbox para demostraciones.

## Usuarios de prueba

Los usuarios incluidos en seeds son de uso academico. No deben reutilizarse en entornos productivos.

Ejemplos:

```text
admin / admin
carlos.mendez@ironzone.ec / admin123
pruebasjos04@gmail.com / admin123
```

## Reporte de problemas

Si se detecta un problema de seguridad:

1. Registrar el hallazgo.
2. Indicar modulo afectado.
3. Describir pasos para reproducirlo.
4. Proponer recomendacion de correccion.
5. Notificar al equipo antes de publicarlo.

## Recomendaciones

- Separar usuarios por rol.
- No compartir credenciales personales.
- Revisar permisos `ir.model.access.csv` e `ir.rule`.
- No ejecutar seeds con usuarios sin permisos suficientes.
- Mantener integraciones de pago en modo prueba.

