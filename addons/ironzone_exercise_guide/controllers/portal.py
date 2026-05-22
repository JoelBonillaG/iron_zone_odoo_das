from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class ExerciseGuidePortalController(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "exercise_guide_count" in counters:
            partner = request.env.user.partner_id if request.env.user._is_public() is False else False
            domain = request.env["ironzone.exercise.guide"]._get_portal_accessible_domain(partner)
            values["exercise_guide_count"] = request.env["ironzone.exercise.guide"].sudo().search_count(domain)
        return values

    def _guide_search_domain(self, partner, search=None, difficulty=None, exercise_type=None, muscle_group_id=None, equipment_id=None):
        domain = request.env["ironzone.exercise.guide"]._get_portal_accessible_domain(partner)
        if search:
            domain += [
                "|",
                "|",
                ("name", "ilike", search),
                ("recommendations", "ilike", search),
                ("common_mistakes", "ilike", search),
            ]
        if difficulty:
            domain.append(("difficulty", "=", difficulty))
        if exercise_type:
            domain.append(("exercise_type", "=", exercise_type))
        if muscle_group_id:
            domain.append(("primary_muscle_group_id", "=", muscle_group_id))
        if equipment_id:
            domain.append(("equipment_id", "=", equipment_id))
        return domain

    @http.route(["/exercise-guides", "/exercise-guides/page/<int:page>"], type="http", auth="public", website=True)
    def exercise_guides(self, page=1, search=None, difficulty=None, exercise_type=None, muscle_group_id=None, equipment_id=None, **kwargs):
        Guide = request.env["ironzone.exercise.guide"]
        Category = request.env["ironzone.exercise.category"]
        # Treat backend trainers as public-like visitors for portal content (no subscription UI)
        is_trainer = request.env.user.has_group('iz_backend_theme.group_ironzone_trainers')
        partner = False if request.env.user._is_public() or is_trainer else request.env.user.partner_id
        muscle_group_id = int(muscle_group_id) if str(muscle_group_id or "").isdigit() else False
        equipment_id = int(equipment_id) if str(equipment_id or "").isdigit() else False
        if equipment_id:
            exercise_type = "machine"
        domain = self._guide_search_domain(
            partner,
            search=search,
            difficulty=difficulty,
            exercise_type=exercise_type,
            muscle_group_id=muscle_group_id,
            equipment_id=equipment_id,
        )
        guide_count = Guide.sudo().search_count(domain)
        pager = request.website.pager(
            url="/exercise-guides",
            total=guide_count,
            page=page,
            step=6,
            url_args={
                "search": search,
                "difficulty": difficulty,
                "exercise_type": exercise_type,
                "muscle_group_id": muscle_group_id,
                "equipment_id": equipment_id,
            },
        )
        guides = Guide.sudo().search(domain, order="sequence, name", limit=6, offset=pager["offset"])
        equipment_domain = self._guide_search_domain(partner, exercise_type="machine")
        equipment_ids = Guide.sudo().search(equipment_domain).mapped("equipment_id")
        muscle_groups = Category.sudo().search(
            [("category_type", "=", "muscle"), ("active", "=", True)],
            order="sequence, name",
        )
        plan = request.env["iz.subscription.plan"]
        subscription = request.env["sale.subscription"]
        if partner:
            plan, subscription = partner.sudo()._get_current_subscription_plan()
        values = {
            "guides": guides,
            "pager": pager,
            "search": search or "",
            "difficulty": difficulty or "",
            "exercise_type": exercise_type or "",
            "muscle_group_id": muscle_group_id or "",
            "equipment_id": equipment_id or "",
            "equipments": equipment_ids.sorted("name"),
            "muscle_groups": muscle_groups,
            "current_plan": plan,
            "current_subscription": subscription,
            "hide_subscription_ctas": bool(is_trainer),
            "is_trainer": bool(is_trainer),
            "page_name": "exercise_guides",
        }
        return request.render("ironzone_exercise_guide.portal_exercise_guides", values)

    @http.route("/exercise-guides/<int:guide_id>", type="http", auth="public", website=True)
    def exercise_guide_detail(self, guide_id, **kwargs):
        guide = request.env["ironzone.exercise.guide"].sudo().browse(guide_id).exists()
        if not guide:
            return request.not_found()
        is_trainer = request.env.user.has_group('iz_backend_theme.group_ironzone_trainers')
        partner = False if request.env.user._is_public() or is_trainer else request.env.user.partner_id
        if not guide.is_published or guide.state != "published" or not guide.active:
            return request.not_found()
        if not guide._is_accessible_for_partner(partner):
            # If trainer, show a simplified locked message without purchase CTAs
            ctx = {"guide": guide, "page_name": "exercise_guides", "hide_subscription_ctas": bool(is_trainer)}
            response = request.render("ironzone_exercise_guide.portal_exercise_guide_locked", ctx)
            response.status_code = 403
            return response
        return request.render(
            "ironzone_exercise_guide.portal_exercise_guide_detail",
            {"guide": guide, "page_name": "exercise_guides", "hide_subscription_ctas": bool(is_trainer)},
        )
