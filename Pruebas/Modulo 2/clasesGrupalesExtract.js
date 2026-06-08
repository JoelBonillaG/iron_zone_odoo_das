import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import {
    DEPLOYED_BASE_URL,
    extractFirstEventData,
    runPlaywrightFlow,
} from "./testHelpers.js";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const outputPath = path.join(moduleDir, "clase_grupal_extraida.json");

runPlaywrightFlow("extraccion de clases grupales", async (page) => {
    const datosExtraidos = await extractFirstEventData(page, DEPLOYED_BASE_URL);
    fs.writeFileSync(outputPath, JSON.stringify(datosExtraidos, null, 2), "utf8");
    console.log(`Resultados guardados en: ${outputPath}`);
}).catch((error) => {
    console.error("QA Eval FALLIDO: extraccion de clases grupales", error);
    process.exitCode = 1;
});
