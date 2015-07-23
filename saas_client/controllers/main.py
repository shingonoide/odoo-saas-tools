# -*- coding: utf-8 -*-
import werkzeug
import simplejson
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools import config

import logging
_logger = logging.getLogger(__name__)

class SaasClient(http.Controller):

    @http.route('/saas_client/new_database', type='http', auth='none')
    def new_database(self, **post):
        params = werkzeug.url_encode(post)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % params)

    @http.route('/saas_client/upgrade_database', type='http',
                auth='none', methods=['POST'])
    def upgrade_database(self, **kwargs):
        try:
            db = request.httprequest.host.replace('.', '_')
            post = simplejson.loads(request.httprequest.data)
            _logger.info("Performing upgrade on %s with %s", db, post)
            pwd = config.get('tenant_passwd')
            uid = request.session.authenticate(db, 'admin', pwd)
            if uid:
                status_code = 0
                module = request.registry['ir.module.module']
                # 1. Update addons
                update_addons = post.get('update_addons', "").split(',')
                if update_addons and update_addons[0]:
                    upids = module.search(request.cr, SUPERUSER_ID,
                                          [('name', 'in', update_addons)])
                    if upids:
                        try:
                            module.button_immediate_upgrade(
                                request.cr, SUPERUSER_ID, upids
                            )
                            status_code = 200
                            _logger.info("Update success")
                        except Exception as e:
                            _logger.error(e)
                            status_code = 500
                    else:
                        _logger.info("Update candidates not found")
                        status_code = 404
                # 2. Install addons
                install_addons = post.get('install_addons', "").split(',')
                if install_addons and install_addons[0]:
                    inids = module.search(request.cr, SUPERUSER_ID,
                                          [('name', 'in', install_addons)])
                    if inids:
                        try:
                            module.button_immediate_install(
                                request.cr, SUPERUSER_ID, inids
                            )
                            status_code = 200 if status_code in (
                                0, 200) else 207
                            _logger.info("Install success")
                        except Exception as e:
                            _logger.info(e)
                            status_code = 500 if status_code in (
                                0, 500) else 207
                    else:
                        _logger.info("Install candidates not found")
                        status_code = 404 if status_code in (
                            0, 404) else 207
                # 3. Uninstall addons
                uninstall_addons = post.get('uninstall_addons', "").split(',')
                if uninstall_addons and uninstall_addons[0]:
                    unids = module.search(request.cr, SUPERUSER_ID,
                                          [('name', 'in', uninstall_addons)])
                    if unids:
                        try:
                            module.button_immediate_uninstall(
                                request.cr, SUPERUSER_ID, unids
                            )
                            status_code = 200 if status_code in (
                                0, 200) else 207
                            _logger.info("Uninstall success")
                        except Exception as e:
                            _logger.error(e)
                            status_code = 500 if status_code in (
                                0, 500) else 207
                    else:
                        _logger.info("Uninstall candidates not found")
                        status_code = 404 if status_code in (
                            0, 404) else 207
                # 4. Run fixes
                fixes = post.get('fixes', "").split(',')
                for fix in fixes:
                    if fix:
                        model, method = fix.split('-')
                        try:
                            getattr(request.registry[model], method)(request.cr,
                                                                     SUPERUSER_ID)
                            status_code = 200 if status_code in (
                                0, 200) else 207
                            _logger.info("Fix success")
                        except Exception as e:
                            _logger.error(e)
                            status_code = 500 if status_code in (
                                0, 500) else 207
            else:
                status_code = 401
        except:
            status_code = 500
        return werkzeug.wrappers.Response(status=status_code)
