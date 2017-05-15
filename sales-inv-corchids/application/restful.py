'''
Created on Dec 17, 2016

@author: jason

THis is just my way of making the REST stuff work
'''
from application.models import Plant,Customer,GrowWeek,Supplier, Concept,PlantGrow,Product,ProductConcept,\
    ProductReserve,ProductPlant,PlantGrowSupply, PlantGrowNotes, EmailNotifications

from application.views.admin import authen
from datetime import datetime
from application.rest import DispatcherException, Dispatcher
from flask import make_response,jsonify

from exceptions import AttributeError
import sys, traceback
from application.decorators import login_required, admin_required

Dispatcher.base_url = "/rest"
Dispatcher.add_models({"plant": Plant,'productplant':ProductPlant,
                       "customer":Customer,'productconcept':ProductConcept,
                       "week":GrowWeek,'product':Product,'plantgrowsupply':PlantGrowSupply,
                       "supplier":Supplier,"concept":Concept,
                       "plantgrow":PlantGrow,"productreserve":ProductReserve})


updates = {'Product':{'options':[], 
                      'fields':{'name':'i','sale_price':'i','qty_per_case':'i',
                                'box_height':'i','box_width':'i','box_length':'i',
                                'ti':'i','hi':'i'},
                      'order':['name','sale_price','qty_per_case','box_height','box_width',
                               'box_length','ti','hi'],
                      'style':'new_screen'},
           'Plant':{'options':[],
                    'fields':{'name':'i','display_name':'i','inactive':'i'},
                    'order':['name','display_name','inactive'],
                    'style':'in_line'},
           'Customer':{'options':[],
                       'fields':{'customer_name':'i','description':'i','address':'i'},
                       'order':['customer_name','description','address'],
                       'style':'in_line'},
           'Supplier':{'options':[],'fields':{'name':'i'},'order':['name'],'style':'in_line'},
           'Concept':{'options':[],'fields':{'name':'i'},'order':['name'],'style':'in_line'}    
           }

Dispatcher.authenticator = authen.BasicAuthenticator()
Dispatcher.authorizer = authen.OwnerAuthorizer()

def process_rest_request(path, request,response):
    print(path)
    d = Dispatcher(request,response)
    try:
        if request.method == "PUT":
            d.put()
        elif request.method == "DELETE":
            d.delete()
        elif request.method == "POST":
            d.post()
        elif request.method == "GET":
            d.get()
        response = d.response
    except DispatcherException as e:
        #if d.response.status_code == 200:
        traceback.print_exc(file=sys.stdout)
        response = make_response("<html><body>{}: {}</body></html>".format(e.error_code,e.message),e.error_code)
    except AttributeError as err:
        print(err)
        traceback.print_exc(file=sys.stdout)
        response = make_response("<html><body>{}: Attribute Error</body></html>".format(err.message),500)
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        response = make_response("<html><body>{}: Bad Request</body></html>".format(sys.exc_info()[0]),500)
        
        
    
    return response

@login_required
def get_update_info(update_name):
    if update_name in updates.keys():
        return jsonify({'status':'success','message':'Pulled update info for: '+update_name,'payload':updates[update_name]})
    else:
        return jsonify({'status':'failed','message':'Update Name Does Not Exist','payload':{}})

@login_required
def get_week_summary(year, week_num):
    try:
        day =  str(year)+'-'+str(week_num)+'-1'
        dt = datetime.strptime(day, '%Y-%W-%w')
        #qry = GrowWeek.query(GrowWeek.week_monday == dt)
        week = GrowWeek.create_week(dt)
        resp = {}
        if week:
            resp = week.week_summary()
            dlist = []
            for plant in resp.keys():
                d = resp[plant]
                d['plant'] = plant
                dlist.append(d)
            resp = dlist
        return jsonify(resp)
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])
        
        return jsonify({'status':'failed'})

@login_required
def update_plant_grow(plant_key, week_key, actual):
    return jsonify(PlantGrow.update_plantgrow(plant_key, week_key, actual))

@admin_required
def send_test_email():
    EmailNotifications.send_test_email()
    return jsonify({"Status":"Success"})

@login_required
def get_availability(plantgrow_id):
    try:
        pg = PlantGrow.get_by_id(plantgrow_id)
        return pg.availability()
    except:
        traceback.print_exc(file=sys.stdout)
        print("Unexpected error:", sys.exc_info()[0])

    
    return 0

@login_required
def update_plantweek_entry(inData):
    if inData['service_name'] == 'customer_reserve':
        if 'soft_delete' in inData:
            resp = ProductReserve.delete(inData['id'])
        else:
            resp = ProductReserve.update(inData['id'],inData['customer'], inData['week'], inData['product'], inData['num_reserved'])
        return jsonify(resp)
    
    if inData['service_name'] == 'supplier_plants':
        resp = PlantGrowSupply.update(inData['id'], inData['plant'], inData['week'], inData['supplier'], inData['forecast'], inData['confirmation_num'])
        return jsonify(resp)
                                                                                                                                    

@login_required
def notes_wrapper(plantgrow_key=None,note_key=None, note="", method='save'):
    if method == 'save':
        return jsonify(PlantGrowNotes.save_note(note,plantgrow_key))
    elif method == 'delete':
        return jsonify(PlantGrowNotes.delete_note(note_key))
    else:
        return jsonify(PlantGrowNotes.get_notes(plantgrow_key))

#class PlantSvc(Resource):
#        def get(self):
#            plants = Plants.query()
            