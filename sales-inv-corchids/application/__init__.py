"""
Initialize Flask app

"""
from flask import Flask, jsonify, request, make_response
import os, sys
import traceback
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.debug import DebuggedApplication
from flask_sqlalchemy import SQLAlchemy
from models import Plant, Supplier, update_model, GrowWeek
from standard_models import DBEntry

from google.appengine.api.taskqueue import taskqueue


app = Flask('application')

app.config['SQLALCHEMY_DATABASE_URI'] = DBEntry.get_connection_string('Datawarehouse')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

@app.route('/update_info/<path:path>/',methods=['DELETE', 'GET', 'GET_METADATA', 'POST', 'PUT'])
def get_update_info(path):
    return restful.get_update_info(path)

@app.route('/options/<path:path>/',methods=['GET'])
def get_options(path):
    r = restful.get_option_field(path, request.values)
    return jsonify(r)

@app.route('/log_message',methods=['GET','POST'])
def process_add_log_message():
    uJson = request.get_json()
    return restful.add_logging_message(uJson['message'],uJson['msg_type'])

@app.route("/test_email", methods=['GET'])
def send_test_email():
    return restful.send_test_email()

@app.route('/push_dw',methods=['GET','POST'])
def process_dw_task():
    process_task = request.values.get("task")
    process_step = request.values.get('process')
    task = taskqueue.add(
        url='/run_dw_task',
        target='worker',
        params={'task':process_task,'process':process_step})
    
    return jsonify({'task_name':task.name,'task_eta':task.eta})

@app.route('/run_dw_task',methods=['POST','GET'])
def run_dw_task():
    runtask = request.values.get('task')
    process = request.values.get("process") # either prep or run
    
    try:
        if runtask == 'newprop':
            update_model(process)
        elif runtask == 'fix_dates':
            GrowWeek.set_mondays()
        elif runtask == 'date':
            if process == 'prep':
                database.set_date()
            else:
                database.get_date()
        elif runtask == 'supply':
            if process == 'prep':
                database.set_supply()
            else:
                database.get_supply()
        elif runtask == 'reserve':
            if process == 'prep':
                database.set_reserves()
            else:
                database.get_reserves()
        elif runtask == 'summary':
            if process == 'prep':
                database.set_summary()
            else:
                database.get_summary()
        elif runtask == 'all':
            if process == 'prep':
                database.set_date()
                database.set_supply()
                database.set_reserves()
                database.set_summary()
            else:
                database.get_date()
                database.get_supply()
                database.get_reserves()
                database.get_summary()
        else:
            print("Got {}, not sure what to do!!1".format(runtask))
        return jsonify({"status":"success"})
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        return jsonify({"status":"failed"})
    
if __name__ == "__main__":
    app.run()