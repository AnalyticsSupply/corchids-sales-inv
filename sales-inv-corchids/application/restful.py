'''
Created on Dec 17, 2016

@author: jason
'''
from application.models import Plant,Customer,GrowWeek,PlantWeek,Supplier, Concept, ConceptPlant, ConceptReserve,PlantGrow,ConceptWeek

from application.views.admin import authen
from application.rest import DispatcherException, Dispatcher
from flask import make_response

from exceptions import AttributeError
import sys

Dispatcher.base_url = "/rest"
Dispatcher.add_models({"plant": Plant,"customer":Customer,
                       "week":GrowWeek,"plantweek":PlantWeek,
                       "supplier":Supplier,"concept":Concept,
                       "conceptplant":ConceptPlant,"conceptreserve":ConceptReserve,
                       "plantgrow":PlantGrow,"conceptweek":ConceptWeek})

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

#class PlantSvc(Resource):
#        def get(self):
#            plants = Plants.query()
            