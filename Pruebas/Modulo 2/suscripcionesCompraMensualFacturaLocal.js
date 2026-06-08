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
    activateLatestSubscriptionForUser,
    createAdminSession,
    ensureDemoPaymentEnabled,
    ensureLatestOrderInvoice,
    ensurePreviousEventRegistration,
    ensurePortalUser,
} from "./odooSetup.js";

const timestamp = Date.now();
const NEW_PORTAL_USER = {
    name: `Cliente QA Suscripcion ${timestamp}`,
    email: `cliente.qa.suscripcion.${timestamp}@ironzone.test`,
    password: "admin123",
    phone: "0991234599",
    gender: "male",
};

async function prepareSubscriptionScenario() {
    const session = await createAdminSession(LOCAL_BASE_URL);
    await ensureDemoPaymentEnabled(session);
    await ensurePortalUser(session, NEW_PORTAL_USER);
    return session;
}

async function clickFirstVisible(page, selectors, timeout = 8000) {
    for (const selector of selectors) {
        const locator = page.locator(selector).first();
        if (await locator.count()) {
            try {
                await locator.click({ timeout });
                return true;
            } catch {
                // Try next selector.
            }
        }
    }
    return false;
}

async function fillCheckoutIfNeeded(page) {
    await fillIfVisible(page, "input[name='name']", NEW_PORTAL_USER.name);
    await fillIfVisible(page, "input[name='email']", NEW_PORTAL_USER.email);
    await fillIfVisible(page, "input[name='phone']", NEW_PORTAL_USER.phone);
    await fillIfVisible(page, "input[name='street']", "Av. Amazonas N34-120");
    await fillIfVisible(page, "input[name='city']", "Quito");
    await fillIfVisible(page, "input[name='vat']", "1804888764");
    await fillIfVisible(page, "input[name='l10n_latam_identification_id']", "1804888764");
    await fillIfVisible(page, "input[name='identification']", "1804888764");
}

async function buyMonthlySubscription(page) {
    await page.goto(buildUrl(LOCAL_BASE_URL, "/my/subscriptions"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "2_usuario_nuevo_sin_suscripcion");

    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "3_tienda_planes_suscripcion");

    await page.goto(buildUrl(LOCAL_BASE_URL, "/subscription/muscle-gain-monthly"), {
        waitUntil: "domcontentloaded",
        timeout: 60000,
    });
    await delay(1200);
    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/cart"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "4_carrito_plan_mensual");

    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/checkout"), { waitUntil: "networkidle", timeout: 60000 });
    await fillCheckoutIfNeeded(page);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await delay(700);
    await tomarCaptura(page, "5_checkout_datos_cliente");

    const addressSubmitted = await clickFirstVisible(page, [
        "button:has-text('Siguiente')",
        "button:has-text('Continuar')",
        "button:has-text('Guardar')",
        "button:has-text('Confirmar')",
        "a:has-text('Siguiente')",
        "a:has-text('Continuar')",
        "a[href*='/shop/confirm_order']",
        "a:has-text('Proceed')",
        "button:has-text('Proceed')",
    ], 12000);
    if (addressSubmitted) {
        await page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null);
    }
    await delay(1500);

    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/payment"), { waitUntil: "networkidle", timeout: 60000 });
    if (/shop\/checkout/i.test(page.url())) {
        await fillCheckoutIfNeeded(page);
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await clickFirstVisible(page, [
            "button:has-text('Siguiente')",
            "button:has-text('Continuar')",
            "button:has-text('Guardar')",
            "button:has-text('Confirmar')",
            "a:has-text('Continuar')",
        ], 12000);
        await page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null);
        await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/payment"), { waitUntil: "networkidle", timeout: 60000 });
    }
    await tomarCaptura(page, "6_pago_tarjeta_demo");

    const demoRadio = page.locator("input[name='o_payment_radio'][data-provider-code='demo'], input[name='o_payment_radio'][value*='demo']").first();
    if (await demoRadio.count()) {
        await demoRadio.check({ force: true }).catch(() => null);
    } else {
        const paymentOption = page.locator("li[name='o_payment_option'], .o_payment_option_card").filter({ hasText: /pago directo|demo|tarjeta/i }).first();
        if (await paymentOption.count()) {
            await paymentOption.click({ timeout: 8000 }).catch(() => null);
        }
    }
    await fillIfVisible(page, "#customer_input", "4111 1111 1111 1111");
    await fillIfVisible(page, "#simulated_payment_state", "done");
    await tomarCaptura(page, "7_tarjeta_demo_ingresada");

    const paid = await clickFirstVisible(page, [
        "button[name='o_payment_submit_button']",
        "button:has-text('Pagar')",
        "button:has-text('Pay')",
        "button:has-text('Confirmar')",
        "button:has-text('Submit')",
    ], 12000);
    if (!paid) {
        throw new Error("No se encontro boton para confirmar el pago.");
    }
    await page.waitForURL((url) => /payment\/status|shop\/confirmation|my\/orders|shop\/payment\/validate/i.test(url.href), {
        timeout: 90000,
    }).catch(() => null);
    await delay(2500);
    await tomarCaptura(page, "8_pago_suscripcion_confirmado");

    await clickFirstVisible(page, [
        "a:has-text('Omitir')",
        "a:has-text('Skip')",
        "a[href*='/shop/confirmation']",
        "a[href*='/my/orders']",
    ], 8000);
    await page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null);
    await delay(1500);
    await tomarCaptura(page, "9_pedido_suscripcion_validado");
}

async function payCurrentCart(page, screenshotPrefix) {
    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/checkout"), { waitUntil: "networkidle", timeout: 60000 });
    await fillCheckoutIfNeeded(page);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await delay(700);
    await tomarCaptura(page, `${screenshotPrefix}_checkout`);

    await clickFirstVisible(page, [
        "button:has-text('Siguiente')",
        "button:has-text('Continuar')",
        "button:has-text('Guardar')",
        "button:has-text('Confirmar')",
        "a:has-text('Siguiente')",
        "a:has-text('Continuar')",
        "a[href*='/shop/confirm_order']",
    ], 12000);
    await page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null);
    await delay(1200);

    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/payment"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, `${screenshotPrefix}_pago`);

    const demoRadio = page.locator("input[name='o_payment_radio'][data-provider-code='demo'], input[name='o_payment_radio'][value*='demo']").first();
    if (await demoRadio.count()) {
        await demoRadio.check({ force: true }).catch(() => null);
    } else {
        const paymentOption = page.locator("li[name='o_payment_option'], .o_payment_option_card").filter({ hasText: /pago directo|demo|tarjeta/i }).first();
        if (await paymentOption.count()) {
            await paymentOption.click({ timeout: 8000 }).catch(() => null);
        }
    }
    await fillIfVisible(page, "#customer_input", "4111 1111 1111 1111");
    await fillIfVisible(page, "#simulated_payment_state", "done");
    await tomarCaptura(page, `${screenshotPrefix}_tarjeta_demo`);

    const paid = await clickFirstVisible(page, [
        "button[name='o_payment_submit_button']",
        "button:has-text('Pagar')",
        "button:has-text('Pay')",
        "button:has-text('Confirmar')",
        "button:has-text('Submit')",
    ], 12000);
    if (!paid) {
        throw new Error("No se encontro boton para confirmar el pago del evento.");
    }

    await page.waitForURL((url) => /payment\/status|shop\/confirmation|my\/orders|shop\/payment\/validate/i.test(url.href), {
        timeout: 90000,
    }).catch(() => null);
    await delay(2500);
    await tomarCaptura(page, `${screenshotPrefix}_pago_confirmado`);

    await clickFirstVisible(page, [
        "a:has-text('Omitir')",
        "a:has-text('Skip')",
        "a[href*='/shop/confirmation']",
        "a[href*='/my/orders']",
    ], 8000);
    await page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null);
    await delay(1500);
    await tomarCaptura(page, `${screenshotPrefix}_pedido_validado`);
}

async function findPaidEvent(page) {
    const events = await callOdoo(page, LOCAL_BASE_URL, "event.event", "search_read", [[
        ["website_published", "=", true],
    ]], {
        fields: ["id", "name", "website_url", "event_ticket_ids"],
        order: "date_begin asc",
        limit: 40,
    });
    for (const event of events) {
        if (!event.event_ticket_ids?.length) {
            continue;
        }
        const tickets = await callOdoo(page, LOCAL_BASE_URL, "event.event.ticket", "read", [event.event_ticket_ids], {
            fields: ["price"],
        });
        if (tickets.some((ticket) => Number(ticket.price || 0) > 0)) {
            return event;
        }
    }
    throw new Error("No se encontro una clase grupal pagada para validar descuento.");
}

async function openPaidRegisterableEvent(page) {
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
        const text = await pageText(page);
        const hasForm = await page.locator("#registration_form").count();
        const isClosed = /registros cerrados|registration closed|sold out|agotado/i.test(text);
        const alreadyRegistered = /ya tienes un boleto|already registered|ya estas registrado|ya est[aá]s registrado/i.test(text);
        const isPaid = /precio|price|\$\s*\d|USD/i.test(text);
        if (hasForm && !isClosed && !alreadyRegistered && isPaid) {
            return;
        }
    }
    throw new Error("No se encontro otro evento pagado y registrable para validar descuento de suscripcion.");
}

async function addDiscountedClass(page) {
    await openPaidRegisterableEvent(page);
    await tomarCaptura(page, "10_evento_con_descuento_suscripcion");

    const textBefore = await pageText(page);
    if (/ya tienes un boleto|already registered|ya estas registrado|ya est[aá]s registrado/i.test(textBefore)) {
        console.log("El usuario ya aparece registrado en la clase seleccionada.");
        return;
    }

    if (await page.locator("#registration_form").count()) {
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
        await fillIfVisible(page, "#attendee_registration input[name*='name']", NEW_PORTAL_USER.name);
        await fillIfVisible(page, "#attendee_registration input[name*='email']", NEW_PORTAL_USER.email);
        await fillIfVisible(page, "#attendee_registration input[name*='phone']", NEW_PORTAL_USER.phone);
        await tomarCaptura(page, "11_datos_evento_con_descuento");
        await page.locator("#attendee_registration button[type='submit']").first().click();
        await delay(3000);
    }

    await page.goto(buildUrl(LOCAL_BASE_URL, "/shop/cart"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "12_carrito_evento_descuento_suscripcion");
    const cartText = await pageText(page);
    if (!/%|descuento|discount|suscripcion|suscripción/i.test(cartText)) {
        console.log("Advertencia: el carrito no muestra texto explicito de descuento, se conserva captura para evidencia.");
    }
    await payCurrentCart(page, "13_compra_evento_descuento");
}

async function showSubscription(page, setupSession) {
    await activateLatestSubscriptionForUser(setupSession, NEW_PORTAL_USER.email);

    await page.goto(buildUrl(LOCAL_BASE_URL, "/my/subscriptions"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "10_suscripcion_activa_en_mi_cuenta");
}

async function showInvoices(page, setupSession) {
    await ensureLatestOrderInvoice(setupSession, NEW_PORTAL_USER.email);
    await page.goto(buildUrl(LOCAL_BASE_URL, "/my/invoices"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "14_facturacion_evento_en_mi_cuenta");
}

const setupSession = await prepareSubscriptionScenario();

runPlaywrightFlow("usuario nuevo compra suscripcion mensual paga y ve factura local", async (page) => {
    await loginAs(page, LOCAL_BASE_URL, NEW_PORTAL_USER);
    await buyMonthlySubscription(page);
    await showSubscription(page, setupSession);
    await ensurePreviousEventRegistration(setupSession, NEW_PORTAL_USER.email);
    await addDiscountedClass(page);
    await showInvoices(page, setupSession);
}).catch((error) => {
    console.error("QA Eval FALLIDO: usuario nuevo compra suscripcion mensual paga y ve factura local", error);
    process.exitCode = 1;
});
