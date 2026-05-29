/**
 * Utilidades para tests de Stagehand
 */

/**
 * Esperar a que un elemento sea visible y clickeable
 */
export async function waitForElementAndClick(page, selector, timeout = 5000) {
  await page.waitForSelector(selector, { timeout });
  await page.click(selector);
}

/**
 * Esperar y llenar un campo
 */
export async function fillField(page, selector, value, timeout = 5000) {
  await page.waitForSelector(selector, { timeout });
  await page.fill(selector, value);
}

/**
 * Verificar que se muestre un mensaje de éxito
 */
export async function verifySuccessMessage(page, timeout = 5000) {
  // Odoo muestra mensajes en diferentes formatos según la versión
  const selectors = [
    '.alert.alert-success',
    '.o_notification.bg-success',
    '[role="alert"]:has-text("success")',
    'div:has-text("saved")',
  ];

  for (const selector of selectors) {
    try {
      await page.waitForSelector(selector, { timeout: 2000 });
      return true;
    } catch {
      continue;
    }
  }
  return false;
}

/**
 * Esperar a que un modal se cierre
 */
export async function waitForModalClose(page, timeout = 5000) {
  try {
    await page.waitForSelector('.modal-backdrop', { state: 'hidden', timeout });
  } catch {
    // Si no hay modal, continuar
  }
}

/**
 * Obtener tabla de datos
 */
export async function getTableData(page, tableSelector = 'table') {
  const rows = await page.$$eval(`${tableSelector} tbody tr`, (elements) =>
    elements.map((row) => {
      const cells = row.querySelectorAll('td');
      return Array.from(cells).map((cell) => cell.textContent.trim());
    })
  );
  return rows;
}

/**
 * Verificar que un item existe en una lista
 */
export async function verifyItemInList(page, itemName) {
  try {
    await page.waitForSelector(`text="${itemName}"`, { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Logout de Odoo
 */
export async function logout(page) {
  const baseURL = process.env.BASE_URL || 'http://localhost:8069';
  await page.goto(`${baseURL}/web`);

  // Hacer clic en el avatar del usuario (esquina superior derecha)
  await page.click('.oe_topbar_name').catch(() => {
    return page.click('[role="button"]:has-text("admin")');
  });

  // Hacer clic en logout
  await page.click('a:has-text("Log out")');

  // Esperar que se redirija al login
  await page.waitForURL(/.*\/web\/login/);
}
