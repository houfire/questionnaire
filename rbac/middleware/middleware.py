import re

from django.conf import settings
from django.shortcuts import render, redirect, reverse, HttpResponse


# from django.utils.deprecation import MiddlewareMixin
class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class RbacMiddleware(MiddlewareMixin):
    def process_request(self, request):
        current_url = request.path_info

        '''匹配白名单'''
        for url in settings.VALID_URLS:
            re_url = "^{}$".format(url)
            if re.match(re_url, current_url):
                return None

        '''权限匹配'''
        per_index = request.session.get('per_index')

        if not per_index:  # 没有用户登录
            return redirect(reverse('login.css'))

        per_info_dict = request.session.get('per_info_dict')

        flag = False
        for dict_item in per_info_dict.values():
            for url_dict in dict_item['urls_info']:
                url = url_dict.get('url')
                re_url = "^{}$".format(url)
                if re.match(re_url, current_url):
                    request.session['codes_list'] = dict_item['codes']
                    flag = True
                    break
            if flag:
                break

        if not flag:
            return HttpResponse('无权访问')
