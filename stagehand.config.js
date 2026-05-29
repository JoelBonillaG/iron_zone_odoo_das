module.exports = {
  // Configuración base de Stagehand
  testDir: 'tests/e2e',
  timeout: 30000,
  retries: 1,
  workers: 1,

  // Configuración del navegador
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8069',
    headless: process.env.HEADLESS !== 'false',
    viewport: { width: 1280, height: 720 },
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },

  // Proyectos/navegadores
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'firefox',
      use: { browserName: 'firefox' },
    },
  ],

  // Servidor web (opcional si tienes Odoo localmente)
  webServer: process.env.SKIP_SERVER ? undefined : {
    command: 'docker-compose up',
    url: 'http://localhost:8069',
    reuseExistingServer: !process.env.CI,
  },
};
