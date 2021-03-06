"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app

from application.views.public.public_warmup import PublicWarmup
from application.views.public.public_index import PublicIndex
from application.views.public.public_say_hello import PublicSayHello

from application.views.admin.admin_main import AdminInvHome,AdminLogout
#from application.views.admin.admin_list_examples_cached import AdminListExamplesCached
from application.views.admin.admin_secret import AdminSecret, AdminUpdate
from application.views.admin.admin_list_weeks import AdminListWeeks,AdminShowWeek,AdminShowPlantWeek, AdminEditCreateProduct


# URL dispatch rules

# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'public_warmup', view_func=PublicWarmup.as_view('public_warmup'))

app.add_url_rule('/', 'public_index', view_func=PublicIndex.as_view('public_index'))
app.add_url_rule('/hello/<username>', 'public_say_hello', view_func=PublicSayHello.as_view('public_say_hello'))
app.add_url_rule('/logout', 'logout', view_func=AdminLogout.as_view("logout"))
app.add_url_rule('/sales_inventory', 'inv_home',view_func=AdminInvHome.as_view('inv_home'))

app.add_url_rule('/weeks', 'list_weeks', view_func=AdminListWeeks.as_view('list_weeks'), methods=['GET', 'POST'])
app.add_url_rule('/week/<int:week_id>',view_func=AdminShowWeek.as_view('show_week'), methods=['GET','POST'])
app.add_url_rule('/plantweek/<int:plantgrow_id>',view_func=AdminShowPlantWeek.as_view("show_plantweek"), methods=['GET','POST'])
app.add_url_rule('/Product/<int:product_id>',view_func=AdminEditCreateProduct.as_view("edit_product"), methods=['GET','POST'])
app.add_url_rule('/admin_only', 'admin_only', view_func=AdminSecret.as_view('admin_only'), methods=['GET', 'POST'])
app.add_url_rule('/admin_update', 'admin_update',view_func=AdminUpdate.as_view('admin_update'), methods=['GET','POST'])

# Error handlers

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
