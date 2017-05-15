# -*- coding: utf-8 -*-

from flask.views import View

from flask import flash, redirect, url_for, render_template, request

from application.decorators import admin_required

from application.forms import RestUserAdd

from application.standard_models import User


class AdminSecret(View):

    @admin_required
    def dispatch_request(self):
        form = RestUserAdd()
        if request.method == "POST":
            if form.validate_on_submit():
                u = form.data.get("username")
                p = form.data.get("password")
                user = User(u,p).get_model()
                user.put()
                flash(u'Rest User successfully saved.', 'success')
                return redirect(url_for('inv_home'))
        return render_template('register.html', form=form)


class AdminUpdate(View):
    
    @admin_required
    def dispatch_request(self):
        model_list = ['Plant','Customer','Supplier','Concept','Product']
        return render_template('update_backend.html',models=model_list)