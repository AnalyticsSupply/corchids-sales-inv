"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb
#from google.appengine.ext import db
from werkzeug.security import generate_password_hash

from datetime import datetime


class NDBBase(ndb.Model):
    added_by = ndb.UserProperty(auto_current_user_add=True)
    updated_by = ndb.UserProperty(auto_current_user=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    up_timestamp = ndb.DateTimeProperty(auto_now=True)
    
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
    
    def convert_bool(self, value):
        if str(value).lower().strip()  == "true":
            return True
        
        if str(value).lower().strip() == "1":
            return True
        return False
    
    def update_resp(self):
        resp = {'status':'success','msg':'Updated Successfully'}
        try:
            key = self.put()
            resp['key'] = key.id()
        except Exception as e:
            resp = {'status':'failed','msg': str(e)}
        return resp
    
    def delete_resp(self):
        resp = {'status':'success','msg':'Deleted Successfully'}
        try:
            self.key.delete()
        except Exception as e:
            resp = {'status':'failed','msg': str(e)}
        return resp

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

class Plant(NDBBase):
    """ Plants for which we have forecasted values"""
    name = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    image_name = ndb.StringProperty(required=True)    
    
    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.plant == self.key)
    
    @property
    def products(self):
        return ProductPlant.query(ProductPlant.plant == self.key)
    
 #   @property
 #   def concept_plants(self):
 #       return ConceptPlant.query(ConceptPlant.plant == self.key)


class Customer(NDBBase):
    """ Customer that has plant orders against forecasted volume """
    customer_name = ndb.StringProperty(required=True)
    description = ndb.StringProperty(required=False)
    address = ndb.StringProperty()
    
    @property
    def reserves(self):
        return ProductReserve.query(ProductReserve.customer == self.key)

class GrowWeek(NDBBase):
    """ Represents a Week where we can have reserve orders """
    week_number = ndb.IntegerProperty(required=True)
    year = ndb.IntegerProperty(required=True)
    week_monday = ndb.DateProperty()
   
    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.finish_week == self.key)
    
    @property 
    def reserves(self):
        return ProductReserve.query(ProductReserve.finish_week == self.key)
    
    def chk_create(self, din, name, plant):
        if name not in din.keys():
            din[name] = {'wanted':0,'actual':0,'forecast':0, 'reserved':0}
            din[name]['plant_key'] = plant.id
            din[name]['week_key'] = self.id
    
    def week_summary(self):
        pgs = self.plantgrow
        rsvs = self.reserves
        
        pgd = {}
        for pg in pgs:
            plant = pg.plant.get()
            name = plant.display_name
            self.chk_create(pgd,name,plant)            
            pgd[name]['actual'] = pgd[name]['actual'] + pg.actual
            pgd[name]['wanted'] = pgd[name]['wanted'] + pg.want_qty
            pgd[name]['id'] = pg.id
            
            supps = pg.supplies
            for supp in supps:
                pgd[name]['forecast'] = pgd[name]['forecast'] + supp.forecast
            
        for rsv in rsvs:
            pps = rsv.product.get().product_plants
            for pp in pps:
                plant = pp.plant.get()
                name = plant.display_name
                self.chk_create(pgd, name, plant) 
                pgd[name]['reserved'] = pgd[name]['reserved'] + (pp.qty * rsv.num_reserved)
        
        return pgd
    
class Supplier(NDBBase):
    """ Represents the supplier of plants """
    name = ndb.StringProperty(required=True)
    
    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.supplier == self.key)

class PlantGrow(NDBBase):
    """ This is the class represents all plants that are available during a specific week """
    plant = ndb.KeyProperty(kind=Plant)
    finish_week = ndb.KeyProperty(kind=GrowWeek)
    actual = ndb.IntegerProperty(default=0)
    want_qty = ndb.IntegerProperty(default=0)
    
    @property
    def supplies(self):
        return PlantGrowSupply.query(PlantGrowSupply.plantgrow == self.key)
    
    
    @classmethod
    def get_plantgrow(cls, argPlant, argWeek):
        qry = PlantGrow.query().filter(PlantGrow.plant == ndb.Key(Plant,argPlant)).filter(PlantGrow.finish_week == ndb.Key(GrowWeek,argWeek))
        return qry.get()
    
    @classmethod
    def update_plantgrow(cls, plant_key, week_key, wanted, actual):
        resp = {'status':'success','msg':'PlantGrow Updated Successfully'}
        try:
            pg = PlantGrow.get_plantgrow(plant_key, week_key)
            if pg:
                pg.want_qty = int(wanted)
                pg.actual = int(actual)
                pg.put()
            else:
                resp = {'status':'failed','msg':'No record found to update'}
        except Exception as e:
            resp = {'status':'failed','msg': str(e)}
        return resp
    
class PlantGrowNotes(NDBBase):
    note = ndb.StringProperty(required=True)
    plant_grow = ndb.KeyProperty(kind=PlantGrow)
    
    @classmethod
    def get_notes(cls, plant_grow_key):
        qry = PlantGrowNotes.query().filter(PlantGrowNotes.plant_grow == ndb.Key(PlantGrow,int(plant_grow_key)))
        note_list = []
        for note in qry:
            note_list.append({'noteId':note.id,'note':note.note,'added_by':note.added_by.email(),'added_date':note.timestamp.strftime("%m/%d/%Y")})
        return note_list
    
    @classmethod
    def save_note(cls,note, plantgrow_key):
        pgn = PlantGrowNotes()
        pgn.note = note
        pgn.plant_grow = ndb.Key(PlantGrow,int(plantgrow_key))
            
        return pgn.update_resp()
    
    @classmethod
    def delete_note(cls, note_id):
        pgn = PlantGrowNotes.get_by_id(int(note_id))
        return pgn.delete_resp()
        
    
     
class PlantGrowSupply(NDBBase):
    ''' this class represents the supply of plants for a given week '''
    plantgrow = ndb.KeyProperty(kind=PlantGrow, required=True)
    supplier = ndb.KeyProperty(kind=Supplier, required=True)
    forecast = ndb.IntegerProperty(default=0)
    confirmation_num = ndb.StringProperty()
    cost = ndb.FloatProperty()
    
    @classmethod
    def update(cls,argId, argPlant, argWeek, argSupplier, argForecast=0, argConfirmation=None, argCost=0):
        pgs = PlantGrowSupply.get_by_id(int(argId))
        pg = PlantGrow.get_plantgrow(int(argPlant), int(argWeek))
        pgs.plantgrow = ndb.Key(PlantGrow,pg.id)
        pgs.supplier = ndb.Key(Supplier,int(argSupplier))
        pgs.forecast = int(argForecast)
        pgs.confirmation_num = str(argConfirmation)
        pgs.cost = int(argCost)
        return pgs.update_resp()
         
class Concept(NDBBase):
    """ many plants can be combined to create 1 concept """
    name = ndb.StringProperty(required=True)
    
    @property
    def product_concepts(self):
        return ProductConcept.query(ProductConcept == self.key)
    
    
class Product(NDBBase):
    ''' this is the product name for customers '''
    name = ndb.StringProperty(required=True)
    sale_price = ndb.FloatProperty(default=0.0)
    
    @property
    def product_concepts(self):
        return ProductConcept.query(ProductConcept.product == self.key)
    
    @property
    def product_reserve(self):
        return ProductReserve.query(ProductReserve.product == self.key)
    
    @property
    def product_plants(self):
        return ProductPlant.query(ProductPlant.product == self.key)
 
class ProductPlant(NDBBase):
    ''' this relates plants to products '''
    plant = ndb.KeyProperty(kind=Plant, required=True)
    product = ndb.KeyProperty(kind=Product, required=True)
    qty = ndb.IntegerProperty(default=1)  
   
class ProductConcept(NDBBase):
    concept = ndb.KeyProperty(kind=Concept)
    product = ndb.KeyProperty(kind=Product)
    
class ProductReserve(NDBBase):
    """ This is the plant that is being reserved by a customer """
    customer = ndb.KeyProperty(kind=Customer)
    finish_week = ndb.KeyProperty(kind=GrowWeek)
    product = ndb.KeyProperty(kind=Product)
    num_reserved = ndb.IntegerProperty(default=0)
    shipped = ndb.BooleanProperty()    
    
    @classmethod
    def update(cls,argId, argCustomer, argWeek, argProduct, argReserved=0, argShipped=False):
        pr = ProductReserve.get_by_id(long(argId))
        pr.customer = ndb.Key(Customer,int(argCustomer))
        pr.finish_week = ndb.Key(GrowWeek,int(argWeek))
        pr.product = ndb.Key(Product,int(argProduct))
        pr.num_reserved = int(argReserved)
        pr.shipped = pr.convert_bool(argShipped)
        return pr.update_resp()

class ProductReserveWrap():
    
    def __init__(self, product_reserve):
        self.pr = product_reserve
        self.plant_name = None
        self.plant_reserve = 0
        self.id = product_reserve.id
        
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