import argparse
import shlex
import subprocess
import sys

from blessed import Terminal

from conf import PAGES, QUIT_KEY
from picasso import Picasso
from store import Store
from threading import Thread, Lock


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, help='The path to the Nginx log file')
parser.add_argument('-d', '--delay', type=int, default=1, help='Seconds to wait between updates')
parser.add_argument('-n', type=str, default='1000', help='Number of lines to start tailing from')
args = parser.parse_args()


class Viewer(object):
    def __init__(self, _args):
        self.args = _args
        self.lock = Lock()
        self.store = Store()
        self.terminal = Terminal()
        self.picasso = Picasso(_args, self.lock, self.store, self.terminal)

    def start(self):
        thread = Thread(target=self.tail)
        thread.setDaemon(True)
        thread.start()
        with self.terminal.fullscreen(), \
             self.terminal.hidden_cursor(), \
             self.terminal.keypad(), \
             self.terminal.cbreak():
            while True:
                self.picasso.paint()

                key = self.terminal.inkey(timeout=self.args.delay)
                if key in PAGES.keys():
                    self.picasso.set_active_page(PAGES[key])
                if key == QUIT_KEY:
                    sys.exit()

    def tail(self):
        f = subprocess.Popen(
            ['tail', '-n', self.args.n, '-F', self.args.file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        while True:
            line = f.stdout.readline()
            data = shlex.split(line.decode("utf-8"))

            self.lock.acquire()
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
            self.lock.release()


if __name__ == '__main__':
    Viewer(args).start()
