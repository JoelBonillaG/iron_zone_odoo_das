/** @odoo-module **/

import { publicWidget } from "@web/legacy/js/public/public_widget";

publicWidget.registry.IronZoneQuantity = publicWidget.Widget.extend({
    selector: '.js_add_cart_json',
    events: {
        'mousedown': '_onMouseDown',
        'mouseup': '_onMouseUp',
        'mouseleave': '_onMouseUp',
    },

    _onMouseDown: function (ev) {
        const btn = ev.currentTarget;
        if (btn.querySelector('.fa-plus') || btn.querySelector('.fa-minus')) {
            this.interval = setInterval(() => btn.click(), 150);
        }
    },

    _onMouseUp: function () {
        if (this.interval) {
            clearInterval(this.interval);
        }
    },
});
