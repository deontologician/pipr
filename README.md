pipr
====

An AngularJS tutorial building a Twitter-like application called Pipr

To run on heroku, you'll need to attach a Redis instance and set the environment
variable `REDIS_URL` to point to it.

To run it locally, you'll want to copy .env.example to .env and fill in the
values of the environment variables. Then you can start the server with:

```
$ source .env
$ python server/server.py
```
