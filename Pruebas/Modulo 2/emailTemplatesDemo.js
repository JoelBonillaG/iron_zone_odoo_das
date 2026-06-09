import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import {
    runPlaywrightFlow,
    loginAs,
    LOCAL_BASE_URL,
    callOdoo,
} from "./testHelpers.js";

const ADMIN_USER = {
    email: "admin@ironzone.com",
    password: "admin123",
};

const moduleDir = path.dirname(fileURLToPath(import.meta.url));

const DEMO_USER = {
    name: "Socio de Prueba",
    email: "socio.demo@ironzone.ec",
    goal: "Pérdida de peso",
    level: "Intermedio",
    gender: "masculino",
};

function cleanTemplate(html) {
    if (!html) return "<h1>Plantilla vacía</h1>";

    return html
        .replace(/<t t-esc="object.name"\s*\/>/g, DEMO_USER.name)
        .replace(/<t t-esc="object.email"\s*\/>/g, DEMO_USER.email)
        .replace(
            /<t t-esc="object.iz_fitness_goal or '.*?'"\s*\/>/g,
            DEMO_USER.goal
        )
        .replace(
            /<t t-esc="object.iz_experience_level or '.*?'"\s*\/>/g,
            DEMO_USER.level
        );
}

async function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function showTemplate(page, config) {
    const html = cleanTemplate(config.html);

    await page.setContent(`
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>
*{
    box-sizing:border-box;
}

body{
    margin:0;
    background:#0f172a;
    font-family:Segoe UI;
    overflow:hidden;
}

.wrapper{
    display:grid;
    grid-template-columns:350px 1fr;
    height:100vh;
}

.sidebar{
    background:#111827;
    color:white;
    padding:35px;
}

.brand{
    color:#38ef7d;
    font-size:22px;
    font-weight:900;
    letter-spacing:6px;
}

.badge{
    margin-top:25px;
    display:inline-block;
    padding:8px 16px;
    border-radius:999px;
    background:#1e293b;
    color:#38ef7d;
    font-size:12px;
    font-weight:bold;
}

.sidebar h1{
    font-size:34px;
    line-height:1.2;
}

.sidebar p{
    color:#cbd5e1;
}

.user{
    margin-top:40px;
    padding:20px;
    border-radius:12px;
    background:#1e293b;
}

.preview{
    background:#020617;
    overflow:hidden;
}

.header{
    height:60px;
    background:#1e293b;
    color:white;
    display:flex;
    align-items:center;
    padding-left:20px;
    font-weight:bold;
}

.scroll{
    height:calc(100vh - 60px);
    overflow-y:auto;
    padding:30px;
}

.email{
    width:650px;
    margin:auto;
}
</style>
</head>

<body>

<div class="wrapper">

<div class="sidebar">

<div class="brand">
IRON ZONE
</div>

<div class="badge">
${config.badge}
</div>

<h1>${config.title}</h1>

<p>${config.description}</p>

<div class="user">
<b>Socio de prueba</b>
<br><br>
${DEMO_USER.name}
<br>
${DEMO_USER.level}
<br>
${DEMO_USER.goal}
</div>

</div>

<div class="preview">

<div class="header">
Vista previa de Email Marketing
</div>

<div id="scroll" class="scroll">
<div class="email">
${html}
</div>
</div>

</div>

</div>

</body>
</html>
`);

    await delay(1500);

    await page.evaluate(() => {
        const scroll = document.getElementById("scroll");
        scroll.scrollTop = scroll.scrollHeight * 0.5;
    });

    await delay(1500);

    await page.evaluate(() => {
        const scroll = document.getElementById("scroll");
        scroll.scrollTop = scroll.scrollHeight;
    });

    await delay(1500);
}

async function getTemplate(page, nameSearch) {
    const result = await callOdoo(
        page,
        LOCAL_BASE_URL,
        "mail.template",
        "search_read",
        [
            [
                ["name", "ilike", nameSearch],
            ],
        ],
        {
            fields: ["name", "subject", "body_html"],
            limit: 1,
        }
    );

    if (!result.length) {
        throw new Error(
            `No se encontró la plantilla: ${nameSearch}`
        );
    }

    return result[0];
}

runPlaywrightFlow(
    "Demo Plantillas Email Marketing",
    async (page) => {

        console.log("Login administrador...");
        await loginAs(
            page,
            LOCAL_BASE_URL,
            ADMIN_USER
        );

        console.log("Plantilla Nivel Intermedio...");
        const intermedio = await getTemplate(
            page,
            "Intermedio"
        );

        await showTemplate(page, {
            title: "Campaña Nivel Intermedio",
            badge: "Segmentación",
            description:
                "Promoción automática enviada a socios que alcanzan un nivel intermedio.",
            html: intermedio.body_html,
        });

        console.log("Plantilla Pérdida de Peso...");
        const perdidaPeso = await getTemplate(
            page,
            "Pérdida"
        );

        await showTemplate(page, {
            title: "Objetivo Pérdida de Peso",
            badge: "Objetivo Fitness",
            description:
                "Correo personalizado para usuarios enfocados en reducir grasa corporal.",
            html: perdidaPeso.body_html,
        });

        console.log("Plantilla Día del Hombre...");
        const diaHombre = await getTemplate(
            page,
            "Día del Hombre"
        );

        await showTemplate(page, {
            title: "Campaña Día del Hombre",
            badge: "Evento Especial",
            description:
                "Campaña promocional estacional para socios masculinos.",
            html: diaHombre.body_html,
        });

        await page.setContent(`
            <body style="
                background:#0f172a;
                color:white;
                display:grid;
                place-items:center;
                height:100vh;
                font-family:Segoe UI;
                margin:0;
            ">
                <div style="text-align:center">
                    <h1>✓ Demo Finalizada</h1>
                    <p>Email Marketing Iron Zone</p>
                </div>
            </body>
        `);

        await delay(3000);
    }
).catch((err) => {
    console.error(err);
    process.exitCode = 1;
});