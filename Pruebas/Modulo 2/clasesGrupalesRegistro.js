import {
    DEPLOYED_BASE_URL,
    assertEventRegistrationFlow,
    login,
    runPlaywrightFlow,
} from "./testHelpers.js";

runPlaywrightFlow("clases grupales desplegado", async (page) => {
    await login(page, DEPLOYED_BASE_URL);
    await assertEventRegistrationFlow(page, DEPLOYED_BASE_URL);
}).catch((error) => {
    console.error("QA Eval FALLIDO: clases grupales desplegado", error);
    process.exitCode = 1;
});
