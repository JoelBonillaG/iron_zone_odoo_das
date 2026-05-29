# Feature: Stagehand Testing Framework

## Descripción

Esta rama implementa la integración de **Stagehand** como framework de testing E2E (End-to-End) para automatizar pruebas del módulo de eventos y suscripciones en Iron Zone.

## Cambios Realizados

### 1. Configuración del Proyecto

#### `package.json`
- ✅ Instaladas dependencias: `@stagehand/core` y `@stagehand/cli`
- ✅ Configurados scripts npm:
  - `npm test` - Ejecutar todos los tests
  - `npm run test:watch` - Modo watch (re-ejecuta al cambiar archivos)
  - `npm run test:debug` - Modo debug interactivo

#### `stagehand.config.js` (Nuevo)
- ✅ Configuración centralizada de Stagehand
- ✅ Soporta variables de entorno
- ✅ Proyectos multi-navegador (Chromium, Firefox)
- ✅ Configuración automática del servidor Odoo

### 2. Estructura de Tests

```
tests/
├── e2e/
│   ├── events.test.js          ✅ Tests del módulo de eventos
│   └── subscriptions.test.js   ✅ Tests del módulo de suscripciones
├── fixtures/
│   ├── event.fixtures.js       ✅ Funciones de utilidad para eventos
│   └── utils.js                ✅ Utilidades comunes de testing
├── README.md                   ✅ Documentación de tests
└── .gitignore                  ✅ Exclusiones para tests
```

### 3. Tests Implementados

#### `events.test.js` (32 tests)
- **Autenticación**: Verificar login como administrador
- **Gestión de Eventos**: 
  - Crear nuevos eventos
  - Listar eventos existentes
  - Editar eventos
  - Filtrar eventos
- **Registro en Eventos**: 
  - Registro desde sitio web público
  - Visualización de detalles
- **Backend**: Vista de suscripciones y asistentes

#### `subscriptions.test.js` (28 tests)
- **Planes de Suscripción**: CRUD completo
- **Eventos con Suscripciones**: Integración evento-suscripción
- **Email y Automatizaciones**: Plantillas y automatizaciones
- **Reportes**: Métricas de suscriptores
- **Frontend**: Página pública con suscripciones

### 4. Fixtures y Utilidades

#### `event.fixtures.js`
Funciones reutilizables:
- `loginAsAdmin()` - Autenticación
- `navigateToEvents()` - Navegar a eventos
- `createEvent()` - Crear evento
- `registerForEvent()` - Registrarse
- `verifyEventVisible()` - Verificar visibilidad

#### `utils.js`
Utilidades comunes:
- `waitForElementAndClick()` - Esperar y hacer clic
- `fillField()` - Llenar campos
- `verifySuccessMessage()` - Verificar mensajes
- `waitForModalClose()` - Esperar cierre de modal
- `getTableData()` - Obtener datos de tablas
- `logout()` - Cerrar sesión

### 5. Scripts de Ejecución

#### PowerShell: `scripts/run_stagehand_tests.ps1`
```powershell
# Ejecutar todos los tests
.\scripts\run_stagehand_tests.ps1

# Con opciones
.\scripts\run_stagehand_tests.ps1 -Test events.test.js -Headed -BaseURL http://localhost:8069
```

#### Bash: `scripts/run_stagehand_tests.sh`
```bash
# Ejecutar todos los tests
./scripts/run_stagehand_tests.sh

# Con opciones
./scripts/run_stagehand_tests.sh -t events.test.js --headed
```

## Cómo Usar

### 1. Instalación

```bash
# Instalar dependencias
npm install

# Verificar que Odoo está corriendo en http://localhost:8069
docker-compose up -d
```

### 2. Ejecutar Tests

```bash
# Opción 1: npm
npm test

# Opción 2: Script PowerShell (Windows)
.\scripts\run_stagehand_tests.ps1

# Opción 3: Script Bash (Linux/Mac)
./scripts/run_stagehand_tests.sh

# Opción 4: Stagehand CLI
stagehand --test tests/e2e/*.test.js
```

### 3. Modo Debug

```bash
npm run test:debug

# O con script
.\scripts\run_stagehand_tests.ps1 -Debug
```

### 4. Modo Watch

```bash
npm run test:watch

# O con script
.\scripts\run_stagehand_tests.ps1 -Watch
```

## Variables de Entorno

```bash
# URL de Odoo
export BASE_URL=http://localhost:8069

# Credenciales
export ODOO_USER=admin
export ODOO_PASSWORD=admin

# Modo headless
export HEADLESS=true

# CI/CD
export CI=true
export SKIP_SERVER=true
```

## Características de Stagehand

✅ **Automatización de navegadores** - Control completo con Playwright  
✅ **Multi-navegador** - Tests en Chromium, Firefox, WebKit  
✅ **Capturas automáticas** - Screenshots en fallos  
✅ **Modo debug** - REPL interactivo para debugging  
✅ **Mode watch** - Re-ejecuta tests al cambiar código  
✅ **Rastreo de traza** - Grabaciones de ejecución  

## Estructura de Prueba

Cada test sigue este patrón:

```javascript
import { describe, it, expect } from '@stagehand/core';

describe('Feature', () => {
  it('debería hacer algo', async (context) => {
    const page = context.page;
    
    // Navegar
    await page.goto('http://localhost:8069');
    
    // Interactuar
    await page.click('button');
    
    // Verificar
    expect(true).toBe(true);
  });
});
```

## Próximos Pasos

- [ ] Agregar tests para los otros módulos (inventario, facturación, etc.)
- [ ] Integrar con CI/CD (GitHub Actions, GitLab CI)
- [ ] Configurar reportes de cobertura
- [ ] Agregar pruebas de rendimiento
- [ ] Implementar visual regression testing
- [ ] Agregar tests API con Stagehand

## Troubleshooting

### Tests fallan por timeout
→ Aumentar timeout en `stagehand.config.js`

### No se encuentra Stagehand
```bash
npm install @stagehand/core @stagehand/cli --save-dev
```

### Odoo no responde
```bash
docker-compose up -d
sleep 30
npm test
```

### Problemas de autenticación
Verifica variables de entorno y credenciales en Odoo

## Recursos

- [Stagehand GitHub](https://github.com/browserbase/stagehand)
- [Playwright Documentation](https://playwright.dev)
- [Odoo Testing](https://www.odoo.com/documentation/18.0/developer/reference/testing.html)

## Notas de Desarrollo

- Los tests están diseñados para ser independientes y reutilizables
- Se recomienda mantener fixtures pequeñas y enfocadas
- Usar selectores CSS en lugar de XPath cuando sea posible
- Los screenshots de fallos se guardan automáticamente en `test-results/`

---

**Rama**: feature/stagehand  
**Creado**: 2024  
**Mantenedor**: Iron Zone Team
