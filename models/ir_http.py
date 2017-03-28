# -*- coding: utf-8 -*-

from openerp.http import request
from openerp.osv import orm
import json

class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        x = super(ir_http, self)._dispatch()
        if request.website_enabled:
            request.context['website_id'] = request.website.id
        if request.context.get('website_version_experiment'):
            data=json.dumps(request.context['website_version_experiment'], ensure_ascii=False)
            x.set_cookie('website_version_experiment', data)
        return x

    def get_page_key(self):
        key = super(ir_http, self).get_page_key()
        seq_ver = [int(ver) for ver in request.context.get('website_version_experiment', {}).values()]
        key += (str(sorted(seq_ver)),)
        return key

    # def _dispatch(self):
    #     first_pass = not hasattr(request, 'website')
    #     request.website = None
    #     func = None
    #     try:
    #         if request.httprequest.method == 'GET' and '//' in request.httprequest.path:
    #             new_url = request.httprequest.path.replace('//', '/') + '?' + request.httprequest.query_string
    #             return werkzeug.utils.redirect(new_url, 301)
    #         func, arguments = self._find_handler()
    #         request.website_enabled = func.routing.get('website', False)
    #     except werkzeug.exceptions.NotFound:
    #         # either we have a language prefixed route, either a real 404
    #         # in all cases, website processes them
    #         request.website_enabled = True

    #     request.website_multilang = (
    #         request.website_enabled and
    #         func and func.routing.get('multilang', func.routing['type'] == 'http')
    #     )

    #     cook_lang = request.httprequest.cookies.get('website_lang')
    #     if request.website_enabled:
    #         try:
    #             if func:
    #                 self._authenticate(func.routing['auth'])
    #             elif request.uid is None:
    #                 self._auth_method_public()
    #         except Exception as e:
    #             return self._handle_exception(e)

    #         request.redirect = lambda url, code=302: werkzeug.utils.redirect(url_for(url), code)
    #         request.website = request.registry['website'].get_current_website(request.cr, request.uid, context=request.context)
    #         request.context['website_id'] = request.website.id
    #         langs = [lg[0] for lg in request.website.get_languages()]
    #         path = request.httprequest.path.split('/')
    #         if first_pass:
    #             nearest_lang = not func and self.get_nearest_lang(path[1])
    #             url_lang = nearest_lang and path[1]
    #             preferred_lang = ((cook_lang if cook_lang in langs else False)
    #                               or self.get_nearest_lang(request.lang)
    #                               or request.website.default_lang_code)

    #             is_a_bot = self.is_a_bot()

    #             request.lang = request.context['lang'] = nearest_lang or preferred_lang
    #             # if lang in url but not the displayed or default language --> change or remove
    #             # or no lang in url, and lang to dispay not the default language --> add lang
    #             # and not a POST request
    #             # and not a bot or bot but default lang in url
    #             if ((url_lang and (url_lang != request.lang or url_lang == request.website.default_lang_code))
    #                     or (not url_lang and request.website_multilang and request.lang != request.website.default_lang_code)
    #                     and request.httprequest.method != 'POST') \
    #                     and (not is_a_bot or (url_lang and url_lang == request.website.default_lang_code)):
    #                 if url_lang:
    #                     path.pop(1)
    #                 if request.lang != request.website.default_lang_code:
    #                     path.insert(1, request.lang)
    #                 path = '/'.join(path) or '/'
    #                 redirect = request.redirect(path + '?' + request.httprequest.query_string)
    #                 redirect.set_cookie('website_lang', request.lang)
    #                 return redirect
    #             elif url_lang:
    #                 request.uid = None
    #                 path.pop(1)
    #                 return self.reroute('/'.join(path) or '/')

    #         if not request.context.get('tz'):
    #             request.context['tz'] = request.session.get('geoip', {}).get('time_zone')
    #         # bind modified context
    #         request.website = request.website.with_context(request.context)

    #     # cache for auth public
    #     cache_time = getattr(func, 'routing', {}).get('cache')
    #     cache_enable = cache_time and request.httprequest.method == "GET" and request.website.user_id.id == request.uid
    #     cache_response = None
    #     if cache_enable:
    #         key = self.get_page_key()
    #         try:
    #             r = self.pool.cache[key]
    #             if r['time'] + cache_time > time.time():
    #                 cache_response = openerp.http.Response(r['content'], mimetype=r['mimetype'])
    #             else:
    #                 del self.pool.cache[key]
    #         except KeyError:
    #             pass

    #     if cache_response:
    #         request.cache_save = False
    #         resp = cache_response
    #     else:
    #         request.cache_save = key if cache_enable else False
    #         resp = super(ir_http, self)._dispatch()

    #     if request.website_enabled and cook_lang != request.lang and hasattr(resp, 'set_cookie'):
    #         resp.set_cookie('website_lang', request.lang)
    #     x = resp
    #     if request.context.get('website_version_experiment'):
    #         data=json.dumps(request.context['website_version_experiment'], ensure_ascii=False)
    #         x.set_cookie('website_version_experiment', data)
    #     return x
