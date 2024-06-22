from odoo import fields, models, api, _
from odoo.exceptions import AccessError, ValidationError
import vonage
from datetime import datetime
from twilio.rest import Client
import json
import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException


class SendMessageWizard(models.TransientModel):
    _name = "message.wizard"

    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_ids = fields.Many2many('res.partner', string='Customers')
    message = fields.Text('Content')
    mobile = fields.Char('Mobile')
    channel = fields.Selection(selection=[
        ('sms', 'SMS'),
    ], string="Channel", default='sms')

    gateway = fields.Selection(selection=[
        ('nexmo', 'Nexmo'),
        ('twilio', 'Twilio'),
        ('clicksendsms', 'Click Send SMS'),
    ], string="SMS Gateway", config_parameter='message_gateway.gateway')

    @api.onchange('gateway')
    def onchange_gateway(self):
        """By Onchange Set Gateway Value"""
        if self.gateway:
            self.env['ir.config_parameter'].sudo().set_param('message_gateway.gateway', self.gateway)

    def get_active_context(self):
        """Get Active ID,Model from Context"""
        if self.env.context.get('active_id'):
            active_id = self.env.context.get('active_id')
            active_model = self.env.context.get('active_model')
            order_id = self.env[active_model].browse(active_id)
            return active_id, active_model, order_id

    def _get_nexmo_api_values(self):
        """Get Nexmo API Credentials"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('message_gateway.api_key') or False
        api_secret = self.env['ir.config_parameter'].sudo().get_param('message_gateway.api_secret') or False
        sender_no = self.env['ir.config_parameter'].sudo().get_param('message_gateway.sender_no') or False
        return api_key, api_secret, sender_no

    def _get_twilio_api_values(self):
        """Get Twilio API Credentials"""
        account_sid = self.env['ir.config_parameter'].sudo().get_param('message_gateway.account_sid') or False
        auth_token = self.env['ir.config_parameter'].sudo().get_param('message_gateway.auth_token') or False
        twilio_no = self.env['ir.config_parameter'].sudo().get_param('message_gateway.twilio_no') or False
        return account_sid, auth_token, twilio_no

    def _get_clicksendsms_api_values(self):
        """Get Click Send SMS API Credentials"""
        clicksend_username = self.env['ir.config_parameter'].sudo().get_param('message_gateway.clicksend_username') or False
        click_send_api_key = self.env['ir.config_parameter'].sudo().get_param('message_gateway.click_send_api_key') or False
        click_send_sender_no = self.env['ir.config_parameter'].sudo().get_param('message_gateway.click_send_sender_no') or False
        return clicksend_username, click_send_api_key, click_send_sender_no

    def create_sms_history(self, gateway, partner_id):
        if gateway == 'nexmo':
            from_no = self.env['ir.config_parameter'].sudo().get_param('message_gateway.sender_no') or False
        elif gateway == 'twilio':
            from_no = self.env['ir.config_parameter'].sudo().get_param('message_gateway.twilio_no') or False
        else:
            from_no = self.env['ir.config_parameter'].sudo().get_param('message_gateway.click_send_sender_no') or False

        history_data = {
            'partner_id': partner_id.id,
            'gateway': gateway,
            'from_no': from_no,
            'to_no': self.mobile,
            'message': self.message,
            'datetime': datetime.now()
        }
        create_history = self.env['sms.history'].create(history_data)
        return create_history

    def send_sms_nexmo_gateway(self, order_id, api_key, api_secret, sender_no, message, to_no, gateway):
        client = vonage.Client(key=api_key, secret=api_secret)
        sms = vonage.Sms(client)
        responseData = sms.send_message(
            {
                "from": sender_no,
                "to": to_no,
                "text": message,
            }
        )
        if responseData["messages"][0]["status"] == "0":
            _log_message = f"Message Sent Successfully"
            if not self.env.context.get('no_create'):
                partner_id = self.partner_id
                self.create_sms_history(gateway, partner_id)
            else:
                history_id = self.env.context.get('history_id')
                history_id.datetime = datetime.now()
        else:
            _log_message = f"Message  UnSuccessfully {responseData['messages'][0]['error-text']}"
        if order_id:
            order_id._message_log(body=_log_message)

    def send_sms_twilio_gatway(self, order_id, acct_sid, token, twilio_no, message, to_no,gateway):
        client = Client(acct_sid, token)
        message = client.messages.create(
            body=message,
            from_=twilio_no,
            to=to_no
        )
        _log_message = 'Message Sent Successfully'
        if message.sid:
            if not self.env.context.get('login_page'):
                order_id._message_log(body=_log_message)
            if not self.env.context.get('no_create'):
                partner_id = self.partner_id
                self.create_sms_history(gateway, partner_id)
            else:
                history_id = self.env.context.get('history_id')
                history_id.datetime = datetime.now()

    def send_sms_clicksendsms_gateway(self, order_id, clicksend_username, click_send_api_key, click_send_sender_no, message, to_no, gateway):
        configuration = clicksend_client.Configuration()
        configuration.username = clicksend_username
        configuration.password = click_send_api_key
        api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
        sms_message = SmsMessage(source="php", _from= click_send_sender_no,
                                 body=message,
                                 to=to_no)
        sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])

        try:
            api_response = api_instance.sms_send_post(sms_messages)
            if 'SUCCESS' in api_response and not self.env.context.get('login_page'):
                print(api_response)
                _log_message = f"Message Sent Successfully"
                order_id._message_log(body=_log_message)
                if not self.env.context.get('no_create'):
                    partner_id = self.partner_id
                    self.create_sms_history(gateway, partner_id)
                else:
                    history_id = self.env.context.get('history_id')
                    history_id.datetime = datetime.now()
        except ApiException as e:
            raise ValidationError("Exception when calling SMSApi->sms_send_post: %s\n" % e)

    def button_send_sms(self):
        gateway = self.env['ir.config_parameter'].sudo().get_param('message_gateway.gateway') or False
        message, to_no = self.message, self.mobile

        if self.env.context.get('menu_page') == False:
            active_id, active_model, order_id = self.get_active_context()
        else:
            order_id = self.partner_id

        if gateway == 'nexmo':
            api_key, api_secret, sender_no = self._get_nexmo_api_values()  # Get Nexmo Credentials
            (self.with_context(no_create=False).
             send_sms_nexmo_gateway(order_id, api_key, api_secret, sender_no, message, to_no, gateway))
        elif gateway == "twilio":
            acct_sid, token, twilio_no = self._get_twilio_api_values()  # Get Twilio Credentials
            (self.with_context(no_create=False).
             send_sms_twilio_gatway(order_id, acct_sid, token, twilio_no, message, to_no, gateway))
        elif gateway == "clicksendsms":
            clicksend_username, click_send_api_key, click_send_sender_no = self._get_clicksendsms_api_values()   # Get ClickSendSMS Credentials
            (self.with_context(no_create=False).
             send_sms_clicksendsms_gateway(order_id, clicksend_username, click_send_api_key, click_send_sender_no, message, to_no, gateway))

    def button_resend_sms(self, history):
        history_id = self.env['sms.history'].browse(history)
        message, to_no, gateway = history_id.message, history_id.to_no, history_id.gateway
        order_id = history_id.partner_id
        if gateway == 'nexmo':
            sender_no = history_id.from_no
            api_key = self.env['ir.config_parameter'].sudo().get_param('message_gateway.api_key') or False
            api_secret = self.env['ir.config_parameter'].sudo().get_param('message_gateway.api_secret') or False
            (self.with_context(no_create=True, history_id=history_id).
             send_sms_nexmo_gateway(order_id, api_key, api_secret, sender_no, message, to_no, gateway))
        elif gateway == "twilio":
            twilio_no = history_id.from_no
            account_sid = self.env['ir.config_parameter'].sudo().get_param('message_gateway.account_sid') or False
            auth_token = self.env['ir.config_parameter'].sudo().get_param('message_gateway.auth_token') or False
            (self.with_context(no_create=True, history_id=history_id).
             send_sms_twilio_gatway(order_id, account_sid, auth_token, twilio_no, message, to_no, gateway))
        elif gateway == "clicksendsms":
            click_send_sender_no = history_id.from_no
            clicksend_username = self.env['ir.config_parameter'].sudo().get_param('message_gateway.clicksend_username') or False
            click_send_api_key = self.env['ir.config_parameter'].sudo().get_param('message_gateway.click_send_api_key') or False
            (self.with_context(no_create=True, history_id=history_id).
             send_sms_clicksendsms_gateway(order_id, clicksend_username, click_send_api_key, click_send_sender_no, message, to_no, gateway))