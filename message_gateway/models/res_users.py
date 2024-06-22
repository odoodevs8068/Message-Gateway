from odoo import fields, models, api, _


class ResUsersInherit(models.Model):
    _inherit = "res.users"

    otp = fields.Char('')

