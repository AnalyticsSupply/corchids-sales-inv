"""
Initialize Flask app

"""
from flask import Flask, jsonify, request, make_response
import os, sys
import traceback
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.debug import DebuggedApplication
from flask_sqlalchemy import SQLAlchemy
from models import DBEntry, Plant, Supplier


app = Flask('application')

app.config['SQLALCHEMY_DATABASE_URI'] = DBEntry.get_connection_string('Datawarehouse')
db = SQLAlchemy(app)

import database

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
    
    Plant.dev_get_create()
    Supplier.dev_get_create()
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


@app.route('/notes/save/<int:pg_key>',methods=['POST'])
def save_note(pg_key):
    #jin = request.form
    jin = request.get_json(force=True)
    return restful.notes_wrapper(plantgrow_key=pg_key, note = jin['note'], method='save')

@app.route('/notes/get/<int:pg_key>',methods=['GET'])
def get_notes(pg_key):
    return restful.notes_wrapper(plantgrow_key=pg_key, method='get')

@app.route('/notes/delete/<int:nt_key>',methods=['GET'])
def delete_note(nt_key):
    return restful.notes_wrapper(note_key=nt_key, method='delete')

@app.route('/week_summary/<int:year>/<int:week_num>', methods=['GET'])
def get_summary(year, week_num):
    return restful.get_week_summary(year, week_num)


@app.route('/plantgrow/availability/<int:plantgrow>', methods=['GET'])
def get_availability(plantgrow):
    try:
        avail = restful.get_availability(plantgrow)
        return jsonify({'availability': avail})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
    
    return jsonify({'availability':0})

@app.route('/plantgrow/update/',methods=['GET','POST'])
def upd_plantgrow():
    try:
        jpg = request.get_json()
        return restful.update_plant_grow(jpg['plant'], jpg['week'], jpg['actual'])
    except Exception:
        return traceback.format_exc()

@app.route('/supplier_plants/update/',methods=['GET','POST'])
def update_supplier_plants():
    try:
        uJson = request.get_json()
        return restful.update_plantweek_entry(uJson)
    except Exception:
        msg = traceback.format_exc()
        print(msg)
        return {'status':'failed','msg': msg}
    
@app.route('/customer_reserve/update/',methods=['GET','POST'])
def update_customer_reserve():
    try:
        uJson = request.get_json()
        return restful.update_plantweek_entry(uJson)
    except Exception:
        return traceback.format_exc()
    
@app.route('/dw_week',methods=['GET'])
def sync_weeks():
    try:
        database.get_date()
        return jsonify({"status":"success"})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        return jsonify({"status":"failed"})
    
@app.route('/dw_supplies',methods=['GET'])
def sync_supplies():
    try:
        database.get_supply()
        return jsonify({"status":"success"})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        return jsonify({"status":"failed"})
    
@app.route('/dw_reserves',methods=['GET'])
def sync_reserves():
    try:
        database.get_reserves()
        return jsonify({"status":"success"})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        return jsonify({"status":"failed"})

@app.route('/dw_summary',methods=['GET'])
def sync_summary():
    try:
        database.get_summary()
        return jsonify({"status":"success"})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        return jsonify({"status":"failed"})
    
@app.route('/dwsync',methods=['GET'])
def sync_db():
    try:
        database.get_date()
        database.get_supply()
        database.get_reserves()
        database.get_summary()
        return jsonify({"status":"success"})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        return jsonify({"status":"failed"})

if __name__ == "__main__":
    app.run()