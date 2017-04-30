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


NGINX_LOG_FORMAT = """
    $remote_addr - $remote_user [$time_local] "$request" $status $bytes_sent "$http_referer" "$http_user_agent" "$gzip_ratio"
"""

NGINX_LOG_DEFAULT_VARIABLES = {
    'remote_addr': 'IP',
    'http_referer': 'Referrer',
    'status': 'Status Code',
    'http_user_agent': 'HTTP User Agent',
    'time_local': 'Time'
}

NGINX_LOG_REQUEST_VARIABLE = 'request'
NGINX_LOG_TIME_LOCAL_FORMAT = '%d/%b/%Y:%H:%M:%S +0000'

NGINX_LOG_EXTRA_VARIABLES = {}

NGINX_LOG_FORMAT_VARIABLE_INDICES = {}

variable_re = re.compile('\$([\w\d]+)')
for index, variable in enumerate(shlex.split(NGINX_LOG_FORMAT.strip())):
    cleaned_variable = variable
    try:
        cleaned_variable = variable_re.search(variable).groups()[0]
    except AttributeError:
        pass
    if cleaned_variable in NGINX_LOG_DEFAULT_VARIABLES.keys() or \
       cleaned_variable in NGINX_LOG_EXTRA_VARIABLES.keys() or \
       cleaned_variable == NGINX_LOG_REQUEST_VARIABLE:
        NGINX_LOG_FORMAT_VARIABLE_INDICES[cleaned_variable] = index
