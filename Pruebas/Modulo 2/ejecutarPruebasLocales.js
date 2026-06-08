import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));

const tests = [
    {
        name: "clases grupales registro local",
        script: "clasesGrupalesRegistroLocal.js",
    },
    {
        name: "guia de ejercicios registro local",
        script: "guiaEjerciciosRegistro.js",
    },
    {
        name: "suscripciones registro local",
        script: "suscripcionesRegistro.js",
    },
    {
        name: "usuario nuevo registra primer evento gratis local",
        script: "clasesGrupalesPrimerEventoGratisLocal.js",
    },
    {
        name: "entrenador crea guia de ejercicios y la ve publicada local",
        script: "guiaEjerciciosEntrenadorCrearLocal.js",
    },
];

function runNodeScript(test) {
    return new Promise((resolve) => {
        console.log(`\n=== Ejecutando: ${test.name} ===`);
        const child = spawn(process.execPath, [test.script], {
            cwd: moduleDir,
            env: process.env,
            stdio: "inherit",
        });

        child.on("close", (code) => {
            resolve({
                ...test,
                code,
                ok: code === 0,
            });
        });
    });
}

const results = [];
for (const test of tests) {
    results.push(await runNodeScript(test));
}

console.log("\n=== Resumen pruebas locales Modulo 2 ===");
for (const result of results) {
    const status = result.ok ? "OK" : `FALLO (${result.code})`;
    console.log(`${status} - ${result.name}`);
}

const failed = results.filter((result) => !result.ok);
if (failed.length) {
    console.error(`\n${failed.length} prueba(s) fallaron. Revisa capturas y videos en evidencias/.`);
    process.exitCode = 1;
} else {
    console.log("\nTodas las pruebas locales finalizaron correctamente.");
}
