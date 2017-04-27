import argparse
import shlex
import subprocess
import sys

from blessed import Terminal
from copy import copy

from store import Store
from threading import Thread

# TODO: Make store generate presentational data every x lines

# TODO: Create constants for keys
# TODO: Move this to conf
DETAILS_PAGE = 'details'
MAIN_PAGE = 'general'
REFERRERS_PAGE = 'referrers'
USER_AGENT_PAGE = 'user_agent'

ACTIVE_PAGES = (
    DETAILS_PAGE,
    MAIN_PAGE,
    REFERRERS_PAGE,
    USER_AGENT_PAGE
)


parser = argparse.ArgumentParser()
parser.add_argument('--log-file', type=str, help='')
parser.add_argument('--delay', type=str, help='')
parser.add_argument('-n', type=str, help='')
args = parser.parse_args()


class Parseinator(object):
    def __init__(self, _args):
        self.active_page = DETAILS_PAGE
        self.args = _args
        self.store = Store()
        self.terminal = Terminal()

    def paint(self):
        max_y, max_x = self.terminal.height, self.terminal.width
        max_columns = max_y - 5

        print(self.terminal.clear())
        # print(self.terminal.move_y(self.terminal.height // 2) + self.terminal.center('press any key').rstrip())
        # print(self.terminal.move_y(self.terminal.height // 2) + "HI")
        # print(self.terminal.move_y(self.terminal.height // 2 + 1) + str(time.time()))

        print(
            self.terminal.move_y(0) +
            self.terminal.bold('Parseinator is tailing "%s"' % self.args.log_file)
        )
        print(
            self.terminal.move_y(1) +
            self.terminal.bold(
                'Processed %d lines / %d requests per minute' % (
                    self.store.log_lines,
                    sum(self.store.rpm.values()) / len(self.store.rpm) if self.store.rpm else 0
                )
            )
        )

        if self.active_page == USER_AGENT_PAGE:
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold("User agents:")
            )
            total = sum(self.store.status_codes.values())
            for index, (user_agent, count) in enumerate(sorted(self.store.user_agents.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                pct = count / float(total) * 100
                txt = "%s -> %.2f%%" % (user_agent, pct)
                if pct > 5:
                    txt = self.terminal.red("%s -> %.2f%%") % (user_agent, pct)
                print(self.terminal.move_y(4 + index) + self.terminal.move_x(2) + txt)
        elif self.active_page == REFERRERS_PAGE:
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold("Referrers:")
            )
            total = sum(self.store.status_codes.values())
            for index, (referrer, count) in enumerate(sorted(self.store.referrers.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                pct = count / float(total) * 100
                txt = "%s -> %.2f%%" % (referrer, pct)
                if pct > 5:
                    txt = self.terminal.red("%s -> %.2f%%") % (referrer, pct)
                print(self.terminal.move_y(4 + index) + self.terminal.move_x(2) + txt)
        elif self.active_page == DETAILS_PAGE:
            def spaces(n):
                return " " * n
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold(
                    'URL' + spaces(100) +
                    '|  IP' + spaces(40) +
                    '|  20x' + spaces(10) +
                    '|  30x' + spaces(10) +
                    '|  40x' + spaces(10) +
                    '|  50x' + spaces(10) +
                    '|'
                )
            )

            # Convert
            self.store.lock.acquire()
            detail = copy(self.store.detail)
            self.store.lock.release()
            url_ips = {}
            for url_path, ips in sorted(detail.items(), key=lambda k: sum([_c for c in k[1].values() for _c in c.values()]), reverse=True):
                for ip, status_codes in ips.items():
                    url_ips[(url_path, ip)] = status_codes
            for index, ((url_path, ip), status_codes) in enumerate(sorted(url_ips.items(), key=lambda k: sum([c for c in k[1].values()]), reverse=True)):
                if index + 1 == max_columns:
                    break
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(2) +
                    (url_path + spaces(103))[:103] + '| ' +
                    (ip + spaces(43))[:43] + '| ' +
                    (str(status_codes['20x']) + spaces(14))[:14] + '| ' +
                    (str(status_codes['30x']) + spaces(14))[:14] + '| ' +
                    (str(status_codes['40x']) + spaces(14))[:14] + '| ' +
                    (str(status_codes['50x']) + spaces(14))[:14] + '| '
                )
        else:
            # TODO: Check if screen size is big enough to show these
            print(self.terminal.move_y(3) + self.terminal.move_x(2) + self.terminal.bold("Status Codes:"))
            total = sum(self.store.status_codes.values())
            for index, (status_code, count) in enumerate(sorted(self.store.status_codes.items(), key=lambda k: k[1], reverse=True)):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(2) +
                    "%s -> %.2f%%" % (status_code, count / float(total) * 100)
                )

            print(self.terminal.move_y(3) + self.terminal.move_x(40) + self.terminal.bold("URL names:"))
            total = sum(self.store.url_names.values())
            for index, (url_name, count) in enumerate(sorted(self.store.url_names.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(23) +
                    "%30s -> %.2f%%" % (url_name[:30], count / float(total) * 100)
                )

            print(self.terminal.move_y(3) + self.terminal.move_x(77) + self.terminal.bold("IPs:"))
            total = sum(self.store.url_names.values())
            for index, (ip, count) in enumerate(sorted(self.store.ips.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(67) +
                    "%16s -> %.2f%%" % (ip, count / float(total) * 100)
                )

            print(self.terminal.move_y(3) + self.terminal.move_x(107) + self.terminal.bold("ORGs:"))
            total = sum(self.store.url_names.values())
            for index, (org, count) in enumerate(sorted(self.store.orgs.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(97) +
                    "%23s -> %.2f%%" % ("%s..." % org[:20] if len(org) > 20 else org, count / float(total) * 100)
                )

            print(self.terminal.move_y(3) + self.terminal.move_x(137) + self.terminal.bold("Countries:"))
            total = sum(self.store.url_names.values())
            for index, (country, count) in enumerate(sorted(self.store.countries.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(135) +
                    "%4s -> %.2f%%" % (country, count / float(total) * 100)
                )

        # TODO: Bold selected window
        print(self.terminal.move_y(max_y) + self.terminal.move_x(0) + "m: Main" + " | " + "r: Referrers" + " | " + "u: User Agents")

    def start(self):
        thread = Thread(target=self.parse)
        thread.setDaemon(True)
        thread.start()
        with self.terminal.fullscreen(), \
             self.terminal.hidden_cursor(), \
             self.terminal.keypad(), \
             self.terminal.cbreak():
            while True:
                self.paint()

                key = self.terminal.inkey(timeout=1)
                if key == 'u':
                    self.active_page = USER_AGENT_PAGE
                if key == 'r':
                    self.active_page = REFERRERS_PAGE
                if key == 'm':
                    self.active_page = MAIN_PAGE
                if key == 'd':
                    self.active_page = DETAILS_PAGE
                if key == 'q':
                    sys.exit()

    def parse(self):
        f = subprocess.Popen(
            ['tail', '-n', self.args.n, '-F', self.args.log_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        while True:
            line = f.stdout.readline()
            data = shlex.split(line.decode("utf-8"))

            self.store.add_country(data[4])
            self.store.add_ip(data[5])
            self.store.add_log_line()
            self.store.add_org(data[21])
            self.store.add_referrer(data[13])
            self.store.add_rmp(data[0])
            self.store.add_status_code(data[11])
            self.store.add_url_name(data[7])
            self.store.add_url_path(data[9])
            self.store.add_user_agent(data[14])

            self.store.add_detail(data[9], data[5], data[11])


if __name__ == '__main__':
    Parseinator(args).start()
