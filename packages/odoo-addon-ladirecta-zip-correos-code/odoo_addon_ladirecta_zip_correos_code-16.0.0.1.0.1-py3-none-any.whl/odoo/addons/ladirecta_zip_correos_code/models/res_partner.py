from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("zip"):
                zip_code = vals.get("zip")
                correos_code = self.env["zip.correos.code.rel"].search(
                    [("zip", "=", zip_code)]
                )
                if correos_code and not vals.get("correos_code_id"):
                    vals["correos_code_id"] = correos_code.correos_code_id.id
        return super().create(vals_list)
