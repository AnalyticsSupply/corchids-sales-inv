"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb
#from google.appengine.ext import db
from werkzeug.security import generate_password_hash


class NDBBase(ndb.Model):
    @property
    def id(self):
        """Override for getting the ID.
        Resolves NotImplementedError: No `id` attribute - override `get_id`
        :rtype: str
        """
        return self.key.id()

    @classmethod
    def _post_get_hook(cls, key, future):
        self = future.get_result()
        if self:
            self._is_saved = bool(key)

    def _post_put_hook(self, future):
        self._is_saved = future.state == future.FINISHING

    def set_saved(self):
        self._is_saved = True

    def is_saved(self):
        if self._has_complete_key():
            return getattr(self, "_is_saved", False)
        return False

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
    
    

class UserModel(NDBBase):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    added_by = ndb.UserProperty(auto_current_user_add=True)


class Plant(NDBBase):
    """ Plants for which we have forecasted values"""
    name = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    image_name = ndb.StringProperty(required=True)    
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    
    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.plant == self.key)
    
    @property
    def concept_plants(self):
        return ConceptPlant.query(ConceptPlant.plant == self.key)


class Customer(NDBBase):
    """ Customer that has plant orders against forecasted volume """
    customer_name = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=False)
    address = ndb.StringProperty()
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)   
    
    @property
    def reserves(self):
        return ConceptReserve.query(ConceptReserve.customer == self.key)

class GrowWeek(NDBBase):
    """ Represents a Week where we can have reserve orders """
    week_number = ndb.IntegerProperty(required=True)
    year = ndb.IntegerProperty(required=True)
    week_monday = ndb.DateProperty()
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)

    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.finish_week == self.key)
    
    @property 
    def reserves(self):
        return ConceptReserve.query(ConceptReserve.finish_week == self.key)
    
class Supplier(NDBBase):
    """ Represents the supplier of plants """
    name = ndb.StringProperty(required=True)
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    
    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.supplier == self.key)

class PlantGrow(NDBBase):
    """ This is the class that will track orders of plants from different suppliers """
    plant = ndb.KeyProperty(kind=Plant)
    finish_week = ndb.KeyProperty(kind=GrowWeek)
    supplier = ndb.KeyProperty(kind=Supplier)
    actual = ndb.IntegerProperty(default=0)
    actual_qty = ndb.IntegerProperty(default=0)
    forecast = ndb.IntegerProperty(default=0)
    forecast_qty = ndb.IntegerProperty(default=0)
    confirmation_num = ndb.StringProperty()
    cost = ndb.FloatProperty()
    sale_price = ndb.FloatProperty()
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)

class Concept(NDBBase):
    """ many plants can be combined to create 1 concept """
    name = ndb.StringProperty(required=True)
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    
    @property
    def concept_plants(self):
        return ConceptPlant.query(ConceptPlant.concept == self.key)
    
    @property
    def product_concepts(self):
        return ProductConcept.query(ProductConcept == self.key)
    
    @property
    def reserves(self):
        return ConceptReserve.query(ConceptReserve.concept == self.key)
    
class Product(NDBBase):
    ''' this is the product name for customers '''
    name = ndb.StringProperty(required=True)
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    
    @property
    def product_concepts(self):
        return ProductConcept.query(ProductConcept.product == self.key)
   
class ConceptPlant(NDBBase):
    plant = ndb.KeyProperty(kind=Plant)
    concept = ndb.KeyProperty(kind=Concept)
    qty = ndb.IntegerProperty(required=True,default=1)
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
   
class ProductConcept(NDBBase):
    concept = ndb.KeyProperty(kind=Concept)
    product = ndb.KeyProperty(kind=Product)
    qty = ndb.IntegerProperty(required=True, default=1)
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    
class ConceptReserve(NDBBase):
    """ This is the plant that is being reserved by a customer """
    customer = ndb.KeyProperty(kind=Customer)
    finish_week = ndb.KeyProperty(kind=GrowWeek)
    concept = ndb.KeyProperty(kind=Concept)
    num_reserved = ndb.IntegerProperty(default=0)
    shipped = ndb.BooleanProperty()
    ship_date = ndb.DateProperty()
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    

class ConceptReserveWrap():
    
    def __init__(self, concept_resv):
        self.cr = concept_resv
        self.plant_name = None
        self.plant_reserve = 0
        
    def incr_plant(self, num):
        self.plant_reserve = self.plant_reserve + num
    

class RouteEntryMain(NDBBase):
    added_by = ndb.UserProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now_add=True)
    
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