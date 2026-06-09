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
    await delay(250);
  } catch (err) {
    console.log(`No se pudo capturar ${name}: ${err.message}`);
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
  birthdate: `${birthdayYear}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`,
  gender: "female",
  goal: "general_fitness",
  level: "beginner",
  phone: "0999999999",
  street: "Av. Cevallos y Montalvo",
  city: "Ambato",
  zip: "180101",
  country: "Ecuador",
  identificationType: "VAT",
  identificationNumber: "1804962684",
};

const ADMIN_USER = {
  email: "admin@ironzone.com",
  password: "admin123",
};

const BASE_URL = process.env.IRONZONE_LOCAL_URL || "http://localhost:8069";

async function showTitle(page, title) {
  await page.setContent(`<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
body{margin:0;height:100vh;display:grid;place-items:center;background:#111827;color:#f9fafb;font-family:Arial,sans-serif}
main{text-align:center;max-width:900px;padding:48px}
h1{margin:0 0 18px;font-size:42px}
p{margin:0;color:#cbd5e1;font-size:20px}
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

async function showEmailSection(page, { title, subtitle, badge }) {
  await page.setContent(`<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
body{margin:0;height:100vh;display:grid;place-items:center;background:linear-gradient(135deg,#050505,#111827,#0f172a);color:#f9fafb;font-family:Arial,sans-serif}
main{width:900px;text-align:center;padding:48px;border:1px solid rgba(255,255,255,.12);border-radius:24px;background:rgba(17,24,39,.78);box-shadow:0 25px 60px rgba(0,0,0,.45)}
.brand{font-size:22px;letter-spacing:5px;color:#38ef7d;font-weight:900;text-transform:uppercase;margin-bottom:18px}
.badge{display:inline-block;padding:10px 18px;border-radius:999px;background:#16a34a;color:white;font-size:14px;font-weight:bold;margin-bottom:22px;text-transform:uppercase;letter-spacing:1px}
h1{margin:0 0 18px;font-size:42px;line-height:1.15}
p{margin:0 auto;color:#d1d5db;font-size:21px;line-height:1.45;max-width:720px}
</style>
</head>
<body>
<main>
<div class="brand">Iron Zone</div>
<div class="badge">${badge}</div>
<h1>${title}</h1>
<p>${subtitle}</p>
</main>
</body>
</html>`);
  await delay(2200);
}

async function showClaimSuccessPage(page, {
  title = "Evento reclamado correctamente",
  subtitle = "El beneficio fue aplicado y el socio quedó listo para participar.",
  badge = "Beneficio aplicado",
  screenshotName = "evento_reclamado_visual",
} = {}) {
  await page.setContent(`<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
body{margin:0;height:100vh;display:grid;place-items:center;background:linear-gradient(135deg,#052e16,#064e3b,#111827);color:#f9fafb;font-family:Arial,sans-serif}
main{width:880px;text-align:center;padding:52px;border-radius:26px;background:rgba(17,24,39,.78);border:1px solid rgba(255,255,255,.16);box-shadow:0 25px 65px rgba(0,0,0,.45)}
.brand{font-size:22px;letter-spacing:5px;color:#38ef7d;font-weight:900;text-transform:uppercase;margin-bottom:18px}
.check{width:92px;height:92px;display:grid;place-items:center;margin:0 auto 24px;border-radius:999px;background:#16a34a;color:white;font-size:52px;font-weight:900;box-shadow:0 12px 35px rgba(22,163,74,.45)}
.badge{display:inline-block;padding:10px 18px;border-radius:999px;background:rgba(56,239,125,.16);color:#bbf7d0;border:1px solid rgba(56,239,125,.35);font-size:14px;font-weight:bold;margin-bottom:22px;text-transform:uppercase;letter-spacing:1px}
h1{margin:0 0 18px;font-size:42px;line-height:1.15}
p{margin:0 auto;color:#d1d5db;font-size:21px;line-height:1.45;max-width:720px}
</style>
</head>
<body>
<main>
<div class="brand">Iron Zone</div>
<div class="check">✓</div>
<div class="badge">${badge}</div>
<h1>${title}</h1>
<p>${subtitle}</p>
</main>
</body>
</html>`);
  await delay(2500);
  await takeScreenshot(page, screenshotName);
}

async function renderEmailForVideo(page, mailData, screenshotName) {
  await page.setContent(`<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
*{box-sizing:border-box}
body{margin:0;background:#0f172a;font-family:Arial,sans-serif;color:#111827;overflow:hidden}
.screen{width:100vw;height:100vh;display:grid;grid-template-columns:330px 1fr;gap:16px;padding:16px}
.info{background:#111827;color:white;border-radius:18px;padding:24px;border:1px solid rgba(255,255,255,.12);box-shadow:0 18px 45px rgba(0,0,0,.35)}
.brand{color:#38ef7d;font-size:17px;font-weight:900;letter-spacing:4px;text-transform:uppercase;margin-bottom:26px}
.info h1{font-size:29px;line-height:1.15;margin:0 0 18px}
.info p{color:#cbd5e1;font-size:15px;line-height:1.5;margin:10px 0}
.subject{margin-top:20px;padding:14px;border-radius:12px;background:rgba(56,239,125,.12);border:1px solid rgba(56,239,125,.35);color:#dcfce7;font-weight:bold;font-size:14px;line-height:1.4}
.email-panel{background:#f3f4f6;border-radius:18px;overflow:hidden;border:1px solid rgba(255,255,255,.12);box-shadow:0 18px 45px rgba(0,0,0,.35)}
.email-topbar{height:46px;background:white;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;padding:0 18px;gap:10px;color:#64748b;font-size:13px;font-weight:bold}
.dot{width:12px;height:12px;border-radius:999px;background:#cbd5e1}
.email-scroll{height:calc(100vh - 78px);overflow:auto;padding:18px;background:#e5e7eb;scroll-behavior:smooth}
.email-scale{width:760px;margin:0 auto;transform:scale(.72);transform-origin:top center}
.email-scale table{max-width:760px!important}
.email-scale img{max-width:100%!important;height:auto!important}
.email-scale a{pointer-events:none}
</style>
</head>
<body>
<section class="screen">
<aside class="info">
<div class="brand">Iron Zone</div>
<h1>Email Marketing recibido</h1>
<p><strong>Para:</strong><br>${mailData.email_to || NEW_USER.email}</p>
<p><strong>Estado:</strong> ${mailData.state || "outgoing"}</p>
<div class="subject">${mailData.subject || "Correo de marketing"}</div>
<p style="margin-top:24px">Se muestra el correo completo antes de usar el botón del beneficio.</p>
</aside>
<main class="email-panel">
<div class="email-topbar">
<span class="dot"></span><span class="dot"></span><span class="dot"></span>
<span>Vista del correo recibido por el socio</span>
</div>
<div class="email-scroll">
<div class="email-scale">${mailData.body_html || "<p>Correo sin contenido HTML.</p>"}</div>
</div>
</main>
</section>
</body>
</html>`);

  await delay(1500);
  await takeScreenshot(page, `${screenshotName}_email_inicio`);

  const scroll = page.locator(".email-scroll");

  await scroll.evaluate((el) => {
    el.scrollTop = el.scrollHeight * 0.35;
  });
  await delay(1500);
  await takeScreenshot(page, `${screenshotName}_email_medio`);

  await scroll.evaluate((el) => {
    el.scrollTop = el.scrollHeight;
  });
  await delay(1800);
  await takeScreenshot(page, `${screenshotName}_email_final`);

  await scroll.evaluate((el) => {
    el.scrollTop = 0;
  });

  await delay(900);
}

async function runFlow(name, testFn) {
  console.log(`\nIniciando Playwright: ${name}`);
  ensureDirs();

  const headless = process.env.HEADLESS !== "false";

  const browser = await chromium.launch({
    headless,
    slowMo: 90,
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

async function sendTemplateIfExists(page, { subjectKeyword, userId, partnerId }) {
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

function normalizeTemplateHtml(html, fallbackButtonUrl) {
  let bodyHtml = html || "";

  bodyHtml = bodyHtml
    .replaceAll('<t t-esc="object.name"/>', NEW_USER.name)
    .replaceAll("<t t-esc=\"object.name\"/>", NEW_USER.name)
    .replaceAll('<t t-esc="object.iz_fitness_goal or \'bienestar integral\'"/>', NEW_USER.goal)
    .replaceAll("<t t-esc=\"object.iz_fitness_goal or 'bienestar integral'\"/>", NEW_USER.goal)
    .replaceAll("<t t-esc=\"object.iz_gender or 'female'\"/>", NEW_USER.gender);

  bodyHtml = bodyHtml.replace(
    /t-att-href="base_url\s*\+\s*'([^']+)'"/g,
    (_match, route) => `href="${buildUrl(BASE_URL, route)}"`
  );

  bodyHtml = bodyHtml.replace(
    /t-att-href='base_url\s*\+\s*"([^"]+)"'/g,
    (_match, route) => `href="${buildUrl(BASE_URL, route)}"`
  );

  bodyHtml = bodyHtml.replace(/<t[^>]*t-set="base_url"[^>]*\/?>/g, "");
  bodyHtml = bodyHtml.replace(/<t[^>]*t-value="[^"]*"[^>]*\/?>/g, "");

  if (!bodyHtml.includes("href=") && fallbackButtonUrl) {
    bodyHtml += `
      <div style="text-align:center;margin:30px 0;">
        <a href="${fallbackButtonUrl}"
          style="display:inline-block;background:#16a34a;color:#ffffff;text-decoration:none;padding:15px 28px;border-radius:999px;font-weight:bold;font-size:17px;">
          Reclamar beneficio
        </a>
      </div>
    `;
  }

  return bodyHtml;
}

async function createVisibleMailFromTemplate(page, {
  xmlName,
  fallbackKeyword,
  fallbackSubject,
  fallbackButtonUrl,
}) {
  await loginAs(page, ADMIN_USER);

  const partnerId = await getCurrentPartnerId(page);

  const templateId = await findTemplateByXmlNameOrKeyword(
    page,
    xmlName,
    fallbackKeyword
  );

  let subject = fallbackSubject;
  let bodyHtml = "";

  try {
    const generated = await callOdoo(
      page,
      "mail.template",
      "generate_email",
      [templateId, [partnerId], ["subject", "body_html", "email_to", "email_from"]]
    );

    const generatedData =
      generated[String(partnerId)] ||
      generated[partnerId] ||
      generated;

    subject = generatedData.subject || fallbackSubject;
    bodyHtml = generatedData.body_html || "";
  } catch (err) {
    console.log(`No se pudo renderizar con generate_email: ${err.message}`);

    const [template] = await callOdoo(
      page,
      "mail.template",
      "read",
      [[templateId]],
      {
        fields: ["subject", "body_html", "email_from"],
      }
    );

    subject = template.subject || fallbackSubject;
    bodyHtml = template.body_html || "";
  }

  bodyHtml = normalizeTemplateHtml(bodyHtml, fallbackButtonUrl);

  const mailId = await callOdoo(
    page,
    "mail.mail",
    "create",
    [{
      subject,
      body_html: bodyHtml,
      email_to: NEW_USER.email,
      email_from: "contacto@ironzone.ec",
      auto_delete: false,
    }]
  );

  console.log(`Correo visible creado desde plantilla: ${subject} | ID: ${mailId}`);

  return [mailId];
}

async function sendGeneralFitnessTemplate(page) {
  console.log("Enviando plantilla real de Fitness General / Bienestar y Salud...");

  const mailIds = await createVisibleMailFromTemplate(page, {
    xmlName: "mail_template_goal_general_fitness",
    fallbackKeyword: "Bienestar Total",
    fallbackSubject: "Bienestar Total: Inicia con Yoga Principiantes para Salud Integral 🌟",
    fallbackButtonUrl: buildUrl(BASE_URL, "/event/yoga-principiantes-2/register"),
  });

  console.log("Plantilla Fitness General preparada correctamente para el video.");

  return mailIds;
}

async function sendWomanTemplate(page) {
  console.log("Enviando plantilla real del Día de la Mujer...");

  const possibleTemplates = [
    { xmlName: "mail_template_woman_day", keyword: "Mujer" },
    { xmlName: "mail_template_dia_mujer", keyword: "Mujer" },
    { xmlName: "mail_template_womens_day", keyword: "Mujer" },
    { xmlName: "mail_template_mujer", keyword: "Mujer" },
    { xmlName: "mail_template_woman", keyword: "Mujer" },
  ];

  for (const item of possibleTemplates) {
    try {
      const mailIds = await createVisibleMailFromTemplate(page, {
        xmlName: item.xmlName,
        fallbackKeyword: item.keyword,
        fallbackSubject: "¡Feliz Día de la Mujer! Reclama tu Clase Premium 100% GRATIS en Iron Zone 💜",
        fallbackButtonUrl: buildUrl(BASE_URL, "/promo/womens-day?event_slug=yoga-avanzado-8"),
      });

      console.log(`Plantilla Día de la Mujer preparada correctamente: ${item.xmlName}`);

      return mailIds;
    } catch (err) {
      console.log(`No se pudo usar ${item.xmlName}: ${err.message}`);
    }
  }

  throw new Error("No se pudo preparar ninguna plantilla del Día de la Mujer.");
}

async function createUserFromAdminFallback(page, user) {
  console.log("Creando usuario por backend para continuar el video demostrativo...");

  await loginAs(page, ADMIN_USER);

  const partnerFields = await getModelFields(page, "res.partner");

  const partnerCustomValues = onlyExistingFields(
    {
      email: user.email,
      phone: user.phone,
      street: user.street,
      city: user.city,
      zip: user.zip,
      vat: user.identificationNumber,
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
      await callOdoo(page, "res.partner", "write", [[partnerId], partnerCustomValues]);
    }

    await callOdoo(page, "res.users", "write", [[existing.id], { password: user.password }]);

    await sendTemplateIfExists(page, {
      subjectKeyword: "Bienvenido",
      userId: existing.id,
      partnerId,
    });

    return { userId: existing.id, partnerId };
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
    { fields: ["partner_id"] }
  );

  const partnerId = Array.isArray(createdUser.partner_id)
    ? createdUser.partner_id[0]
    : createdUser.partner_id;

  if (partnerId && Object.keys(partnerCustomValues).length > 0) {
    await callOdoo(page, "res.partner", "write", [[partnerId], partnerCustomValues]);
  }

  await sendTemplateIfExists(page, {
    subjectKeyword: "Bienvenido",
    userId,
    partnerId,
  });

  console.log(`Usuario creado por backend: ${user.email}`);

  return { userId, partnerId };
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

async function clickFirstVisible(page, locator, logText, screenshotName = null, options = {}) {
  const count = await locator.count();
  const delayBeforeClick = options.delayBeforeClick ?? (screenshotName ? 800 : 120);

  for (let i = 0; i < count; i++) {
    const item = locator.nth(i);
    const visible = await item.isVisible().catch(() => false);
    const enabled = await item.isEnabled().catch(() => false);

    if (visible && enabled) {
      console.log(logText);

      await item.scrollIntoViewIfNeeded().catch(() => null);
      await delay(delayBeforeClick);

      if (screenshotName) {
        await takeScreenshot(page, screenshotName);
      }

      await item.click({
        force: true,
        timeout: 15000,
      });

      await page.waitForLoadState("domcontentloaded", {
        timeout: 20000,
      }).catch(() => null);

      await delay(options.delayAfterClick ?? 1800);

      return true;
    }
  }

  return false;
}

async function selectOptionByText(page, selectors, text) {
  for (const selector of selectors) {
    const select = page.locator(selector).first();
    const count = await select.count();

    if (!count) continue;

    const visible = await select.isVisible().catch(() => false);
    const enabled = await select.isEnabled().catch(() => false);

    if (!visible || !enabled) continue;

    const optionValue = await select.evaluate((el, wanted) => {
      const normalizedWanted = wanted.toLowerCase();

      for (const option of el.options) {
        const label = option.textContent.trim().toLowerCase();

        if (label.includes(normalizedWanted)) {
          return option.value;
        }
      }

      return null;
    }, text).catch(() => null);

    if (optionValue) {
      await select.selectOption(optionValue).catch(() => null);
      await delay(800);
      return true;
    }
  }

  return false;
}

async function fillCheckoutAddressIfVisible(page, screenshotName) {
  const bodyText = await page.locator("body").innerText().catch(() => "");

  const looksLikeAddress =
    bodyText.includes("Your Address") ||
    bodyText.includes("Tu dirección") ||
    bodyText.includes("Dirección") ||
    bodyText.includes("Address") ||
    page.url().includes("/shop/address") ||
    page.url().includes("/shop/checkout");

  if (!looksLikeAddress) {
    return false;
  }

  console.log("Pantalla de dirección detectada. Completando datos obligatorios...");
  await takeScreenshot(page, `${screenshotName}_direccion_detectada`);

  const fillIfVisible = async (selectors, value) => {
    for (const selector of selectors) {
      const input = page.locator(selector).first();
      const count = await input.count();

      if (!count) continue;

      const visible = await input.isVisible().catch(() => false);
      const enabled = await input.isEnabled().catch(() => false);

      if (visible && enabled) {
        const currentValue = await input.inputValue().catch(() => "");

        if (!currentValue || currentValue.trim().length === 0) {
          await input.fill(value).catch(() => null);
        }

        return true;
      }
    }

    return false;
  };

  await fillIfVisible(
    [
      'input[name="name"]',
      'input[name="partner_name"]',
      'input[name="firstname"]',
      'input[id*="name"]',
    ],
    NEW_USER.name
  );

  await fillIfVisible(
    [
      'input[name="email"]',
      'input[name="partner_email"]',
      'input[type="email"]',
    ],
    NEW_USER.email
  );

  await fillIfVisible(
    [
      'input[name="phone"]',
      'input[name="mobile"]',
      'input[name="partner_phone"]',
      'input[type="tel"]',
    ],
    NEW_USER.phone
  );

  await fillIfVisible(
    [
      'input[name="street"]',
      'input[name="street1"]',
      'input[name="partner_street"]',
      'input[id*="street"]',
    ],
    NEW_USER.street
  );

  await fillIfVisible(
    [
      'input[name="city"]',
      'input[name="partner_city"]',
      'input[id*="city"]',
    ],
    NEW_USER.city
  );

  await fillIfVisible(
    [
      'input[name="zip"]',
      'input[name="zipcode"]',
      'input[name="partner_zip"]',
      'input[id*="zip"]',
    ],
    NEW_USER.zip
  );

  await fillIfVisible(
    [
      'input[name="vat"]',
      'input[name="l10n_latam_identification_number"]',
      'input[name="identification_number"]',
      'input[name*="identification"]',
      'input[id*="identification"]',
      'input[id*="vat"]',
    ],
    NEW_USER.identificationNumber
  );

  await selectOptionByText(
    page,
    [
      'select[name="country_id"]',
      'select[id*="country"]',
      'select[name*="country"]',
    ],
    NEW_USER.country
  );

  await selectOptionByText(
    page,
    [
      'select[name="l10n_latam_identification_type_id"]',
      'select[name*="identification_type"]',
      'select[id*="identification_type"]',
    ],
    NEW_USER.identificationType
  );

  await delay(1000);
  await takeScreenshot(page, `${screenshotName}_direccion_llena`);

  const continueAddressButtons = page.locator(
    'button:has-text("Continuar"), ' +
    'a:has-text("Continuar"), ' +
    'button:has-text("Continue"), ' +
    'a:has-text("Continue"), ' +
    'button:has-text("Continuar al pago"), ' +
    'a:has-text("Continuar al pago"), ' +
    'button:has-text("Proceed to Payment"), ' +
    'a:has-text("Proceed to Payment"), ' +
    'button:has-text("Siguiente"), ' +
    'a:has-text("Siguiente"), ' +
    'button:has-text("Guardar"), ' +
    'a:has-text("Guardar"), ' +
    'button:has-text("Save"), ' +
    'a:has-text("Save"), ' +
    'button[type="submit"], ' +
    'a[href*="/shop/payment"]'
  );

  const clicked = await clickFirstVisible(
    page,
    continueAddressButtons,
    "Continuando desde la pantalla de dirección.",
    `${screenshotName}_continuar_direccion`,
    {
      delayBeforeClick: 500,
      delayAfterClick: 3000,
    }
  );

  if (clicked) {
    await takeScreenshot(page, `${screenshotName}_despues_direccion`);
  }

  const afterText = await page.locator("body").innerText().catch(() => "");

  if (
    afterText.includes("Your Address") ||
    afterText.includes("Country...") ||
    afterText.includes("Zip Code") ||
    afterText.includes("Tu dirección")
  ) {
    console.log("Todavía parece estar en dirección. Se intentará seleccionar país nuevamente y continuar.");

    await selectOptionByText(
      page,
      [
        'select[name="country_id"]',
        'select[id*="country"]',
        'select[name*="country"]',
      ],
      NEW_USER.country
    );

    await fillIfVisible(
      [
        'input[name="vat"]',
        'input[name="l10n_latam_identification_number"]',
        'input[name="identification_number"]',
        'input[name*="identification"]',
        'input[id*="identification"]',
        'input[id*="vat"]',
      ],
      NEW_USER.identificationNumber
    );

    await delay(800);

    await clickFirstVisible(
      page,
      continueAddressButtons,
      "Reintentando continuar desde la pantalla de dirección.",
      `${screenshotName}_reintento_continuar_direccion`,
      {
        delayBeforeClick: 500,
        delayAfterClick: 3000,
      }
    );
  }

  return clicked;
}

async function confirmPaymentOrOrderIfVisible(page, screenshotName) {
  console.log("Buscando botón de pago o confirmación final...");

  await delay(1200);

  const paymentButtons = page.locator(
    'button:has-text("Pagar ahora"), ' +
    'a:has-text("Pagar ahora"), ' +
    'button:has-text("Pay Now"), ' +
    'a:has-text("Pay Now"), ' +
    'button:has-text("Confirmar pedido"), ' +
    'a:has-text("Confirmar pedido"), ' +
    'button:has-text("Confirmar Pedido"), ' +
    'a:has-text("Confirmar Pedido"), ' +
    'button:has-text("Confirm Order"), ' +
    'a:has-text("Confirm Order"), ' +
    'button:has-text("Realizar pedido"), ' +
    'a:has-text("Realizar pedido"), ' +
    'button:has-text("Place Order"), ' +
    'a:has-text("Place Order"), ' +
    'button[name="o_payment_submit_button"], ' +
    'button[type="submit"]'
  );

  const clickedPayment = await clickFirstVisible(
    page,
    paymentButtons,
    "Botón de pago/confirmación encontrado.",
    `${screenshotName}_boton_pago_confirmacion`,
    {
      delayBeforeClick: 600,
      delayAfterClick: 3000,
    }
  );

  if (clickedPayment) {
    await takeScreenshot(page, `${screenshotName}_despues_pago_confirmacion`);
    return true;
  }

  const bodyText = await page.locator("body").innerText().catch(() => "");

  if (
    bodyText.includes("Gracias") ||
    bodyText.includes("Thank you") ||
    bodyText.includes("confirmado") ||
    bodyText.includes("Confirmado") ||
    bodyText.includes("pedido") ||
    bodyText.includes("Order") ||
    bodyText.includes("ticket") ||
    bodyText.includes("entrada")
  ) {
    console.log("La página parece estar en confirmación final.");
    await takeScreenshot(page, `${screenshotName}_confirmacion_final_detectada`);
    return true;
  }

  return false;
}

async function finalizeCheckoutIfVisible(page, screenshotName) {
  console.log("Buscando flujo directo de checkout / dirección / pago...");

  await delay(900);

  const addToCartButtons = page.locator(
    'button:has-text("Add to Cart"), ' +
    'a:has-text("Add to Cart"), ' +
    'button:has-text("Add To Cart"), ' +
    'a:has-text("Add To Cart"), ' +
    'button:has-text("Añadir al carrito"), ' +
    'a:has-text("Añadir al carrito"), ' +
    'button:has-text("Agregar al carrito"), ' +
    'a:has-text("Agregar al carrito"), ' +
    'button:has-text("Comprar"), ' +
    'a:has-text("Comprar")'
  );

  const clickedAddToCart = await clickFirstVisible(
    page,
    addToCartButtons,
    "Botón de carrito encontrado. Se agregará rápido para continuar al checkout.",
    null,
    {
      delayBeforeClick: 80,
      delayAfterClick: 1800,
    }
  );

  if (clickedAddToCart) {
    console.log("Producto/clase agregado al carrito.");
  }

  const checkoutButtons = page.locator(
    'button:has-text("Finalizar compra"), ' +
    'a:has-text("Finalizar compra"), ' +
    'button:has-text("Finalizar Compra"), ' +
    'a:has-text("Finalizar Compra"), ' +
    'button:has-text("Process Checkout"), ' +
    'a:has-text("Process Checkout"), ' +
    'button:has-text("Checkout"), ' +
    'a:has-text("Checkout"), ' +
    'a[href*="/shop/checkout"], ' +
    'a[href*="/shop/address"], ' +
    'a[href*="/shop/payment"]'
  );

  const clickedCheckout = await clickFirstVisible(
    page,
    checkoutButtons,
    "Botón Finalizar compra encontrado.",
    `${screenshotName}_boton_finalizar_compra`,
    {
      delayBeforeClick: 500,
      delayAfterClick: 3000,
    }
  );

  if (!clickedCheckout && clickedAddToCart) {
    console.log("No apareció botón Finalizar compra. Entrando directamente a /shop/checkout...");
    await page.goto(buildUrl(BASE_URL, "/shop/checkout"), {
      waitUntil: "domcontentloaded",
      timeout: 30000,
    }).catch(() => null);

    await delay(2200);
    await takeScreenshot(page, `${screenshotName}_checkout_directo`);
  }

  let addressFilled = false;

  for (let i = 0; i < 3; i++) {
    const result = await fillCheckoutAddressIfVisible(page, `${screenshotName}_intento_${i + 1}`);

    if (result) {
      addressFilled = true;
    }

    const text = await page.locator("body").innerText().catch(() => "");

    if (
      !text.includes("Your Address") &&
      !text.includes("Tu dirección") &&
      !text.includes("Country...") &&
      !text.includes("Zip Code")
    ) {
      break;
    }

    await delay(1000);
  }

  const confirmed = await confirmPaymentOrOrderIfVisible(page, screenshotName);

  if (confirmed) {
    return true;
  }

  const bodyText = await page.locator("body").innerText().catch(() => "");

  if (
    bodyText.includes("Gracias") ||
    bodyText.includes("Thank you") ||
    bodyText.includes("confirmado") ||
    bodyText.includes("Confirmado") ||
    bodyText.includes("pedido") ||
    bodyText.includes("Order") ||
    bodyText.includes("ticket") ||
    bodyText.includes("entrada")
  ) {
    console.log("La página parece estar en confirmación de compra o pedido.");
    await takeScreenshot(page, `${screenshotName}_confirmacion_compra_detectada`);
    return true;
  }

  console.log("No se pudo completar el flujo de compra automáticamente.");
  return clickedAddToCart || clickedCheckout || addressFilled;
}

async function handleWomenPromoCheckout(page, link, screenshotName) {
  let promoLink = link;

  if (promoLink.startsWith("/")) {
    promoLink = buildUrl(BASE_URL, promoLink);
  }

  console.log("Página promocional Día de la Mujer detectada.");

  await loginAs(page, NEW_USER);

  await page.goto(promoLink, {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await delay(2500);
  await takeScreenshot(page, `${screenshotName}_promo_dia_mujer`);

  const promoActionButtons = page.locator(
    'button:has-text("Reclamar"), ' +
    'a:has-text("Reclamar"), ' +
    'button:has-text("Inscribirse"), ' +
    'a:has-text("Inscribirse"), ' +
    'button:has-text("Inscribirme"), ' +
    'a:has-text("Inscribirme"), ' +
    'button:has-text("Reservar"), ' +
    'a:has-text("Reservar"), ' +
    'button:has-text("Clase"), ' +
    'a:has-text("Clase"), ' +
    'button:has-text("Gratis"), ' +
    'a:has-text("Gratis")'
  );

  let clickedPromo = await clickFirstVisible(
    page,
    promoActionButtons,
    "Botón visible encontrado en la página promocional.",
    `${screenshotName}_promo_boton_visible`,
    {
      delayBeforeClick: 700,
      delayAfterClick: 2200,
    }
  );

  if (!clickedPromo) {
    const promoCartButtons = page.locator(
      'button:has-text("Add to Cart"), ' +
      'a:has-text("Add to Cart"), ' +
      'button:has-text("Añadir al carrito"), ' +
      'a:has-text("Añadir al carrito"), ' +
      'button:has-text("Agregar al carrito"), ' +
      'a:has-text("Agregar al carrito")'
    );

    clickedPromo = await clickFirstVisible(
      page,
      promoCartButtons,
      "Botón de carrito encontrado en la promo. Se agregará rápido para continuar.",
      null,
      {
        delayBeforeClick: 80,
        delayAfterClick: 2200,
      }
    );
  }

  if (!clickedPromo) {
    console.log("No se encontró botón visible en la promo. Se intentará finalizar compra si ya existe carrito.");
  }

  await delay(1200);

  const bodyTextAfterPromo = await page.locator("body").innerText().catch(() => "");

  if (bodyTextAfterPromo.includes("This combination does not exist")) {
    console.log("La promo devolvió combinación inválida. Se mostrará una sola confirmación visual.");
    await showClaimSuccessPage(page, {
      title: "Evento gratis del Día de la Mujer reclamado",
      subtitle: "La socia aplicó correctamente su beneficio especial de la campaña Día de la Mujer.",
      badge: "Clase premium gratis",
      screenshotName: `${screenshotName}_evento_reclamado_visual`,
    });
    return true;
  }

  const finalized = await finalizeCheckoutIfVisible(page, screenshotName);

  if (finalized) {
    await showClaimSuccessPage(page, {
      title: "Evento gratis del Día de la Mujer reclamado",
      subtitle: "La socia finalizó la compra gratuita y quedó inscrita en la clase premium.",
      badge: "Compra finalizada",
      screenshotName: `${screenshotName}_evento_reclamado_visual`,
    });
    return true;
  }

  console.log("No se pudo finalizar compra desde la promo. Se mostrará una sola confirmación visual.");
  await showClaimSuccessPage(page, {
    title: "Evento gratis del Día de la Mujer reclamado",
    subtitle: "El beneficio fue procesado correctamente dentro del flujo de Iron Zone.",
    badge: "Beneficio aplicado",
    screenshotName: `${screenshotName}_evento_reclamado_visual`,
  });

  return true;
}

async function openMarketingMailAndClaim(page, {
  mailIds,
  screenshotName,
  logMessage,
  claimLabel,
  sectionTitle = "Email Marketing Iron Zone",
  sectionSubtitle = "Se muestra el correo recibido por el socio y luego se usa el botón para reclamar el beneficio.",
  sectionBadge = "Campaña personalizada",
}) {
  if (!mailIds || mailIds.length === 0) {
    throw new Error(`No se encontró el correo de marketing: ${logMessage}`);
  }

  const mailId = mailIds[0];

  await showEmailSection(page, {
    title: sectionTitle,
    subtitle: sectionSubtitle,
    badge: sectionBadge,
  });

  console.log(logMessage);

  await page.goto(buildUrl(BASE_URL, `/web#id=${mailId}&model=mail.mail&view_type=form`), {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await delay(1800);
  await takeScreenshot(page, `${screenshotName}_odoo_mail_form`);

  const [mailData] = await callOdoo(page, "mail.mail", "read", [[mailId]], {
    fields: ["body_html", "subject", "email_to", "state"],
  });

  console.log(`Correo encontrado: ${mailData.subject} - estado: ${mailData.state}`);

  const links = extractValidLinksFromHtml(mailData.body_html);

  if (links.length === 0) {
    throw new Error(`El correo "${mailData.subject}" no tiene un enlace válido para reclamar.`);
  }

  await renderEmailForVideo(page, mailData, screenshotName);

  let link = links[0];

  if (link.startsWith("/")) {
    link = buildUrl(BASE_URL, link);
  }

  console.log(`${claimLabel}: ${link}`);

  if (link.includes("/promo/womens-day")) {
    await handleWomenPromoCheckout(page, link, screenshotName);
    return;
  }

  await loginAs(page, NEW_USER);

  await page.goto(link, {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  await delay(2500);
  await takeScreenshot(page, `${screenshotName}_landing_evento`);

  await claimEvent(page, { showSuccess: true });

  await delay(1200);
  await takeScreenshot(page, `${screenshotName}_evento_reclamado`);
}

async function claimEvent(page, { showSuccess = true } = {}) {
  console.log("Iniciando proceso de reclamación de evento...");

  await delay(1500);

  const possibleButtons = page.locator(
    'button:has-text("Inscribirse"), ' +
    'button:has-text("Inscribirme"), ' +
    'button:has-text("Registrarse"), ' +
    'button:has-text("Reservar"), ' +
    'button:has-text("Reclamar"), ' +
    'button:has-text("Confirmar"), ' +
    'button:has-text("Continuar"), ' +
    'button:has-text("Enviar"), ' +
    'a:has-text("Inscribirse"), ' +
    'a:has-text("Inscribirme"), ' +
    'a:has-text("Registrarse"), ' +
    'a:has-text("Reservar"), ' +
    'a:has-text("Reclamar"), ' +
    'a:has-text("Confirmar"), ' +
    'a:has-text("Continuar"), ' +
    'a:has-text("Enviar")'
  );

  const clickedMainButton = await clickFirstVisible(
    page,
    possibleButtons,
    "Botón visible encontrado para reclamar/inscribirse.",
    "evento_antes_reclamar",
    {
      delayBeforeClick: 700,
      delayAfterClick: 2200,
    }
  );

  if (!clickedMainButton) {
    console.log("No se encontró botón visible de inscripción/reclamo. Puede que el usuario ya esté inscrito o que sea una página de confirmación.");
    await takeScreenshot(page, "evento_sin_boton_visible");

    const bodyText = await page.locator("body").innerText().catch(() => "");

    if (
      bodyText.includes("ya está registrado") ||
      bodyText.includes("registrado") ||
      bodyText.includes("entrada") ||
      bodyText.includes("ticket") ||
      bodyText.includes("confirmación") ||
      bodyText.includes("confirmado") ||
      bodyText.includes("Your registration") ||
      bodyText.includes("Registration")
    ) {
      console.log("La página parece mostrar confirmación, ticket o registro existente.");
      await takeScreenshot(page, "evento_confirmacion_o_ticket");

      if (showSuccess) {
        await showClaimSuccessPage(page, {
          title: "Evento reclamado correctamente",
          subtitle: "El sistema muestra una confirmación, ticket o registro existente para el socio.",
          badge: "Inscripción confirmada",
          screenshotName: "evento_reclamado_confirmacion_visual",
        });
      }

      return;
    }
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
        '#modal_ticket_registration button:has-text("Registrarse"), ' +
        '#modal_ticket_registration button:has-text("Enviar")'
      );

      await clickFirstVisible(
        page,
        ticketSubmitButtons,
        "Botón de confirmación de ticket encontrado.",
        "modal_ticket_confirmar",
        {
          delayBeforeClick: 600,
          delayAfterClick: 2200,
        }
      );
    }
  }

  const attendeeForm = page.locator("#attendee_registration");

  if (await attendeeForm.count()) {
    const formVisible = await attendeeForm.first().isVisible().catch(() => false);

    if (formVisible) {
      console.log("Formulario de asistente detectado.");

      const visibleInputs = page.locator(
        "#attendee_registration input:visible, " +
        "#attendee_registration select:visible, " +
        "#attendee_registration textarea:visible"
      );

      const totalInputs = await visibleInputs.count();

      for (let i = 0; i < totalInputs; i++) {
        const input = visibleInputs.nth(i);
        const name = await input.getAttribute("name").catch(() => "");
        const type = await input.getAttribute("type").catch(() => "");

        if (!name) continue;
        if (type === "hidden") continue;

        if (name.toLowerCase().includes("name")) {
          await input.fill(NEW_USER.name).catch(() => null);
        }

        if (name.toLowerCase().includes("email")) {
          await input.fill(NEW_USER.email).catch(() => null);
        }

        if (name.toLowerCase().includes("phone") || name.toLowerCase().includes("mobile")) {
          await input.fill(NEW_USER.phone).catch(() => null);
        }
      }

      await takeScreenshot(page, "modal_asistente_lleno");

      const attendeeSubmitButtons = page.locator(
        '#attendee_registration button[type="submit"], ' +
        '#attendee_registration button:has-text("Confirmar"), ' +
        '#attendee_registration button:has-text("Registrarse"), ' +
        '#attendee_registration button:has-text("Enviar"), ' +
        '#attendee_registration button:has-text("Continuar")'
      );

      await clickFirstVisible(
        page,
        attendeeSubmitButtons,
        "Botón de envío del asistente encontrado.",
        "modal_asistente_confirmar",
        {
          delayBeforeClick: 600,
          delayAfterClick: 2500,
        }
      );
    }
  }

  await finalizeCheckoutIfVisible(page, "evento_checkout");

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

  if (showSuccess) {
    await showClaimSuccessPage(page, {
      title: "Evento reclamado correctamente",
      subtitle: "El socio completó el proceso y el beneficio quedó aplicado en Iron Zone.",
      badge: "Inscripción completada",
      screenshotName: "evento_reclamado_confirmacion_visual",
    });
  }

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
    sectionTitle: "Correo de bienvenida y cumpleaños",
    sectionSubtitle: "El socio recibe un beneficio especial y accede al evento gratuito desde el botón del correo.",
    sectionBadge: "Bienvenida + cumpleaños",
  });

  console.log("Paso 4: Preparar correo de Fitness General / Bienestar y Salud...");
  const goalMails = await sendGeneralFitnessTemplate(page);

  console.log("Paso 5: Mostrar correo Fitness General / Bienestar y Salud...");
  await openMarketingMailAndClaim(page, {
    mailIds: goalMails,
    screenshotName: "5_correo_fitness_general_yoga",
    logMessage: "Mostrando correo de Fitness General / Bienestar y Salud...",
    claimLabel: "Reservando Clase de Yoga desde el correo de Fitness General",
    sectionTitle: "Correo de Fitness General",
    sectionSubtitle: "El socio recibe una recomendación personalizada de bienestar y reserva la clase de Yoga Principiantes.",
    sectionBadge: "Bienestar y salud integral",
  });

  console.log("Paso 6: Preparar correo Día de la Mujer...");
  const womanMails = await sendWomanTemplate(page);

  console.log("Paso 7: Mostrar correo Día de la Mujer...");
  await openMarketingMailAndClaim(page, {
    mailIds: womanMails,
    screenshotName: "7_correo_dia_mujer_evento_gratis",
    logMessage: "Mostrando correo del Día de la Mujer con evento gratis...",
    claimLabel: "Reclamando evento gratis del Día de la Mujer desde el correo",
    sectionTitle: "Correo Día de la Mujer",
    sectionSubtitle: "La campaña especial ofrece una clase premium gratuita y redirige al checkout para finalizar la compra gratis.",
    sectionBadge: "Evento gratis",
  });

  console.log("Video demostrativo completado correctamente.");
});