# Nginx Parser

![NGINX Parser Preview](https://raw.githubusercontent.com/davarisg/nginx-parser/master/assets/nginx-monitor.gif?token=ABAAkmvJh8JAhuzW2Cituxgp0JRknuukks5ZD5tFwA%3D%3D)

## How to use

* Install the nginx-monitor package from pip `pip install nginx-monitor`.
* Run it `nginx-parser --file=/path/to/nginx/access.log -n 1000`

##### Available command line arguments

```
usage: nginx-parser [-h] [-f FILE] [-d DELAY] [-n N] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The path to the Nginx log file
  -d DELAY, --delay DELAY
                        Seconds to wait between updates
  -n N                  Number of lines to start tailing from
  -c CONFIG, --config CONFIG
                        The path to your configuration file
```

## Configure for different Nginx log formats

`nginx-parser` works for different Nginx log formats. You can also configure the parser to pull extra variables from your Nginx access log.

Example:

```bash
$ cat config.yaml

nginx:
  log_format: '$remote_addr - $remote_user "$time_local" "$request" $status $bytes_sent "$http_referer" "$http_user_agent" "$gzip_ratio" $geo_ip $variable_you_want_to_track'
  extra_variables:
    geoip_org:
      title: ORGs
      width: 50
    variable_you_want_to_track:
      title: My other variable
      width: 55
```

Then just use your config:
`nginx-parser --file=/path/to/nginx/access.log -n 1000 --config=config.yaml`

## TODO

* Ability to filter by status_code/IP address/URL
* Better visualizations
