#!/usr/bin/python3
import time
import os
import logging
import json

import requests

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('reporter')

admin_user = os.environ.get('ADMIN_USERNAME')
admin_password = os.environ.get('ADMIN_PASSWORD')

while 1:
  time.sleep(4)
  logger.debug('Cycling')

  s = requests.Session()

  entries = os.listdir('/reports')
  if len(entries) > 0:
    path = 'http://webserver:8000/admin'
    res = s.post(path, params={ 'key': 'XbcuJevW$9oOvMXdLgW9NohL1fxpj#qvp%LRrBt#4SK%qtOjPP%fTSVNDyplPejp' }, data={
      'username': admin_user,
      'password': admin_password,
    })

    for entry in entries:
      location = os.path.join('/reports', entry)
      logger.info("Making report for entry " + location)


      try:
        with open(location, 'r') as f:
          data = f.read()
          logger.info(data)
          report = json.loads(data)
          logger.info("This loaded")
          if 'session' in report and 'bad_apple' in report['session']:
            logger.info("Bad Apple!")
          else:
            path = 'http://' + report['url']
            logger.info('Hitting path ' + path)
            res = s.get(path)
            if res.status_code != 200:
              logger.info("Could not hit server from our side")
              logger.info(res.text)

            cookies = {}
            for k, v in dict(s.cookies).items():
              cookies[k] = {
                'value': v,
                'path': '/',
              }

            path = "http://xssbot:5000/visit"
            params = {
              'job': json.dumps({
                'url': "http://" + report['url'],
                'cookies': cookies,
              }),
            }

            res = requests.get(path, params=params)
            logger.info(res.text)
            if res.status_code != 200:
              logger.info('xssbot appears to be down')
      except Exception as e:
        logger.info("Could not load json " + location + " with error " + str(e))

    os.unlink(location)