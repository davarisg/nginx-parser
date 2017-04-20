import argparse
import curses
import shlex
import subprocess
import time

from threading import Thread

import sys

from blessed import Terminal

from store import Store

parser = argparse.ArgumentParser()
parser.add_argument('--log-file', type=str, help='')
parser.add_argument('--delay', type=str, help='')
parser.add_argument('-n', type=str, help='')
args = parser.parse_args()


class Parseinator(object):
    def __init__(self, _args):
        self.args = _args
        self.store = Store()
        self.terminal = Terminal()

        self.show_detail = False
        self.show_referrers = False
        self.show_user_agent = False

    def paint(self):
        curses.start_color()
        # curses.init_color(0, 0, 0, 0)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        self.window.nodelay(1)
        self.window.clear()
        # self.window.keypad(True)

        max_y, max_x = self.window.getmaxyx()
        max_columns = max_y - 5
        self.window.addstr(0, 0, 'Parseinator is tailing "%s"' % self.args.log_file, curses.A_BOLD)
        self.window.addstr(
            1, 0,
            'Processed %d lines / %d requests per minute' % (
                self.store.log_lines,
                sum(self.store.rpm.values()) / len(self.store.rpm) if self.store.rpm else 0
            ),
            curses.A_BOLD
        )

        if self.show_user_agent:
            self.window.addstr(3, 2, "User agents:", curses.A_BOLD)
            total = sum(self.store.status_codes.values())
            for index, (user_agent, count) in enumerate(sorted(self.store.user_agents.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
                self.window.addstr(4 + index, 2, "%s -> %.2f%%" % (user_agent, count / float(total) * 100))
        # elif self.show_referrers:
        #     self.window.addstr(3, 2, "Referrers:", curses.A_BOLD)
        #     total = sum(self.store.status_codes.values())
        #     for index, (referrer, count) in enumerate(sorted(self.store.referrers.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
        #         self.window.addstr(4 + index, 2, "%s -> %.2f%%" % (referrer, count / float(total) * 100))
        # elif self.show_detail:
        #     self.window.addstr(3, 2, "URL", curses.A_BOLD)
        #     self.window.addstr(3, 103, "|", curses.A_BOLD)
        #     self.window.addstr(3, 105, "IP", curses.A_BOLD)
        #     self.window.addstr(3, 146, "|", curses.A_BOLD)
        #     self.window.addstr(3, 148, "20x", curses.A_BOLD)
        #     self.window.addstr(3, 159, "|", curses.A_BOLD)
        #     self.window.addstr(3, 161, "30x", curses.A_BOLD)
        #     self.window.addstr(3, 172, "|", curses.A_BOLD)
        #     self.window.addstr(3, 174, "40x", curses.A_BOLD)
        #     self.window.addstr(3, 185, "|", curses.A_BOLD)
        #     self.window.addstr(3, 187, "50x", curses.A_BOLD)
        #     self.window.addstr(3, 198, "|", curses.A_BOLD)
        #
        #     # Convert
        #     url_ips = {}
        #     for url_path, ips in sorted(self.store.detail.items(), key=lambda k: sum([_c for c in k[1].values() for _c in c.values()]), reverse=True):
        #         for ip, status_codes in ips.items():
        #             url_ips[(url_path, ip)] = status_codes
        #
        #     for index, ((url_path, ip), status_codes) in enumerate(sorted(url_ips.items(), key=lambda k: sum([c for c in k[1].values()]), reverse=True)):
        #         if index + 1 == max_columns:
        #             break
        #         self.window.addstr(4 + index, 2, url_path[:100])
        #         self.window.addstr(4 + index, 103, '|')
        #         self.window.addstr(4 + index, 105, (ip + " " * 40)[:40])
        #         self.window.addstr(4 + index, 146, '|')
        #         self.window.addstr(4 + index, 148, (str(status_codes['20x']) + " " * 10)[:10])
        #         self.window.addstr(4 + index, 159, '|')
        #         self.window.addstr(4 + index, 161, (str(status_codes['30x']) + " " * 10)[:10])
        #         self.window.addstr(4 + index, 172, '|')
        #         self.window.addstr(4 + index, 174, (str(status_codes['40x']) + " " * 10)[:10])
        #         self.window.addstr(4 + index, 185, '|')
        #         self.window.addstr(4 + index, 187, (str(status_codes['50x']) + " " * 10)[:10])
        #         self.window.addstr(4 + index, 198, '|')
        # else:
        #     # TODO: Check if screen size is big enough to show these
        #     self.window.addstr(3, 2, "Status Codes:", curses.A_BOLD)
        #     total = sum(self.store.status_codes.values())
        #     for index, (status_code, count) in enumerate(sorted(self.store.status_codes.items(), key=lambda k: k[1], reverse=True)):
        #         self.window.addstr(4 + index, 2, "%s -> %.2f%%" % (status_code, count / float(total) * 100))
        #
        #     self.window.addstr(3, 40, "URL names:", curses.A_BOLD)
        #     total = sum(self.store.url_names.values())
        #     for index, (url_name, count) in enumerate(sorted(self.store.url_names.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
        #         self.window.addstr(4 + index, 23, "%30s -> %.2f%%" % (url_name[:30], count / float(total) * 100))
        #
        #     self.window.addstr(3, 77, "IPs:", curses.A_BOLD)
        #     total = sum(self.store.url_names.values())
        #     for index, (ip, count) in enumerate(sorted(self.store.ips.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
        #         self.window.addstr(4 + index, 67, "%16s -> %.2f%%" % (ip, count / float(total) * 100))
        #
        #     self.window.addstr(3, 107, "ORGs:", curses.A_BOLD)
        #     total = sum(self.store.url_names.values())
        #     for index, (org, count) in enumerate(sorted(self.store.orgs.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
        #         self.window.addstr(4 + index, 97, "%23s -> %.2f%%" % ("%s..." % org[:20] if len(org) > 20 else org, count / float(total) * 100))
        #
        #     self.window.addstr(3, 137, "Countries:", curses.A_BOLD)
        #     total = sum(self.store.url_names.values())
        #     for index, (country, count) in enumerate(sorted(self.store.countries.items(), key=lambda k: k[1], reverse=True)[:max_columns]):
        #         self.window.addstr(4 + index, 135, "%4s -> %.2f%%" % (country, count / float(total) * 100))
        #
        # self.window.addstr(max_y - 1, 0, "m: Main", curses.A_STANDOUT if not self.show_referrers and not self.show_user_agent else curses.A_BOLD)
        # self.window.addstr(max_y - 1, 7, " | ")
        # self.window.addstr(max_y - 1, 10, "r: Referrers", curses.A_STANDOUT if self.show_referrers else curses.A_BOLD)
        # self.window.addstr(max_y - 1, 22, " | ")
        # self.window.addstr(max_y - 1, 25, "u: User Agents", curses.A_STANDOUT if self.show_user_agent else curses.A_BOLD)
        # self.window.refresh()

    def start(self):
        thread = Thread(target=self.parse)
        thread.setDaemon(True)
        thread.start()
        with self.terminal.fullscreen(),\
             self.terminal.hidden_cursor(),\
             self.terminal.cbreak(),\
             self.terminal.keypad():
            while True:
                print(self.terminal.clear())
                print(self.terminal.move_y(self.terminal.height // 2) + self.terminal.center('press any key').rstrip())
                print(self.terminal.move_y(self.terminal.height // 2) + "HI")

            # self.paint()
                print(self.terminal.move_y(self.terminal.height // 2 + 1) + "asdfghj")
                _getch = self.terminal.inkey(timeout=1)
                # _getch = self.terminal.getch()
                if _getch == ord('u'):
                    self.show_user_agent = True
                    self.show_referrers = False
                    self.show_detail = False
                if _getch == ord('r'):
                    self.show_referrers = True
                    self.show_user_agent = False
                    self.show_detail = False
                if _getch == ord('m'):
                    self.show_referrers = False
                    self.show_user_agent = False
                    self.show_detail = False
                if _getch == ord('d'):
                    self.show_detail = True
                    self.show_referrers = False
                    self.show_user_agent = False
                if _getch == ord('q'):
                    sys.exit()
                # time.sleep(1)

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
