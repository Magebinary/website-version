# -*- coding: utf-8 -*-
"""
Website-context rendering needs to add some metadata to rendered fields,
as well as render a few fields differently.

Also, adds methods to convert values back to openerp models.
"""

from openerp import models
import logging
_logger = logging.getLogger(__name__)

class QWeb(models.AbstractModel):
    """ QWeb object for rendering stuff in the website context
    """
    _inherit = 'website.qweb'

    def render(self, cr, uid, id_or_xml_id, qwebcontext=None, loader=None, context=None):
        if context is None:
            context = {}
        # Views that are not pages do not have context
        if len(context) == 0:
            context = qwebcontext.context
        website_id = context.get('website_id')
        id_or_xml_ids = {}
        if website_id:
            if 'version_id' in context:
                version_id = context.get('version_id')
                if version_id:
                    id_or_xml_ids = self.pool["ir.ui.view"].search(cr, uid, [('key', '=', id_or_xml_id), '|', ('version_id', '=', False), ('version_id', '=', version_id), '|', ('website_id', '=', website_id), ('website_id', '=', False)], order='website_id, version_id', limit=1, context=context)
                else:
                    id_or_xml_ids = self.pool["ir.ui.view"].search(cr, uid, [('key', '=', id_or_xml_id), ('version_id', '=', False), '|', ('website_id', '=', website_id), ('website_id', '=', False)], order='website_id', limit=1, context=context)

            else:
                id_or_xml_ids = self.pool["ir.ui.view"].search(cr, uid, [('key', '=', id_or_xml_id), '|', ('website_id', '=', website_id), ('website_id', '=', False), ('version_id', '=', False)], order='website_id', limit=1, context=context)
            if len(id_or_xml_ids) > 0:
                id_or_xml_id = id_or_xml_ids[0]
        return super(QWeb, self).render(cr, uid, id_or_xml_id, qwebcontext, loader=loader, context=context)