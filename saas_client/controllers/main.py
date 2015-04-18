# -*- coding: utf-8 -*-
import werkzeug
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.auth_oauth.controllers import main as oauth


class SaasClient(http.Controller):

    @http.route('/saas_client/new_database', type='http', auth='none')
    def new_database(self, **post):
        params = werkzeug.url_encode(post)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % params)

    @http.route('/saas_client/upgrade_database', type='http', auth='none')
    def upgrade_database(self, **post):
        update_addons = post.get('update_addons', '').split(',')
        if update_addons:
            module = request.registry['ir.module.module']
            aids = module.search(request.cr, SUPERUSER_ID,
                                 [('name', 'in', update_addons)])
            if aids:
                module.button_upgrade(request.cr, SUPERUSER_ID, aids)
