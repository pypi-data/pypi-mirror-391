from odoo import fields, models


class ZipCorreosCodeRel(models.Model):
    _name = "zip.correos.code.rel"
    _description = "Correos Codes by Zip"

    zip = fields.Char(required=True)
    correos_code_id = fields.Many2one(
        "correos.shipment.code", string="Correos Code", required=True
    )

    _sql_constraints = [
        (
            "zip_correos_code_uniq",
            "UNIQUE(zip, correos_code_id)",
            "Relation between zip and correos code must be unique!",
        ),
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.zip} - {rec.correos_code_id.code}"
            result.append((rec.id, name))
        return result
