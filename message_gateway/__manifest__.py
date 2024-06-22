
{
    'name' : 'Message Gateway',
    'version' : '1.2',
    'summary': 'Send Message via SMS and Reset Password using OTP',
    'sequence': 10,
    'depends': ['base', 'base_setup', 'sale', 'purchase'],
    'author': "JD DEVS",
    'data': [
        'views/res_config_settings.xml',
        'views/orders.xml',
        'views/res_partner.xml',
        'views/sms_history.xml',
        'security/ir.model.access.csv',
        'wizards/message_wizard.xml',
        'template/reset_psswd_template.xml',
        'template/verify_otp_template.xml',
        'template/create_password_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
    'images': ['static/description/assets/screenshots/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
