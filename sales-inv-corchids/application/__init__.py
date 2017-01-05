"""
Initialize Flask app

"""
from flask import Flask, jsonify, request, make_response
import os
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.debug import DebuggedApplication

from models import Plant

app = Flask('application')

if os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('application.settings.Testing')

elif 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    # Development settings
    app.config.from_object('application.settings.Development')
    # Flask-DebugToolbar
    toolbar = DebugToolbarExtension(app)

    # Google app engine mini profiler
    # https://github.com/kamens/gae_mini_profiler
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
    _temp = __import__('gae_mini_profiler', globals(), locals(), ['profiler', 'templatetags'], -1)
    profiler = _temp.profiler
    templatetags = _temp.templatetags
    #from gae_mini_profiler import profiler, templatetags
    #from flasext.gae_mini_profiler import profiler

    @app.context_processor
    def inject_profiler():
        return dict(profiler_includes=templatetags.profiler_includes())
    app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)
else:
    app.config.from_object('application.settings.Production')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Pull in URL dispatch routes
import urls
import restful

@app.route('/rest')
@app.route('/rest/<path:path>/',methods=['DELETE', 'GET', 'GET_METADATA', 'POST', 'PUT'])
def rest_impl(path):
    return restful.process_rest_request(path, request,make_response())

@app.route('/week_summary/<int:year>/<int:week_num>', methods=['GET'])
def get_summary(year, week_num):
    return restful.get_week_summary(year, week_num)

if __name__ == "__main__":
    app.run()