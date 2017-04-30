import conf
from conf import DETAILS_PAGE_NAME, USER_AGENT_PAGE_NAME, REFERRERS_PAGE_NAME, PAGES


class Picasso(object):
    def __init__(self, args, lock, store, terminal):
        self.active_page = DETAILS_PAGE_NAME
        self.args = args
        self.lock = lock
        self.store = store
        self.terminal = terminal

    @staticmethod
    def spaces(n):
        return " " * n

    def paint(self):
        max_y, max_x = self.terminal.height, self.terminal.width
        max_columns = max_y - 5

        self.lock.acquire()
        print(self.terminal.clear())
        print(
            self.terminal.move_y(0) +
            self.terminal.bold('Nginx viewer is tailing "%s"\n' % self.args.file) +
            self.terminal.bold(
                'Processed %d lines / %d requests per minute' % (
                    self.store.log_lines,
                    sum(self.store.rpm.values()) / len(self.store.rpm) if self.store.rpm else 0
                )
            )
        )

        if self.active_page == USER_AGENT_PAGE_NAME:
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold("User agents:")
            )
            total = sum(self.store.status_codes.values())
            for index, (user_agent, count) in enumerate(sorted(self.store.user_agents.items(), key=lambda k: k[1], reverse=True)[:max_columns - 2]):
                pct = count / float(total) * 100
                txt = "%s -> %.2f%%" % (user_agent, pct)
                if pct > 5:
                    txt = self.terminal.red("%s -> %.2f%%") % (user_agent, pct)
                print(self.terminal.move_y(4 + index) + self.terminal.move_x(2) + txt)
        elif self.active_page == REFERRERS_PAGE_NAME:
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold("Referrers:")
            )
            total = sum(self.store.status_codes.values())
            for index, (referrer, count) in enumerate(sorted(self.store.referrers.items(), key=lambda k: k[1], reverse=True)[:max_columns - 2]):
                pct = count / float(total) * 100
                txt = "%s -> %.2f%%" % (referrer, pct)
                if pct > 5:
                    txt = self.terminal.red("%s -> %.2f%%") % (referrer, pct)
                print(self.terminal.move_y(4 + index) + self.terminal.move_x(2) + txt)
        elif self.active_page == DETAILS_PAGE_NAME:
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold(
                    'URL' + self.spaces(100) +
                    '|  IP' + self.spaces(40) +
                    '|  20x' + self.spaces(10) +
                    '|  30x' + self.spaces(10) +
                    '|  40x' + self.spaces(10) +
                    '|  50x' + self.spaces(10) +
                    '|'
                )
            )

            for index, ((url_path, ip), status_codes) in enumerate(self.store.url_and_ips_by_status_code[:max_columns - 2]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(2) +
                    (url_path + self.spaces(103))[:103] + '| ' +
                    (ip + self.spaces(43))[:43] + '| ' +
                    (str(status_codes['20x']) + self.spaces(14))[:14] + '| ' +
                    (str(status_codes['30x']) + self.spaces(14))[:14] + '| ' +
                    (str(status_codes['40x']) + self.spaces(14))[:14] + '| ' +
                    (str(status_codes['50x']) + self.spaces(14))[:14] + '| '
                )
        else:
            print(self.terminal.move_y(3) + self.terminal.move_x(2) + self.terminal.bold("Status Codes:"))
            total = sum(self.store.status_codes.values())
            for index, (status_code, count) in enumerate(sorted(self.store.status_codes.items(), key=lambda k: k[1], reverse=True)):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(2) +
                    "%s -> %.2f%%" % (status_code, count / float(total) * 100)
                )

            print(self.terminal.move_y(3) + self.terminal.move_x(20) + self.terminal.bold("IPs:"))
            total = sum(self.store.ips.values())
            for index, (ip, count) in enumerate(sorted(self.store.ips.items(), key=lambda k: k[1], reverse=True)[:max_columns - 2]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(20) +
                    "%16s -> %.2f%%" % (ip, count / float(total) * 100)
                )

            current_x = 70
            for variable in sorted(conf.NGINX_LOG_FORMAT_EXTRA_VARIABLES):
                detail = conf.NGINX_LOG_FORMAT_EXTRA_VARIABLES[variable]
                if variable not in self.store.extra:
                    continue
                print(self.terminal.move_y(3) + self.terminal.move_x(current_x + (detail['width'] // 2) - 10) + self.terminal.bold("%s:" % detail['title']))
                total = sum(self.store.extra[variable].values())
                for index, (value, count) in enumerate(
                        sorted(self.store.extra[variable].items(), key=lambda k: k[1], reverse=True)[:max_columns - 2]):
                    print(
                        self.terminal.move_y(4 + index) +
                        self.terminal.move_x(current_x) +
                        "%s -> %.2f%%" % (value, count / float(total) * 100)
                    )

                current_x += detail['width']


        # Render footer
        text = ''
        for page_key in sorted(PAGES):
            title = '%s: %s' % (page_key, PAGES[page_key])
            if self.active_page == PAGES[page_key]:
                text += self.terminal.bold(title)
            else:
                text += title
            text += ' | '
        print(self.terminal.move_y(max_y - 2) + self.terminal.move_x(0) + text + 'q: Quit')

        # Release the lock
        self.lock.release()

    def set_active_page(self, page):
        self.active_page = page
