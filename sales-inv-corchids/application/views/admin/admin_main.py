# -*- coding: utf-8 -*-

from flask.views import View

from flask import flash, redirect, url_for, render_template, request

from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from decorators import login_required
from datetime import datetime


class AdminInvHome(View):

    @login_required
    def dispatch_request(self):
        return render_template('inv_home.html')
    
class AdminLogout(View):
    
    @login_required
    def dispatch_request(self):
        return redirect(users.create_logout_url(url_for('inv_home')))
