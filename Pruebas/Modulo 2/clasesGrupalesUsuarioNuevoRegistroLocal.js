import {
    LOCAL_BASE_URL,
    buildUrl,
    delay,
    fillIfVisible,
    loginAs,
    pageText,
    runPlaywrightFlow,
    tomarCaptura,
} from "./testHelpers.js";
import {
    createAdminSession,
    ensurePortalUser,
} from "./odooSetup.js";

const timestamp = Date.now();
const NEW_CLASS_USER = {
    name: `Cliente QA Clase ${timestamp}`,
    email: `cliente.qa.clase.${timestamp}@ironzone.test`,
    password: "admin123",
    phone: "0991234577",
    gender: "male",
    vat: "1804888764",
};

async function prepareClassUser() {
    const session = await createAdminSession(LOCAL_BASE_URL);
    await ensurePortalUser(session, NEW_CLASS_USER);
}

async function openRegisterableEvent(page) {
    await page.goto(buildUrl(LOCAL_BASE_URL, "/event"), { waitUntil: "networkidle", timeout: 60000 });
    const links = await page.locator("a[href*='/event/']").evaluateAll((anchors) => {
        const seen = new Set();
        return anchors
            .map((anchor) => ({
                href: anchor.getAttribute("href") || "",
                text: (anchor.innerText || "").replace(/\s+/g, " ").trim(),
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
            });
    });

    for (const link of links) {
        await page.goto(buildUrl(LOCAL_BASE_URL, link.href), { waitUntil: "networkidle", timeout: 60000 });
        const detailText = await pageText(page);
        const hasForm = await page.locator("#registration_form").count();
        const isClosed = /registros cerrados|registration closed|sold out|agotado/i.test(detailText);
        if (hasForm && !isClosed) {
            return;
        }
    }
    throw new Error("No se encontro una clase grupal con registro activo.");
}

async function registerInClass(page) {
    await page.goto(buildUrl(LOCAL_BASE_URL, "/my"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "2_usuario_nuevo_portal");

    await page.goto(buildUrl(LOCAL_BASE_URL, "/event"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "3_clases_grupales_disponibles");

    await openRegisterableEvent(page);
    await tomarCaptura(page, "4_detalle_clase_grupal");

    await page.evaluate(() => {
        const modal = document.querySelector("#modal_ticket_registration");
        if (!modal) return;
        modal.classList.add("show");
        modal.style.display = "block";
        modal.removeAttribute("aria-hidden");
        document.body.classList.add("modal-open");
    });
    const ticketSelect = page.locator("#modal_ticket_registration select[name^='nb_register-']").first();
    if (await ticketSelect.count()) {
        await ticketSelect.selectOption("1").catch(() => null);
    }
    await page.locator("#modal_ticket_registration button[type='submit']").first().click();
    await page.waitForSelector("#attendee_registration, input[name*='email']", { timeout: 20000 });

    await fillIfVisible(page, "#attendee_registration input[name*='name']", NEW_CLASS_USER.name);
    await fillIfVisible(page, "#attendee_registration input[name*='email']", NEW_CLASS_USER.email);
    await fillIfVisible(page, "#attendee_registration input[name*='phone']", NEW_CLASS_USER.phone);
    await tomarCaptura(page, "5_datos_asistente");

    await page.locator("#attendee_registration button[type='submit']").first().click();
    await delay(3500);
    await tomarCaptura(page, "6_registro_clase_finalizado");

    const text = await pageText(page);
    if (!/confirmation|gracias|pedido|confirmado|carrito|cart|checkout|payment/i.test(`${page.url()} ${text}`)) {
        throw new Error(`No se detecto estado final valido tras registrar clase. URL=${page.url()}`);
    }
}

await prepareClassUser();

runPlaywrightFlow("usuario nuevo se registra en clase grupal local", async (page) => {
    await loginAs(page, LOCAL_BASE_URL, NEW_CLASS_USER);
    await registerInClass(page);
}).catch((error) => {
    console.error("QA Eval FALLIDO: usuario nuevo se registra en clase grupal local", error);
    process.exitCode = 1;
});
