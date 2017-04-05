'''
Created on Mar 28, 2017

@author: jason
'''
from datetime import datetime
from datetime import timedelta

from application import db
from application.models import ProductReserve, GrowWeek, PlantGrowSupply, PlantGrow,LastUpdate

def get_reserves():
    lstup = LastUpdate.get_last_update("PlantReserves")
    prs = ProductReserve.get_lastupdated(lstup.last_updated)
    summ_d = []
    for pr in prs:
        presv = ProductReserve.get_db_reserve(pr.id)
        summ_d.append({'week_id':presv['week_id'],'plant_id':presv['plant_id']})
        add_reserves(presv)
    
    for summ in summ_d:
        getadd_summary(summ['week_id'], summ['plant_id'])
        
    lstup.update()
    return 0

def add_reserves(presv):
    instance = db.session.query(PlantReserves).filter_by(id=presv['_id']).first()
    if instance:
        del presv['_id']
        instance.update(**presv)
    else:
        instance = PlantReserves(**presv)
        db.session.add(instance)
    db.session.commit()
    

class PlantReserves(db.Model):
    __tablename__ = 'plant_reserves'
    id = db.Column(db.String(150), primary_key=True)
    plant = db.Column(db.String(150))
    product = db.Column(db.String(150))
    plant_id = db.Column(db.String(150))
    product_id = db.Column(db.String(150))
    num_reserved = db.Column(db.String(150))
    week_id = db.Column(db.String(150))
    customer = db.Column(db.String(150))
    customer_id = db.Column(db.String(150))
    sales_rep = db.Column(db.String(150))
    add_date = db.Column(db.String(150))
    
    def udate(self, plant, product, plant_id, product_id, num_reserved, week_id, customer, customer_id, sales_rep, add_date):
        self.plant=plant
        self.product=product
        self.plant_id=plant_id
        self.product_id=product_id
        self.num_reserved=num_reserved
        self.week_id=week_id
        self.customer=customer
        self.customer_id=customer_id
        self.sales_rep=sales_rep
        self.add_date=add_date
        
    def __init__(self, _id, plant, product, plant_id, product_id, num_reserved, week_id, customer, customer_id, sales_rep, add_date):
        self.id = _id
        self.plant=plant
        self.product=product
        self.plant_id=plant_id
        self.product_id=product_id
        self.num_reserved=num_reserved
        self.week_id=week_id
        self.customer=customer
        self.customer_id=customer_id
        self.sales_rep=sales_rep
        self.add_date=add_date

def set_next_2yrs():
    dt = datetime.now()
    dt2 = dt + timedelta(days=(365*2))
    dt1 = dt
    while dt1 <= dt2:
        add_date(dt1)
        dt1 = dt1 + timedelta(days=1)    

def add_date(dt_entry):
    dwdb = {}
    dwdb['_id'] = str(dt_entry.timetuple().tm_yday).zfill(3)+str(dt_entry.year)
    dwdb['date_entry'] = dt_entry
    week = GrowWeek.create_week(dt_entry)
    dwdb['week_id'] = week.id
    instance = db.session.query(DateWeek).filter_by(id=dwdb['_id']).first()
    if not instance:
        instance = DateWeek(**dwdb)
        db.session.add(instance)
        db.session.commit()

class DateWeek(db.Model):
    __tablename__ = 'date_week'
    id = db.Column(db.String(150), primary_key=True)
    date_entry = db.Column(db.String(150))
    week_id = db.Column(db.String(150))
    
    def update(self, date_entry, week_id):
        self.date_entry = date_entry
        self.week_id = week_id
    
    def __init__(self, _id, date_entry, week_id):
        self.id = _id
        self.date_entry = date_entry
        self.week_id = week_id

def get_supply():
    lstup = LastUpdate.get_last_update("PlantSupplies")
    summ_d = []
    pgss = PlantGrowSupply.get_lastupdated(lstup.last_updated)
    for pgs in pgss:
        pgsdb = PlantGrowSupply.get_supply(pgs.id)
        summ_d.append({'week_id':pgsdb['week_id'],'plant_id':pgsdb['plant_id']})
        add_supply(pgsdb)
    
    for summ in summ_d:
        getadd_summary(summ['week_id'], summ['plant_id'])
    
    lstup.update()
    return 0

def add_supply(pgsdb):
    instance = db.session.query(PlantSupplies).filter_by(id=pgsdb['_id']).first()
    if instance:
        del pgsdb['_id']
        instance.update(**pgsdb)
    else:
        instance = PlantSupplies(**pgsdb)
        db.session.add(instance)
    db.session.commit()
    
class PlantSupplies(db.Model):
    __tablename__ = 'plant_supplies'
    id = db.Column(db.String(150), primary_key=True)
    supplier = db.Column(db.String(150))
    supplier_id = db.Column(db.String(150))
    forecast = db.Column(db.String(150))
    week_id = db.Column(db.String(150))
    add_date = db.Column(db.String(150))
    plant = db.Column(db.String(150))
    plant_id = db.Column(db.String(150))
    
    def update(self,supplier, supplier_id, forecast, week_id, add_date, plant, plant_id):
        self.supplier=supplier
        self.supplier_id=supplier_id
        self.forecast=forecast
        self.week_id=week_id
        self.add_date=add_date
        self.plant=plant
        self.plant_id=plant_id
        
    def __init__(self, _id, supplier, supplier_id, forecast, week_id, add_date, plant, plant_id):
        self.id = _id
        self.supplier=supplier
        self.supplier_id=supplier_id
        self.forecast=forecast
        self.week_id=week_id
        self.add_date=add_date
        self.plant=plant
        self.plant_id=plant_id

def get_summary():
    lstup = LastUpdate.get_last_update("PlantSummary")
    pgs = PlantGrow.get_lastupdated(lstup.last_updated)
    for pg in pgs:
        add_summary(pg.pg_summary())
    lstup.update()
    return 0

def getadd_summary(week_id, plant_id):
    pg = PlantGrow.plant_summary(week_id, plant_id)
    add_summary(pg)
        
def add_summary(pg):
    instance = db.session.query(PlantSummary).filter_by(id=pg['_id']).first()
    if instance:
        del pg['_id']
        instance.update(**pg)
    else:
        instance = PlantSummary(**pg)
        db.session.add(instance)
    db.session.commit()
    
class PlantSummary(db.Model):
    __tablename__ = 'plant_summary'
    id = db.Column(db.String(150), primary_key=True)
    plant = db.Column(db.String(150))
    plant_id = db.Column(db.String(150))
    week_id = db.Column(db.String(150))
    num_reserved = db.Column(db.String(150))
    forecast = db.Column(db.String(150))
    actual = db.Column(db.String(150))
    
    def update(self, plant, plant_id, week_id, num_reserved, forecast, actual):
        self.plant=plant
        self.plant_id=plant_id
        self.week_id=week_id
        self.num_reserved=num_reserved
        self.forecast=forecast
        self.actual=actual
        
    def __init__(self, _id, plant, plant_id, week_id, num_reserved, forecast, actual):
        self.id=_id
        self.plant=plant
        self.plant_id=plant_id
        self.week_id=week_id
        self.num_reserved=num_reserved
        self.forecast=forecast
        self.actual=actual

def get_date():
    lstUp = LastUpdate.get_last_update('Weeks')
    wks = GrowWeek.get_lastupdated(lstUp.last_updated)
    for wk in wks:
        add_week(wk)
    lstUp.update()
    return 0

def add_week(gw):
    #gw = GrowWeek.get_by_id(week_id)
    week={}
    week['_id'] = gw.id
    week['week_number'] = gw.week_number
    week['year'] = gw.year
    week['monday_date'] = gw.week_monday
    instance = db.session.query(Weeks).filter_by(id=week['_id']).first()
    if instance:
        del week['_id']
        #instance.update(**week)
        #db.session.commit()
    else:
        instance = Weeks(**week)
        db.session.add(instance)
        db.session.commit()

class Weeks(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.String(150), primary_key=True)
    week_number = db.Column(db.String(150))
    year = db.Column(db.String(150))
    monday_date = db.Column(db.DateTime())
    
    def update(self, week_number, year, monday_date):
        self.week_number=week_number
        self.year=year
        self.monday_date=monday_date
        
    def __init__(self, _id, week_number, year, monday_date):
        self.id=_id
        self.week_number=week_number
        self.year=year
        self.monday_date=monday_date