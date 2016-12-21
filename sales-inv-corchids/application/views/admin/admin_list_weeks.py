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
from application.models import GrowWeek,PlantGrow, ConceptReserveWrap
from application.models import ConceptPlant, ConceptReserve
from google.appengine.ext.db import Model,Query

from application.decorators import login_required
#from datetime import datetime


class AdminListWeeks(View):

    @login_required
    def dispatch_request(self):
        weeks = Query(GrowWeek)
        tday = datetime.date.today()
        d = datetime.timedelta(days=-14)
        t = tday + d
        weeks.filter('week_monday >= ',t)
        weeks.order('week_monday')
        form = WeekForm()
        errors = 0
        if form.validate_on_submit():
            week = GrowWeek(
                week_number=form.week_number.data,
                year=form.year.data,
                week_monday=form.week_monday.data
            )
            try:
                week.put()
                week_id = week.key.id()
                flash(u'Route %s successfully saved.' % week_id, 'success')
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
    
    def chk_create(self, din, name, plant, week):
        if name not in din.keys():
            din[name] = {'actual':0,'actual_qty':0,'forecast':0,'forecast_qty':0, 'reserved':0}
            din[name]['plant_key'] = plant.key()
            din[name]['week_key'] = week.key()
    
    @login_required
    def dispatch_request(self,week_id):
        week = Model.get(week_id)
        pgs = week.plantgrow
        rsvs = week.reserves
        
        pgd = {}
        for pg in pgs:
            name = pg.plant.display_name
            self.chk_create(pgd,name,pg.plant,week)            
            pgd[name]['actual'] = pgd[name]['actual'] + pg.actual
            pgd[name]['actual_qty'] = pgd[name]['actual_qty'] + pg.actual_qty
            pgd[name]['forecast'] = pgd[name]['forecast'] + pg.forecast
            pgd[name]['forecast_qty'] = pgd[name]['forecast_qty'] + pg.forecast_qty
        
        for rsv in rsvs:
            cplants = rsv.concept.concept_plants
            for cplant in cplants:
                name = cplant.plant.display_name
                self.chk_create(pgd, name, cplant.plant, week)
                pgd[name]['reserved'] = pgd[name]['reserved'] + \
                                         (cplant.qty * rsv.num_reserved)
            
        
        return render_template("show_week.html",week=week,plantgrows=pgd)

class AdminShowPlantWeek(View):
    
    @login_required
    def dispatch_request(self,week_id,plant_id):
        pg = Query(PlantGrow)
        week = Model.get(week_id)
        plant = Model.get(plant_id)
        pg.filter('plant = ',plant)
        pg.filter('finish_week = ',week)
        
        cps = Query(ConceptPlant)
        cps.filter('plant = ',plant)
        cr_list = []
        for cp in cps:
            crs = Query(ConceptReserve)
            crs.filter('concept = ',cp.concept)
            crs.filter('finish_week = ',week)
            for cr in crs:
                crw = ConceptReserveWrap(cr)
                crw.plant_name = plant.display_name
                crw.incr_plant(cp.qty * crw.cr.num_reserved)
                cr_list.append(crw)
            
        return render_template("show_plantweek.html",week=week, plant=plant, pweeks=pg, creserve=cr_list)
        
        