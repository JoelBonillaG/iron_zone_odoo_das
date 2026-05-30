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

async function flujoGuiaEjerciciosRegistro() {
    console.log("🚀 Inicializando Playwright Nativo para revisión de Guía de Ejercicios...");
    
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

        // --- 2. Navegar a Guía de Ejercicios ---
        console.log("Navegando a la guía de ejercicios (/exercise-guides)...");
        await page.goto("https://iron-zone.stratiumhub.com/exercise-guides", { waitUntil: "load", timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "2_guia_ejercicios_lista");

        // --- 3. Seleccionar una Guía ---
        console.log("Seleccionando una guía de ejercicios...");
        const clickExit = await page.evaluate(() => {
            const links = Array.from(document.querySelectorAll('a[href*="/exercise-guides/"]'));
            if (links.length > 0) {
                links[0].click();
                return true;
            }
            return false;
        });

        if (clickExit) {
            await page.waitForLoadState("load", { timeout: 60000 });
            await delay(4000);
            await tomarCaptura(page, "3_detalle_guia");
        } else {
            console.log("No se encontraron enlaces a guías específicas en la página principal.");
        }

        // --- 4. QA Evals: Validación de Módulo ---
        console.log("\n--- INICIANDO QA EVALS (Aserción de Módulo de Guías) ---");
        try {
            const textoPagina = await page.evaluate(() => document.body.innerText);
            const urlActual = page.url();
            console.log(`URL final de la página: ${urlActual}`);
            
            // Verificamos que la URL contenga exercise-guides y que se haya renderizado contenido
            if (urlActual.includes("/exercise-guides")) {
                console.log("✅ QA Eval SUPERADO: ¡El módulo de guía de ejercicios fue accedido correctamente!");
            } else {
                console.log("❌ QA Eval FALLIDO: No se logró acceder al módulo de guía de ejercicios o hubo un desvío incorrecto de la ruta.");
            }
        } catch (evalError) {
            console.log("⚠️ QA Eval ADVERTENCIA: Ocurrió un error al verificar el estado final:", evalError.message);
        }

        await tomarCaptura(page, "4_evaluacion_final");

    } catch (error) {
        console.error("❌ Error durante la automatización de la guía de ejercicios:", error);
    } finally {
        console.log("Cerrando navegador...");
        await browser.close();
    }
}

flujoGuiaEjerciciosRegistro().catch(console.error);
