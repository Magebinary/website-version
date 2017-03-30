# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.http import request


class NewWebsite(models.Model):

    _inherit = "website"

    @api.model
    def get_current_version(self, context=None):
        Version = request.env['website_version.version']
        version_id = request.context.get('version_id')

        if not version_id:
            request.context['version_id'] = 0
            return (0, '')
        return (version_id, Version.browse(version_id).name)

    @api.model
    def get_current_website(self):
        website = super(NewWebsite, self).get_current_website()
        request.context['website_id'] = website.id

        if 'version_id' in request.session:
            request.context['version_id'] = request.session.get('version_id')
        elif self.env['res.users'].has_group('base.group_website_publisher'):
            request.context['version_id'] = 0
        return website