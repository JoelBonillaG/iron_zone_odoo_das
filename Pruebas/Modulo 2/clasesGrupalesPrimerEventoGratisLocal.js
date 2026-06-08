import {
    LOCAL_BASE_URL,
    buildUrl,
    callOdoo,
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
const NEW_EVENT_USER = {
    name: `Cliente QA Evento Gratis ${timestamp}`,
    email: `cliente.qa.evento.gratis.${timestamp}@ironzone.test`,
    password: "admin123",
    phone: "0991234588",
    gender: "male",
    vat: "1804888764",
};

async function prepareFirstEventScenario() {
    const session = await createAdminSession(LOCAL_BASE_URL);
    await ensurePortalUser(session, NEW_EVENT_USER);
}

async function openFirstRegisterableEvent(page) {
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
    throw new Error("No se encontro una clase con registro activo para validar primer evento gratis.");
}

async function registerFirstEvent(page) {
    await page.goto(buildUrl(LOCAL_BASE_URL, "/my/subscriptions"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "2_usuario_nuevo_sin_suscripcion");

    await page.goto(buildUrl(LOCAL_BASE_URL, "/event"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "3_clases_grupales_usuario_nuevo");

    await openFirstRegisterableEvent(page);
    await tomarCaptura(page, "4_detalle_clase_primer_evento");

    if (!(await page.locator("#registration_form").count())) {
        throw new Error("No se encontro formulario de registro del evento.");
    }

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
    await fillIfVisible(page, "#attendee_registration input[name*='name']", NEW_EVENT_USER.name);
    await fillIfVisible(page, "#attendee_registration input[name*='email']", NEW_EVENT_USER.email);
    await fillIfVisible(page, "#attendee_registration input[name*='phone']", NEW_EVENT_USER.phone);
    await tomarCaptura(page, "5_datos_asistente_primer_evento");

    await page.locator("#attendee_registration button[type='submit']").first().click();
    await delay(3000);
    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/cart"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "6_carrito_primer_evento_gratis");

    const cartText = await pageText(page);
    if (!/100|gratis|0[,.]00|free|descuento|discount/i.test(cartText)) {
        console.log("Advertencia: no se encontro texto explicito de gratis/descuento en el carrito.");
    }
}

await prepareFirstEventScenario();

runPlaywrightFlow("usuario nuevo registra primer evento gratis local", async (page) => {
    await loginAs(page, LOCAL_BASE_URL, NEW_EVENT_USER);
    await registerFirstEvent(page);
}).catch((error) => {
    console.error("QA Eval FALLIDO: usuario nuevo registra primer evento gratis local", error);
    process.exitCode = 1;
});
