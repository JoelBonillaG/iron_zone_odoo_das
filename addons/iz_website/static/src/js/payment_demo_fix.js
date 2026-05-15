/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc, RPCError } from "@web/core/network/rpc";
import paymentForm from "@payment/js/payment_form";
import paymentDemoMixin from "@payment_demo/js/payment_demo_mixin";

async function processDemoPayment(processingValues) {
    const customerInput = document.getElementById("customer_input")?.value || "4111 1111 1111 1111";
    const simulatedPaymentState = document.getElementById("simulated_payment_state")?.value || "done";

    try {
        await rpc("/payment/demo/simulate_payment", {
            reference: processingValues.reference,
            payment_details: customerInput,
            simulated_state: simulatedPaymentState,
        });
        window.location = "/payment/status";
    } catch (error) {
        if (error instanceof RPCError) {
            this._displayErrorDialog?.(_t("Payment processing failed"), error.data.message);
            this._enableButton?.();
            return;
        }
        throw error;
    }
}

paymentDemoMixin.processDemoPayment = processDemoPayment;

paymentForm.include({
    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== "demo") {
            return this._super(...arguments);
        }
        return processDemoPayment.call(this, processingValues);
    },
});
