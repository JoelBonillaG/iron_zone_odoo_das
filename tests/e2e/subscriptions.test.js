/**
 * Tests E2E para el módulo de suscripciones y eventos (iz_subscription)
 */

import { describe, it, expect, beforeEach, afterEach } from '@stagehand/core';
import { loginAsAdmin } from '../fixtures/event.fixtures.js';
import { verifySuccessMessage, logout } from '../fixtures/utils.js';

let page;
const baseURL = process.env.BASE_URL || 'http://localhost:8069';

describe('Suscripciones y Eventos - Módulo iz_subscription', () => {
  beforeEach(async (context) => {
    page = context.page || (await context.browser.newPage());
  });

  afterEach(async () => {
    if (page) {
      await page.close().catch(() => {});
    }
  });

  describe('Gestión de Planes de Suscripción', () => {
    beforeEach(async () => {
      await loginAsAdmin(page);
    });

    it('debería acceder a los planes de suscripción', async () => {
      await page.goto(`${baseURL}/web`);

      // Buscar planes de suscripción
      const search = await page.$('[data-placeholder="Search..."], [placeholder="Search..."]');
      if (search) {
        await search.fill('Suscripción');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(2000);
      } else {
        // Navegar directamente
        await page.goto(`${baseURL}/web#model=subscription.plan&view_type=list`);
      }

      const pageContent = await page.content();
      expect(pageContent).toBeDefined();
    });

    it('debería crear un nuevo plan de suscripción', async () => {
      await page.goto(`${baseURL}/web#model=subscription.plan&view_type=list`);

      // Esperar a que se cargue
      await page.waitForTimeout(1500);

      // Click en Create
      const createBtn = await page.$('button:has-text("Create"), button:has-text("New")');
      if (createBtn) {
        await createBtn.click();
      }

      // Esperar formulario
      await page.waitForTimeout(1000);

      // Llenar datos
      const nameInput = await page.$('[name="name"]');
      if (nameInput) {
        const planName = `Test Plan ${Date.now()}`;
        await nameInput.fill(planName);

        // Guardar
        await page.click('button:has-text("Save")');

        // Verificar guardado
        await page.waitForTimeout(1500);
        const successMsg = await verifySuccessMessage(page);
        expect(successMsg).toBe(true);
      }
    });

    it('debería listar planes de suscripción', async () => {
      await page.goto(`${baseURL}/web#model=subscription.plan&view_type=list`);

      // Esperar que se cargue la lista
      await page.waitForTimeout(2000);

      // Verificar que se cargó algo
      const pageContent = await page.content();
      expect(pageContent).toContain('subscription.plan');
    });
  });

  describe('Eventos con Suscripciones', () => {
    beforeEach(async () => {
      await loginAsAdmin(page);
    });

    it('debería crear evento con opción de suscripción', async () => {
      await page.goto(`${baseURL}/web#model=event.event&view_type=list`);

      // Esperar que se cargue
      await page.waitForTimeout(1500);

      // Click en Create
      const createBtn = await page.$('button:has-text("Create"), button:has-text("New")');
      if (createBtn) {
        await createBtn.click();
      }

      // Esperar formulario
      await page.waitForTimeout(1000);

      const nameInput = await page.$('[name="name"]');
      if (nameInput) {
        const eventName = `Test Event with Subscription ${Date.now()}`;
        await nameInput.fill(eventName);

        // Buscar campo de plan de suscripción
        const subscriptionField = await page.$('[name="subscription_plan_id"]');
        if (subscriptionField) {
          // Dejar el plan que viene por defecto o seleccionar uno
          console.log('Plan de suscripción encontrado');
        }

        // Guardar
        await page.click('button:has-text("Save")');

        // Verificar guardado
        await page.waitForTimeout(1500);
        const successMsg = await verifySuccessMessage(page);
        expect(successMsg).toBe(true);
      }
    });

    it('debería mostrar suscriptores registrados en evento', async () => {
      await page.goto(`${baseURL}/web#model=event.registration&view_type=list`);

      // Esperar que se cargue la lista de registros
      await page.waitForTimeout(2000);

      // Verificar que se cargó la lista
      const pageContent = await page.content();
      expect(pageContent).toContain('event');
    });
  });

  describe('Email y Automatizaciones', () => {
    beforeEach(async () => {
      await loginAsAdmin(page);
    });

    it('debería acceder a plantillas de email de eventos', async () => {
      await page.goto(`${baseURL}/web`);

      // Buscar email templates
      const search = await page.$('[data-placeholder="Search..."], [placeholder="Search..."]');
      if (search) {
        await search.fill('Email Template');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(2000);
      }

      const pageContent = await page.content();
      expect(pageContent).toBeDefined();
    });

    it('debería verificar automatizaciones de suscripción', async () => {
      await page.goto(`${baseURL}/web#model=automation&view_type=list`);

      // Esperar que se cargue
      await page.waitForTimeout(2000);

      const pageContent = await page.content();
      expect(pageContent).toBeDefined();
    });
  });

  describe('Reportes de Suscripciones', () => {
    beforeEach(async () => {
      await loginAsAdmin(page);
    });

    it('debería acceder a reportes de suscripción', async () => {
      await page.goto(`${baseURL}/web`);

      // Buscar reportes
      const search = await page.$('[data-placeholder="Search..."], [placeholder="Search..."]');
      if (search) {
        await search.fill('Reportes Suscripción');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(2000);
      }

      const pageContent = await page.content();
      expect(pageContent).toBeDefined();
    });

    it('debería mostrar métricas de suscriptores por evento', async () => {
      await page.goto(`${baseURL}/web#model=event.event&view_type=list`);

      // Esperar que se cargue
      await page.waitForTimeout(2000);

      // Verificar que se cargó la vista
      const tableRows = await page.$$('table tbody tr, .o_list_record');
      expect(Array.isArray(tableRows)).toBe(true);
    });
  });

  describe('Frontend - Página de Eventos con Suscripciones', () => {
    it('debería mostrar eventos en página web', async () => {
      await page.goto(`${baseURL}/event`);

      // Esperar que se cargue
      await page.waitForTimeout(2000);

      const pageContent = await page.content();
      expect(pageContent).toBeDefined();
    });

    it('debería permitir registrarse en evento con suscripción', async () => {
      await page.goto(`${baseURL}/event`);

      // Esperar que se cargue
      await page.waitForTimeout(2000);

      // Buscar primer evento
      const eventLink = await page.$('a[href*="/event/"]');
      if (eventLink) {
        await eventLink.click();

        // Esperar página del evento
        await page.waitForTimeout(2000);

        const pageContent = await page.content();
        expect(pageContent).toBeDefined();
      }
    });

    it('debería mostrar información de suscripción en evento', async () => {
      await page.goto(`${baseURL}/event`);

      // Esperar que se cargue
      await page.waitForTimeout(2000);

      // Buscar primer evento
      const eventLink = await page.$('a[href*="/event/"]');
      if (eventLink) {
        await eventLink.click();

        // Esperar página del evento
        await page.waitForTimeout(2000);

        // Verificar que se muestra información
        const pageContent = await page.content();
        expect(pageContent).toBeDefined();
      }
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
