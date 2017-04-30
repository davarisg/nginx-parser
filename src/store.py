import conf
import re

from collections import defaultdict
from datetime import datetime


REQUEST_RE = re.compile(r'^\w+\s(.+)\s')


class Store(object):
    def __init__(self):
        self.log_lines = 0
        self.detail = defaultdict(dict)
        self.extra = defaultdict(dict)
        self.ips = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.referrers = defaultdict(int)
        self.rpm = defaultdict(int)
        self.url_paths = defaultdict(int)
        self.user_agents = defaultdict(int)

        # Transforms
        self.url_and_ips_by_status_code = []

    def aggregate(self, data):
        """
        Takes a log line split by shlex and updates counters
        """
        # Special case for $request variable ("$method $url_path $server_protocol"). Extract the URL path only.
        request = data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES[conf.NGINX_LOG_FORMAT_REQUEST_VARIABLE]]
        url_path = request
        if conf.NGINX_LOG_FORMAT_REQUEST_VARIABLE == 'request':
            try:
                url_path = REQUEST_RE.search(request).groups()[0]
            except AttributeError:
                pass

        self.add_log_line()
        self.add_ip(data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['remote_addr']])
        self.add_referrer(data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['http_referer']])
        self.add_rmp(data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['time_local']])
        self.add_status_code(data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['status']])
        self.add_url_path(url_path)
        self.add_user_agent(data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['http_user_agent']])
        self.add_detail(
            url_path,
            data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['remote_addr']],
            data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES['status']]
        )

        # Process extra Nginx variables (if any)
        for extra_variable in conf.NGINX_LOG_FORMAT_EXTRA_VARIABLES.keys():
            self.add_extra(extra_variable, data[conf.NGINX_LOG_FORMAT_VARIABLE_INDICES[extra_variable]])

    def transform_details_page(self):
        """
        Transforms the detail dict from: {"url": {"ip": {"200": X}}...} to a sorted list
        of [((url, ip), status_codes)...]

        This is done to improve the speed of the paint method.
        """
        url_and_ips_by_status_code = {}
        for url_path, ips in sorted(self.detail.items(), key=lambda k: sum([_c for c in k[1].values() for _c in c.values()]), reverse=True):
            for ip, status_codes in ips.items():
                url_and_ips_by_status_code[(url_path, ip)] = status_codes

        self.url_and_ips_by_status_code = sorted(
            url_and_ips_by_status_code.items(),
            key=lambda k: sum([c for c in k[1].values()]),
            reverse=True
        )

    def add_detail(self, url, ip, status_code):
        """
        Keeps track of status codes by url and IP address.
        """
        if ip not in self.detail[url]:
            self.detail[url][ip] = defaultdict(int)
        self.detail[url][ip]["%sx" % status_code[:2]] += 1

        if self.log_lines % 1000 == 0:
            self.transform_details_page()

    def add_extra(self, key, value):
        """
        Keeps track of any extra Nginx variables specified in the conf file.
        """
        if key not in self.extra:
            self.extra[key] = defaultdict(int)
        self.extra[key][value] += 1

    def add_ip(self, ip):
        self.ips[ip] += 1

    def add_log_line(self):
        self.log_lines += 1

    def add_referrer(self, referrer):
        self.referrers[referrer] += 1

    def add_rmp(self, date):
        """
        Retrieve the hour and minute from time_local to calculate requests per minute
        """
        date = datetime.strptime(date, "%d/%b/%Y:%H:%M:%S +0000")
        date_string = "%s:%s" % (date.hour, date.minute)
        self.rpm[date_string] += 1

    def add_status_code(self, status_code):
        self.status_codes[status_code] += 1

    def add_url_path(self, url_path):
        self.url_paths[url_path] += 1

    def add_user_agent(self, user_agent):
        self.user_agents[user_agent] += 1
