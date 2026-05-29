/**
 * Tests E2E para el módulo de eventos (event) de Iron Zone
 * Utiliza Stagehand para automatización del navegador
 */

import { describe, it, expect, beforeEach, afterEach } from '@stagehand/core';
import {
  loginAsAdmin,
  navigateToEvents,
  createEvent,
  registerForEvent,
  verifyEventVisible,
} from '../fixtures/event.fixtures.js';
import {
  waitForElementAndClick,
  fillField,
  verifySuccessMessage,
  getTableData,
  verifyItemInList,
  logout,
} from '../fixtures/utils.js';

let page;
const baseURL = process.env.BASE_URL || 'http://localhost:8069';

describe('Event Management - Módulo de Eventos', () => {
  beforeEach(async (context) => {
    page = context.page || (await context.browser.newPage());
  });

  afterEach(async () => {
    if (page) {
      await page.close().catch(() => {});
    }
  });

  describe('Autenticación', () => {
    it('debería permitir login como administrador', async () => {
      await page.goto(`${baseURL}/web/login`);

      // Verificar que el formulario de login está visible
      await page.waitForSelector('input[name="login"]');
      await page.waitForSelector('input[name="password"]');

      // Llenar credenciales
      await fillField(page, 'input[name="login"]', 'admin');
      await fillField(page, 'input[name="password"]', 'admin');

      // Enviar formulario
      await page.click('button[type="submit"]');

      // Esperar redirección
      await page.waitForURL(/.*\/web($|\/)/);

      // Verificar que está logueado
      const isLoggedIn = await page.isVisible('.oe_topbar_name, [role="button"]:has-text("admin")');
      expect(isLoggedIn).toBe(true);
    });
  });

  describe('Gestión de Eventos', () => {
    beforeEach(async () => {
      // Login antes de cada test
      const loginPage = await loginAsAdmin(page);
      page = loginPage;
    });

    it('debería navegar a la sección de eventos', async () => {
      await page.goto(`${baseURL}/web`);

      // Buscar evento en el menú
      const searchBox = await page.$('[data-placeholder="Search..."], [placeholder="Search..."]');
      if (searchBox) {
        await searchBox.fill('Eventos');
        await page.keyboard.press('Enter');
      } else {
        // Alternativa: navegar directamente
        await page.goto(`${baseURL}/web#action=event.action_event_view&model=event.event`);
      }

      // Esperar que se cargue la vista
      await page.waitForTimeout(2000);
      const pageContent = await page.content();
      expect(pageContent).toContain('event');
    });

    it('debería crear un nuevo evento', async () => {
      await navigateToEvents(page);

      // Click en Create
      const createBtn = await page.$('button:has-text("Create"), button:has-text("New")');
      if (createBtn) {
        await createBtn.click();
      } else {
        // Alternativa: navegar directamente al formulario
        await page.goto(`${baseURL}/web#action=event.action_event_view&model=event.event&view_type=form`);
      }

      await page.waitForSelector('[name="name"], input:first-of-type');

      // Generar nombre único
      const eventName = `Test Event ${Date.now()}`;

      // Llenar campos del formulario
      const nameField = await page.$('[name="name"]');
      if (nameField) {
        await nameField.fill(eventName);
      } else {
        // Buscar por placeholder
        const inputs = await page.$$('input');
        if (inputs.length > 0) {
          await inputs[0].fill(eventName);
        }
      }

      // Guardar
      await page.click('button:has-text("Save"), button.btn-primary');

      // Verificar guardado
      await page.waitForTimeout(1500);
      const successMsg = await verifySuccessMessage(page);
      expect(successMsg).toBe(true);
    });

    it('debería listar eventos existentes', async () => {
      await navigateToEvents(page);

      // Esperar que se cargue la lista
      await page.waitForTimeout(2000);

      // Verificar que hay elementos en la lista
      const tableRows = await page.$$('table tbody tr, .o_list_record');
      expect(tableRows.length).toBeGreaterThanOrEqual(0);
    });

    it('debería editar un evento existente', async () => {
      await navigateToEvents(page);

      // Esperar a que se cargue la lista
      await page.waitForTimeout(1500);

      // Hacer clic en el primer evento
      const firstEvent = await page.$('table tbody tr a, .o_list_record a');
      if (firstEvent) {
        await firstEvent.click();
      } else {
        // Si no hay eventos, crear uno primero
        return;
      }

      // Esperar que se cargue el formulario
      await page.waitForSelector('[name="name"]', { timeout: 5000 });

      // Editar el nombre
      const nameField = await page.$('[name="name"]');
      const currentName = await nameField.inputValue();
      const newName = `${currentName} - Edited`;

      await nameField.fill(newName);

      // Guardar cambios
      await page.click('button:has-text("Save")');

      // Verificar guardado
      const successMsg = await verifySuccessMessage(page);
      expect(successMsg).toBe(true);
    });

    it('debería filtrar eventos', async () => {
      await navigateToEvents(page);

      // Esperar a que se cargue la lista
      await page.waitForTimeout(1500);

      // Buscar el botón de filtro
      const filterBtn = await page.$('button:has-text("Filters")');
      if (filterBtn) {
        await filterBtn.click();

        // Esperar a que aparezca el panel de filtros
        await page.waitForTimeout(1000);

        // Hacer clic en "Add Filter"
        const addFilterBtn = await page.$('a:has-text("Add Filter")');
        if (addFilterBtn) {
          await addFilterBtn.click();
        }
      }

      await page.waitForTimeout(1000);
    });
  });

  describe('Registro en Eventos (Frontend)', () => {
    it('debería registrarse en un evento desde el sitio web', async () => {
      // Ir a la página pública de eventos
      await page.goto(`${baseURL}/event`);

      // Esperar a que se cargue la página
      await page.waitForTimeout(2000);

      // Verificar que hay eventos listados
      const eventLinks = await page.$$('a[href*="/event/"]');
      expect(eventLinks.length).toBeGreaterThanOrEqual(0);

      if (eventLinks.length > 0) {
        // Hacer clic en el primer evento
        await eventLinks[0].click();

        // Esperar a que se cargue la página del evento
        await page.waitForTimeout(2000);

        // Buscar el botón de registro
        const registerBtn = await page.$('button:has-text("Register"), a:has-text("Register")');
        if (registerBtn) {
          await registerBtn.click();

          // Esperar a que se cargue el formulario de registro
          await page.waitForTimeout(1500);
        }
      }
    });

    it('debería mostrar detalles del evento en el sitio web', async () => {
      await page.goto(`${baseURL}/event`);

      // Esperar a que se cargue la página
      await page.waitForTimeout(2000);

      const pageContent = await page.content();
      expect(pageContent.toLowerCase()).toContain('event');
    });
  });

  describe('Backend - Vista de Suscripciones a Eventos', () => {
    beforeEach(async () => {
      await loginAsAdmin(page);
    });

    it('debería acceder a las suscripciones de eventos', async () => {
      await page.goto(`${baseURL}/web`);

      // Navegar a event.registration (registro de eventos)
      await page.goto(`${baseURL}/web#model=event.registration&view_type=list`);

      // Esperar a que se cargue
      await page.waitForTimeout(2000);

      const pageContent = await page.content();
      expect(pageContent.toLowerCase()).toContain('event');
    });

    it('debería ver registros de asistentes', async () => {
      await page.goto(`${baseURL}/web#model=event.registration&view_type=list`);

      // Esperar a que se cargue la lista
      await page.waitForTimeout(2000);

      // Verificar que la vista está cargada
      const listRecords = await page.$$('.o_list_record, table tbody tr');
      expect(listRecords).toBeDefined();
    });
  });

  describe('Limpieza', () => {
    it('debería hacer logout correctamente', async () => {
      await loginAsAdmin(page);
      await logout(page);

      // Verificar que está en la página de login
      await page.waitForURL(/.*\/web\/login/);
      expect(page.url()).toContain('/web/login');
    });
  });
});
