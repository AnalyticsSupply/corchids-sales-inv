"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb
from google.appengine.ext import db
from werkzeug.security import generate_password_hash
from google.storage.speckle.proto.jdbc_type import NULL


class NDBBase(ndb.Model):
    @property
    def id(self):
        """Override for getting the ID.
        Resolves NotImplementedError: No `id` attribute - override `get_id`
        :rtype: str
        """
        return self.key.id()

class RouteEntryMain(NDBBase):
    added_by = ndb.UserProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now_add=True)

class User:
    pw_hash = None
    username = None
    
    def __init__(self, user, pw):
        self.username = user
        self.set_password(pw)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def get_model(self):
        return UserModel(username=self.username, pw_hash=self.pw_hash)
    
    

class UserModel(ndb.Model):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)


class Plant(db.Model):
    """ Plants for which we have forecasted values"""
    name = db.StringProperty(required=True)
    display_name = db.StringProperty(required=True)
    image_name = db.StringProperty(required=True)    
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)


class Customer(db.Model):
    """ Customer that has plant orders against forecasted volume """
    customer_name = db.StringProperty(required=True)
    description = db.StringProperty(required=False)
    address = db.StringProperty()
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)   

class GrowWeek(db.Model):
    """ Represents a Week where we can have reserve orders """
    week_number = db.IntegerProperty(required=True)
    year = db.IntegerProperty(required=True)
    week_monday = db.DateProperty()
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)

class Supplier(db.Model):
    """ Represents the supplier of plants """
    name = db.StringProperty(required=True)
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)
    

class PlantGrow(db.Model):
    """ This is the class that will track orders of plants from different suppliers """
    plant = db.ReferenceProperty(Plant,collection_name="plantgrow")
    finish_week = db.ReferenceProperty(GrowWeek,collection_name="plantgrow")
    supplier = db.ReferenceProperty(Supplier, collection_name="plantgrow")
    actual = db.IntegerProperty(default=0)
    actual_qty = db.IntegerProperty(default=0)
    forecast = db.IntegerProperty(default=0)
    forecast_qty = db.IntegerProperty(default=0)
    confirmation_num = db.StringProperty()
    cost = db.FloatProperty()
    sale_price = db.FloatProperty()
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)

class Concept(db.Model):
    """ many plants can be combined to create 1 concept """
    name = db.StringProperty(required=True)
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)
   
class ConceptPlant(db.Model):
    plant = db.ReferenceProperty(Plant, collection_name="concept_plants")
    concept = db.ReferenceProperty(Concept, collection_name="concept_plants")
    qty = db.IntegerProperty(required=True)
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)


class PlantWeek(db.Model):
    """ Model that tracks the numbers and plant availability by week """
    plant = db.Reference(Plant,collection_name='plantweeks')
    week = db.ReferenceProperty(GrowWeek, collection_name="plantweeks")
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)  

class ConceptWeek(db.Model):
    """ Model to track the number of concepts reserved by week """
    concept = db.ReferenceProperty(Concept,collection_name="conceptweeks")
    week = db.ReferenceProperty(GrowWeek,collection_name="conceptweeks")
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)  
   
class ConceptReserve(db.Model):
    """ This is the plant that is being reserved by a customer """
    customer = db.Reference(Customer,collection_name='reserves')
    finish_week = db.ReferenceProperty(GrowWeek,collection_name='reserves')
    concept = db.ReferenceProperty(Concept,collection_name='reserves')
    num_reserved = db.IntegerProperty(default=0)
    shipped = db.BooleanProperty()
    ship_date = db.DateProperty()
    added_by = db.UserProperty(auto_current_user_add=True)
    updated_by = db.UserProperty(auto_current_user=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    up_timestamp = db.DateTimeProperty(auto_now=True)
    

class ConceptReserveWrap():
    
    def __init__(self, concept_resv):
        self.cr = concept_resv
        self.plant_name = None
        self.plant_reserve = 0
        
    def incr_plant(self, num):
        self.plant_reserve = self.plant_reserve + num
    

class RouteStops(NDBBase):
    """ Route Stop """
    stop_name = ndb.StringProperty(required=True)
    stop_ship_to = ndb.StringProperty(required=True)
    stop_zip = ndb.StringProperty(required=True)
    stop_dist = ndb.IntegerProperty(required=True)
    stop_load = ndb.IntegerProperty(required=True)
    stop_pallets = ndb.IntegerProperty()
    stop_ret_carts = ndb.IntegerProperty()
    stop_carts = ndb.IntegerProperty()
    
    #route = ndb.KeyProperty(kind=RouteEntryMain)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now_add=True)