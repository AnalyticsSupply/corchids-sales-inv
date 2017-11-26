'''
Created on Dec 17, 2016

@author: jason

THis is just my way of making the REST stuff work
'''
from .models import Plant,Customer,GrowWeek,Supplier, Concept,PlantGrow,Product,ProductConcept,\
    ProductReserve,ProductPlant,PlantGrowSupply, PlantGrowNotes, EmailNotifications, LoggingMessages

from google.appengine.ext import ndb

from .views.admin import authen
from datetime import datetime
from datetime import timedelta
from .rest import DispatcherException, Dispatcher
from flask import make_response,jsonify

from exceptions import AttributeError
import sys, traceback
from .decorators import login_required, admin_required

Dispatcher.base_url = "/rest"
Dispatcher.add_models({"plant": Plant,'productplant':ProductPlant,
                       "customer":Customer,'productconcept':ProductConcept,
                       "week":GrowWeek,'product':Product,'plantgrowsupply':PlantGrowSupply,
                       "supplier":Supplier,"concept":Concept,
                       "plantgrow":PlantGrow,"productreserve":ProductReserve})


form_options = {'boolean':{'type':'fixed',
                           'values':['true','false'],
                           'field':'boolean',
                           'key':'id',
                           'name':'boolean',
                           'filters':[]},
               'customers':{'type':'model',
                            'values':[],
                            'field':'customer_name',
                            'key':'id',
                            'name':'Customer',
                            'filters':[]},
                'suppliers':{'type':'model',
                             'values':[],
                             'field':'name',
                             'name':'Supplier',
                             'key':'id',
                             'filters':[]},
                'plants':{'type':'model',
                          'values':[],
                          'field':'name',
                          'key':'id',
                          'name':'Plant',
                          'filters':[{'field':'inactive','key':False,'type':'Long'}]},
                'concepts':{'type':'model',
                            'values':[],
                            'field':'name',
                            'key':'id',
                            'name':'Concept',
                            'filters':[]},
                'product_concepts':{'type':'model',
                            'values':[],
                            'field':'concept.name',
                            'key':'concept.id',
                            'name':'ProductConcept',
                            'filters':[{'field':'product','key':True,'type':'Product'}]},
                'product_plants':{'type':'model',
                                  'values':[],
                                  'field':'plant.name',
                                  'key':'plant.id',
                                  'name':'ProductPlant',
                                  'filters':[{'field':'product','key':True,'type':'Product'}]},
                'products':{'type':'model',
                            'values':[],
                            'field':'product.name',
                            'key':'product.id',
                            'name':'ProductPlant',
                            'filters':[{'field':'plant','key':True,'type':'Plant'}]}
                           }
@admin_required
def get_option_field(field, filters):
    form_field = form_options.get(field,None)
    resp = {}
    resp['values'] = []
    if form_field:
        if form_field['type'] == 'fixed':
            for value in form_field['values']:
                resp['values'].append({'key':value, 'value':value})
        else:
            if form_field['type'] == 'model':
                where_cls = ""
                if filters and len(form_field['filters']) > 0:
                    wheres = []
                    for filt in form_field['filters']:
                        name = filt['field']
                        isKey = filt['key']
                        mType = filt['type']
                        if name in filters.keys():
                            if not isKey:                            
                                wheres.append("{} = {}".format(name,filters[name]))
                            else:
                                wheres.append("{} = KEY('{}',{})".format(name,mType,filters[name]))
                    if len(wheres) > 0:
                        where_cls = "WHERE "
                        for w in wheres:
                            where_cls = where_cls + w + " AND "
                        where_cls = where_cls[:-5]
                stmt = "SELECT * FROM {} "+where_cls
                stmt = stmt.format(form_field['name'])
                model = ndb.gql(stmt)
                for m in model:
                    key = ""
                    field = ""
                    field_name = form_field['field']
                    if len(field_name.split(".")) > 1:
                        parts = field_name.split(".")
                        p = m
                        for i in range(len(parts)):
                            if i+1 < len(parts):
                                p = getattr(p,parts[i]).get()
                            else:
                                field = getattr(p,parts[i])
                    else:
                        field = getattr(m,form_field['field'])
                    key_name = form_field['key']
                    if len(key_name.split(".")) > 1:
                        parts = key_name.split(".")
                        p = m
                        for i in range(len(parts)):
                            if i+1 < len(parts):
                                p = getattr(p,parts[i]).get()
                            else:
                                key = getattr(p,parts[i])
                    else:
                        key = getattr(m,form_field['key'])
                            
                    resp['values'].append({'key':key,'value':field})
    return resp
                
        
    

updates = {'Product':{'options':[], 
                      'update_name':'Product',
                      'fields':{'name':'i','sale_price':'i','qty_per_case':'i'},
                      'order':['name','sale_price','qty_per_case'],
                      'style':'new_screen'},
           'Plant':{'options':[{'field_name':'inactive', 'option_name':'boolean'}],
                    'update_name':'Plant',
                    'fields':{'name':'i','display_name':'i','inactive':'o'},
                    'order':['name','display_name','inactive'],
                    'style':'in_line'},
           'Customer':{'options':[],
                       'update_name':'Customer',
                       'fields':{'customer_name':'i','description':'i','address':'i'},
                       'order':['customer_name','description','address'],
                       'style':'in_line'},
           'Supplier':{'options':[],'update_name':'Supplier','fields':{'name':'i'},'order':['name'],'style':'in_line'},
           'Concept':{'options':[],'update_name':'Concept','fields':{'name':'i'},'order':['name'],'style':'in_line'}    
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
        
        if dt.isocalendar()[1] > week_num:
            dt = dt + timedelta(days=-7)
            
        if dt.isocalendar()[1] < week_num:
            dt = dt + timedelta(days=7)
            
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
    if inData['service_name'].startswith('customer_reserve'):
        if 'soft_delete' in inData:
            resp = ProductReserve.delete(inData['id'])
        else:
            resp = ProductReserve.update(inData['id'],inData['customer'], inData['week'], inData['product'], inData['num_reserved'])
        return jsonify(resp)
    
    if inData['service_name'].startswith('supplier_plants'):
        resp = PlantGrowSupply.update(inData['id'], inData['plant'], inData['week'], inData['supplier'], inData['forecast'], inData['confirmation_num'])
        return jsonify(resp)
    return {'status':'Failed','message':'No valid service found'}
                                                                                                                                    

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
            