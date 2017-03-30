# -*- coding: utf-8 -*-
import datetime
from openerp import http
from openerp.http import request
from openerp.addons.website.controllers.main import Website
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class Versioning_Controller(Website):

    @http.route('/website_version/change_version', type='json', auth="user", website=True)
    def change_version(self, version_id):
        request.session['version_id'] = version_id
        return version_id

    @http.route('/website_version/create_version', type='json', auth="user", website=True)
    def create_version(self, name, version_id=None):
        if not name:
            name = datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        new_version = request.env['website_version.version'].create({'name': name, 'website_id': request.website.id})
        if version_id:
            request.env['website_version.version'].browse(version_id).copy_version(new_version.id)
        request.session['version_id'] = new_version.id
        return new_version.id

    @http.route('/website_version/delete_version', type='json', auth="user", website=True)
    def delete_version(self, version_id):
        version = request.env['website_version.version'].browse(version_id)
        name = version.name
        version.unlink()
        current_id = request.context.get('version_id')
        if version_id == current_id:
            request.session['version_id'] = 0
        return name

    @http.route('/website_version/all_versions', type='json', auth="public", website=True)
    def all_versions(self, view_id):
        #To get all versions in the menu
        view = request.env['ir.ui.view'].browse(view_id)
        Version = request.env['website_version.version']
        website_id = request.website.id
        versions = Version.search([('website_id', '=', website_id)])
        context = request.context
        current_version_id = request.context.get('version_id')
        check = False
        result = []
        for ver in versions:
            if ver.id == current_version_id:
                #To show in bold the current version in the menu
                result.append({'id': ver.id, 'name': ver.name, 'bold': 1})
                check = True
            else:
                result.append({'id': ver.id, 'name': ver.name, 'bold': 0})
        #To always show in the menu the current version
        if not check and current_version_id:
            result.append({'id': current_version_id, 'name': Version.browse(current_version_id).name, 'bold': 1})
        return result

    @http.route('/website_version/publish_version', type='json', auth="user", website=True)
    def publish_version(self, version_id, save_master, copy_master_name):
        request.session['version_id'] = 0
        return request.env['website_version.version'].browse(version_id).publish_version(save_master, copy_master_name)

    @http.route('/website_version/diff_version', type='json', auth="user", website=True)
    def diff_version(self, version_id):
        mod_version = request.env['website_version.version']
        version = mod_version.browse(version_id)
        name_list = []
        for view in version.view_ids:
            name_list.append({'name': view.name, 'url': '/page/' + view.name.replace(' ', '').lower()})
        return name_list