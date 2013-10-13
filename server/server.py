import os
import uuid
import json
import logging
import urlparse
import functools
import datetime

from tornado import web, ioloop
import redis

# Normalize serialization in Redis
jdump = functools.partial(json.dumps, separators=(',',':'), sort_keys=True)


class APIHandler(web.RequestHandler):
    def initialize(self, *args, **kwargs):
        #  Allow access from other domains
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header("Access-Control-Allow-Headers",
                        "Origin, X-Requested-With, Content-Type, Accept")
        self.set_header('Content-Type', 'application/json')
        self.redis = self.application.settings['redis']

class PipsHandler(APIHandler):
    '''Returns pips'''

    def options(self):
        # OPTIONS is needed for CORS
        self.set_header('Allow', 'GET,POST')
        self.set_header('Access-Control-Allow-Methods', 'GET,POST')

    def get(self):
        try:
            limit = max(abs(int(self.get_argument('limit', '10'))), 1)
            offset = abs(int(self.get_argument('offset', '0')))
        except TypeError as e:
            raise web.HTTPError(400, jdump({'error': str(e)}))
        
        pips = self.redis.lrange('pips', offset, (offset + limit) - 1)
        self.write(jdump(map(json.loads, pips)))

    def post(self):
        try:
            # input validation
            pip = json.loads(self.request.body)
            assert 'name' in pip, 'A pip must have a name'
            assert isinstance(pip['name'], basestring), \
                'name must be a string'
            assert 0 < len(pip['name']) <= 100, \
                'name must be between 1 and 100 chars'
            assert 'pip' in pip, 'A pip must have a body'
            assert isinstance(pip['pip'], basestring), 'pip must be a string'
            assert 0 < len(pip['pip']) <= 100, \
                'pip must be between 1 and 100 chars'
            tags = pip.setdefault('tags', [])
            assert isinstance(tags, list), 'tags must be a list'
            for tag in tags:
                assert isinstance(tag, basestring), 'each tag must be a string'
            assert len(''.join(pip.get('tags', []))) < 100, \
                'tags have a cumulative 100 char limit'
        except (ValueError, KeyError, TypeError, AssertionError) as e:
            self.set_status(400)
            self.write({'error': str(e)})
        else:
            pip['id'] = str(uuid.uuid4())
            self.redis.lpush('pips', jdump({
                'name': pip['name'],
                'pip': pip['pip'],
                'tags': pip.get('tags', []),
                'id': pip.get('id'),
                'created': datetime.datetime.utcnow().isoformat(),
            }))
            logging.info('{} pipped {}'.format(pip['name'], pip['pip']))
            self.redis.ltrim('pips', 0, self.application.settings['max_pips'])

            # Now send them to the location of their new pip
            url = 'http://{hostname}/api/pips/{pipid}'.format(
                pipid=pip['id'],
                hostname=self.request.host,
            )
            self.set_status(201)
            self.set_header('Location', url)


class PipHandler(APIHandler):

    def options(self, pipid):
        # OPTIONS is needed for CORS
        self.set_header('Allow', 'GET,DELETE')
        self.set_header('Access-Control-Allow-Methods', 'GET,DELETE')

    def one_pip(self, pipid):
        all_pips = self.redis.lrange('pips', 0, self.redis.llen('pips'))
        for pip in all_pips:
            pipj = json.loads(pip)
            if pipj.get('id') == pipid:
                return pipj
                break
        else:
            return None

    def get(self, pipid):
        pip = self.one_pip(pipid)
        if pip is None:
            self.set_status(404)
            self.write({'error': 'no such pip'})
        else:
            self.write(pip)

    def delete(self, pipid):
        pip = self.one_pip(pipid)
        if pip is None:
            self.set_status(404)
            self.write({'error': 'no such pip'})
        elif self.redis.llen('pips') <= 2:
            self.set_status(400)
            self.write({'error': "Can't delete the last 2 pips"})
        else:
            logging.info("Removing {name}'s pip: {pip}".format(**pip))
            self.redis.lrem('pips', 0, jdump(pip))


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)    

    # SET up redis connection
    redis_url = urlparse.urlparse(os.getenv('REDIS_URL'))
    logging.info('Connecting to redis: ' + os.getenv('REDIS_URL'))
    redisconn = redis.StrictRedis(host=redis_url.hostname or 'localhost',
                              port=redis_url.port or 6379,
                              password=redis_url.password or '',
    )
    
    application = web.Application(
        [
            (r"/api/pips", PipsHandler),
            (r"/api/pips/", PipsHandler),
            (r"/api/pips/(.*)", PipHandler),
            (r"/", web.RedirectHandler, {'url': '/index.html'}),
            (r"/(.+)", web.StaticFileHandler, {'path': 'pipr/app'}),
        ],
        debug=True,
        gzip=True,
        redis=redisconn,
        max_pips=int(os.getenv('MAX_PIPS', 1000)),
    )
    application.listen(os.getenv('PORT', 9000))

    ioloop.IOLoop.instance().start()
