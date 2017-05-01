import sys
import yaml
import re
import shlex


# Keyboard Shortcut names
DETAILS_PAGE_NAME = 'Details'
MAIN_PAGE_NAME = 'General'
REFERRERS_PAGE_NAME = 'Referrers'
URL_PAGE_NAME = 'URLs'
USER_AGENT_PAGE_NAME = 'User Agent'
QUIT_NAME = 'Quit'

# Keyboard Shortcuts
DETAILS_PAGE_KEY = 'd'
MAIN_PAGE_KEY = 'm'
REFERRERS_PAGE_KEY = 'r'
USER_AGENT_PAGE_KEY = 'u'
URL_PAGE_KEY = 'l'
QUIT_KEY = 'q'

# Available keyboard actions
PAGES = {
    DETAILS_PAGE_KEY: DETAILS_PAGE_NAME,
    MAIN_PAGE_KEY: MAIN_PAGE_NAME,
    REFERRERS_PAGE_KEY: REFERRERS_PAGE_NAME,
    URL_PAGE_KEY: URL_PAGE_NAME,
    USER_AGENT_PAGE_KEY: USER_AGENT_PAGE_NAME,
}


class NginxConfig(object):
    DEFAULT_VARIABLES = {
        'remote_addr': 'IP',
        'http_referer': 'Referrer',
        'status': 'Status Code',
        'http_user_agent': 'HTTP User Agent',
        'time_local': 'Time'
    }
    LOG_FORMAT = '$remote_addr - $remote_user [$time_local] "$request" $status $bytes_sent "$http_referer" "$http_user_agent" "$gzip_ratio"'
    TIME_LOCAL_FORMAT = '%d/%b/%Y:%H:%M:%S +0000'

    REQUEST_RE = re.compile(r'[\s"\[{]\$request[\s"\]}]')
    REQUEST_URI_RE = re.compile(r'\$request_uri')

    def __init__(self, yaml_file):
        self.extra_variables = None
        self.log_format = None
        self.request_variable_name = None
        self.variable_indices = {}
        try:
            with open(yaml_file, 'r') as config_file:
                try:
                    self.yaml_config = yaml.load(config_file)
                except yaml.YAMLError as exc:
                    print(exc)
                    sys.exit(1)
        except TypeError:
            self.yaml_config = None

    def get_time_local_format(self):
        return self.TIME_LOCAL_FORMAT

    def get_default_variables(self):
        return self.DEFAULT_VARIABLES

    def get_log_format(self):
        if self.log_format is not None:
            return self.log_format
        try:
            self.log_format = self.yaml_config['nginx']['log_format']
        except (KeyError, TypeError):
            self.log_format = self.LOG_FORMAT
        return self.log_format

    def get_extra_variables(self):
        if self.extra_variables is not None:
            return self.extra_variables
        try:
            self.extra_variables = self.yaml_config['nginx']['extra_variables']
        except (KeyError, TypeError):
            self.extra_variables = {}
        return self.get_extra_variables()

    def get_request_variable_name(self):
        if self.request_variable_name is not None:
            return self.request_variable_name
        log_format = self.get_log_format()
        if self.REQUEST_RE.search(log_format):
            self.request_variable_name = 'request'
            return self.request_variable_name
        elif self.REQUEST_URI_RE.search(log_format):
            self.request_variable_name = 'request_uri'
            return self.request_variable_name
        else:
            raise Exception("Could not find $request or $request_uri in Nginx log format")

    def get_variable_indices(self):
        if self.variable_indices:
            return self.variable_indices
        variable_re = re.compile('\$([\w\d]+)')
        for index, variable in enumerate(shlex.split(self.get_log_format().strip())):
            cleaned_variable = variable
            try:
                cleaned_variable = variable_re.search(variable).groups()[0]
            except AttributeError:
                pass
            if cleaned_variable in self.get_default_variables().keys() or \
               cleaned_variable in self.get_extra_variables().keys() or \
               cleaned_variable == self.get_request_variable_name():
                self.variable_indices[cleaned_variable] = index
        return self.variable_indices

    def get_index_for_variable(self, variable):
        return self.get_variable_indices()[variable]
