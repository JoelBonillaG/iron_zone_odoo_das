import "dotenv/config";
import { Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";
import fs from "fs";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function flujoClasesGrupalesExtract() {
    console.log("🚀 Inicializando Stagehand para extracción por IA...");
    const stagehand = new Stagehand({
        env: "LOCAL",
        model: "google/gemini-2.5-flash",
        timeout: 90000,
    });

    await stagehand.init();
    const page = stagehand.context.pages()[0];

    try {
        console.log("Navegando a la lista de clases en Iron Zone...");
        await page.goto("https://iron-zone.stratiumhub.com/event");
        await delay(5000);

        console.log("Observando las clases grupales disponibles en la página...");
        const observacionesClases = await stagehand.observe(
            "Encuentra las tarjetas o enlaces que representan las clases grupales o sesiones de entrenamiento colectivo (como CrossFit AM, Yoga Principiantes, etc.)."
        );
        console.log(`Se detectaron ${observacionesClases.length} elementos de clases.`);

        console.log("Haciendo clic en la primera clase grupal disponible...");
        await stagehand.act(
            "Haz clic en el título o tarjeta de la primera clase grupal que aparezca en la lista, por ejemplo 'CrossFit AM' o 'Yoga Principiantes'."
        );
        await delay(8000);

        console.log("Extrayendo detalles de la clase grupal (Modelo 2)...");
        const esquemaClaseGrupal = z.object({
            claseGrupal: z.object({
                nombre: z.string().describe("El nombre de la clase grupal/sesión de entrenamiento colectivo"),
                entrenador: z.string().describe("El nombre del entrenador o instructor (hr.employee) asignado a la clase"),
                horario: z.string().describe("La fecha y hora programada para la sesión (horario)"),
                cupoMaximo: z.number().describe("El cupo máximo de personas permitido para la clase"),
                cupoDisponible: z.number().describe("El número de cupos disponibles actualmente"),
                salaEspacio: z.string().describe("La sala, espacio físico o zona donde se impartirá la sesión"),
                nivelDificultad: z.string().describe("El nivel de dificultad de la clase (principiante, intermedio, avanzado, etc.)"),
            }),
        });

        const datosExtraidos = await stagehand.extract(
            "Analiza detalladamente la página actual y extrae el nombre de la clase, el entrenador, el horario, el cupo máximo, el cupo disponible, la sala o espacio físico, y el nivel de dificultad especificado.",
            esquemaClaseGrupal
        );

        console.log("Datos extraídos exitosamente:", JSON.stringify(datosExtraidos, null, 2));

        const rutaArchivo = "clase_grupal_extraida.json";
        fs.writeFileSync(rutaArchivo, JSON.stringify(datosExtraidos, null, 2));
        console.log(`💾 Resultados guardados en: ${rutaArchivo}`);

    } catch (error) {
        console.error("❌ Error durante la automatización de extracción:", error);
    } finally {
        console.log("Cerrando navegador...");
        await stagehand.close();
    }
}

flujoClasesGrupalesExtract().catch(console.error);
