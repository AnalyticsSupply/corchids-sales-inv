"""
models.py

App Engine datastore models

"""

from math import floor
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
    
    def get_products(self):
        pp = self.products
        prds = []
        for p in pp:
            prds.append(p.product.get())
            
        return prds
    
    
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
    def next_week(self):
        nxtWk = self.week_number + 1
        nxtYr = self.year
        
        if nxtWk > 52:
            nxtWk = 1
            nxtYr = self.year+1
        
        qry = GrowWeek.query(GrowWeek.week_number == nxtWk).filter(GrowWeek.year==nxtYr)
        return qry.get() 
    
    @property
    def prior_week(self):
        nxtWk = self.week_number - 1
        nxtYr = self.year
        
        if nxtWk == 0:
            nxtWk = 52
            nxtYr = self.year-1
        
        qry = GrowWeek.query(GrowWeek.week_number == nxtWk).filter(GrowWeek.year==nxtYr)
        return qry.get()
   
    @property
    def plantgrow(self):
        return PlantGrow.query(PlantGrow.finish_week == self.key)
    
    @property 
    def reserves(self):
        return ProductReserve.query(ProductReserve.finish_week == self.key)
    
    def chk_create(self, din, name, plant):
        if name not in din.keys():
            din[name] = {'wanted':0,'actual':0,'forecast':0, 'reserved':0, 'notes':0}
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
            pgd[name]['notes'] = len(PlantGrowNotes.get_notes(pg.id))
            #pgd[name]['available'] = pgd[name]['available'] + pg.want_qty
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
                
            
        for key in pgd.keys():
            pgd[key]['available'] = pgd[key]['forecast'] - pgd[key]['reserved']
            if pgd[key]['actual'] > 0:
                pgd[key]['available'] = pgd[key]['actual'] - pgd[key]['reserved']
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
    def next(self):
        qry = PlantGrow.query(PlantGrow.plant == self.plant).filter(PlantGrow.finish_week == self.finish_week.get().next_week.key)
        return qry.get()
    
    @property
    def prior(self):
        qry = PlantGrow.query(PlantGrow.plant == self.plant).filter(PlantGrow.finish_week == self.finish_week.get().prior_week.key)
        return qry.get()
    
    @property
    def supplies(self):
        return PlantGrowSupply.query(PlantGrowSupply.plantgrow == self.key)
    
    @property
    def forecasts(self):
        supps = self.supplies
        fcast = 0
        for supp in supps:
            fcast = fcast + supp.forecast
        return fcast
    
    @property
    def reserves(self):
        prds = self.plant.get().products
        resv = 0
        for prd in prds:
            p = prd.product.get()
            pr = p.get_plant_reserved(self.finish_week,self.plant)
            resv = resv + pr
        
        
        return resv
    
    
    def availability(self):
        rsvs = self.reserves
        fcast = self.forecasts
        if self.actual > 0:
            return self.actual - rsvs
        
        return fcast - rsvs
        
    
    @classmethod
    def get_plantgrow(cls, argPlant, argWeek):
        qry = PlantGrow.query().filter(PlantGrow.plant == ndb.Key(Plant,argPlant)).filter(PlantGrow.finish_week == ndb.Key(GrowWeek,argWeek))
        return qry.get()
    
    @classmethod
    def update_plantgrow(cls, plant_key, week_key, actual):
        resp = {'status':'success','msg':'PlantGrow Updated Successfully'}
        try:
            pg = PlantGrow.get_plantgrow(plant_key, week_key)
            if pg:
                #pg.want_qty = int(wanted)
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
    image = ndb.StringProperty()
    qty_per_case = ndb.IntegerProperty()
    box_height = ndb.StringProperty()
    box_width = ndb.StringProperty()
    box_length = ndb.StringProperty()
    ti = ndb.IntegerProperty()
    hi = ndb.IntegerProperty()
    
    @property
    def product_concepts(self):
        return ProductConcept.query(ProductConcept.product == self.key)
    
    @property
    def product_reserve(self):
        return ProductReserve.query(ProductReserve.product == self.key)
    
    @property
    def product_plants(self):
        return ProductPlant.query(ProductPlant.product == self.key)
    
    def get_qty_available(self, finish_week, plant=None):
        resv = self.get_reserved(finish_week)
        pp_avail = []
        pp_qry = ProductPlant.query(ProductPlant.product == self.key)
        if plant:
            pp_qry.filter(ProductPlant.plant == plant)
            
        for pp in pp_qry:
            pp_resv = pp.qty * resv
            pp_avail.append(floor(self.get_actual(finish_week, pp.plant)/pp_resv))
            
        return min(pp_avail)
    
    def get_actual(self, finish_week, plant):
        return PlantGrow.query(PlantGrow.plant == plant, PlantGrow.finish_week == finish_week).get().actual
        
    def get_reserved(self, finish_week):
        num_reserved = 0
        pr_qry = ProductReserve.query(ProductReserve.product == self.key).filter(ProductReserve.finish_week == finish_week)
        
        for pr in pr_qry:
            num_reserved = num_reserved + pr.num_reserved
            
        return num_reserved
    
    def get_plant_reserved(self, finish_week, plant):
        resv = self.get_reserved(finish_week)
        pp = ProductPlant.query(ProductPlant.product == self.key).filter(ProductPlant.plant == plant).get()
        return pp.qty * resv
    
class ProductNotes(NDBBase):
    note = ndb.StringProperty(required=True)
    product = ndb.KeyProperty(kind=Product)
    
    @classmethod
    def get_notes(cls, product_key):
        qry = Product.query().filter(ProductNotes.product == ndb.Key(Product,int(product_key)))
        note_list = []
        for note in qry:
            note_list.append({'noteId':note.id,'note':note.note,'added_by':note.added_by.email(),'added_date':note.timestamp.strftime("%m/%d/%Y")})
        return note_list
    
    @classmethod
    def save_note(cls,note, product_key):
        pgn = ProductNotes()
        pgn.note = note
        pgn.product = ndb.Key(Product,int(product_key))
            
        return pgn.update_resp()
    
    @classmethod
    def delete_note(cls, note_id):
        pgn = ProductNotes.get_by_id(int(note_id))
        return pgn.delete_resp()
 
class ProductPlant(NDBBase):
    ''' this relates plants to products '''
    plant = ndb.KeyProperty(kind=Plant, required=True)
    product = ndb.KeyProperty(kind=Product, required=True)
    qty = ndb.IntegerProperty(default=1)  
   
class CurrentDeal(NDBBase):
    ''' this is a product that is designed to help sell a plant that is overstocked '''
    product = ndb.KeyProperty(kind=Product,required=True)
    
    @property
    def qty_available(self):
        qry = CurrentDealWeeks.query(CurrentDealWeeks.current_deal == self.key)
        qty = 0
        for cdw in qry:
            cqty = self.product.get().get_qty_available(cdw.finish_week)
            qty = qty + cqty
            
        return qty
    
    def get_current_deal(self):
        resp = {}
        p = self.product.get()
        resp['name'] = p.name
        resp['sale_price'] = p.sale_price
        resp['image'] = p.image
        resp['qty_per_case'] = p.qty_per_case
        resp['box_height'] = p.box_height
        resp['box_width'] = p.box_width
        resp['ti'] = p.ti
        resp['hi'] = p.hi
        
        resp['weeks'] = []
        
        cdw_qry = CurrentDealWeeks.query(CurrentDealWeeks.product == self.key)
        
        for cdw in cdw_qry:
            wk_resp = {}
            fw = cdw.finish_week.get()
            wk_resp['year'] = fw.year
            wk_resp['week_number'] = fw.week_number
            wk_resp['week_monday'] = fw.week_monday
            wk_resp['qty_available'] = p.get_qty_available(fw.key)
            resp['weeks'].append(wk_resp)
            
        return resp
            
    
    @classmethod
    def get_current_deals(cls):
        qry = CurrentDeal.query()
        
        resp = []
        for cd in qry:
            resp.append(cd.get_current_deal())
                
        return resp
            
    
class CurrentDealWeeks(NDBBase):
    current_deal = ndb.KeyProperty(kind=CurrentDeal,required=True)
    finish_week = ndb.KeyProperty(kind=GrowWeek,required=True)
    
    
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