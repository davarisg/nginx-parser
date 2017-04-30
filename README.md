# Nginx Parser

![NGINX Parser Preview](https://raw.githubusercontent.com/davarisg/nginx-parser/master/assets/nginx-monitor.gif?token=ABAAkmvJh8JAhuzW2Cituxgp0JRknuukks5ZD5tFwA%3D%3D)

## How to run

* Create a Python 3 virtualenv (`virtualenv -p python3 venv`) and load it (`source venv/bin/activate`)
* Install requirements (`pip install -r requirements.txt`)
* Run the script:
`python src/parser.py --file=/path/to/nginx/access.log -n 1000`

##### Available command line arguments

```
usage: parser.py [-h] [-f FILE] [-d DELAY] [-n N]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The path to the Nginx log file
  -d DELAY, --delay DELAY
                        Seconds to wait between updates
  -n N                  Number of lines to start tailing from
```

<!-- ## Configure for different Nginx log formats -->
