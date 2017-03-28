# -*- coding: utf-8 -*-
from lxml import etree
from openerp import tools, fields, models, api
from itertools import groupby

class view(models.Model):

    _inherit    = "ir.ui.view"
    website_id  = fields.Many2one('website', ondelete='cascade', string="Website")
    version_id  = fields.Many2one('website_version.version', ondelete='cascade', string="Version")
    key = fields.Char(string='Key')

    _defaults = {
        'website_id': 1,
    }


    # def unlink(self, cr, uid, ids, context=None):
    #     res = super(view, self).unlink(cr, uid, ids, context=context)
    #     self.clear_caches()
    #     return res

    def filter_duplicate(self):
        """
        Filter current recordset only keeping the most suitable view per distinct key
        """
        filtered = self.browse([])
        for _, group in groupby(self, key=lambda r:r.key):
            filtered += sorted(group, key=lambda r:r._sort_suitability_key())[0]
        return filtered

    def _sort_suitability_key(self):
        """
        Key function to sort views by descending suitability

        Suitability of a view is defined as follow:

        * if the view and request version are matched,
        * then fallback on previously defined suitability
        """
        context_website_id = self.env.context.get('website_id', 1)
        website_id = self.website_id.id or 0
        different_website = context_website_id != website_id

        original_suitability = (different_website, website_id)

        context_version_id = self.env.context.get('version_id', 0)
        different_version = context_version_id != (self.version_id.id or 0)

        return (different_version, original_suitability)

    @api.multi
    def write(self, vals):
        if self.env.context is None:
            self.env.context = {}
        version_id = self.env.context.get('version_id')
        version_id2 = self.env
        print "version_id={}".format(version_id)
        print "self.env.context={}".format(self.env.context)
        #If you write on a shared view, your modifications will be seen on every website wich uses these view.
        #To dedicate a view for a specific website, you must create a version and publish these version.
        if version_id and not self.env.context.get('write_on_view') and not 'active' in vals and not self.env.context.get('uid'):
            print "write on version {}".format(version_id)
            self.env.context = dict(self.env.context, write_on_view=True)
            version = self.env['website_version.version'].browse(version_id)
            website_id = version.website_id.id
            version_view_ids = self.env['ir.ui.view']
            for current in self:
                # print "version_id={}".format(version_id)
                #check if current is in version
                if current.version_id.id == version_id:
                    version_view_ids += current
                else:
                    new_v = self.search([('website_id', '=', website_id), ('version_id', '=', version_id), ('key', '=', current.key)])
                    if new_v:
                        version_view_ids += new_v
                    else:
                        copy_v = current.copy({'version_id': version_id, 'website_id': website_id, 'seo_url': None})
                        version_view_ids += copy_v
            return super(view, version_view_ids).write(vals)
        else:
            print "write on master"
            self.env.context = dict(self.env.context, write_on_view=True)
            return super(view, self).write(vals)

    @api.one
    def publish(self):
        #To delete and replace views which are in the website( in fact with website_id)
        master_record = self.search([('key', '=', self.key), ('version_id', '=', False), ('website_id', '=', self.website_id.id)])
        if master_record:
            master_record.unlink()
        self.copy({'version_id': None})

    #To publish a view in backend
    @api.multi
    def action_publish(self):
        self.publish()

    @tools.ormcache_context(accepted_keys=('website_id',))
    def get_view_id(self, cr, uid, xml_id, context=None):
        if self.env.context and 'website_id' in self.env.context and not isinstance(xml_id, (int, long)):
            domain = [('key', '=', xml_id), '|', ('website_id', '=', self.env.context['website_id']), ('website_id', '=', False)]
            if 'version_id' in self.env.context:
                domain += ['|', ('version_id', '=', self.env.context['version_id']), ('version_id', '=', False)]
            xml_id = self.search(domain, order='website_id,version_id', limit=1).id
        elif context and 'website_id' in context and not isinstance(xml_id, (int, long)):
            domain = [('key', '=', xml_id), '|', ('website_id', '=', context['website_id']), ('website_id', '=', False)]
            [view_id] = self.search(cr, uid, domain, order='website_id', limit=1, context=context) or [None]
            if not view_id:
                raise ValueError('View %r in website %r not found' % (xml_id, context['website_id']))
        else:
            xml_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, xml_id, raise_if_not_found=True)
        return xml_id

    @tools.ormcache_context(**dict(accepted_keys=('lang', 'inherit_branding', 'editable', 'translatable', 'website_id', 'version_id')))
    def _read_template(self, cr, uid, view_id, context=None):
        arch = self.read_combined(cr, uid, view_id, fields=['arch'], context=context)['arch']
        arch_tree = etree.fromstring(arch)

        if 'lang' in context:
            arch_tree = self.translate_qweb(cr, uid, view_id, arch_tree, context['lang'], context)

        self.distribute_branding(arch_tree)
        root = etree.Element('templates')
        root.append(arch_tree)
        arch = etree.tostring(root, encoding='utf-8', xml_declaration=True)
        return arch

    #To active or desactive the right views according to the key
    def toggle(self, cr, uid, ids, context=None):
        """ Switches between enabled and disabled statuses
        """
        for view in self.browse(cr, uid, ids, context=dict(context or {}, active_test=False)):
            all_id = self.search(cr, uid, [('key', '=', view.key)], context=dict(context or {}, active_test=False))
            for v in self.browse(cr, uid, all_id, context=dict(context or {}, active_test=False)):
                v.write({'active': not v.active})

    @api.model
    # def translate_qweb(self, cr, uid, id_, arch, lang, context):
    def translate_qweb(self, id_, arch, lang):
        website_view = self.browse(id_)
        # print "website_view={}".format(website_view)
        # if hasattr(website_view, 'seo_url'):
            # print "website_view.seo_url={}".format(website_view.seo_url)
        # print "website_view.key={}".format(website_view.key)
        # print "website_view.write={}".format((website_view.type == 'qweb') and (website_view.xml_id) and (website_view.key == False))
        if (website_view.type == 'qweb') and (website_view.xml_id) and (website_view.key == False):
            user = self.env['res.users'].browse(self.env.uid)
            # print "user={}".format(user)
            if user.has_group('base.group_website_designer'):
                # website_view.write({'key': website_view.xml_id, 'seo_url': False})
                website_view.key = website_view.xml_id
            # else:
            #     print 'This user is not a salesman'
            # flaggroupdi= flag.browse([id_])['groups_id']
            # print "flaggroupdi={}".format(flag.browse([id_])['groups_id'])
            # website_view.write({'key': website_view.xml_id})
            # website_view.key = website_view.xml_id
            # print "website_view.key={}".format(website_view.key)
        if not website_view.key:
            return super(view, self).translate_qweb(id_, arch, lang)
        views = self.search([('key', '=', website_view.key), '|',
                             ('website_id', '=', website_view.website_id.id), ('website_id', '=', False)])
        fallback_views = self
        for v in views:
            if v.mode == 'primary' and v.inherit_id.mode == 'primary':
                # template is `cloned` from parent view
                fallback_views += website_view.inherit_id
        views += fallback_views
        def translate_func(term):
            Translations = self.env['ir.translation']
            trans = Translations._get_source('website', 'view', lang, term, views.ids)
            return trans
        self._translate_qweb(arch, translate_func)
        return arch

    @api.model
    def customize_template_get(self, key, full=False, bundles=False, **kw):
        result = super(view, self).customize_template_get(key, full=full, bundles=bundles, **kw)
        check = []
        res = []
        for data in result:
            if data['name'] not in check:
                check.append(data['name'])
                res.append(data)
        return res

    @api.model
    def get_view_translations(self, xml_id, lang,
                              field=['id', 'res_id', 'value', 'state', 'gengo_translation']):
        irt = self.pool['ir.translation']
        view = self.browse(xml_id)
        view_list = self.search([('key', '=', view.key),
                                 '|', ('website_id', '=', view.website_id.id), ('website_id', '=', False)])
        views_ids = []
        for v in view_list:
            views = self.customize_template_get(v.id, full=True)
            views_ids += [v.get('id') for v in views if v.get('active')]
        domain = [('type', '=', 'view'), ('res_id', 'in', views_ids), ('lang', '=', lang)]
        element_list = irt.search_read(self.env.cr, self.env.uid,
                                       domain, field, context=self.env.context)
        for element in element_list:
            if element['res_id'] in view_list.ids:
                element['res_id'] = xml_id
        return element_list