from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    sms_history_ids = fields.One2many('sms.history', 'partner_id')

