import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

export const TEST_USER = {
    name: process.env.IRONZONE_TEST_NAME || "Cliente Portal 04",
    email: process.env.IRONZONE_TEST_EMAIL || "pruebasjos04@gmail.com",
    password: process.env.IRONZONE_TEST_PASSWORD || "admin123",
    phone: process.env.IRONZONE_TEST_PHONE || "0991234501",
};

export const LOCAL_BASE_URL = process.env.IRONZONE_LOCAL_URL || "http://localhost:8069";
export const DEPLOYED_BASE_URL = process.env.IRONZONE_DEPLOYED_URL || "https://iron-zone.stratiumhub.com";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const evidenceDir = path.join(moduleDir, "evidencias");

export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export function buildUrl(baseUrl, route) {
    return new URL(route, baseUrl).toString();
}

export function ensureEvidenceDir() {
    if (!fs.existsSync(evidenceDir)) {
        fs.mkdirSync(evidenceDir, { recursive: true });
    }
    return evidenceDir;
}

export async function tomarCaptura(page, nombreFase) {
    const ruta = path.join(ensureEvidenceDir(), `${Date.now()}_${nombreFase}.png`);
    try {
        await page.screenshot({ path: ruta, fullPage: false });
        console.log(`Captura guardada: ${ruta}`);
    } catch (error) {
        console.log(`Advertencia: no se pudo guardar captura de ${nombreFase} (${error.message})`);
    }
}

export async function runPlaywrightFlow(nombre, testFn) {
    console.log(`Inicializando Playwright para ${nombre}...`);
    ensureEvidenceDir();
    const headless = process.env.HEADLESS !== "false";
    const browser = await chromium.launch({ headless });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        await testFn(page, context);
        console.log(`QA Eval SUPERADO: ${nombre}`);
    } finally {
        console.log("Cerrando navegador...");
        await browser.close();
    }
}

export async function pageText(page) {
    return (await page.locator("body").innerText({ timeout: 15000 })).replace(/\s+/g, " ").trim();
}

export async function login(page, baseUrl) {
    console.log(`Iniciando sesion con ${TEST_USER.email}...`);
    await page.goto(buildUrl(baseUrl, "/web/login"), { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForSelector("#login", { state: "visible", timeout: 20000 });
    await page.fill("#login", TEST_USER.email);
    await page.fill("#password", TEST_USER.password);
    await Promise.all([
        page.waitForURL((url) => !url.href.includes("/web/login"), { timeout: 60000 }).catch(() => null),
        page.locator(".oe_login_form button[type='submit'], button[type='submit'].btn-primary").first().click(),
    ]);
    await page.waitForLoadState("domcontentloaded", { timeout: 60000 }).catch(() => null);
    await delay(1000);

    if (page.url().includes("/web/login")) {
        const text = await pageText(page);
        throw new Error(`No se pudo iniciar sesion con ${TEST_USER.email}. Texto visible: ${text.slice(0, 300)}`);
    }
    await tomarCaptura(page, "1_login_exitoso");
}

export async function goToPortalSubscriptions(page, baseUrl) {
    await page.goto(buildUrl(baseUrl, "/my/subscriptions"), { waitUntil: "networkidle", timeout: 60000 });
    const text = await pageText(page);
    return {
        text,
        hasSubscription: /plan vigente|suscripciones|suscripcion activa|activa|borrador|pendiente/i.test(text),
    };
}

export async function openSubscriptionProduct(page, baseUrl) {
    console.log("Abriendo producto de suscripcion...");
    await page.goto(buildUrl(baseUrl, "/shop"), { waitUntil: "networkidle", timeout: 60000 });
    const productHref = await page.locator("a[href*='/shop/']").evaluateAll((links) => {
        const candidates = links
            .map((link) => ({
                href: link.getAttribute("href") || "",
                text: (link.innerText || link.closest(".oe_product, .card, article")?.innerText || "").toLowerCase(),
            }))
            .filter((item) => (
                item.href.includes("/shop/")
                && !item.href.includes("/shop/cart")
                && !item.href.includes("/shop/category")
                && !item.href.includes("/shop/change_pricelist")
                && !item.href.endsWith("/shop")
                && (item.text.includes("suscripcion") || item.text.includes("mensual") || item.text.includes("anual"))
            ));
        return candidates[0]?.href || "";
    });
    if (!productHref) {
        throw new Error("No se encontro un producto de suscripcion en /shop.");
    }
    await page.goto(buildUrl(baseUrl, productHref), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "2_producto_suscripcion");
}

export async function attemptSubscriptionCartUpdate(page, baseUrl) {
    await openSubscriptionProduct(page, baseUrl);
    await page.locator("#add_to_cart, .js_check_product.a-submit, a.a-submit").first().click({ timeout: 20000 });
    await delay(3000);
    await page.goto(buildUrl(baseUrl, "/shop/cart"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "3_carrito_suscripcion");
    const text = await pageText(page);
    const hasSubscriptionLine = /suscripcion mensual|suscripcion anual|suscripción mensual|suscripción anual/i.test(text);
    const isEmpty = /your cart is empty|tu carrito esta vacio|tu carrito está vacío/i.test(text);
    const hasRestriction = /solo puedes comprar una suscripci|ya tienes una suscripci|suscripci.n activa|suscripci.n pendiente/i.test(text);
    return { text, hasSubscriptionLine, isEmpty, hasRestriction };
}

export async function assertSubscriptionFlow(page, baseUrl) {
    const portalState = await goToPortalSubscriptions(page, baseUrl);
    await tomarCaptura(page, "2_portal_suscripciones");
    const cartState = await attemptSubscriptionCartUpdate(page, baseUrl);

    if (portalState.hasSubscription && (cartState.isEmpty || cartState.hasRestriction || !cartState.hasSubscriptionLine)) {
        console.log("Resultado esperado: el usuario ya tiene suscripcion, por eso no se agrega otra al carrito.");
        return;
    }
    if (!portalState.hasSubscription && cartState.hasSubscriptionLine) {
        console.log("Resultado esperado: el usuario sin suscripcion puede agregar una unica suscripcion al carrito.");
        return;
    }
    throw new Error(`Flujo de suscripcion inconsistente. Portal=${portalState.hasSubscription}, Carrito=${cartState.text.slice(0, 500)}`);
}

export async function getEventLinks(page, baseUrl) {
    await page.goto(buildUrl(baseUrl, "/event"), { waitUntil: "networkidle", timeout: 60000 });
    return page.locator("a[href*='/event/']").evaluateAll((links) => {
        const seen = new Set();
        return links
            .map((link) => ({
                href: link.getAttribute("href") || "",
                text: (link.innerText || "").replace(/\s+/g, " ").trim(),
            }))
            .filter((item) => (
                item.href.includes("/event/")
                && item.href.includes("/register")
                && !item.href.includes("/event/page/")
            ))
            .filter((item) => {
                if (seen.has(item.href)) return false;
                seen.add(item.href);
                return true;
            })
            .slice(0, 12);
    });
}

export async function openFirstAvailableEvent(page, baseUrl) {
    const links = await getEventLinks(page, baseUrl);
    if (!links.length) {
        throw new Error("No se encontraron eventos disponibles en /event.");
    }

    for (const link of links) {
        if (/registered|registrado|registrada/i.test(link.text)) {
            continue;
        }
        await page.goto(buildUrl(baseUrl, link.href), { waitUntil: "networkidle", timeout: 60000 });
        const text = await pageText(page);
        if (!/ya tienes un boleto|solo puedes tener un boleto|already registered|ya estas registrado|ya estás registrado/i.test(text)) {
            console.log(`Evento seleccionado: ${link.text || link.href}`);
            await tomarCaptura(page, "2_detalle_evento");
            return link;
        }
    }

    console.log("Todos los eventos revisados parecen registrados o bloqueados para este usuario.");
    await tomarCaptura(page, "2_eventos_bloqueados");
    return null;
}

async function forceShowModal(page, selector) {
    await page.locator(selector).waitFor({ state: "attached", timeout: 20000 });
    await page.evaluate((modalSelector) => {
        const modal = document.querySelector(modalSelector);
        if (!modal) return;
        modal.classList.add("show");
        modal.style.display = "block";
        modal.removeAttribute("aria-hidden");
        document.body.classList.add("modal-open");
    }, selector);
}

export async function startEventRegistration(page, baseUrl) {
    const selectedEvent = await openFirstAvailableEvent(page, baseUrl);
    if (!selectedEvent) {
        console.log("Resultado esperado: no hay eventos sin registro para este usuario en la pagina revisada.");
        return { status: "already_registered" };
    }
    const textBefore = await pageText(page);
    if (/ya tienes un boleto|solo puedes tener un boleto|already registered|ya estas registrado|ya estás registrado/i.test(textBefore)) {
        console.log("Resultado esperado: el usuario ya tiene un boleto para el evento seleccionado.");
        return { status: "already_registered" };
    }

    if (!(await page.locator("#registration_form").count())) {
        throw new Error("No se encontro el formulario #registration_form en el detalle del evento.");
    }

    await forceShowModal(page, "#modal_ticket_registration");
    const ticketSelect = page.locator("#modal_ticket_registration select[name^='nb_register-']").first();
    if (await ticketSelect.count()) {
        await ticketSelect.selectOption("1").catch(() => null);
    }
    await page.locator("#modal_ticket_registration button[type='submit']").first().click();
    await page.waitForSelector("#attendee_registration, input[name*='email']", { timeout: 20000 });
    await tomarCaptura(page, "3_modal_asistentes");

    const attendeeForms = await page.locator("#attendee_registration").count();
    const emailInputs = await page.locator("#attendee_registration input[name*='email']").count();
    if (!attendeeForms || emailInputs !== 1) {
        throw new Error(`El flujo actual debe generar exactamente un asistente. Formularios=${attendeeForms}, emails=${emailInputs}`);
    }

    await fillIfVisible(page, "#attendee_registration input[name*='name']", TEST_USER.name);
    await fillIfVisible(page, "#attendee_registration input[name*='email']", TEST_USER.email);
    await fillIfVisible(page, "#attendee_registration input[name*='phone']", TEST_USER.phone);
    await tomarCaptura(page, "4_asistente_completo");
    return { status: "attendee_ready" };
}

export async function finishEventRegistrationToCheckout(page) {
    if (!(await page.locator("#attendee_registration").count())) {
        return { status: "no_attendee_form" };
    }
    await Promise.all([
        page.waitForLoadState("load", { timeout: 60000 }).catch(() => null),
        page.locator("#attendee_registration button[type='submit']").first().click(),
    ]);
    await delay(4000);
    await tomarCaptura(page, "5_evento_post_registro");
    const text = await pageText(page);
    const url = page.url();
    if (
        /confirmation|registration\/success|shop\/cart|shop\/checkout|shop\/payment|payment\/status/i.test(url)
        || /gracias|thank you|pedido|confirmado|exitosa|solo puedes|ya tienes un boleto/i.test(text)
    ) {
        return { status: "accepted", url, text };
    }
    throw new Error(`No se detecto estado valido tras registrar evento. URL=${url}; texto=${text.slice(0, 500)}`);
}

export async function assertEventRegistrationFlow(page, baseUrl) {
    const started = await startEventRegistration(page, baseUrl);
    if (started.status === "already_registered") {
        return;
    }
    const finished = await finishEventRegistrationToCheckout(page);
    console.log(`Estado final del evento: ${finished.status} (${finished.url || page.url()})`);
}

export async function fillIfVisible(page, selector, value) {
    const locator = page.locator(selector).first();
    if (await locator.count()) {
        await locator.fill(value).catch(async () => {
            await locator.evaluate((input, nextValue) => {
                input.value = nextValue;
                input.dispatchEvent(new Event("input", { bubbles: true }));
                input.dispatchEvent(new Event("change", { bubbles: true }));
            }, value);
        });
    }
}

export async function assertExerciseGuideFlow(page, baseUrl) {
    await page.goto(buildUrl(baseUrl, "/exercise-guides"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "2_guias_lista");

    const guideSearch = page.locator("input[placeholder='Buscar guía'], input[placeholder='Buscar guia']").first();
    if (!(await guideSearch.count())) {
        throw new Error("No se encontro el buscador de guias.");
    }
    await guideSearch.fill("spinning");
    await Promise.all([
        page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null),
        guideSearch.evaluate((input) => {
            input.dispatchEvent(new Event("input", { bubbles: true }));
            input.dispatchEvent(new Event("change", { bubbles: true }));
            const form = input.closest("form");
            if (form) {
                form.requestSubmit();
            }
        }),
    ]);
    await delay(1500);
    await tomarCaptura(page, "3_guias_filtradas");

    const guideLinks = page.locator("a[href*='/exercise-guides/']");
    if (!(await guideLinks.count())) {
        throw new Error("No se encontraron guias despues de aplicar la busqueda.");
    }
    await Promise.all([
        page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null),
        guideLinks.first().click(),
    ]);
    await delay(1000);
    await tomarCaptura(page, "4_detalle_guia");

    const url = page.url();
    const text = await pageText(page);
    if (!url.includes("/exercise-guides/") || !/guia|guía|spinning|ejercicio|tecnica|técnica/i.test(text)) {
        throw new Error(`No se llego al detalle de guia esperado. URL=${url}; texto=${text.slice(0, 500)}`);
    }
}

export async function extractFirstEventData(page, baseUrl) {
    const links = await getEventLinks(page, baseUrl);
    if (!links.length) {
        throw new Error("No se encontraron eventos para extraer.");
    }
    await page.goto(buildUrl(baseUrl, links[0].href), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "1_evento_extraer");
    return page.evaluate(() => {
        const clean = (value) => (value || "").replace(/\s+/g, " ").trim();
        const text = clean(document.body.innerText);
        const heading = clean(document.querySelector("h1, h2")?.innerText);
        const priceMatch = text.match(/Precio:\s*([^\s]+\s*[\d.,]+)/i) || text.match(/\$\s*[\d.,]+/);
        const seatsMatch = text.match(/Cupos Disponibles:\s*(\d+)\s*\/\s*(\d+)/i);
        const dateMatch = text.match(/(\d{2}\s+[a-zA-Z]+ \s*\d{4}|\d{2}\s+[a-zA-Z]+\s+\d{4})/i);
        const timeMatch = text.match(/(\d{1,2}:\d{2}\s+\d{1,2}:\d{2})/);
        return {
            claseGrupal: {
                nombre: heading,
                entrenador: clean((text.match(/Organizer\s+([^$]+?)\s+Share/i) || [])[1]) || "Iron Zone",
                horario: clean(`${dateMatch?.[1] || ""} ${timeMatch?.[1] || ""}`) || "No especificado",
                cupoMaximo: seatsMatch ? Number(seatsMatch[2]) : 0,
                cupoDisponible: seatsMatch ? Number(seatsMatch[1]) : 0,
                salaEspacio: clean((text.match(/Location\s+(.+?)\s+Get directions/i) || [])[1]) || "No especificado",
                nivelDificultad: "No especificado",
                precio: clean(priceMatch?.[1] || priceMatch?.[0] || ""),
            },
        };
    });
}
