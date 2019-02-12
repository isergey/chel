from django.conf import settings
from django.shortcuts import HttpResponse

DEFAULT_DISALLOW_BOTS = [
    'ahrefsbot',
    'altavista', 'slurp', 'blackwidow', 'chinaclaw', 'custo', 'disco', 'download', 'demon',
    'ecatch',
    'eirgrabber', 'emailsiphon', 'emailwolf', 'superhttp', 'surfbot', 'webwhacker',
    'express', 'webpictures', 'extractorpro', 'eyenetie', 'flashget', 'getright', 'getweb!', 'go!zilla',
    'go-ahead-got-it',
    'grabnet', 'grafula', 'hmview', 'go!zilla', 'go-ahead-got-it',
    'rafula', 'hmview', 'httrack', 'stripper', 'sucker', 'indy', 'interget',
    'ninja', 'jetcar', 'spider', 'larbin',
    'leechftp', 'downloader', 'tool', 'navroad', 'nearsite', 'netants', 'takeout', 'wwwoffle',
    'grabnet', 'netspider', 'vampire',
    'netzip', 'octopus', 'offline', 'pagegrabber', 'foto', 'pavuk', 'pcbrowser',
    'realdownload', 'reget', 'sitesnagger', 'smartdownload', 'superbot', 'webspider',
    'teleport', 'voideye', 'collector', 'webauto',
    'webcopier', 'webfetch', 'webgo', 'webleacher', 'webreaper',
    'websauger', 'extractor', 'quester', 'webstripper', 'webzip', 'wget', 'widow', 'zeus',
    'twengabot', 'htmlparser', 'libwww',
    'scan', 'pyth',
    'pyq', 'webcollector', 'webcopy', 'webcraw'
]

DISALLOW_BOTS = getattr(settings, 'ACCESS_DISALLOW_BOTS', DEFAULT_DISALLOW_BOTS)


class AccessMiddleware:
    def process_response(self, request, response):
        for bot in DISALLOW_BOTS:
            if bot in request.META.get('HTTP_USER_AGENT', '').lower():
                return HttpResponse(status=410)
        return response
