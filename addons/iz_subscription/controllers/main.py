from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_event.controllers.main import WebsiteEventController


class IzWebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(
        self, product_id, add_qty=1, set_qty=0,
        product_custom_attribute_values=None,
        no_variant_attribute_value_ids=None,
        **kw
    ):
        user = request.env.user
        if user and not user._is_public():
            # Detect if the product is tied to an event ticket
            ticket = request.env['event.event.ticket'].sudo().search(
                [('product_id', '=', int(product_id))], limit=1
            )
            if ticket:
                # Block if user is already registered to this event
                event = ticket.event_id
                if event and user.partner_id.id in event.inscritos_ids.ids:
                    return request.redirect('/shop/cart')

                partner = user.partner_id
                benefits = partner._get_current_subscription_benefits("events")
                # Only filter by plan if the event explicitly restricts to specific plans
                if event and event.subscription_plan_ids:
                    benefits = benefits.filtered(
                        lambda b: b.plan_id in event.subscription_plan_ids
                    )
                # (no else: if no restriction, benefit applies to all events)

                # Restrict qty to 1 if user has any active benefit for this event
                if benefits:
                    _add_qty = float(add_qty or 0)
                    _set_qty = float(set_qty or 0)

                    order = request.website.sale_get_order()
                    current_qty = 0
                    if order:
                        existing = order.order_line.filtered(
                            lambda l: l.product_id.id == int(product_id)
                        )
                        if existing:
                            current_qty = sum(existing.mapped('product_uom_qty'))

                    if _set_qty > 1:
                        set_qty = 1
                    elif _add_qty > 0 and current_qty + _add_qty > 1:
                        add_qty = max(1 - current_qty, 0)

        return super().cart_update(
            product_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_value_ids=no_variant_attribute_value_ids,
            **kw
        )

    @http.route(
        '/shop/checkout', type='http', methods=['GET'], auth='public', website=True, sitemap=False
    )
    def shop_checkout(self, try_skip_step=None, **query_params):
        """Override to auto-confirm $0 event-only orders, bypassing the checkout page."""
        order = request.website.sale_get_order()
        if order and order.amount_total == 0.0:
            # Only auto-confirm if ALL lines are event ticket lines (no mixed carts)
            event_lines = order.order_line.filtered(
                lambda l: "event_ticket_id" in l._fields and l.event_ticket_id
            )
            non_event_lines = order.order_line - event_lines
            if event_lines and not non_event_lines:
                order.sudo().action_confirm()
                return request.redirect('/shop/confirmation')

        return super().shop_checkout(try_skip_step=try_skip_step, **query_params)


class IzWebsiteEvent(WebsiteEventController):

    @http.route('/event/<int:event_id>/free-register', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def free_event_register(self, event_id, **kw):
        """Direct registration — bypasses cart and payment.
        Applies when:
          (a) event is free (all tickets $0),
          (b) it's the user's first event ever, or
          (c) the user has an active subscription benefit covering this event.
        """
        user = request.env.user
        if user._is_public():
            return request.redirect('/web/login')

        event = request.env['event.event'].sudo().browse(event_id)
        if not event.exists():
            return request.redirect('/event')

        # Determine eligibility
        paid_tickets = event.event_ticket_ids.filtered(lambda t: t.price > 0)
        is_free_event = event.event_ticket_ids and not paid_tickets
        is_first_time = not user.partner_id._has_previous_event_registration()

        # Check subscription benefit
        all_benefits = user.partner_id._get_current_subscription_benefits('events')
        if event.subscription_plan_ids:
            all_benefits = all_benefits.filtered(lambda b: b.plan_id in event.subscription_plan_ids)
        has_subscription_benefit = bool(all_benefits[:1])

        if not is_free_event and not is_first_time and not has_subscription_benefit:
            # No eligibility — send to regular modal flow
            return request.redirect('/event/%s/register' % event_id)

        # Block if already registered
        if user.partner_id.id in event.inscritos_ids.ids:
            return request.redirect('/event/%s/register' % event_id)

        # Block if no seats available
        if event.seats_limited and event.seats_available <= 0:
            return request.redirect('/event/%s/register' % event_id)

        ticket = event.event_ticket_ids[:1] if event.event_ticket_ids else False

        reg_vals = {
            'event_id': event.id,
            'partner_id': user.partner_id.id,
            'name': user.partner_id.name,
            'email': user.partner_id.email or '',
            'phone': user.partner_id.phone or '',
            'state': 'open',
        }
        if ticket:
            reg_vals['event_ticket_id'] = ticket.id

        registration = request.env['event.registration'].sudo().create(reg_vals)

        iCal_url = '/event/%d/ics' % event.id
        google_url = ''
        if hasattr(event, '_get_google_url'):
            google_url = event._get_google_url()

        return request.render('website_event.registration_complete', {
            'event': event,
            'attendees': registration,
            'iCal_url': iCal_url,
            'google_url': google_url,
        })

