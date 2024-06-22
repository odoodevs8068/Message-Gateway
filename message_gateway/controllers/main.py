from odoo import http
from odoo.http import request
from odoo import api, models, fields
from odoo.exceptions import AccessError, UserError, AccessDenied, ValidationError
import random


class WebResetPassword(http.Controller):

    @http.route('/reset_password_opt', auth='public', type='http', website=True,csrf=False)
    def reset_password_opt(self, **kwargs):
        return request.render("message_gateway.reset_password_with_otp")

    @http.route('/send_otp', type='http', auth="public", website=True, csrf=False)
    def send_otp(self, **kwargs):
        check_email = kwargs.get('check_email')
        mobile_no = kwargs.get('mobile_no')
        countrycode = kwargs.get('countrycode')
        without_cc = kwargs.get('without_ccout_cc')
        get_gateway = kwargs.get('sms_gateway')
        request.env['ir.config_parameter'].sudo().set_param('message_gateway.gateway', get_gateway)
        user = request.env['res.users'].sudo().search([('login', '=', check_email)])

        if not user:
            error_message = "User not found. Please check the email provided."
            raise ValidationError(error_message)

        if without_cc == 'on':
            to_no = user.partner_id.mobile
        else:
            to_no = f"{countrycode} {user.partner_id.mobile}"

        if not mobile_no:
            raise ValidationError(f"Please Enter Mobile Number")
        elif not user.partner_id.mobile:
            raise ValidationError(f"Phone Number for {user.name} is not Registered,")
        elif mobile_no != user.partner_id.mobile:
            error_message = f"Sorry , Your Registered Mobile Number is {user.partner_id.mobile}"
            raise ValidationError(error_message)
        elif "+" not in to_no:
            error_message = (f"Sorry, To Send OTP Country code is Manditory, Your Registered Number is {user.partner_id.mobile}")
            raise ValidationError(error_message)

        get_otp = self.get_random_otp()
        request.session['sended_otp'] = get_otp
        request.session['user_login_id'] = user.id

        gateway = request.env['ir.config_parameter'].sudo().get_param('message_gateway.gateway') or False
        message_wizard = request.env['message.wizard']
        message = "Your Password Reset OTP is '%s' \n Dont Share OTP With Others" % get_otp
        order_id = None
        if gateway == 'nexmo':
            api_key, api_secret, sender_no = message_wizard._get_nexmo_api_values()
            self._check_credentials(api_key,api_secret, sender_no, gateway)
            message_wizard.with_context(login_page=True).send_sms_nexmo_gateway(order_id, api_key, api_secret, sender_no, message, to_no, gateway)
        elif gateway == 'twilio':
            account_sid, auth_token, twilio_no = message_wizard._get_twilio_api_values()
            self._check_credentials(account_sid,auth_token, twilio_no, gateway)
            message_wizard.with_context(login_page=True).send_sms_twilio_gatway(order_id, account_sid, auth_token, twilio_no, message, to_no,gateway)
        elif gateway == "clicksendsms":
            clicksend_username, click_send_api_key, click_send_sender_no = message_wizard._get_clicksendsms_api_values()
            self._check_credentials(clicksend_username,click_send_api_key, click_send_sender_no, gateway)
            message_wizard.with_context(login_page=True).send_sms_clicksendsms_gateway(order_id, clicksend_username, click_send_api_key, click_send_sender_no, message, to_no, gateway)
        return request.render("message_gateway.verify_otp_template")

    def _check_credentials(self, key, token, number, gateway):
        if not any(key or token or number):
            raise ValidationError(f"Credentials are Not Configured for {gateway}, Please Contact Your Administrator")

    def get_random_otp(self):
        opt_list = []
        for x in range(0, 6):
            opt_list.append(x)
        random.shuffle(opt_list)
        random_otp = "".join(str(n) for n in opt_list)
        return random_otp

    @http.route('/verify_otp', type='http', auth="public", website=True, csrf=False)
    def verify_opt(self, **kwargs):
        otp = kwargs.get('otp')
        sended_otp = request.session.get('sended_otp')
        if otp != sended_otp:
            raise ValidationError("Please Entered Correct OTP")
        else:
            return request.render("message_gateway.create_new_password")

    @http.route('/create_password', type='http', auth="public", website=True, csrf=False)
    def create_password(self, **kwargs):
        new_psswd = kwargs.get('new_password')
        confirm_psswd = kwargs.get('confirm_password')
        if confirm_psswd != new_psswd:
            raise ValidationError(f"Please ensure that the confirm password matches the new password.")
        user_login_id = request.session.get('user_login_id')
        user_id = request.env['res.users'].sudo().browse(user_login_id)
        user_id.write({'password': confirm_psswd})
        values = {'user_id': user_id}
        return request.render("message_gateway.password_success", values)


    @http.route('/check_login_page', auth='public', type='http', website=True,csrf=False)
    def check_login_page(self, **kwargs):
        return request.render("message_gateway.check_login_page")

    @http.route('/check_login_page_2', auth='public', type='http', website=True,csrf=False)
    def check_login_page_2(self, **kwargs):
        return request.render("message_gateway.check_login_page_2")
