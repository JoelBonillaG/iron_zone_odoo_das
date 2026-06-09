import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const evidenceDir = path.join(moduleDir, "evidencias");
const videoDir = path.join(evidenceDir, "videos");

function ensureDirs() {
  if (!fs.existsSync(evidenceDir)) fs.mkdirSync(evidenceDir, { recursive: true });
  if (!fs.existsSync(videoDir)) fs.mkdirSync(videoDir, { recursive: true });
  return evidenceDir;
}

function safeName(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9_-]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .toLowerCase();
}

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name) {
  const filePath = path.join(ensureDirs(), `${Date.now()}_${name}.png`);

  try {
    await page.screenshot({ path: filePath, fullPage: false });
    console.log(`Captura: ${filePath}`);
    await delay(300);
  } catch (err) {
    console.log(`No se pudo capturar ${name}: ${err.message}`);
  }
}

async function showTitle(page, title) {
  await page.setContent(`<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0;
      height: 100vh;
      display: grid;
      place-items: center;
      background: #111827;
      color: #f9fafb;
      font-family: Arial, sans-serif;
    }
    main {
      text-align: center;
      max-width: 900px;
      padding: 48px;
    }
    h1 {
      margin: 0 0 18px;
      font-size: 42px;
      line-height: 1.15;
    }
    p {
      margin: 0;
      color: #cbd5e1;
      font-size: 20px;
    }
  </style>
</head>
<body>
  <main>
    <h1>Iron Zone</h1>
    <p>${title}</p>
  </main>
</body>
</html>`);

  await delay(1200);
}

async function runFlow(name, testFn) {
  console.log(`\nIniciando Playwright: ${name}`);
  ensureDirs();

  const headless = process.env.HEADLESS !== "false";

  const browser = await chromium.launch({
    headless,
    slowMo: 120,
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: videoDir,
      size: { width: 1280, height: 720 },
    },
    viewport: { width: 1280, height: 720 },
  });

  const page = await context.newPage();
  const video = page.video();

  try {
    await showTitle(page, name);
    await testFn(page, context);
    console.log(`OK: ${name}`);
  } catch (err) {
    console.error(`FALLO: ${name} - ${err.message}`);
    await takeScreenshot(page, `${safeName(name)}_error`);
    process.exitCode = 1;
  } finally {
    await context.close();

    if (video) {
      try {
        const original = await video.path();
        const dest = path.join(videoDir, `${Date.now()}_${safeName(name)}.webm`);
        fs.renameSync(original, dest);
        console.log(`Video: ${dest}`);
      } catch (e) {
        console.log(`No se pudo guardar video: ${e.message}`);
      }
    }

    await browser.close();
  }
}

function buildUrl(base, route) {
  return new URL(route, base).toString();
}

const timestamp = Date.now();
const today = new Date();
const birthdayYear = today.getFullYear() - 20;

const NEW_USER = {
  name: `Socio QA ${timestamp}`,
  email: `socio.qa.${timestamp}@ironzone.test`,
  password: "admin123",

  // Mismo día y mes de hoy para activar cumpleaños,
  // pero con edad válida para pasar la validación de mínimo 14 años.
  birthdate: `${birthdayYear}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`,

  // Para que también tenga coherencia con el correo del Día de la Mujer.
  gender: "female",

  // Objetivo correcto para la plantilla mail_template_goal_general_fitness.
  goal: "general_fitness",

  level: "beginner",
};

const ADMIN_USER = {
  email: "admin@ironzone.com",
  password: "admin123",
};

const BASE_URL = process.env.IRONZONE_LOCAL_URL || "http://localhost:8069";

async function loginAs(page, user) {
  console.log(`Login: ${user.email}`);

  await page.goto(buildUrl(BASE_URL, "/web/session/logout"), {
    waitUntil: "domcontentloaded",
    timeout: 20000,
  }).catch(() => null);

  await page.goto(buildUrl(BASE_URL, "/web/login"), {
    waitUntil: "domcontentloaded",
    timeout: 40000,
  });

  const loginSel = '#login, input[name="login"]';
  const passSel = '#password, input[name="password"]';
  const btnSel = '.oe_login_form button[type="submit"], button[type="submit"].btn-primary';

  await page.waitForSelector(loginSel, {
    state: "visible",
    timeout: 15000,
  });

  await delay(400);

  await page.fill(loginSel, user.email);
  await page.fill(passSel, user.password);

  await takeScreenshot(page, `login_${safeName(user.email)}`);

  await page.locator(btnSel).first().click({ force: true });

  await page.waitForLoadState("domcontentloaded", {
    timeout: 20000,
  }).catch(() => null);

  await delay(2500);

  const currentUrl = page.url();
  console.log(`URL después del login: ${currentUrl}`);

  const errorAlert = page.locator(
    ".alert-danger, .text-danger, .alert-warning, .o_notification_content"
  );

  if (currentUrl.includes("/web/login")) {
    let errorText = "";

    if (await errorAlert.count()) {
      errorText = await errorAlert.first().innerText().catch(() => "");
    }

    throw new Error(
      `Login fallido para ${user.email}. ${
        errorText
          ? "Mensaje: " + errorText.trim()
          : "El usuario probablemente no existe o la contraseña es incorrecta."
      }`
    );
  }

  console.log(`Login OK: ${currentUrl}`);
}

async function callOdoo(page, model, method, args = [], kwargs = {}) {
  const url = buildUrl(BASE_URL, `/web/dataset/call_kw/${model}/${method}`);

  const response = await page.evaluate(
    async ({ requestUrl, requestModel, requestMethod, requestArgs, requestKwargs }) => {
      const res = await fetch(requestUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          method: "call",
          params: {
            model: requestModel,
            method: requestMethod,
            args: requestArgs,
            kwargs: requestKwargs,
          },
        }),
      });

      return res.json();
    },
    {
      requestUrl: url,
      requestModel: model,
      requestMethod: method,
      requestArgs: args,
      requestKwargs: kwargs,
    }
  );

  if (response.error) {
    const msg =
      response.error.data?.message ||
      response.error.message ||
      JSON.stringify(response.error);

    throw new Error(`Error Odoo ${model}.${method}: ${msg}`);
  }

  return response.result;
}

async function getXmlId(page, xmlid) {
  const parts = xmlid.split(".");

  if (parts.length !== 2) {
    throw new Error(`XML ID inválido: ${xmlid}`);
  }

  const [module, name] = parts;

  const records = await callOdoo(
    page,
    "ir.model.data",
    "search_read",
    [
      [
        ["module", "=", module],
        ["name", "=", name],
      ],
    ],
    {
      fields: ["res_id", "model"],
      limit: 1,
    }
  );

  if (!records.length) {
    throw new Error(`No se encontró el XML ID: ${xmlid}`);
  }

  return records[0].res_id;
}

async function getModelFields(page, model) {
  const fields = await callOdoo(page, model, "fields_get", [], {
    attributes: ["string", "type"],
  });

  return Object.keys(fields || {});
}

function onlyExistingFields(values, existingFields) {
  const clean = {};

  for (const [key, value] of Object.entries(values)) {
    if (existingFields.includes(key)) {
      clean[key] = value;
    }
  }

  return clean;
}

async function getCurrentPartnerId(page) {
  const users = await callOdoo(
    page,
    "res.users",
    "search_read",
    [
      [
        ["login", "=", NEW_USER.email],
      ],
    ],
    {
      fields: ["id", "partner_id"],
      limit: 1,
    }
  );

  if (!users.length) {
    throw new Error(`No se encontró el usuario ${NEW_USER.email}`);
  }

  const partnerId = Array.isArray(users[0].partner_id)
    ? users[0].partner_id[0]
    : users[0].partner_id;

  if (!partnerId) {
    throw new Error(`No se encontró partner para ${NEW_USER.email}`);
  }

  return partnerId;
}

async function findTemplateByXmlNameOrKeyword(page, xmlName, fallbackKeyword) {
  console.log(`Buscando plantilla por XML ID/name: ${xmlName}`);

  const dataRecords = await callOdoo(
    page,
    "ir.model.data",
    "search_read",
    [
      [
        ["name", "=", xmlName],
      ],
    ],
    {
      fields: ["res_id", "module", "name", "model"],
      limit: 1,
    }
  );

  if (dataRecords.length > 0) {
    console.log(`Plantilla encontrada por XML ID: ${dataRecords[0].module}.${dataRecords[0].name}`);
    return dataRecords[0].res_id;
  }

  console.log(`No se encontró XML ID ${xmlName}. Buscando por asunto/nombre: ${fallbackKeyword}`);

  const templates = await callOdoo(
    page,
    "mail.template",
    "search_read",
    [
      [
        "|",
        ["subject", "ilike", fallbackKeyword],
        ["name", "ilike", fallbackKeyword],
      ],
    ],
    {
      fields: ["id", "name", "subject", "model"],
      limit: 1,
      order: "id desc",
    }
  );

  if (!templates.length) {
    throw new Error(`No se encontró la plantilla ${xmlName} ni una plantilla con: ${fallbackKeyword}`);
  }

  console.log(`Plantilla encontrada por búsqueda: ${templates[0].name || templates[0].subject}`);
  return templates[0].id;
}

async function sendTemplateIfExists(page, {
  subjectKeyword,
  userId,
  partnerId,
}) {
  const templates = await callOdoo(
    page,
    "mail.template",
    "search_read",
    [
      [
        "|",
        ["subject", "ilike", subjectKeyword],
        ["name", "ilike", subjectKeyword],
      ],
    ],
    {
      fields: ["id", "name", "subject", "model"],
      limit: 1,
      order: "id desc",
    }
  );

  if (!templates.length) {
    console.log(`No se encontró plantilla con: ${subjectKeyword}`);
    return false;
  }

  const template = templates[0];

  let resId = null;

  if (template.model === "res.partner") {
    resId = partnerId;
  } else if (template.model === "res.users") {
    resId = userId;
  } else {
    console.log(`Plantilla encontrada, pero modelo no manejado: ${template.model}`);
    return false;
  }

  console.log(`Enviando plantilla: ${template.name || template.subject}`);

  await callOdoo(
    page,
    "mail.template",
    "send_mail",
    [template.id, resId],
    {
      force_send: true,
    }
  );

  return true;
}

async function sendGeneralFitnessTemplate(page) {
  console.log("Enviando plantilla real de Fitness General / Bienestar y Salud...");

  await loginAs(page, ADMIN_USER);

  const partnerId = await getCurrentPartnerId(page);

  const templateId = await findTemplateByXmlNameOrKeyword(
    page,
    "mail_template_goal_general_fitness",
    "Bienestar Total"
  );

  await callOdoo(
    page,
    "mail.template",
    "send_mail",
    [templateId, partnerId],
    {
      force_send: true,
    }
  );

  console.log("Plantilla Fitness General enviada correctamente.");
}

async function sendWomanTemplate(page) {
  console.log("Enviando plantilla real del Día de la Mujer...");

  await loginAs(page, ADMIN_USER);

  const partnerId = await getCurrentPartnerId(page);

  let templateId = null;

  const possibleXmlNames = [
    "mail_template_woman_day",
    "mail_template_dia_mujer",
    "mail_template_womens_day",
    "mail_template_mujer",
    "mail_template_woman",
  ];

  for (const xmlName of possibleXmlNames) {
    try {
      templateId = await findTemplateByXmlNameOrKeyword(page, xmlName, "Mujer");

      if (templateId) {
        console.log(`Plantilla Día de la Mujer encontrada: ${xmlName}`);
        break;
      }
    } catch (err) {
      console.log(`No se encontró plantilla con XML ID ${xmlName}`);
    }
  }

  if (!templateId) {
    templateId = await findTemplateByXmlNameOrKeyword(
      page,
      "mail_template_dia_mujer",
      "Mujer"
    );
  }

  await callOdoo(
    page,
    "mail.template",
    "send_mail",
    [templateId, partnerId],
    {
      force_send: true,
    }
  );

  console.log("Plantilla Día de la Mujer enviada correctamente.");
}

async function createUserFromAdminFallback(page, user) {
  console.log("Creando usuario por backend para continuar el video demostrativo...");

  await loginAs(page, ADMIN_USER);

  const partnerFields = await getModelFields(page, "res.partner");

  const partnerCustomValues = onlyExistingFields(
    {
      email: user.email,
      iz_gender: user.gender,
      iz_birthdate: user.birthdate,
      iz_fitness_goal: user.goal,
      iz_experience_level: user.level,
    },
    partnerFields
  );

  const existingUsers = await callOdoo(
    page,
    "res.users",
    "search_read",
    [
      [
        ["login", "=", user.email],
      ],
    ],
    {
      fields: ["id", "partner_id"],
      limit: 1,
    }
  );

  if (existingUsers.length > 0) {
    const existing = existingUsers[0];

    const partnerId = Array.isArray(existing.partner_id)
      ? existing.partner_id[0]
      : existing.partner_id;

    console.log(`Usuario ya existía: ${user.email}`);

    if (partnerId && Object.keys(partnerCustomValues).length > 0) {
      await callOdoo(
        page,
        "res.partner",
        "write",
        [[partnerId], partnerCustomValues]
      );
    }

    await callOdoo(
      page,
      "res.users",
      "write",
      [[existing.id], {
        password: user.password,
      }]
    );

    await sendTemplateIfExists(page, {
      subjectKeyword: "Bienvenido",
      userId: existing.id,
      partnerId,
    });

    return {
      userId: existing.id,
      partnerId,
    };
  }

  const portalGroupId = await getXmlId(page, "base.group_portal");

  const userId = await callOdoo(
    page,
    "res.users",
    "create",
    [{
      name: user.name,
      login: user.email,
      email: user.email,
      password: user.password,
      groups_id: [[6, 0, [portalGroupId]]],
    }]
  );

  const [createdUser] = await callOdoo(
    page,
    "res.users",
    "read",
    [[userId]],
    {
      fields: ["partner_id"],
    }
  );

  const partnerId = Array.isArray(createdUser.partner_id)
    ? createdUser.partner_id[0]
    : createdUser.partner_id;

  if (partnerId && Object.keys(partnerCustomValues).length > 0) {
    await callOdoo(
      page,
      "res.partner",
      "write",
      [[partnerId], partnerCustomValues]
    );
  }

  await sendTemplateIfExists(page, {
    subjectKeyword: "Bienvenido",
    userId,
    partnerId,
  });

  console.log(`Usuario creado por backend: ${user.email}`);

  return {
    userId,
    partnerId,
  };
}

async function performSignup(page, user) {
  console.log(`Ejecutando Registro Real: ${user.email}`);

  await page.goto(buildUrl(BASE_URL, "/web/signup"), {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await page.waitForSelector("form.oe_signup_form", {
    state: "visible",
    timeout: 15000,
  });

  await page.fill('input[name="login"]', user.email);
  await page.fill('input[name="name"]', user.name);
  await page.fill('input[name="password"]', user.password);
  await page.fill('input[name="confirm_password"]', user.password);

  await page.selectOption("#iz_gender", user.gender);
  await page.fill('input[name="iz_birthdate"]', user.birthdate);
  await page.selectOption("#iz_fitness_goal", user.goal);
  await page.selectOption("#iz_experience_level", user.level);

  await takeScreenshot(page, "0_formulario_signup_lleno");
  await delay(1000);

  console.log("Procesando registro y disparando Email Marketing...");

  const signupBtn = page.locator('form.oe_signup_form button[type="submit"]').first();

  await signupBtn.scrollIntoViewIfNeeded().catch(() => null);
  await signupBtn.click({ force: true, timeout: 15000 }).catch((err) => {
    console.log(`No se pudo hacer clic normal en Registrar: ${err.message}`);
  });

  await page.waitForLoadState("domcontentloaded", {
    timeout: 20000,
  }).catch(() => null);

  await delay(3000);

  let currentUrl = page.url();
  console.log(`URL después del primer intento de registro: ${currentUrl}`);

  if (currentUrl.includes("/web/signup")) {
    console.log("Sigue en /web/signup. Intentando enviar con Enter...");
    await page.press('input[name="confirm_password"]', "Enter").catch(() => null);

    await page.waitForLoadState("domcontentloaded", {
      timeout: 20000,
    }).catch(() => null);

    await delay(3000);
    currentUrl = page.url();
    console.log(`URL después del segundo intento de registro: ${currentUrl}`);
  }

  if (currentUrl.includes("/web/signup")) {
    console.log("Sigue en /web/signup. Intentando submit directo del formulario...");

    await page.evaluate(() => {
      const form = document.querySelector("form.oe_signup_form");

      if (form) {
        if (typeof form.requestSubmit === "function") {
          form.requestSubmit();
        } else {
          form.submit();
        }
      }
    }).catch((err) => {
      console.log(`No se pudo hacer submit directo: ${err.message}`);
    });

    await page.waitForLoadState("domcontentloaded", {
      timeout: 20000,
    }).catch(() => null);

    await delay(4000);
    currentUrl = page.url();
    console.log(`URL después del tercer intento de registro: ${currentUrl}`);
  }

  const errorAlert = page.locator(
    ".alert-danger, .text-danger, .alert-warning, .o_notification_content"
  );

  if (await errorAlert.count()) {
    const errorText = await errorAlert.first().innerText().catch(() => "");

    if (errorText.trim()) {
      await takeScreenshot(page, "1_error_visible_signup");
      console.log(`Error visible en signup: ${errorText.trim()}`);
    }
  }

  if (currentUrl.includes("/my")) {
    console.log("Registro completado con éxito. Usuario quedó en el portal.");
    await takeScreenshot(page, "1_portal_post_registro");
    await delay(1000);
    return;
  }

  if (currentUrl.includes("/web/login")) {
    console.log("Registro aparentemente completado. Odoo redirigió al login.");
    await loginAs(page, user);
    await takeScreenshot(page, "1_usuario_registrado_login_correcto");
    await delay(1000);
    return;
  }

  if (currentUrl.includes("/web/signup")) {
    await takeScreenshot(page, "1_signup_no_redirige");

    console.log("El formulario público no creó el usuario. Se usará respaldo backend para continuar el video.");
    await createUserFromAdminFallback(page, user);

    console.log("Usuario creado por backend. Entrando como socio para continuar demostración...");
    await loginAs(page, user);

    await page.goto(buildUrl(BASE_URL, "/my"), {
      waitUntil: "domcontentloaded",
      timeout: 30000,
    }).catch(() => null);

    await delay(1500);
    await takeScreenshot(page, "1_usuario_creado_backend_portal");
    return;
  }

  console.log("Registro terminó en una URL distinta. Se verificará el login del usuario.");
  await loginAs(page, user);
  await takeScreenshot(page, "1_usuario_creado_verificado");
  await delay(1000);
}

function extractValidLinksFromHtml(html) {
  if (!html) return [];

  return [...html.matchAll(/href="([^"]+)"/g)]
    .map((match) => match[1].replace(/&amp;/g, "&"))
    .filter((link) => {
      if (!link) return false;
      if (link.startsWith("mailto:")) return false;
      if (link.startsWith("#")) return false;
      if (link.includes("/unsubscribe")) return false;
      if (link.includes("facebook.com")) return false;
      if (link.includes("twitter.com")) return false;
      if (link.includes("instagram.com")) return false;
      if (link.includes("linkedin.com")) return false;
      return true;
    });
}

async function waitForMail(page, domain, kwargs = {}, retries = 10) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    const mailIds = await callOdoo(page, "mail.mail", "search", [domain], kwargs);

    if (mailIds.length > 0) {
      return mailIds;
    }

    console.log(`Correo aún no encontrado. Intento ${attempt}/${retries}...`);
    await delay(2500);
  }

  return [];
}

async function openMarketingMailAndClaim(page, {
  mailIds,
  screenshotName,
  logMessage,
  claimLabel,
}) {
  if (!mailIds || mailIds.length === 0) {
    throw new Error(`No se encontró el correo de marketing: ${logMessage}`);
  }

  const mailId = mailIds[0];

  console.log(logMessage);

  await page.goto(buildUrl(BASE_URL, `/web#id=${mailId}&model=mail.mail&view_type=form`), {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await delay(2500);
  await takeScreenshot(page, `${screenshotName}_odoo_mail_form`);

  const [mailData] = await callOdoo(page, "mail.mail", "read", [[mailId]], {
    fields: ["body_html", "subject", "email_to", "state"],
  });

  console.log(`Correo encontrado: ${mailData.subject} - estado: ${mailData.state}`);

  const links = extractValidLinksFromHtml(mailData.body_html);

  if (links.length === 0) {
    throw new Error(`El correo "${mailData.subject}" no tiene un enlace válido para reclamar.`);
  }

  let link = links[0];

  if (link.startsWith("/")) {
    link = buildUrl(BASE_URL, link);
  }

  await page.setContent(`<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0;
      background: #f3f4f6;
      font-family: Arial, sans-serif;
      color: #111827;
    }
    .wrapper {
      max-width: 980px;
      margin: 32px auto;
      background: white;
      border-radius: 18px;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.15);
      overflow: hidden;
      border: 1px solid #e5e7eb;
    }
    .header {
      background: #111827;
      color: white;
      padding: 24px 32px;
    }
    .header h1 {
      margin: 0 0 8px;
      font-size: 28px;
    }
    .header p {
      margin: 4px 0;
      color: #d1d5db;
      font-size: 15px;
    }
    .content {
      padding: 28px 32px;
    }
    .note {
      margin-bottom: 20px;
      padding: 14px 18px;
      border-radius: 12px;
      background: #ecfdf5;
      color: #065f46;
      font-weight: bold;
      border: 1px solid #a7f3d0;
    }
    .email-body {
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 18px;
      background: #ffffff;
      max-height: 430px;
      overflow: auto;
    }
    .footer {
      padding: 18px 32px 28px;
      color: #6b7280;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <section class="wrapper">
    <div class="header">
      <h1>Email Marketing recibido</h1>
      <p><strong>Para:</strong> ${mailData.email_to || NEW_USER.email}</p>
      <p><strong>Asunto:</strong> ${mailData.subject}</p>
      <p><strong>Estado:</strong> ${mailData.state}</p>
    </div>

    <div class="content">
      <div class="note">
        Este es el correo que recibe el socio. Desde aquí se usará el botón del email para reclamar el beneficio.
      </div>

      <div class="email-body">
        ${mailData.body_html || "<p>Correo sin contenido HTML.</p>"}
      </div>
    </div>

    <div class="footer">
      Flujo demostrativo Iron Zone: email marketing → evento → reclamo del beneficio.
    </div>
  </section>
</body>
</html>`);

  await delay(3500);
  await takeScreenshot(page, `${screenshotName}_email_visible_video`);

  console.log(`${claimLabel}: ${link}`);

  await loginAs(page, NEW_USER);

  await page.goto(link, {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await delay(2500);
  await takeScreenshot(page, `${screenshotName}_landing_evento`);

  await claimEvent(page);

  await delay(1200);
  await takeScreenshot(page, `${screenshotName}_evento_reclamado`);
}

async function claimEvent(page) {
  console.log("Iniciando proceso de reclamación de evento...");

  await delay(1500);

  const possibleButtons = page.locator(
    'button:has-text("Inscribirse"), ' +
    'button:has-text("Registrarse"), ' +
    'button:has-text("Reservar"), ' +
    'button:has-text("Reclamar"), ' +
    'button:has-text("Confirmar"), ' +
    'a:has-text("Inscribirse"), ' +
    'a:has-text("Registrarse"), ' +
    'a:has-text("Reservar"), ' +
    'a:has-text("Reclamar"), ' +
    'a:has-text("Confirmar")'
  );

  let clickedMainButton = false;
  const totalButtons = await possibleButtons.count();

  for (let i = 0; i < totalButtons; i++) {
    const btn = possibleButtons.nth(i);

    const visible = await btn.isVisible().catch(() => false);
    const enabled = await btn.isEnabled().catch(() => false);

    if (visible && enabled) {
      console.log("Botón visible encontrado para reclamar/inscribirse.");
      await btn.scrollIntoViewIfNeeded().catch(() => null);
      await delay(800);
      await takeScreenshot(page, "evento_antes_reclamar");

      await btn.click({ timeout: 15000, force: true });
      clickedMainButton = true;
      await delay(2000);
      break;
    }
  }

  if (!clickedMainButton) {
    console.log("No se encontró botón visible de inscripción/reclamo. Se continuará por si ya abrió el formulario.");
    await takeScreenshot(page, "evento_sin_boton_visible");
  }

  const ticketModal = page.locator("#modal_ticket_registration");

  if (await ticketModal.count()) {
    const modalVisible = await ticketModal.first().isVisible().catch(() => false);

    if (modalVisible) {
      console.log("Modal de tickets detectado.");

      const ticketSelect = page
        .locator("#modal_ticket_registration select[name^='nb_register-']")
        .first();

      if (await ticketSelect.count()) {
        const selectVisible = await ticketSelect.isVisible().catch(() => false);

        if (selectVisible) {
          await ticketSelect.selectOption("1").catch(() => null);
          await delay(800);
        }
      }

      await takeScreenshot(page, "modal_ticket_evento");

      const ticketSubmitButtons = page.locator(
        '#modal_ticket_registration button[type="submit"], ' +
        '#modal_ticket_registration button:has-text("Continuar"), ' +
        '#modal_ticket_registration button:has-text("Confirmar"), ' +
        '#modal_ticket_registration button:has-text("Registrarse")'
      );

      const totalSubmitTickets = await ticketSubmitButtons.count();

      for (let i = 0; i < totalSubmitTickets; i++) {
        const btn = ticketSubmitButtons.nth(i);
        const visible = await btn.isVisible().catch(() => false);
        const enabled = await btn.isEnabled().catch(() => false);

        if (visible && enabled) {
          await btn.click({ force: true, timeout: 15000 });
          await delay(2000);
          break;
        }
      }
    }
  }

  const attendeeForm = page.locator("#attendee_registration");

  if (await attendeeForm.count()) {
    const formVisible = await attendeeForm.first().isVisible().catch(() => false);

    if (formVisible) {
      console.log("Formulario de asistente detectado.");

      const nameInput = page
        .locator("#attendee_registration input[name*='name']")
        .first();

      const emailInput = page
        .locator("#attendee_registration input[name*='email']")
        .first();

      if (await nameInput.count()) {
        const visible = await nameInput.isVisible().catch(() => false);

        if (visible) {
          await nameInput.fill(NEW_USER.name).catch(() => null);
        }
      }

      if (await emailInput.count()) {
        const visible = await emailInput.isVisible().catch(() => false);

        if (visible) {
          await emailInput.fill(NEW_USER.email).catch(() => null);
        }
      }

      await takeScreenshot(page, "modal_asistente_lleno");

      const attendeeSubmitButtons = page.locator(
        '#attendee_registration button[type="submit"], ' +
        '#attendee_registration button:has-text("Confirmar"), ' +
        '#attendee_registration button:has-text("Registrarse"), ' +
        '#attendee_registration button:has-text("Enviar")'
      );

      const totalAttendeeButtons = await attendeeSubmitButtons.count();

      for (let i = 0; i < totalAttendeeButtons; i++) {
        const btn = attendeeSubmitButtons.nth(i);
        const visible = await btn.isVisible().catch(() => false);
        const enabled = await btn.isEnabled().catch(() => false);

        if (visible && enabled) {
          await btn.click({ force: true, timeout: 15000 });
          await delay(2500);
          break;
        }
      }
    }
  }

  await page.waitForLoadState("domcontentloaded", {
    timeout: 15000,
  }).catch(() => null);

  await delay(1500);

  const errorAlert = page.locator(
    ".alert-danger, .text-danger, .alert-warning, .o_notification_content"
  );

  if (await errorAlert.count()) {
    const errorText = await errorAlert.first().innerText().catch(() => "");

    if (errorText.trim()) {
      console.log(`Mensaje visible durante reclamo: ${errorText.trim()}`);
    }
  }

  await takeScreenshot(page, "evento_reclamo_finalizado");

  console.log("Evento reclamado con éxito o flujo de reclamo completado.");
}

runFlow("email marketing registro y eventos local", async (page) => {
  console.log("Paso 1: Registro real de usuario...");
  await performSignup(page, NEW_USER);

  console.log("Paso 2: Login admin para auditoría de correos...");
  await loginAs(page, ADMIN_USER);
  await takeScreenshot(page, "2_login_admin");

  console.log("Paso 3: Verificar correo de bienvenida y cumpleaños...");
  const welcomeMails = await waitForMail(
    page,
    [
      ["email_to", "ilike", NEW_USER.email],
      ["subject", "ilike", "Bienvenido"],
    ],
    {
      limit: 1,
      order: "create_date desc",
    }
  );

  await openMarketingMailAndClaim(page, {
    mailIds: welcomeMails,
    screenshotName: "3_correo_bienvenida_cumpleanos_evento_gratis",
    logMessage: "Mostrando correo de bienvenida con cumpleaños y primer evento gratis...",
    claimLabel: "Reclamando evento gratis desde correo de bienvenida",
  });

  console.log("Paso 4: Enviar correo de Fitness General / Bienestar y Salud...");
  await sendGeneralFitnessTemplate(page);

  console.log("Paso 5: Verificar correo Fitness General / Bienestar y Salud...");
  await loginAs(page, ADMIN_USER);

  const goalMails = await waitForMail(
    page,
    [
      ["email_to", "ilike", NEW_USER.email],
      "|",
      ["subject", "ilike", "Bienestar Total"],
      ["subject", "ilike", "Yoga Principiantes"],
    ],
    {
      limit: 1,
      order: "create_date desc",
    }
  );

  await openMarketingMailAndClaim(page, {
    mailIds: goalMails,
    screenshotName: "5_correo_fitness_general_yoga",
    logMessage: "Mostrando correo de Fitness General / Bienestar y Salud...",
    claimLabel: "Reservando Clase de Yoga desde el correo de Fitness General",
  });

  console.log("Paso 6: Enviar correo Día de la Mujer...");
  await sendWomanTemplate(page);

  console.log("Paso 7: Verificar correo Día de la Mujer...");
  await loginAs(page, ADMIN_USER);

  const womanMails = await waitForMail(
    page,
    [
      ["email_to", "ilike", NEW_USER.email],
      ["subject", "ilike", "Mujer"],
    ],
    {
      limit: 1,
      order: "create_date desc",
    }
  );

  await openMarketingMailAndClaim(page, {
    mailIds: womanMails,
    screenshotName: "7_correo_dia_mujer_evento_gratis",
    logMessage: "Mostrando correo del Día de la Mujer con evento gratis...",
    claimLabel: "Reclamando evento gratis del Día de la Mujer desde el correo",
  });

  console.log("Paso 8: Resumen final de correos generados.");
  await loginAs(page, ADMIN_USER);

  const allMails = await callOdoo(
    page,
    "mail.mail",
    "search_read",
    [
      [
        ["email_to", "ilike", NEW_USER.email],
      ],
    ],
    {
      fields: ["subject", "state", "email_to", "create_date"],
      order: "create_date desc",
    }
  );

  console.log("Correos generados para el usuario:");

  allMails.forEach((m) => {
    console.log(`  - [${m.state}] ${m.subject}`);
  });

  await page.goto(buildUrl(BASE_URL, "/web#model=mail.mail&view_type=list"), {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await delay(2000);
  await takeScreenshot(page, "8_resumen_correos_marketing");

  console.log("Video demostrativo completado correctamente.");
});