from odoo import fields, models, api, _
from datetime import datetime, date


class SMSHistory(models.Model):
    _name = "sms.history"

    gateway = fields.Selection(selection=[
        ('nexmo', 'Nexmo'),
        ('twilio', 'Twilio'),
        ('clicksendsms', 'clicksendsms'),
    ], string="Gateway", config_parameter='message_gateway.gateway')
    from_no = fields.Char('From')
    to_no = fields.Char('To')
    partner_id = fields.Many2one('res.partner', string='Customer')
    message = fields.Text('Content')
    datetime = fields.Datetime(string="Datetime")

    def button_resend(self):
        mssge_wizard = self.env['message.wizard']
        history = self.id
        mssge_wizard.button_resend_sms(history)