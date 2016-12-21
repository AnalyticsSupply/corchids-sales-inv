# -*- coding: utf-8 -*-

from flask.views import View

from flask import flash, redirect, url_for, request

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from models import RouteEntryMain

from decorators import login_required


class AdminDeleteExample(View):

    @login_required
    def dispatch_request(self, route_id):
        route = RouteEntryMain.get_by_id(route_id)
        if request.method == "POST":
            try:
                route.key.delete()
                flash(u'Route %s successfully deleted.' % route_id, 'success')
                return redirect(url_for('list_routes'))
            except CapabilityDisabledError:
                flash(u'App Engine Datastore is currently in read-only mode.', 'info')
                return redirect(url_for('list_routes'))
