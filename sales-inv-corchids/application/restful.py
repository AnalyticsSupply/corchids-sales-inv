'''
Created on Dec 17, 2016

@author: jason

THis is just my way of making the REST stuff work
'''
from application.models import Plant,Customer,GrowWeek,Supplier, Concept,PlantGrow,Product,ProductConcept,\
    ProductReserve,ProductPlant,PlantGrowSupply

from application.views.admin import authen
from application.rest import DispatcherException, Dispatcher
from flask import make_response,jsonify

from exceptions import AttributeError
import sys
from application.decorators import login_required

Dispatcher.base_url = "/rest"
Dispatcher.add_models({"plant": Plant,'productplant':ProductPlant,
                       "customer":Customer,'productconcept':ProductConcept,
                       "week":GrowWeek,'product':Product,'plantgrowsupply':PlantGrowSupply,
                       "supplier":Supplier,"concept":Concept,
                       "plantgrow":PlantGrow,"productreserve":ProductReserve})

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
        response = make_response("<html><body>{}: {}</body></html>".format(e.error_code,e.message),e.error_code)
    except AttributeError as err:
        print(err)
        response = make_response("<html><body>{}: Attribute Error</body></html>".format(err.message),500)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        response = make_response("<html><body>{}: Bad Request</body></html>".format(sys.exc_info()[0]),500)
        
        
    
    return response

@login_required
def get_week_summary(year, week_num):
    qry = GrowWeek.query(GrowWeek.year == year, GrowWeek.week_number == week_num)
    week = qry.get()
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
        
#class PlantSvc(Resource):
#        def get(self):
#            plants = Plants.query()
            