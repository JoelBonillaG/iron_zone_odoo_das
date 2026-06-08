import {
    DEPLOYED_BASE_URL,
    assertSubscriptionFlow,
    login,
    runPlaywrightFlow,
} from "./testHelpers.js";

runPlaywrightFlow("suscripciones desplegado", async (page) => {
    await login(page, DEPLOYED_BASE_URL);
    await assertSubscriptionFlow(page, DEPLOYED_BASE_URL);
}).catch((error) => {
    console.error("QA Eval FALLIDO: suscripciones desplegado", error);
    process.exitCode = 1;
});
