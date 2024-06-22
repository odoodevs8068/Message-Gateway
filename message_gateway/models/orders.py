from odoo import fields, models, api, _
from odoo.exceptions import AccessError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def button_send_mssge(self):
        mobile = f"{self.partner_id.mobile}"
        if not self.partner_id.mobile:
            raise AccessError \
                (f"Sorry ,Without Mobile Number Cannot Send SMS! Please Fill The Mobile NUmber for {self.partner_id.name}")
        return {
            'type': 'ir.actions.act_window',
            'name': f"Send Message",
            'res_model': 'message.wizard',
            'context':{
                'default_partner_id': self.partner_id.id,
                'default_mobile': mobile,
                'default_message': f"SalesPerson : {self.user_id.name} \n"
                                   f"Sale Order : {self.name} \n"
                                   f"Total Amount: {self.amount_total} \n",
                'menu_page' : False,
                'hide_message': True
            },
            'view_mode': 'form',
            'target': 'new'
        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_send_mssge(self):
        mobile = f"{self.partner_id.mobile}"
        if not self.partner_id.mobile:
            raise AccessError \
                (f"Sorry ,Without Mobile Number Cannot Send SMS! Please Fill The Mobile NUmber for {self.partner_id.name}")
        return {
            'type': 'ir.actions.act_window',
            'name': f"Send Message",
            'res_model': 'message.wizard',
            'context':{
                'default_partner_id': self.partner_id.id,
                'default_mobile': mobile,
                'default_message': f"Purchase Order : {self.name} has Moved to {self.state} \n Total Amount: {self.amount_total}",
                'menu_page': False,
                'hide_message': True
            },
            'view_mode': 'form',
            'target': 'new'
        }

