import conf


# TODO: Better visualizations/graph
# TODO: Colors for important values
# TODO: Elipsis

class Picasso(object):
    def __init__(self, args, lock, store, terminal):
        self.active_page = conf.DETAILS_PAGE_NAME
        self.args = args
        self.max_columns = 0
        self.lock = lock
        self.store = store
        self.terminal = terminal

    @staticmethod
    def spaces(n):
        return " " * n

    def paint(self):
        max_y, max_x = self.terminal.height, self.terminal.width
        self.max_columns = max_y - 5

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

        if self.active_page == conf.USER_AGENT_PAGE_NAME:
            self.paint_page('User agents', self.store.user_agents)
        elif self.active_page == conf.URL_PAGE_NAME:
            self.paint_page('URLs', self.store.url_paths)
        elif self.active_page == conf.REFERRERS_PAGE_NAME:
            self.paint_page('Referrers', self.store.referrers)
        elif self.active_page == conf.DETAILS_PAGE_NAME:
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

            for index, ((url_path, ip), status_codes) in enumerate(self.store.url_and_ips_by_status_code[:self.max_columns - 2]):
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
            self.paint_main_page_section('Status Codes', self.store.status_codes, 20, 0)
            self.paint_main_page_section('IP', self.store.ips, 50, 20)

            current_x = 70
            for variable in sorted(conf.NGINX_LOG_FORMAT_EXTRA_VARIABLES):
                detail = conf.NGINX_LOG_FORMAT_EXTRA_VARIABLES[variable]
                if variable not in self.store.extra:
                    continue
                self.paint_main_page_section(detail['title'], self.store.extra[variable], detail['width'], current_x)
                current_x += detail['width']

        # Render footer
        self.paint_footer(max_y)

        # Release the lock
        self.lock.release()

    def paint_main_page_section(self, title, store_data, width, current_x):
        print(
            self.terminal.move_y(3) +
            self.terminal.move_x(current_x + (width // 2) - 10) +
            self.terminal.bold("%s:" % title)
        )
        total = sum(store_data.values())
        for index, (value, count) in enumerate(sorted(store_data.items(), key=lambda k: k[1], reverse=True)[:self.max_columns - 2]):
            print(
                self.terminal.move_y(4 + index) +
                self.terminal.move_x(current_x) +
                "%s -> %.2f%%" % (value, count / float(total) * 100)
            )

    def paint_footer(self, max_y):
        text = ''
        for page_key in sorted(conf.PAGES):
            title = '%s: %s' % (page_key, conf.PAGES[page_key])
            if self.active_page == conf.PAGES[page_key]:
                text += self.terminal.bold(title)
            else:
                text += title
            text += ' | '
        print(self.terminal.move_y(max_y - 2) + self.terminal.move_x(0) + text + 'q: Quit')

    def paint_page(self, title, data):
        print(
            self.terminal.move_y(3) +
            self.terminal.move_x(2) +
            self.terminal.bold("%s:" % title)
        )
        total = sum(data.values())
        for index, (key, count) in enumerate(
                sorted(data.items(), key=lambda k: k[1], reverse=True)[:self.max_columns - 2]):
            pct = count / float(total) * 100
            txt = "%s -> %.2f%%" % (key, pct)
            if pct > 5:
                txt = self.terminal.red("%s -> %.2f%%") % (key, pct)
            print(self.terminal.move_y(4 + index) + self.terminal.move_x(2) + txt)

    def set_active_page(self, page):
        self.active_page = page
