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
"$time_local" $upstream_http_x_mixcloud_request_uuid $upstream_http_x_mixcloud_session $request_time $upstream_http_x_mixcloud_country_code $remote_addr $upstream_http_x_mixcloud_user $upstream_http_x_mixcloud_view_name $request_method "$request_uri" $server_protocol $status $body_bytes_sent "$http_referer" "$http_user_agent" "$upstream_addr" "$upstream_response_time" "$upstream_status" "$upstream_http_x_speedbar_sql_count" "$scheme" "$http2" "$geoip_org"
"""

NGINX_LOG_FORMAT_DEFAULT_VARIABLES = {
    'remote_addr': 'IP',
    'http_referer': 'Referrer',
    'status': 'Status Code',
    'request_uri': 'Request',
    'http_user_agent': 'HTTP User Agent',
    'time_local': 'Time'
}

NGINX_LOG_FORMAT_EXTRA_VARIABLES = {
    'upstream_http_x_mixcloud_country_code': {'title': 'Countries', 'width': 20},
    'geoip_org': {'title': 'ORGs', 'width': 50},
    'upstream_http_x_mixcloud_view_name': {'title': 'URL Names', 'width': 50}
}

NGINX_LOG_FORMAT_VARIABLE_INDICES = {}

variable_re = re.compile('\$([\w\d]+)')
for index, variable in enumerate(shlex.split(NGINX_LOG_FORMAT.strip())):
    cleaned_variable = variable
    try:
        cleaned_variable = variable_re.search(variable).groups()[0]
    except AttributeError:
        pass
    if cleaned_variable in NGINX_LOG_FORMAT_DEFAULT_VARIABLES.keys() or \
       cleaned_variable in NGINX_LOG_FORMAT_EXTRA_VARIABLES.keys():
        NGINX_LOG_FORMAT_VARIABLE_INDICES[cleaned_variable] = index
