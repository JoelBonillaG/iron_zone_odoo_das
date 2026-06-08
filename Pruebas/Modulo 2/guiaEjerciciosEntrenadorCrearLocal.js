import {
    LOCAL_BASE_URL,
    TRAINER_USER,
    buildUrl,
    callOdoo,
    delay,
    loginAs,
    pageText,
    runPlaywrightFlow,
    tomarCaptura,
} from "./testHelpers.js";

async function createAndPublishGuide(page, guideName) {
    const createdGuide = await callOdoo(page, LOCAL_BASE_URL, "ironzone.exercise.guide", "create", [[{
        name: guideName,
        exercise_type: "individual",
        difficulty: "beginner",
        instructions: "<p>Coloca los pies al ancho de los hombros, baja con control y sube manteniendo el tronco estable.</p>",
        recommendations: "Calentar antes de iniciar y mantener respiracion controlada.",
        common_mistakes: "Inclinar demasiado el torso o levantar los talones.",
        safety_notes: "Detener el ejercicio si aparece dolor articular.",
        requires_subscription: false,
    }]]);
    const guideId = Array.isArray(createdGuide) ? createdGuide[0] : createdGuide;

    await callOdoo(page, LOCAL_BASE_URL, "ironzone.exercise.guide", "action_publish", [[guideId]]);
    const [guide] = await callOdoo(page, LOCAL_BASE_URL, "ironzone.exercise.guide", "read", [[guideId]], {
        fields: ["id", "name", "website_url"],
    });
    return guide;
}

async function assertGuideVisibleInPortal(page, guide) {
    await page.goto(buildUrl(LOCAL_BASE_URL, `/web#id=${guide.id}&model=ironzone.exercise.guide&view_type=form`), {
        waitUntil: "domcontentloaded",
        timeout: 60000,
    });
    await delay(2500);
    await tomarCaptura(page, "2_guia_creada_backend_entrenador");

    await page.goto(buildUrl(LOCAL_BASE_URL, "/exercise-guides"), { waitUntil: "networkidle", timeout: 60000 });
    await tomarCaptura(page, "3_portal_guias_antes_busqueda");

    const guideSearch = page.locator("input[placeholder='Buscar guía'], input[placeholder='Buscar guia'], input[placeholder='Buscar guÃ­a']").first();
    if (!(await guideSearch.count())) {
        throw new Error("No se encontro el buscador de guias en el portal.");
    }

    await guideSearch.fill(guide.name);
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
    await tomarCaptura(page, "4_guia_creada_visible_en_lista");

    const listText = await pageText(page);
    if (!listText.includes(guide.name)) {
        throw new Error(`No se encontro la guia creada en el listado: ${guide.name}`);
    }

    const guideLink = page.locator("a[href*='/exercise-guides/']").filter({ hasText: guide.name }).first();
    if (await guideLink.count()) {
        await Promise.all([
            page.waitForLoadState("networkidle", { timeout: 60000 }).catch(() => null),
            guideLink.click(),
        ]);
    } else if (guide.website_url) {
        await page.goto(buildUrl(LOCAL_BASE_URL, guide.website_url), { waitUntil: "networkidle", timeout: 60000 });
    } else {
        throw new Error(`La guia aparece en texto, pero no se encontro enlace de detalle: ${guide.name}`);
    }

    await delay(1200);
    await tomarCaptura(page, "5_detalle_guia_creada");

    const detailText = await pageText(page);
    if (!page.url().includes("/exercise-guides/") || !detailText.includes(guide.name)) {
        throw new Error(`No se abrio el detalle de la guia creada. URL=${page.url()}`);
    }
}

runPlaywrightFlow("entrenador crea guia de ejercicios y la ve publicada local", async (page) => {
    const guideName = `Guia QA Entrenador ${Date.now()}`;
    await loginAs(page, LOCAL_BASE_URL, TRAINER_USER);
    const guide = await createAndPublishGuide(page, guideName);
    await assertGuideVisibleInPortal(page, guide);
}).catch((error) => {
    console.error("QA Eval FALLIDO: entrenador crea guia de ejercicios y la ve publicada local", error);
    process.exitCode = 1;
});
