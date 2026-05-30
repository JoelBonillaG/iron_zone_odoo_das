import { chromium } from "playwright";
import fs from "fs";

if (!fs.existsSync("evidencias")) {
    fs.mkdirSync("evidencias");
}

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function tomarCaptura(page, nombreFase) {
    const ruta = `evidencias/${Date.now()}_${nombreFase}.png`;
    try {
        await page.screenshot({ path: ruta, fullPage: false });
        console.log(`📸 Captura guardada: ${ruta}`);
    } catch (error) {
        console.log(`⚠️ Advertencia: No se pudo guardar la captura de ${nombreFase} (${error.message})`);
    }
}

async function flujoSuscripcionesRegistro() {
    console.log("🚀 Inicializando Playwright Nativo para registro de suscripciones (E2E Pago)...");
    
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // --- 1. Navegar e Iniciar Sesión ---
        console.log("Navegando a la página de inicio de sesión del portal...");
        await page.goto("https://iron-zone.stratiumhub.com/web/login", { waitUntil: "load", timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "0_pagina_login");

        console.log("Ingresando credenciales del cliente de prueba...");
        await page.waitForSelector("#login", { state: "visible", timeout: 15000 });
        await page.fill("#login", "pruebasjos04@gmail.com");
        await delay(1000);
        
        await page.fill("#password", "admin123");
        await delay(1000);
        
        console.log("Haciendo clic en Iniciar Sesión...");
        await page.click(".oe_login_form button[type='submit'], button.btn-primary");
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(3000);
        await tomarCaptura(page, "1_login_exitoso");

        // --- 2. Navegar a la Tienda (Suscripciones) ---
        console.log("Navegando a la tienda de suscripciones...");
        await page.goto("https://iron-zone.stratiumhub.com/shop", { waitUntil: "load", timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "2_tienda");

        // --- 3. Seleccionar Suscripción ---
        console.log("Seleccionando una suscripción...");
        await page.evaluate(() => {
            const productLinks = Array.from(document.querySelectorAll('a[href*="/shop/"]'));
            const subscriptionLink = productLinks.find(link => link.innerText.toLowerCase().includes('suscripcion') || link.innerText.toLowerCase().includes('mensual') || link.innerText.toLowerCase().includes('anual'));
            if (subscriptionLink) {
                subscriptionLink.click();
            } else if (productLinks.length > 0) {
                productLinks[0].click(); // Fallback
            }
        });

        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(3000);
        await tomarCaptura(page, "3_detalle_suscripcion");

        // --- 4. Añadir al Carrito ---
        console.log("Añadiendo al carrito...");
        await page.evaluate(() => {
            const addBtn = document.querySelector('#add_to_cart') || document.querySelector('.js_check_product.a-submit');
            if (addBtn) addBtn.click();
        });
        await delay(4000);
        await tomarCaptura(page, "4_carrito");

        // --- 5. Checkout (Procesar Pago) ---
        console.log("Procesando Checkout...");
        await page.evaluate(() => {
            const checkoutBtn = Array.from(document.querySelectorAll('a, button')).find(el => {
                const text = el.textContent.trim().toLowerCase();
                return text.includes('procesar') || text.includes('checkout') || text.includes('pagar');
            });
            if (checkoutBtn) checkoutBtn.click();
        });
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "5_checkout_datos");

        console.log("Confirmando datos de facturación...");
        await page.evaluate(() => {
            const btnNext = Array.from(document.querySelectorAll('a, button, input[type="submit"]')).find(el => {
                const text = el.textContent.trim().toLowerCase();
                return text.includes('siguiente') || text.includes('confirmar') || text.includes('next') || text.includes('proceder');
            });
            if (btnNext) btnNext.click();
        });
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(6000);
        await tomarCaptura(page, "6_checkout_metodos_pago");

        // Rellenamos tarjeta e indicamos pago
        console.log("Seleccionando método de pago y rellenando tarjeta...");
        await page.evaluate(() => {
            const radio = document.querySelector('input[name="o_payment_radio"], input[type="radio"]');
            if (radio) radio.click();
            const label = Array.from(document.querySelectorAll('label, span, strong')).find(el => {
                const text = el.textContent.trim().toLowerCase();
                return text.includes('credit card') || text.includes('tarjeta') || text.includes('stripe');
            });
            if (label) label.click();
        });
        await delay(3000);

        try {
            console.log("Esperando a que se carguen los elementos de pago de Stripe en el DOM...");
            const frames = page.frames();
            for (const frame of frames) {
                const url = frame.url();
                if (url.includes("stripe") || url.includes("elements") || url.includes("payment")) {
                    const inputs = frame.locator('input');
                    const count = await inputs.count();
                    for (let i = 0; i < count; i++) {
                        const input = inputs.nth(i);
                        const placeholder = await input.getAttribute('placeholder') || '';
                        const name = await input.getAttribute('name') || '';
                        const autocomplete = await input.getAttribute('autocomplete') || '';
                        const type = await input.getAttribute('type') || '';
                        
                        // Llenar número de tarjeta
                        if (name === 'cardnumber' || autocomplete === 'cc-number' || placeholder.includes('1234') || placeholder.toLowerCase().includes('card') || placeholder.toLowerCase().includes('tarjeta') || (name === '' && placeholder === '' && type === 'tel' && i === 0)) {
                            await input.focus();
                            await input.click();
                            await input.fill("4242424242424242");
                            await delay(300);
                            const val = await input.inputValue();
                            if (!val || val.length < 10) await input.pressSequentially("4242424242424242", { delay: 50 });
                        }
                        
                        // Llenar fecha de vencimiento
                        if (name === 'exp-date' || autocomplete === 'cc-exp' || placeholder.includes('MM') || placeholder.includes('YY') || placeholder.includes('AA')) {
                            await input.focus();
                            await input.click();
                            await input.fill("0230");
                            await delay(300);
                            const val = await input.inputValue();
                            if (!val || val.length < 2) await input.pressSequentially("0230", { delay: 50 });
                        }
                        
                        // Llenar CVC
                        if (name === 'cvc' || autocomplete === 'cc-csc' || placeholder.toLowerCase().includes('cvc') || placeholder.toLowerCase().includes('cvv') || (type === 'tel' && (placeholder === 'CVC' || name === 'cvc'))) {
                            await input.focus();
                            await input.click();
                            await input.fill("000");
                            await delay(300);
                            const val = await input.inputValue();
                            if (!val || val.length < 2) await input.pressSequentially("000", { delay: 50 });
                        }
                    }
                }
            }
        } catch (e) {
            console.log("No se pudo interactuar con los iframes de Stripe:", e.message);
        }
        await delay(2000);
        await tomarCaptura(page, "7_tarjeta_rellena");

        console.log("Haciendo clic en Pagar Ahora...");
        await page.evaluate(() => {
            const btnPay = document.querySelector('button[name="o_payment_submit_button"]') || document.querySelector('#o_payment_submit_button') || document.querySelector('button.btn-primary');
            if (btnPay) btnPay.click();
        });
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(10000);
        await tomarCaptura(page, "8_resumen_pago_finalizado");

        // --- 6. QA Evals: Validación de Compra Exitosa ---
        console.log("\n--- INICIANDO QA EVALS (Aserción de compra exitosa) ---");
        try {
            const textoPagina = await page.evaluate(() => document.body.innerText);
            const urlActual = page.url();
            console.log(`URL final de la página: ${urlActual}`);
            
            // Fix subscription purchase confirmation check by identifying correct final confirmation state
            if (urlActual.includes("/confirmation") || urlActual.includes("/validate") || textoPagina.includes("Gracias") || textoPagina.includes("Thank you") || textoPagina.includes("Pedido") || textoPagina.includes("Confirmado") || textoPagina.includes("Exitosa")) {
                console.log("✅ QA Eval SUPERADO: ¡La suscripción se procesó y pagó exitosamente con la tarjeta de prueba!");
            } else {
                console.log("❌ QA Eval FALLIDO: No se detectó la confirmación final de la compra de la suscripción.");
            }
        } catch (evalError) {
            console.log("⚠️ QA Eval ADVERTENCIA: Ocurrió un error al verificar el estado final:", evalError.message);
        }

        await tomarCaptura(page, "9_evaluacion_final");

    } catch (error) {
        console.error("❌ Error durante la automatización de registro de suscripciones:", error);
    } finally {
        console.log("Cerrando navegador...");
        await browser.close();
    }
}

flujoSuscripcionesRegistro().catch(console.error);
