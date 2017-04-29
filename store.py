from collections import defaultdict
from datetime import datetime
from threading import Lock


class Store(object):
    def __init__(self):
        self.lock = Lock()
        self.log_lines = 0
        self.detail = defaultdict(dict)
        self.countries = defaultdict(int)
        self.ips = defaultdict(int)
        self.orgs = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.referrers = defaultdict(int)
        self.rpm = defaultdict(int)
        self.url_names = defaultdict(int)
        self.url_paths = defaultdict(int)
        self.user_agents = defaultdict(int)

        # Accumulators
        self.url_and_ips_by_status_code = []

    def accumulate_details_page(self):
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
        self.lock.acquire()
        if ip not in self.detail[url]:
            self.detail[url][ip] = defaultdict(int)
        self.detail[url][ip]["%sx" % status_code[:2]] += 1

        if self.log_lines % 1000 == 0:
            self.accumulate_details_page()
        self.lock.release()

    def add_country(self, country):
        self.countries[country] += 1

    def add_ip(self, ip):
        self.ips[ip] += 1

    def add_log_line(self):
        self.log_lines += 1

    def add_org(self, org):
        self.orgs[org] += 1

    def add_referrer(self, referrer):
        self.referrers[referrer] += 1

    def add_rmp(self, date):
        date = datetime.strptime(date, "%d/%b/%Y:%H:%M:%S +0000")
        date_string = "%s:%s" % (date.hour, date.minute)
        self.rpm[date_string] += 1

    def add_status_code(self, status_code):
        self.status_codes[status_code] += 1

    def add_url_name(self, url_name):
        self.url_names[url_name] += 1

    def add_url_path(self, url_path):
        self.url_paths[url_path] += 1

    def add_user_agent(self, user_agent):
        self.user_agents[user_agent] += 1
