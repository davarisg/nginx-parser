import argparse
import subprocess
import sys

from .conf import PAGES, QUIT_KEY, NginxConfig
from .picasso import Picasso
from .store import Store

from blessed import Terminal
from threading import Thread, Lock


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True, help='The path to the Nginx log file')
parser.add_argument('-d', '--delay', type=int, default=1, help='Seconds to wait between updates')
parser.add_argument('-n', type=str, default='1000', help='Number of lines to start tailing from')
parser.add_argument('-c', '--config', type=str, help='The path to your YAML configuration file')
args = parser.parse_args()


class Parser(object):
    def __init__(self):
        nginx_config = NginxConfig(args.config)
        self.lock = Lock()
        self.store = Store(nginx_config)
        self.terminal = Terminal()
        self.picasso = Picasso(
            args.file,
            self.lock,
            self.store,
            self.terminal,
            nginx_config.get_extra_variables()
        )

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

                key = self.terminal.inkey(timeout=args.delay)
                if key in PAGES.keys():
                    self.picasso.set_active_page(PAGES[key])
                if key == QUIT_KEY:
                    sys.exit()

    def tail(self):
        f = subprocess.Popen(
            ['tail', '-n', args.n, '-F', args.file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        while True:
            line = f.stdout.readline()
            # Grab the lock before we update our store as we don't want the data to change as we are painting.
            self.lock.acquire()
            self.store.aggregate(line)
            self.lock.release()


def main():
    Parser().start()


if __name__ == '__main__':
    main()
