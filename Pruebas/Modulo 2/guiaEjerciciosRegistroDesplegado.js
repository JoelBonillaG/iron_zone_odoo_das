import {
    DEPLOYED_BASE_URL,
    assertExerciseGuideFlow,
    login,
    runPlaywrightFlow,
} from "./testHelpers.js";

runPlaywrightFlow("guia de ejercicios desplegado", async (page) => {
    await login(page, DEPLOYED_BASE_URL);
    await assertExerciseGuideFlow(page, DEPLOYED_BASE_URL);
}).catch((error) => {
    console.error("QA Eval FALLIDO: guia de ejercicios desplegado", error);
    process.exitCode = 1;
});
