/**
 * Fixture para autenticación en Odoo
 */
export async function loginAsAdmin(page) {
  const baseURL = process.env.BASE_URL || 'http://localhost:8069';
  await page.goto(`${baseURL}/web/login`);
  
  // Llenar credenciales
  await page.fill('input[name="login"]', process.env.ODOO_USER || 'admin');
  await page.fill('input[name="password"]', process.env.ODOO_PASSWORD || 'admin');
  
  // Hacer clic en el botón de inicio de sesión
  await page.click('button[type="submit"]');
  
  // Esperar a que se cargue el dashboard
  await page.waitForURL(/.*dashboard.*/, { timeout: 10000 }).catch(() => {
    // Si no hay dashboard, puede ser Odoo 18, intentar llegar a /web
    return page.waitForURL(/.*\/web($|\/)/);
  });
  
  return page;
}

/**
 * Fixture para navegar a eventos
 */
export async function navigateToEvents(page) {
  const baseURL = process.env.BASE_URL || 'http://localhost:8069';
  await page.goto(`${baseURL}/web`);
  
  // Abrir el menú de aplicaciones
  await page.click('[data-menu-xmlid="event.event_event_menu_action"]').catch(() => {
    // Si no funciona la búsqueda por xmlid, usar búsqueda de menú
    return page.fill('[data-placeholder="Search..."]', 'Eventos');
  });
  
  // Esperar que se cargue la vista de eventos
  await page.waitForSelector('[data-model="event.event"]', { timeout: 10000 }).catch(() => {
    return page.waitForURL(/.*event\.event/);
  });
}

/**
 * Fixture para crear un evento
 */
export async function createEvent(page, eventData = {}) {
  const defaultData = {
    name: `Test Event ${Date.now()}`,
    date: new Date().toISOString().split('T')[0],
    seats: 50,
    ...eventData,
  };
  
  // Hacer clic en el botón "Create"
  await page.click('button:has-text("Create")').catch(() => {
    return page.click('button:has-text("New")');
  });
  
  // Esperar el formulario
  await page.waitForSelector('[name="name"]', { timeout: 5000 });
  
  // Llenar el nombre
  await page.fill('[name="name"]', defaultData.name);
  
  // Llenar la fecha
  if (defaultData.date) {
    await page.fill('[name="date_begin"]', defaultData.date);
  }
  
  // Llenar cantidad de asientos
  if (defaultData.seats) {
    await page.fill('[name="seats_available"]', defaultData.seats.toString());
  }
  
  // Guardar
  await page.click('button.btn-primary:has-text("Save")');
  
  // Esperar confirmación
  await page.waitForTimeout(1000);
  
  return defaultData;
}

/**
 * Fixture para registrarse en un evento
 */
export async function registerForEvent(page, eventName) {
  const baseURL = process.env.BASE_URL || 'http://localhost:8069';
  
  // Ir a la página de eventos públicos
  await page.goto(`${baseURL}/event`);
  
  // Buscar el evento
  await page.waitForSelector('a:has-text("' + eventName + '")', { timeout: 5000 });
  
  // Hacer clic en el evento
  await page.click('a:has-text("' + eventName + '")');
  
  // Esperar página del evento
  await page.waitForSelector('button:has-text("Register")', { timeout: 5000 }).catch(() => {
    return page.waitForSelector('a:has-text("Register")');
  });
  
  // Hacer clic en registrarse
  await page.click('button:has-text("Register")').catch(() => {
    return page.click('a:has-text("Register")');
  });
  
  return page;
}

/**
 * Fixture para verificar que un evento está visible
 */
export async function verifyEventVisible(page, eventName) {
  await page.waitForSelector(`text="${eventName}"`, { timeout: 5000 });
  const isVisible = await page.isVisible(`text="${eventName}"`);
  return isVisible;
}
