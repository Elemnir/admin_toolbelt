import datetime
import re

import requests


PATTERNS = {
    'ssh': ( 
          r'(?P<when>\w{3}\s+\d+ \d{2}:\d{2}:\d{2}) (?P<host>\S+) '
        + r'(?P<service>\S+)\[\d+\]: Accepted (?P<method>.+) for (?P<user>.+) ' 
        + r'from (?P<from>.+) port \d+ (?P<rem>.*)$'
    ),
}


def send_record(url, token, when, host, service, user, fromhost, method=None):
    payload = {
        'token': token, 'when': when, 'host': host, 
        'service': service, 'user': user, 'fromhost': fromhost,
    }
    if method != None: payload['method'] = method
    resp = requests.post(url, data=payload)
    resp.raise_for_status()
    if resp.status_code != 200:
        raise RuntimeError('Server responded: {}'.format(r.status_code))


def scan_file(path, patterns=['ssh']):
    with open(path) as f:
        for line in f:
            for label in patterns:
                m = re.search(PATTERNS[label], line.rstrip())
                if m: 
                    yield m


def scan_and_report(path, url, token, year=None, patterns=['ssh']):
    if year == None:
        year = datetime.date.today().year
    
    for m in scan_file(path, patterns):
        send_record(
            url,
            token,
            datetime.datetime.strptime(
                "{} {}".format(year, m.group('when')), '%Y %b %d %H:%M:%S'
            ),
            m.group('host'),
            m.group('service'),
            m.group('user'),
            m.group('from'),
            m.group('method'),
        )
