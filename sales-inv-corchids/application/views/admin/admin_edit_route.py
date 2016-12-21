# -*- coding: utf-8 -*-

from flask.views import View

from flask import flash, redirect, url_for, render_template, request

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from forms import StopForm, RouteForm
from models import RouteEntryMain, RouteStops

from decorators import login_required

from datetime import datetime

class AdminEditExample(View):

    @login_required
    def dispatch_request(self, route_id):
        route = RouteEntryMain.get_by_id(route_id)
        form = RouteForm(obj=route)
        if request.method == "POST":
            if form.validate_on_submit():
                route.route_date_start = form.data.get('route_date_start')
                route.route_date_end = form.data.get('route_date_end')
                route.operator_name = form.data.get('operator_name')
                route.operator_pay = form.data.get('operator_pay')
                route.operator_pay=form.operator_pay.data
                route.hotel_expenses=form.hotel_expenses.data
                route.fuel_expenses=form.fuel_expenses.data
                route.fuel_gallons=form.fuel_gallons.data
                route.total_miles=form.total_miles.data
                route.total_hours=form.total_hours.data
                route.up_timestamp = datetime.now()
                route.put()
                flash(u'Route %s successfully saved.' % route_id, 'success')
                return redirect(url_for('show_route',route_id=route_id))
        return render_template('edit_route.html', route=route, form=form)


class AdminEditStop(View):

    @login_required
    def dispatch_request(self, route_id, stop_id):
        route = RouteEntryMain.get_by_id(route_id)
        stop = RouteStops.get_by_id(stop_id, parent = route.key)
        form = StopForm(obj=stop)
        if request.method == "POST":
            if form.validate_on_submit():
                stop.stop_name=form.stop_name.data
                stop.stop_ship_to=form.stop_ship_to.data
                stop.stop_zip=form.stop_zip.data
                stop.stop_dist=form.stop_dist.data
                stop.stop_load=form.stop_load.data
                stop.stop_pallets=form.stop_pallets.data
                stop.stop_ret_carts=form.stop_ret_carts.data
                stop.stop_carts=form.stop_carts.data
                stop.up_timestamp=datetime.now()
                stop.put()
                flash(u'Stop %s successfully saved.' % stop_id, 'success')
                return redirect(url_for('show_route',route_id=route.key.id()))
        return render_template('edit_stop.html', route=route,stop=stop, form=form)

class AdminDeleteStop(View):
    @login_required
    def dispatch_request(self, route_id, stop_id):
        route = RouteEntryMain.get_by_id(route_id)
        stop = RouteStops.get_by_id(stop_id, parent = route.key)
        if request.method == "POST":
            try:
                stop.key.delete()
                flash(u'Stop %s successfully deleted.' % stop_id, 'success')
                return redirect(url_for('show_route',route_id=route_id))
            except CapabilityDisabledError:
                flash(u'App Engine Datastore is currently in read-only mode.', 'info')
                return redirect(url_for('show_route',route_id=route_id))

class AdminShowExample(View):
     
    @login_required
    def dispatch_request(self, route_id):
        route = RouteEntryMain.get_by_id(route_id)
        stopQ = RouteStops.query(ancestor=route.key)
        show_form = "no"
       # stopQ.ancestor(route)
        stops = stopQ.fetch()
        form = StopForm()
        #form.stop_name.data = '<enter name>'
        if form.validate_on_submit():
            stop = RouteStops(
                stop_name=form.stop_name.data,
                stop_ship_to=form.stop_ship_to.data,
                stop_zip=form.stop_zip.data,
                stop_dist=form.stop_dist.data,
                stop_load=form.stop_load.data,
                stop_pallets=form.stop_pallets.data,
                stop_ret_carts=form.stop_ret_carts.data,
                stop_carts=form.stop_carts.data,
                timestamp=datetime.now(),
                up_timestamp=datetime.now(),
                parent=route.key)
            try:
                stop.put()
                stop_id = stop.key.id()
                flash(u'Stop %s successfully added.' % stop_id, 'success')
                return redirect(url_for('show_route',route_id=route.key.id(),form=form,stops=stops))
            except CapabilityDisabledError:
                flash(u'App Engine Datastore is currentl in read_only mode.','info')
                return redirect(url_for('show_route',route_id=route.key.id(),form=form,stops=stops))
        else:
            if request.method == 'POST':
                show_form = "#new-stop-modal"
        return render_template('show_route.html',route=route,form=form,stops=stops,show_form=show_form)