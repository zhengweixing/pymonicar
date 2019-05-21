#!/usr/bin/env python
from monicar import create_app
from flask_script import Manager, Server

app = create_app('default')
'''manager = Manager(app)

manager.add_command("start", Server(port=5678, use_debugger=True))


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

'''
if __name__ == '__main__':
    app.run(port=5678)
    """manager.run()"""
