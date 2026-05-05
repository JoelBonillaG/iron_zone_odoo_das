/** @odoo-module **/

import { publicWidget } from "@web/legacy/js/public/public_widget";

if (publicWidget && publicWidget.registry) {
    publicWidget.registry.IronZoneQuantity = publicWidget.Widget.extend({
        selector: ".js_add_cart_json",
        events: {
            mousedown: "_onMouseDown",
            mouseup: "_onMouseUp",
            mouseleave: "_onMouseUp",
        },

        _onMouseDown: function (ev) {
            const btn = ev.currentTarget;
            if (btn.querySelector(".fa-plus") || btn.querySelector(".fa-minus")) {
                this.interval = setInterval(() => btn.click(), 150);
            }
        },

        _onMouseUp: function () {
            if (this.interval) {
                clearInterval(this.interval);
            }
        },
    });

    publicWidget.registry.IronZoneCheckoutTheme = publicWidget.Widget.extend({
        selector: "body",

        start: function () {
            const summary = document.querySelector("#o_wsale_total_accordion_item");
            if (summary) {
                summary.style.background = "var(--iz-surface)";
                summary.style.border = "1px solid var(--iz-line)";
                summary.style.borderRadius = "18px";
                summary.style.color = "var(--iz-text)";

                const summaryButton = summary.querySelector(".accordion-button");
                if (summaryButton) {
                    summaryButton.style.background = "var(--iz-surface)";
                    summaryButton.style.color = "var(--iz-text)";
                    summaryButton.style.boxShadow = "none";
                    summaryButton.style.paddingLeft = "0";
                    summaryButton.style.paddingRight = "0";
                }

                const cartTotal = summary.querySelector("#cart_total");
                if (cartTotal) {
                    cartTotal.style.background = "var(--iz-surface)";
                    cartTotal.style.borderTop = "1px solid var(--iz-line)";
                    cartTotal.style.color = "var(--iz-text)";
                }

                const summaryTable = summary.querySelector("#cart_products");
                if (summaryTable) {
                    summaryTable.style.background = "var(--iz-surface)";
                    summaryTable.style.color = "var(--iz-text)";
                }

                const couponForm = summary.querySelector(".coupon_form");
                if (couponForm) {
                    couponForm.style.background = "var(--iz-surface)";
                    couponForm.style.color = "var(--iz-text)";
                }

                const discountInput = summary.querySelector('.coupon_form input[name="promo"]');
                if (discountInput) {
                    discountInput.style.background = "var(--iz-surface-2)";
                    discountInput.style.borderColor = "var(--iz-line)";
                    discountInput.style.color = "var(--iz-text)";
                }

                const discountButton = summary.querySelector('.coupon_form .btn');
                if (discountButton) {
                    discountButton.style.background = "linear-gradient(135deg, #ff6a42, #ff4f86)";
                    discountButton.style.border = "0";
                    discountButton.style.color = "#fff";
                    discountButton.style.boxShadow = "0 12px 26px rgba(255, 90, 47, 0.28)";
                }

                const payButton = summary.querySelector('button[name="o_payment_submit_button"]');
                if (payButton) {
                    payButton.style.background = "linear-gradient(135deg, #ff6a42, #ff4f86)";
                    payButton.style.border = "0";
                    payButton.style.color = "#fff";
                    payButton.style.boxShadow = "0 12px 26px rgba(255, 90, 47, 0.28)";
                }

                const backLink = summary.querySelector('a[href="/shop/checkout"]');
                if (backLink) {
                    backLink.style.color = "var(--iz-muted)";
                }
            }

            const paymentHeading = document.querySelector("#o_payment_tokens_heading");
            if (paymentHeading) {
                paymentHeading.style.color = "#fff";
            }

            document.querySelectorAll('li[name="o_payment_option"]').forEach((item) => {
                item.style.background = "var(--iz-surface)";
                item.style.border = "1px solid var(--iz-line)";
                item.style.borderRadius = "16px";
                item.style.color = "var(--iz-text)";
                item.style.marginBottom = "1rem";
            });

            return Promise.resolve();
        },
    });
}

function applyIronZoneCheckoutTheme() {
    const summary = document.querySelector("#o_wsale_total_accordion_item");
    if (!summary) {
        return;
    }

    // Inject a high-priority stylesheet to force orange buttons if not already present.
    if (!document.getElementById('iz-orange-buttons-style')) {
        const style = document.createElement('style');
        style.id = 'iz-orange-buttons-style';
        style.textContent = `#o_wsale_total_accordion_item .coupon_form .btn, #o_wsale_total_accordion_item button[name="o_payment_submit_button"] { background: linear-gradient(135deg, #ff6a42, #ff4f86) !important; border: 0 !important; color: #fff !important; box-shadow: 0 12px 26px rgba(255, 90, 47, 0.28) !important; } #o_wsale_total_accordion_item .coupon_form .btn:hover, #o_wsale_total_accordion_item button[name="o_payment_submit_button"]:hover { filter: brightness(0.95) !important; }`;
        document.head.appendChild(style);
    }

    summary.style.background = "var(--iz-surface)";
    summary.style.border = "1px solid var(--iz-line)";
    summary.style.borderRadius = "18px";
    summary.style.color = "var(--iz-text)";

    const summaryButton = summary.querySelector(".accordion-button");
    if (summaryButton) {
        summaryButton.style.background = "var(--iz-surface)";
        summaryButton.style.color = "var(--iz-text)";
        summaryButton.style.boxShadow = "none";
        summaryButton.style.paddingLeft = "0";
        summaryButton.style.paddingRight = "0";
    }

    const cartTotal = summary.querySelector("#cart_total");
    if (cartTotal) {
        cartTotal.style.background = "var(--iz-surface)";
        cartTotal.style.borderTop = "1px solid var(--iz-line)";
        cartTotal.style.color = "var(--iz-text)";
    }

    const summaryTable = summary.querySelector("#cart_products");
    if (summaryTable) {
        summaryTable.style.background = "var(--iz-surface)";
        summaryTable.style.color = "var(--iz-text)";
    }

    const couponForm = summary.querySelector(".coupon_form");
    if (couponForm) {
        couponForm.style.background = "var(--iz-surface)";
        couponForm.style.color = "var(--iz-text)";
    }

    const discountInput = summary.querySelector('.coupon_form input[name="promo"]');
    if (discountInput) {
        discountInput.style.background = "var(--iz-surface-2)";
        discountInput.style.borderColor = "var(--iz-line)";
        discountInput.style.color = "var(--iz-text)";
    }

    const discountButton = summary.querySelector('.coupon_form .btn');
    if (discountButton) {
        discountButton.style.background = "linear-gradient(135deg, #ff6a42, #ff4f86)";
        discountButton.style.border = "0";
        discountButton.style.color = "#fff";
        discountButton.style.boxShadow = "0 12px 26px rgba(255, 90, 47, 0.28)";
    }

    const payButton = summary.querySelector('button[name="o_payment_submit_button"]');
    if (payButton) {
        payButton.style.background = "linear-gradient(135deg, #ff6a42, #ff4f86)";
        payButton.style.border = "0";
        payButton.style.color = "#fff";
        payButton.style.boxShadow = "0 12px 26px rgba(255, 90, 47, 0.28)";
    }

    const backLink = summary.querySelector('a[href="/shop/checkout"]');
    if (backLink) {
        backLink.style.color = "var(--iz-muted)";
    }

    const paymentHeading = document.querySelector("#o_payment_tokens_heading");
    if (paymentHeading) {
        paymentHeading.style.color = "#fff";
    }

    document.querySelectorAll('li[name="o_payment_option"]').forEach((item) => {
        item.style.background = "var(--iz-surface)";
        item.style.border = "1px solid var(--iz-line)";
        item.style.borderRadius = "16px";
        item.style.color = "var(--iz-text)";
        item.style.marginBottom = "1rem";
    });
}

function runIronZoneCheckoutTheme() {
    window.requestAnimationFrame(applyIronZoneCheckoutTheme);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runIronZoneCheckoutTheme, { once: true });
} else {
    runIronZoneCheckoutTheme();
}

// Replace invoice residual amounts in the portal list with invoice total (more user-friendly)
async function applyInvoiceListTotals() {
    try {
        if (!location.pathname.startsWith('/my/invoices')) {
            return;
        }
        const rows = Array.from(document.querySelectorAll('table tr')).slice(1);
        for (const tr of rows) {
            const link = tr.querySelector('a[href*="/my/invoices/"]');
            const amountCell = tr.children[3] || tr.children[2];
            if (!link || !amountCell) continue;
            try {
                const res = await fetch(link.href, { credentials: 'same-origin' });
                const text = await res.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(text, 'text/html');
                // find a table cell that has a strong 'Total' label nearby
                let totalText = null;
                const strongs = Array.from(doc.querySelectorAll('strong'));
                for (const s of strongs) {
                    if (s.textContent && s.textContent.trim() === 'Total') {
                        const parentRow = s.closest('tr');
                        if (parentRow) {
                            const cells = parentRow.querySelectorAll('td');
                            if (cells.length >= 2) {
                                totalText = cells[1].textContent.trim();
                                break;
                            }
                        }
                    }
                }
                if (!totalText) {
                    // fallback: look for 'Cantidad por pagar' row and the total in the detail
                    const rows2 = Array.from(doc.querySelectorAll('tr'));
                    for (const r of rows2) {
                        if (r.textContent && r.textContent.indexOf('Total') !== -1) {
                            const tds = r.querySelectorAll('td');
                            if (tds.length >= 2) { totalText = tds[1].textContent.trim(); break; }
                        }
                    }
                }
                if (totalText) {
                    amountCell.textContent = totalText;
                }
            } catch (e) {
                // ignore per-row failures
            }
        }
    } catch (e) {
        console && console.error && console.error('applyInvoiceListTotals failed', e);
    }
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
    applyInvoiceListTotals();
} else {
    document.addEventListener('DOMContentLoaded', applyInvoiceListTotals, { once: true });
}
