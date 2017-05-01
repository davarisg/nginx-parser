from .conf import PAGES, USER_AGENT_PAGE_NAME, URL_PAGE_NAME, REFERRERS_PAGE_NAME, DETAILS_PAGE_NAME


# TODO: Better visualizations/graph
HIGH_THRESHOLD = 7
MEDIUM_THRESHOLD = 5
LOW_THRESHOLD = 3


class Picasso(object):
    def __init__(self, filename, lock, store, terminal, extra_variables):
        self.active_page = DETAILS_PAGE_NAME
        self.extra_variables = extra_variables
        self.filename = filename
        self.max_rows = 0
        self.lock = lock
        self.store = store
        self.terminal = terminal

    @staticmethod
    def append_spaces(string, spaces):
        """
        Helper function to append spaces to the end of a string.
        :param string: The string to append spaces to.
        :param spaces: The number of spaces to append.
        """
        return ("%s%s" % (string, " " * spaces))[:spaces]

    @staticmethod
    def ellipsis(string, n):
        if len(string) > n - 15:
            return "%s..." % string[:n-15]
        return string

    def set_active_page(self, page):
        self.active_page = page

    def paint(self):
        """
        Paints the appropriate page to the terminal
        """
        max_y, max_x = self.terminal.height, self.terminal.width
        self.max_rows = max_y - 5

        # Grab the lock before we paint as we don't want the store to update while painting.
        self.lock.acquire()

        # Render header
        print(self.terminal.clear())
        print(
            self.terminal.move_y(0) +
            self.terminal.bold('Nginx viewer is tailing "%s"\n' % self.filename) +
            self.terminal.bold(
                'Processed %d lines / %d requests per minute' % (
                    self.store.log_lines,
                    sum(self.store.rpm.values()) / len(self.store.rpm) if self.store.rpm else 0
                )
            )
        )

        if self.active_page == USER_AGENT_PAGE_NAME:  # User Agent page
            self._paint_page('User agents', self.store.user_agents, max_x)
        elif self.active_page == URL_PAGE_NAME:  # URL page
            self._paint_page('URLs', self.store.url_paths, max_x)
        elif self.active_page == REFERRERS_PAGE_NAME:  # Referrers page
            self._paint_page('Referrers', self.store.referrers, max_x)
        elif self.active_page == DETAILS_PAGE_NAME:  # Details page
            # Render column titles
            print(
                self.terminal.move_y(3) +
                self.terminal.move_x(2) +
                self.terminal.bold(
                    self.append_spaces('URL', 103) + '| ' +
                    self.append_spaces('IP', 40) + '| ' +
                    self.append_spaces('20x', 10) + '| ' +
                    self.append_spaces('30x', 10) + '| ' +
                    self.append_spaces('40x', 10) + '| ' +
                    self.append_spaces('50x', 10) + '|'
                )
            )

            # Render columns
            for index, ((url_path, ip), status_codes) in enumerate(self.store.url_and_ips_by_status_code[:self.max_rows - 2]):
                print(
                    self.terminal.move_y(4 + index) +
                    self.terminal.move_x(2) +
                    self.append_spaces(url_path, 103) + '| ' +
                    self.append_spaces(ip, 40) + '| ' +
                    self.append_spaces(str(status_codes['20x']), 10) + '| ' +
                    self.append_spaces(str(status_codes['30x']), 10) + '| ' +
                    self.append_spaces(str(status_codes['40x']), 10) + '| ' +
                    self.append_spaces(str(status_codes['50x']), 10) + '| '
                )
        else:  # Main Page
            self._paint_main_page_section('Status Codes', self.store.status_codes, 20, 0)
            self._paint_main_page_section('IP', self.store.ips, 50, 20)

            current_x = 70
            for variable in sorted(self.extra_variables):
                detail = self.extra_variables[variable]
                if variable not in self.store.extra:
                    continue
                self._paint_main_page_section(detail['title'], self.store.extra[variable], detail['width'], current_x)
                current_x += detail['width']

        # Render footer
        self._paint_footer(max_y)

        # Release the lock
        self.lock.release()

    def _paint_column(self, store_data, current_x, width):
        """
        Paints a column of data on the terminal window.
        """
        total = sum(store_data.values())
        for index, (value, count) in enumerate(sorted(store_data.items(), key=lambda k: k[1], reverse=True)[:self.max_rows - 2]):
            pct = count / float(total) * 100
            txt = "%s -> %.2f%%" % (self.ellipsis(value, width), pct)
            if pct > HIGH_THRESHOLD:
                txt = self.terminal.bright_red(txt)
            elif pct > MEDIUM_THRESHOLD:
                txt = self.terminal.magenta(txt)
            elif pct > LOW_THRESHOLD:
                txt = self.terminal.cyan(txt)
            print(self.terminal.move_y(4 + index) + self.terminal.move_x(current_x) + txt)

    def _paint_main_page_section(self, title, store_data, width, current_x):
        """
        Renders a section of the main page.
        :param title: The title of the section
        :param store_data: The data for the section
        :param width: The width of the section
        :param current_x: The current horizontal position
        """
        print(
            self.terminal.move_y(3) +
            self.terminal.move_x(current_x + (width // 2) - 10) +
            self.terminal.bold("%s:" % title)
        )
        self._paint_column(store_data, current_x, width)

    def _paint_page(self, title, store_data, max_x):
        print(self.terminal.move_y(3) + self.terminal.move_x(2) + self.terminal.bold("%s:" % title))
        self._paint_column(store_data, 2, max_x)

    def _paint_footer(self, max_y):
        """
        Renders the footer of the application
        :param max_y: The maximum height of the terminal window
        """
        text = ''
        for page_key in sorted(PAGES):
            title = '%s: %s' % (page_key, PAGES[page_key])
            if self.active_page == PAGES[page_key]:
                text += self.terminal.bold(title)
            else:
                text += title
            text += ' | '
        print(self.terminal.move_y(max_y - 2) + self.terminal.move_x(0) + text + 'q: Quit')
