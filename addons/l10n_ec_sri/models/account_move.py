# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError
import base64


class AccountMove(models.Model):
    """
    Extends account.move with SRI integration logic.
    Field definitions inherited from l10n_ec_edi.

    Note: 2026 Consumidor Final validations are handled by l10n_ec_edi module.
    """

    _inherit = "account.move"

    # Additional fields not in l10n_ec_edi
    l10n_ec_authorization_date = fields.Datetime(
        string="Authorization Date", copy=False
    )
    l10n_ec_sri_error = fields.Text(string="SRI Error Message", copy=False)

    def _generate_l10n_ec_xml_content(self):
        self.ensure_one()
        if not self.l10n_ec_sri_access_key:
            self.l10n_ec_sri_access_key = self.env[
                "l10n_ec.sri.xml"
            ].generate_access_key(self)

        xml_content = self.env["l10n_ec.sri.xml"].render_xml(self)
        if not isinstance(xml_content, bytes):
            xml_content = xml_content.encode("utf-8")
        return xml_content

    def action_generate_demo_xml(self):
        for move in self:
            if move.state != "posted":
                raise UserError(_("Invoice must be Posted before generating the demo XML."))

            xml_content = move._generate_l10n_ec_xml_content()
            move.l10n_ec_xml_data = base64.b64encode(xml_content)
            move.l10n_ec_sri_status = "signed"
            move.l10n_ec_sri_error = False
            move.l10n_ec_sri_response = _(
                "Demo local: XML generated without signature and without SRI transmission."
            )

    def action_send_sri(self):
        """
        Orchestrator: Key Gen -> XML Gen -> Sign -> Send
        """
        for move in self:
            if move.l10n_ec_sri_status in ["authorized", "sent"]:
                continue

            if move.company_id.l10n_ec_sri_environment == "demo":
                move.action_generate_demo_xml()
                continue

            # 1. Generate Access Key and XML
            xml_content = move._generate_l10n_ec_xml_content()

            # 2. Sign XML
            signed_xml = self._sign_xml(xml_content)
            move.l10n_ec_xml_data = base64.b64encode(signed_xml)

            # 3. Send to SRI (Real Call)
            env_code = self.env["l10n_ec.sri.xml"]._get_environment_code(move.company_id)
            response = self.env["l10n_ec.sri.service"].send_document(
                signed_xml, environment=env_code
            )

            if response.get("status") == "RECIBIDA":
                move.l10n_ec_sri_status = "sent"
                move.l10n_ec_sri_error = False
            else:
                move.l10n_ec_sri_status = "rejected"
                move.l10n_ec_sri_error = "\n".join(response.get("messages", []))

    def action_check_sri(self):
        """
        Ping Check Status service (Real Implementation)
        """
        for move in self:
            if not move.l10n_ec_sri_access_key:
                raise UserError(_("No Access Key generated yet."))

            response = self.env["l10n_ec.sri.service"].check_authorization(
                move.l10n_ec_sri_access_key
            )

            if response.get("status") == "AUTORIZADO":
                move.l10n_ec_sri_status = "authorized"
                if response.get("date"):
                    move.l10n_ec_authorization_date = response["date"]

                if response.get("authorized_xml"):
                    move.l10n_ec_xml_data = base64.b64encode(
                        response["authorized_xml"].encode("utf-8")
                    )
            elif response.get("status") == "NO AUTORIZADO":
                move.l10n_ec_sri_status = "rejected"
                move.l10n_ec_sri_error = "\n".join(response.get("messages", []))

    def _sign_xml(self, xml_content):
        """
        Internal helper to call the signer lib.
        """
        self.ensure_one()
        certificate = self.company_id.l10n_ec_certificate_id
        if not certificate:
            raise UserError(_("No active Electronic Signature found for this company."))

        return self.env["l10n_ec.sri.signer"].sign_xml(
            xml_content, certificate.content, certificate.password
        )
