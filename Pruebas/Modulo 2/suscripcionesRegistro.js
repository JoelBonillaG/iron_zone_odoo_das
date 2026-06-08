import {
    LOCAL_BASE_URL,
    assertSubscriptionFlow,
    login,
    runPlaywrightFlow,
} from "./testHelpers.js";

runPlaywrightFlow("suscripciones local", async (page) => {
    await login(page, LOCAL_BASE_URL);
    await assertSubscriptionFlow(page, LOCAL_BASE_URL);
}).catch((error) => {
    console.error("QA Eval FALLIDO: suscripciones local", error);
    process.exitCode = 1;
});
