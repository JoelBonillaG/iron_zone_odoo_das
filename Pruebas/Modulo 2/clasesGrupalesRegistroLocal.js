import {
    LOCAL_BASE_URL,
    assertEventRegistrationFlow,
    login,
    runPlaywrightFlow,
} from "./testHelpers.js";

runPlaywrightFlow("clases grupales local", async (page) => {
    await login(page, LOCAL_BASE_URL);
    await assertEventRegistrationFlow(page, LOCAL_BASE_URL);
}).catch((error) => {
    console.error("QA Eval FALLIDO: clases grupales local", error);
    process.exitCode = 1;
});
