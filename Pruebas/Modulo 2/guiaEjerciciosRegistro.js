import {
    LOCAL_BASE_URL,
    assertExerciseGuideFlow,
    login,
    runPlaywrightFlow,
} from "./testHelpers.js";

runPlaywrightFlow("guia de ejercicios local", async (page) => {
    await login(page, LOCAL_BASE_URL);
    await assertExerciseGuideFlow(page, LOCAL_BASE_URL);
}).catch((error) => {
    console.error("QA Eval FALLIDO: guia de ejercicios local", error);
    process.exitCode = 1;
});
