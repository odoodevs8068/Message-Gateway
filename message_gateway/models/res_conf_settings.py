from odoo import fields, models, api, _
from odoo.exceptions import AccessError, ValidationError


class ConfSetting(models.TransientModel):
    _inherit = "res.config.settings"

    # Nexmo Fields
    api_key = fields.Char('API Key', config_parameter='message_gateway.api_key')
    api_secret = fields.Char('API Secret', config_parameter='message_gateway.api_secret')
    sender_no = fields.Char('Sender NO.', config_parameter='message_gateway.sender_no')

    # Twilio Fields
    account_sid = fields.Char('Account SID', config_parameter='message_gateway.account_sid')
    auth_token = fields.Char('Auth Token', config_parameter='message_gateway.auth_token')
    twilio_no = fields.Char('Twilio NO.', config_parameter='message_gateway.twilio_no')

    # Clicksend Fields
    clicksend_username = fields.Char('Username', config_parameter='message_gateway.clicksend_username')
    click_send_api_key = fields.Char('API Key', config_parameter='message_gateway.click_send_api_key')
    click_send_sender_no = fields.Char('Sender NO.', config_parameter='message_gateway.click_send_sender_no')

    gateway = fields.Selection(selection=[
        ('nexmo', 'Nexmo'),
        ('twilio', 'Twilio'),
        ('clicksendsms', 'Click Send SMS'),
    ], string="Gateway",  config_parameter='message_gateway.gateway')

    def set_values(self):
        res = super(ConfSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.api_key', self.api_key)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.api_secret', self.api_secret)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.account_sid', self.account_sid)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.auth_token', self.auth_token)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.sender_no', self.sender_no)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.twilio_no', self.twilio_no)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.clicksend_username', self.clicksend_username)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.click_send_api_key', self.click_send_api_key)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.click_send_sender_no', self.click_send_sender_no)
        self.env['ir.config_parameter'].sudo().set_param('message_gateway.gateway', self.gateway)
        return res

    @api.model
    def get_values(self):
        res = super(ConfSetting, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            api_key=ICPSudo.get_param('message_gateway.api_key'),
            api_secret=ICPSudo.get_param('message_gateway.api_secret'),
            account_sid=ICPSudo.get_param('message_gateway.account_sid'),
            auth_token=ICPSudo.get_param('message_gateway.auth_token'),
            sender_no=ICPSudo.get_param('message_gateway.sender_no'),
            twilio_no=ICPSudo.get_param('message_gateway.twilio_no'),
            clicksend_username=ICPSudo.get_param('message_gateway.clicksend_username'),
            click_send_api_key=ICPSudo.get_param('message_gateway.click_send_api_key'),
            click_send_sender_no=ICPSudo.get_param('message_gateway.click_send_sender_no'),
            gateway=ICPSudo.get_param('message_gateway.gateway'),
        )
        return res

    def execute(self):
        res = super(ConfSetting, self).execute()
        api_key = self.env['ir.config_parameter'].sudo().set_param('message_gateway.api_key', self.api_key)
        api_secret = self.env['ir.config_parameter'].sudo().set_param('message_gateway.api_secret', self.api_secret)
        account_sid = self.env['ir.config_parameter'].sudo().set_param('message_gateway.account_sid', self.account_sid)
        auth_token = self.env['ir.config_parameter'].sudo().set_param('message_gateway.auth_token', self.auth_token)
        sender_no = self.env['ir.config_parameter'].sudo().set_param('message_gateway.sender_no', self.sender_no)
        twilio_no = self.env['ir.config_parameter'].sudo().set_param('message_gateway.twilio_no', self.twilio_no)
        clicksend_username = self.env['ir.config_parameter'].sudo().set_param('message_gateway.clicksend_username', self.clicksend_username)
        click_send_api_key = self.env['ir.config_parameter'].sudo().set_param('message_gateway.click_send_api_key', self.click_send_api_key)
        click_send_sender_no = self.env['ir.config_parameter'].sudo().set_param('message_gateway.click_send_sender_no', self.click_send_sender_no)
        gateway = self.env['ir.config_parameter'].sudo().set_param('message_gateway.gateway', self.gateway)

        if gateway == 'nexmo':
            if not api_key or not api_secret or not sender_no:
                raise AccessError(f"Sorry , Credentials Missing for {gateway}")
        elif gateway == 'twilio':
            if not account_sid or not auth_token or not twilio_no:
                raise AccessError(f"Sorry , Credentials Missing for {gateway}")
        elif gateway == 'clicksendsms':
            if not clicksend_username or not click_send_api_key or not click_send_sender_no:
                raise AccessError(f"Sorry , Credentials Missing for {gateway}")
        return res

    def button_view_sms_history(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"SMS History",
            'res_model': 'sms.history',
            'view_mode': 'tree',
            'target': 'current'
        }