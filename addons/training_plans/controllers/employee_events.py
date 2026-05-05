from odoo import http
from odoo.http import request


class EmployeeEventsController(http.Controller):
    @http.route("/my/events", type="http", auth="user", website=True)
    def employee_events(self, **kwargs):
        events = request.env["event.event"].sudo().search(
            [("user_id", "=", request.env.user.id)],
            order="date_begin asc, id asc",
        )
        registrations = request.env["event.registration"].sudo().read_group(
            [("event_id", "in", events.ids)],
            ["event_id"],
            ["event_id"],
        )
        registration_counts = {
            row["event_id"][0]: row["event_id_count"]
            for row in registrations
            if row.get("event_id")
        }
        return request.render(
            "training_plans.employee_events_page",
            {
                "events": events,
                "registration_counts": registration_counts,
            },
        )
