Flag is configured in docker-compose.yml (or docker-compose.override.yml)

Defined during build time.


This challenge is a chain of multiple challenges


Savvy web folks will notice the X-Powered-By header on the front page. (It's express!)

Some might guess to look at /package.json (but why would they? that doesn't make sense?) So I left a hint in /robots.txt

once they look at /package.json, they will discover that it is, in fact, globally readable. Other information here is that I am using express-session-file-store so thats fun.

Then they look at /index.js (which gives them source for this server.)

The next step is to grab /admin.js (which is also readable), which gives them the key to hit /admin (which should give them a cookie! -- side note, express probably gives a cookie before this as well, but you need to hit this route without the key to get bad_apple in your session, and then use bad_apple to get reported.)

The next step is to use this cookie and the knowledge of the session-file-store package to look in /sessions/$sessid to grab your session (and another key that is required to report people!) 



