import cherrypy
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Webroot():
    """
    The webroot endpoint simply serves the main index.html file.
    """
    exposed = True

    def GET(self):
        return cherrypy.lib.static.serve_file(
            os.path.join(ROOT_DIR, 'clients', 'web', 'static', 'built', 'index.html'),
            content_type='text/html')

if __name__ == '__main__':
    appconf = {
        '/' : {
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tools.staticdir.root' : ROOT_DIR
            },
        '/static' : {
            'tools.staticdir.on' : 'True',
            'tools.staticdir.dir' : 'clients/web/static',
            }
        }
    configs = ['db.local.cfg']
    configs = [os.path.join(ROOT_DIR, 'server', 'conf', config) for config in configs]
    cherrypy.config.update(appconf)
    [cherrypy.config.update(config) for config in configs]

    # Don't import this until after the configs have been read; some module
    # initialization code requires the configuration to be set up.
    from api import api_main

    root = Webroot()
    root = api_main.addApiToNode(root)

    application = cherrypy.tree.mount(root, '/', appconf)
    [application.merge(config) for config in configs]

    cherrypy.engine.start()
    cherrypy.engine.block()