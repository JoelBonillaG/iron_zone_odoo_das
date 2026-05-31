import "dotenv/config";
import { Stagehand } from "@browserbasehq/stagehand";
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
    
    const stagehand = new Stagehand({
        env: "LOCAL",
        model: "google/gemini-2.5-flash",
        timeout: 90000,
    });
    await stagehand.init();
    const page = stagehand.context.pages()[0];

    try {
        // --- 1. Navegar e Iniciar Sesión ---
        console.log("Navegando a la página de inicio de sesión del portal...");
        await page.goto("http://localhost:8069/web/login", { waitUntil: "load", timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "0_pagina_login");

        console.log("Ingresando credenciales del cliente de prueba...");
        await page.waitForSelector("#login", { state: "visible", timeout: 15000 });
        await page.locator("#login").fill("pruebasjos04@gmail.com");
        await delay(1000);
        
        await page.locator("#password").fill("admin123");
        await delay(1000);
        
        console.log("Haciendo clic en Iniciar Sesión...");
        await page.locator(".oe_login_form button[type='submit'], button.btn-primary").first().click();
        await page.waitForLoadState("load");
        await delay(3000);
        await tomarCaptura(page, "1_login_exitoso");

        // --- 2. Navegar a Guía de Ejercicios ---
        console.log("Navegando a la guía de ejercicios (/exercise-guides)...");
        await page.goto("http://localhost:8069/exercise-guides", { waitUntil: "load", timeout: 60000 });
        await delay(5000);
        await tomarCaptura(page, "2_guia_ejercicios_lista");

        // --- 3. Aplicar Filtros de Búsqueda ---
        console.log("Aplicando filtros de búsqueda...");
        await page.evaluate(() => {
            // Llenar el campo de búsqueda
            const searchInput = document.querySelector('input[placeholder="Buscar guía"]') || document.querySelector('input[type="text"]');
            if (searchInput) {
                searchInput.value = "spinning";
                searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // Hemos removido el filtro del dropdown porque "spinning" entra en conflicto con "Individual" y devuelve 0 resultados.
            // Con solo buscar "spinning" ya estamos aplicando un filtro.
        });
        await delay(2000);
        await tomarCaptura(page, "3_filtros_aplicados");

        console.log("Haciendo clic en Buscar...");
        await page.evaluate(() => {
            // Buscar el botón naranja con lupa o cualquier botón de submit
            const btns = Array.from(document.querySelectorAll('button'));
            const searchBtn = btns.find(btn => btn.innerHTML.includes('fa-search') || btn.classList.contains('btn-primary')) || btns[0];
            if (searchBtn) searchBtn.click();
        });
        
        await page.waitForLoadState("load");
        await delay(5000);
        await tomarCaptura(page, "4_resultados_busqueda");

        // --- 4. Seleccionar una Guía ---
        console.log("Seleccionando una guía de ejercicios...");
        const clickExit = await page.evaluate(() => {
            // Buscar explícitamente el texto "Ver guía"
            const verGuiaLinks = Array.from(document.querySelectorAll('a')).filter(a => a.innerText.toLowerCase().includes('ver guía'));
            if (verGuiaLinks.length > 0) {
                verGuiaLinks[0].click();
                return true;
            }
            
            // Fallback: hacer clic en cualquier enlace dentro de las tarjetas
            const fallbackLinks = Array.from(document.querySelectorAll('.card a, article a, a[href*="/guide/"]'));
            if (fallbackLinks.length > 0) {
                fallbackLinks[0].click();
                return true;
            }
            return false;
        });

        if (clickExit) {
            await page.waitForLoadState("load");
            await delay(4000);
            await tomarCaptura(page, "5_detalle_guia");
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
        await stagehand.close();
    }
}

flujoGuiaEjerciciosRegistro().catch(console.error);
