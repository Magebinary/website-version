# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.exceptions import Warning
from openerp.http import request
from openerp.tools.translate import _


class version(models.Model):
    """ A version is a set of qweb views which differs from the qweb views in production for the website.
    """

    _name = "website_version.version"

    name = fields.Char(string="Title", required=True)
    view_ids = fields.One2many('ir.ui.view', 'version_id', string="View", copy=True)
    website_id = fields.Many2one('website', ondelete='cascade', string="Website")
    create_date = fields.Datetime('Create Date')

    _sql_constraints = [
        ('name_uniq', 'unique(name, website_id)', _('You cannot have multiple versions with the same name in the same domain!')),
    ]

    @api.multi
    def action_publish(self):
        for version in self:
            self.view_ids.publish()

    @api.one
    def publish_version(self, save_master, copy_master_name):
        del_l = self.env['ir.ui.view']
        copy_l = self.env['ir.ui.view']
        ir_ui_view = self.env['ir.ui.view']
        for view in self.view_ids:
            master_id = ir_ui_view.search([('key', '=', view.key), ('version_id', '=', False)])
            master_id.write({'arch' : view.arch})
        return self.name

    #To make a version of a version
    @api.one
    def copy_version(self, new_version_id):
        for view in self.view_ids:
            view.copy({'version_id': new_version_id, 'seo_url': None })

