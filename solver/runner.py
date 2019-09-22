from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging
from urllib.parse import urlencode

from solve import main, post_admin_cookie

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.logger = logging.getLogger("solverrunner")
app.logger.setLevel(logging.DEBUG)

@app.route('/')
def index():
  admin_cookie = request.args.get('cookie')
  app.logger.info(admin_cookie)
  post_admin_cookie(admin_cookie)
  return "Hello there"


def run_solver():
  print("Starting solver")
  main()


if __name__ == '__main__':
  sched = BackgroundScheduler(daemon=True)
  sched.add_job(run_solver,'interval', minutes=2)
  sched.start()
  atexit.register(lambda: sched.shutdown(wait=False))

  run_solver()
  app.run('0.0.0.0', port=8000)
