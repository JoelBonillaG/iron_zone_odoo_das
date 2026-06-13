import { chromium } from "playwright";
import fs from "fs";

// Asegurar la existencia del directorio de evidencias
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

async function flujoClasesGrupalesRegistro() {
    console.log("🚀 Inicializando Playwright Nativo para registro de clases (E2E Pago)...");
    
    // Lanzamos Chromium en modo visible (headless: false) para que el usuario pueda ver toda la interacción en vivo
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // --- 1. Navegar e Iniciar Sesión ---
        console.log("Navegando a la página de inicio de sesión del portal...");
        await page.goto("http://localhost:8069/web/login", { waitUntil: "load", timeout: 60000 });
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

        // --- 2. Navegar a la sección de Clases ---
        console.log("Navegando al catálogo de clases grupales...");
        await page.goto("http://localhost:8069/event", { waitUntil: "load", timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "2_catalogo_clases");

        // --- 3. Seleccionar Clase ---
        console.log("Haciendo clic en el detalle de una clase grupal en la que no estemos registrados...");
        await page.waitForSelector("a[href*='/event/']", { state: "visible", timeout: 15000 });
        
        const eventClicked = await page.evaluate(() => {
            const isValidEventLink = (link) => {
                if (!link) return false;
                const href = link.getAttribute('href') || '';
                return href.includes('/event/') && !href.includes('/page/') && href !== '/event/' && href !== '/event';
            };

            // Buscamos todas las tarjetas de eventos de Odoo (.o_wevent_event o .card)
            const cards = Array.from(document.querySelectorAll('.o_wevent_event, .card'));
            
            for (const card of cards) {
                // Buscamos un enlace válido al evento dentro de esta tarjeta
                const links = Array.from(card.querySelectorAll('a'));
                const link = links.find(isValidEventLink);
                
                if (link) {
                    const text = card.innerText || '';
                    // Si la tarjeta no indica que estamos registrados, la seleccionamos
                    if (!text.toLowerCase().includes('registrado') && !text.toLowerCase().includes('registered')) {
                        link.click();
                        return true;
                    }
                }
            }
            
            // Si todas las tarjetas están registradas o no se encontraron clases no registradas,
            // buscamos cualquier enlace a evento válido que no tenga badges de registrado cerca
            const allLinks = Array.from(document.querySelectorAll('a'));
            const eventLinks = allLinks.filter(isValidEventLink);
            
            for (const link of eventLinks) {
                const parentCard = link.closest('.o_wevent_event, .card, li, tr, .col-md-6, .col-lg-4');
                const parentText = parentCard ? (parentCard.innerText || '') : '';
                if (!parentText.toLowerCase().includes('registrado') && !parentText.toLowerCase().includes('registered')) {
                    link.click();
                    return true;
                }
            }
            
            // Fallback: clic en el primer enlace válido que encontremos en la página
            if (eventLinks.length > 0) {
                eventLinks[0].click();
                return true;
            }
            return false;
        });

        if (!eventClicked) {
            throw new Error("No se encontró ningún evento para hacer clic.");
        }

        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(3000);
        await tomarCaptura(page, "3_detalle_clase");

        // --- 4. Registro/Reserva de Cupo (Flujo Doble Modal) ---
        console.log("Iniciando flujo de inscripción...");
        
        // A. Clic en "Register" en la barra lateral para abrir el modal "Boletos"
        console.log("Abriendo modal de Boletos...");
        await page.evaluate(() => {
            const btn = document.querySelector("button.btn-primary") || document.querySelector(".o_wevent_sidebar_block button") || document.querySelector("button");
            if (btn) btn.click();
        });
        await delay(4000);
        await tomarCaptura(page, "4_modal_boletos");

        // B. Clic en el botón naranja "Registrar" del modal "Boletos"
        console.log("Haciendo clic en Registrar (modal Boletos)...");
        await page.evaluate(() => {
            const btnRegistrar = Array.from(document.querySelectorAll('button, a')).find(el => {
                const text = el.textContent.trim().toLowerCase();
                return text === 'registrar' || text.includes('registrar');
            });
            if (btnRegistrar) btnRegistrar.click();
        });
        await delay(4000);
        await tomarCaptura(page, "5_modal_asistentes");

        // C. Rellenar formulario en el modal "Asistentes"
        console.log("Completando formulario de asistentes...");
        await page.evaluate(() => {
            const nameInput = document.querySelector("input[name*='name']");
            if (nameInput) {
                nameInput.value = "Cliente Portal 04";
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            const emailInput = document.querySelector("input[name*='email']");
            if (emailInput) {
                emailInput.value = "pruebasjos04@gmail.com";
                emailInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            const phoneInput = document.querySelector("input[name*='phone']");
            if (phoneInput) {
                phoneInput.value = "0991234501";
                phoneInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        await delay(2000);
        await tomarCaptura(page, "6_asistentes_relleno");

        // D. Clic en "Ir al pago" en el modal "Asistentes"
        console.log("Confirmando inscripción (Ir al pago)...");
        await page.evaluate(() => {
            const btnConfirm = Array.from(document.querySelectorAll('button, a, input[type="submit"]')).find(el => {
                const text = el.textContent.trim().toLowerCase();
                return text.includes('ir al pago') || text.includes('confirmar') || text.includes('confirm') || text.includes('pago');
            });
            if (btnConfirm) btnConfirm.click();
        });
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(6000);
        await tomarCaptura(page, "7_checkout_carrito");

        // --- 5. Procesar Pago y Stripe ---
        console.log("Navegando al proceso de pago...");
        // Hacemos clic en Procesar Pago / Checkout en el carrito
        await page.evaluate(() => {
            const btn = Array.from(document.querySelectorAll('a, button')).find(el => {
                const text = el.textContent.trim().toLowerCase();
                return text.includes('procesar') || text.includes('checkout') || text.includes('pagar') || text.includes('siguiente');
            });
            if (btn) btn.click();
        });
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "8_checkout_datos");

        // Confirmamos billing info si hay botón de continuar/siguiente
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
        await tomarCaptura(page, "9_checkout_metodos_pago");

        // Rellenamos tarjeta e indicamos pago
        console.log("Seleccionando método de pago y rellenando tarjeta...");
        // 1. Intentamos seleccionar tarjeta/Stripe si es necesario
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

        // 2. Intentamos llenar tarjeta en DOM nativo (si es directo)
        try {
            await page.evaluate(() => {
                const ccNum = document.querySelector('input[name="cc_number"], #cc_number, #card_number');
                if (ccNum) ccNum.value = "4242424242424242";
                const ccExp = document.querySelector('input[name="cc_expiry"], #cc_expiry, #cc_exp');
                if (ccExp) ccExp.value = "02/30";
                const ccCvc = document.querySelector('input[name="cc_cvv"], #cc_cvv, #cc_cvc');
                if (ccCvc) ccCvc.value = "000";
            });
        } catch (e) {}

        // 3. Intentamos llenar tarjeta en iframes de Stripe (Stripe Elements)
        try {
            console.log("Esperando a que se carguen los elementos de pago de Stripe en el DOM...");
            try {
                await page.waitForSelector('iframe[src*="stripe"], iframe[src*="elements"], iframe', { timeout: 10000 });
                await delay(3000); // Margen de gracia para inicialización interna de Stripe
            } catch (err) {
                console.log("Aviso: No se detectó selector específico de iframe de Stripe mediante waitForSelector, procediendo con escaneo de frames...");
            }
            
            const frames = page.frames();
            console.log(`Buscando iframes de Stripe (total frames: ${frames.length})...`);
            for (const frame of frames) {
                const url = frame.url();
                console.log(`  - Evaluando frame URL: "${url}"`);
                if (url.includes("stripe") || url.includes("elements") || url.includes("payment")) {
                    console.log(`    -> Coincidencia con iframe Stripe: ${url}`);
                    
                    // Buscamos todos los inputs dentro de este frame
                    const inputs = frame.locator('input');
                    const count = await inputs.count();
                    for (let i = 0; i < count; i++) {
                        const input = inputs.nth(i);
                        const placeholder = await input.getAttribute('placeholder') || '';
                        const name = await input.getAttribute('name') || '';
                        const autocomplete = await input.getAttribute('autocomplete') || '';
                        const type = await input.getAttribute('type') || '';
                        
                        console.log(`  [Input ${i}] name="${name}", placeholder="${placeholder}", autocomplete="${autocomplete}", type="${type}"`);
                        
                        // Llenar número de tarjeta
                        if (
                            name === 'cardnumber' || 
                            autocomplete === 'cc-number' || 
                            placeholder.includes('1234') || 
                            placeholder.toLowerCase().includes('card') || 
                            placeholder.toLowerCase().includes('tarjeta') ||
                            (name === '' && placeholder === '' && type === 'tel' && i === 0)
                        ) {
                            console.log(`    -> Detectado como NÚMERO DE TARJETA. Llenando...`);
                            await input.focus();
                            await input.click();
                            await input.fill("4242424242424242");
                            await delay(300);
                            const val = await input.inputValue();
                            if (!val || val.length < 10) {
                                console.log("    -> El valor de tarjeta sigue incompleto tras fill. Intentando presionar secuencialmente...");
                                await input.pressSequentially("4242424242424242", { delay: 50 });
                            }
                        }
                        
                        // Llenar fecha de vencimiento
                        if (
                            name === 'exp-date' || 
                            autocomplete === 'cc-exp' || 
                            placeholder.includes('MM') || 
                            placeholder.includes('YY') || 
                            placeholder.includes('AA')
                        ) {
                            console.log(`    -> Detectado como VENCIMIENTO. Llenando...`);
                            await input.focus();
                            await input.click();
                            await input.fill("0230");
                            await delay(300);
                            const val = await input.inputValue();
                            if (!val || val.length < 2) {
                                console.log("    -> El vencimiento sigue incompleto. Intentando presionar secuencialmente...");
                                await input.pressSequentially("0230", { delay: 50 });
                            }
                        }
                        
                        // Llenar CVC
                        if (
                            name === 'cvc' || 
                            autocomplete === 'cc-csc' || 
                            placeholder.toLowerCase().includes('cvc') || 
                            placeholder.toLowerCase().includes('cvv') ||
                            (type === 'tel' && (placeholder === 'CVC' || name === 'cvc'))
                        ) {
                            console.log(`    -> Detectado como CVC. Llenando...`);
                            await input.focus();
                            await input.click();
                            await input.fill("000");
                            await delay(300);
                            const val = await input.inputValue();
                            if (!val || val.length < 2) {
                                console.log("    -> El CVC sigue incompleto. Intentando presionar secuencialmente...");
                                await input.pressSequentially("000", { delay: 50 });
                            }
                        }
                    }
                }
            }
        } catch (e) {
            console.log("No se pudo interactuar con los iframes de Stripe:", e.message);
        }
        await delay(2000);
        await tomarCaptura(page, "10_tarjeta_rellena");

        // 4. Clic en Pagar ahora / Confirmar pedido
        console.log("Haciendo clic en Pagar Ahora...");
        await page.evaluate(() => {
            const btnPay = document.querySelector('button[name="o_payment_submit_button"]') || document.querySelector('#o_payment_submit_button') || document.querySelector('button.btn-primary');
            if (btnPay) btnPay.click();
        });
        await page.waitForLoadState("load", { timeout: 60000 });
        await delay(10000);
        await tomarCaptura(page, "11_resumen_pago_finalizado");

        // Esperamos en caso de que Odoo redirija desde /payment/status a /shop/confirmation o similar
        console.log("Esperando posible redirección de estado de pago...");
        try {
            await page.waitForURL('**/*confirmation*', { timeout: 15000 });
        } catch (e) {
            console.log("No hubo redirección a /confirmation, evaluando página actual...");
        }

        // --- 6. QA Evals: Validación de Compra Exitosa ---
        console.log("\n--- INICIANDO QA EVALS (Aserción de compra exitosa) ---");
        try {
            const textoPagina = await page.evaluate(() => document.body.innerText);
            const urlActual = page.url();
            console.log(`URL final de la página: ${urlActual}`);
            
            if (
                urlActual.includes("/confirmation") || 
                urlActual.includes("/validate") || 
                urlActual.includes("/registration/success") || 
                (urlActual.includes("/payment/status") && (textoPagina.includes("Successful") || textoPagina.includes("éxito") || textoPagina.includes("procesado"))) ||
                textoPagina.includes("Gracias") || 
                textoPagina.includes("Thank you") || 
                textoPagina.includes("Pedido") || 
                textoPagina.includes("Confirmado") || 
                textoPagina.includes("Exitosa")
            ) {
                console.log("✅ QA Eval SUPERADO: ¡La clase grupal se inscribió y pagó exitosamente con la tarjeta de prueba!");
            } else {
                console.log("❌ QA Eval FALLIDO: No se detectó la confirmación final de la compra.");
            }
        } catch (evalError) {
            console.log("⚠️ QA Eval ADVERTENCIA: Ocurrió un error al verificar el estado final:", evalError.message);
        }

        await tomarCaptura(page, "12_evaluacion_final");

    } catch (error) {
        console.error("❌ Error durante la automatización de registro:", error);
    } finally {
        console.log("Cerrando navegador...");
        await browser.close();
    }
}

flujoClasesGrupalesRegistro().catch(console.error);
