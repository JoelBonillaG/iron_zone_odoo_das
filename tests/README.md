# Testing con Stagehand en Iron Zone

Esta documentación describe cómo ejecutar y mantener los tests E2E con Stagehand para el módulo de eventos de Iron Zone.

## Requisitos

- Node.js 16+ (preferiblemente 18+)
- Docker y docker-compose ejecutándose
- Odoo 18 corriendo en `http://localhost:8069`

## Instalación

```bash
# Instalar dependencias de Node
npm install

# El script de instalación instalará automáticamente Stagehand y sus dependencias
```

## Estructura de Tests

```
tests/
├── e2e/
│   ├── events.test.js          # Tests del módulo de eventos
│   └── subscriptions.test.js   # Tests del módulo de suscripciones
├── fixtures/
│   ├── event.fixtures.js       # Fixtures para eventos
│   └── utils.js                # Utilidades comunes
└── README.md                   # Este archivo

stagehand.config.js             # Configuración de Stagehand
```

## Ejecutar Tests

### Opción 1: Desde npm

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests en modo watch (re-ejecutar al cambiar archivos)
npm run test:watch

# Ejecutar tests en modo debug (útil para development)
npm run test:debug
```

### Opción 2: Desde línea de comandos con Stagehand CLI

```bash
# Ejecutar todos los tests
stagehand --test tests/e2e/*.test.js

# Ejecutar test específico
stagehand --test tests/e2e/events.test.js

# Ejecutar con navegador visible
stagehand --test tests/e2e/events.test.js --headed

# Ejecutar con modo debug
stagehand --test tests/e2e/events.test.js --debug
```

## Variables de Entorno

Configura estas variables antes de ejecutar los tests:

```bash
# URL base de Odoo (por defecto: http://localhost:8069)
export BASE_URL=http://localhost:8069

# Usuario de Odoo (por defecto: admin)
export ODOO_USER=admin

# Contraseña de Odoo (por defecto: admin)
export ODOO_PASSWORD=admin

# Modo headless (por defecto: true, desactiva con: false)
export HEADLESS=true

# Si estás ejecutando Odoo sin Docker
export SKIP_SERVER=true

# Ejecución en CI/CD (desactiva reutilización de servidor)
export CI=true
```

## Tests Disponibles

### events.test.js
Prueba la funcionalidad principal del módulo de eventos:

- **Autenticación**: Login como administrador
- **Gestión de Eventos**: Crear, listar, editar y filtrar eventos
- **Registro en Eventos**: Registro desde el sitio web público
- **Backend**: Vista de suscripciones y asistentes

### subscriptions.test.js
Prueba la integración de suscripciones con eventos:

- **Planes de Suscripción**: CRUD de planes
- **Eventos con Suscripciones**: Crear eventos vinculados a planes
- **Email y Automatizaciones**: Envío de correos relacionados
- **Reportes**: Métricas de suscriptores
- **Frontend**: Página pública de eventos

## Debugging

### Captura de Pantallas

Los tests automáticamente capturan pantallas cuando fallan:

```bash
stagehand --test tests/e2e/events.test.js --headed
```

### Modo Debug Interactivo

```bash
stagehand --test tests/e2e/events.test.js --debug
```

Esto abre una consola REPL donde puedes interactuar directamente con la página.

### Verificar Logs

Los logs de ejecución se guardan en `test-results/` con timestamp.

## Mejores Prácticas

1. **Usar fixtures**: Reutiliza las funciones en `fixtures/` para acciones comunes
2. **Nombres descriptivos**: Los nombres de tests deben ser claros y específicos
3. **Esperas explícitas**: Usa `waitForSelector` en lugar de `waitForTimeout` cuando sea posible
4. **Limpieza**: Asegúrate de hacer logout después de tests autenticados
5. **Isolamiento**: Cada test debe ser independiente

## Agregar Nuevos Tests

### Plantilla básica

```javascript
import { describe, it, expect } from '@stagehand/core';

describe('Mi Feature', () => {
  it('debería hacer algo', async (context) => {
    const page = context.page;
    
    // Tu test aquí
    expect(true).toBe(true);
  });
});
```

### Plantilla con fixtures

```javascript
import { describe, it, expect, beforeEach } from '@stagehand/core';
import { loginAsAdmin } from '../fixtures/event.fixtures.js';

let page;

describe('Mi Feature', () => {
  beforeEach(async (context) => {
    page = context.page;
    await loginAsAdmin(page);
  });

  it('debería hacer algo después de login', async () => {
    // Tu test aquí
  });
});
```

## Troubleshooting

### "Cannot find module '@stagehand/core'"

```bash
npm install
```

### Tests fallan por timeout

Aumenta el timeout en `stagehand.config.js`:

```javascript
module.exports = {
  timeout: 60000, // Aumentado a 60 segundos
  // ...
};
```

### Odoo no está disponible

```bash
# Asegurate de que Docker está corriendo
docker-compose up -d

# Espera a que Odoo se inicie (puede tardar 30-60 segundos)
sleep 30
npm test
```

### Fallos de autenticación

Verifica las credenciales en `stagehand.config.js` o variables de entorno:

```bash
export ODOO_USER=admin
export ODOO_PASSWORD=admin
npm test
```

## Integración Continua

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          
      odoo:
        image: odoo:18
        ports:
          - 8069:8069
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - run: npm install
      - run: npm test
        env:
          BASE_URL: http://localhost:8069
          CI: true
```

## Recursos

- [Documentación de Stagehand](https://github.com/browserbase/stagehand)
- [Documentación de Playwright](https://playwright.dev)
- [Odoo Testing Guide](https://www.odoo.com/documentation/18.0/developer/reference/testing.html)

## Contacto y Soporte

Para issues con los tests, abre un issue en el repositorio con:
- Comando exacto que ejecutaste
- Output de error completo
- Versión de Node.js y navegadores
- Versión de Odoo
