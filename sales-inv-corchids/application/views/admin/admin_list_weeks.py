'''
Created on Dec 19, 2016

@author: jason
'''
# -*- coding: utf-8 -*-

from flask.views import View
import datetime
from flask import flash, redirect, url_for, render_template, request

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from application.forms import WeekForm
from application.models import GrowWeek,PlantGrow, ProductReserveWrap, Supplier, Customer
from application.models import ProductPlant, ProductReserve,Plant,Product
from google.appengine.ext.ndb import Model,Query,Key

from application.decorators import login_required, admin_required
#from datetime import datetime


class AdminListWeeks(View):

    @login_required
    def dispatch_request(self):
        weeks = GrowWeek.query().order(GrowWeek.week_monday)
        tday = datetime.date.today()
        d = datetime.timedelta(days=-14)
        t = tday + d
        weeks = weeks.filter(GrowWeek.week_monday >= t)
        #weeks.order(GrowWeek.week_monday)
        form = WeekForm()
        errors = 0
        if form.validate_on_submit():
            week = GrowWeek(
                week_number=form.week_number.data,
                year=form.year.data,
                week_monday=form.week_monday.data
            )
            try:
                week.update_ndb()
                week_id = week.key.id()
                flash(u'Week %s successfully saved.' % week_id, 'success')
                #return redirect(url_for('show_route',week_id=week_id))
                return redirect(url_for('list_weeks'))
            except CapabilityDisabledError:
                flash(u'App Engine Datastore is currently in read-only mode.', 'info')
                return redirect(url_for('list_weeks'))
        else:
            if request.method == 'POST':
                errors = 1
        return render_template('list_weeks.html', weeks=weeks, form=form,errors=errors)


class AdminShowWeek(View):
    
    @login_required
    def dispatch_request(self,week_id):
        week = Key(GrowWeek,week_id).get()
        pgd = week.week_summary()
        
        return render_template("show_week.html",week=week,plantgrows=pgd)
    
class AdminEditCreateProduct(View):
    
    @admin_required
    def dispatch_request(self, product_id):
        product = None
        if product_id == 11111:  # we'll use this to symbolize a new entry
            product = Product()
            product.name = ""
            product.put()
            product_id = product.id
        else:
            product = Product.get_by_id(product_id)
        concepts = product.product_concepts
        plants = product.product_plants
        return render_template("edit_new_product.html",productId=product_id, product=product, concepts=concepts, plants=plants)

class AdminShowPlantWeek(View):
    
    @login_required
    def dispatch_request(self,plantgrow_id):
        suppliers = Supplier.query()
        customers = Customer.query()
        
        
        pg = PlantGrow.get_by_id(int(plantgrow_id))
        #week = Key(GrowWeek,week_id)
        #plant = Key(Plant,plant_id)
        #pg = pg.filter(PlantGrow.plant == plant)
        #pg = pg.filter(PlantGrow.finish_week == week)   
        #pweeks = pg.get()
        
        plant = pg.plant.get()
        products = plant.get_products()
        week = pg.finish_week.get()
        avail = pg.availability()
        
        nxt = pg.next
        prior = pg.prior
        
            
        pps = ProductPlant.query()
        pps = pps.filter(ProductPlant.plant == plant.key)
        cr_list = []
        for pp in pps:
            crs = ProductReserve.query()
            crs = crs.filter(ProductReserve.product == pp.product)
            crs = crs.filter(ProductReserve.finish_week == week.key)
            crs = crs.filter(ProductReserve.soft_delete == False)
            
            for cr in crs:
                crw = ProductReserveWrap(cr)
                crw.plant_name = plant.display_name
                crw.incr_plant(pp.qty * crw.pr.num_reserved)
                cr_list.append(crw)
            
        return render_template("show_plantweek.html",week=week, plant=plant, pweeks=pg.supplies, plantgrow = plantgrow_id,
                               creserve=cr_list,suppliers=suppliers, customers=customers,products=products,next=nxt.id, prior=prior.id, availability=avail)
        
        