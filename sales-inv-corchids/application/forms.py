"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

#from flaskext import wtf
#from wtforms.form import Form
#from wtforms.fields import TextField,TextAreaField
from wtforms import fields
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.ext.appengine.ndb import model_form as mf1

from application.models import RouteEntryMain,RouteStops,GrowWeek,PlantGrowSupply


class RestUserAdd(FlaskForm):
    username = fields.TextField("username",validators=[DataRequired()])
    password = fields.PasswordField("password",validators=[DataRequired()])

class RouteEntry(FlaskForm):
    route_date = fields.DateField("route_date",validators=[DataRequired()])
    operator_name = fields.TextField("operator_name",validators=[DataRequired()])
    operator_pay = fields.FloatField('operator_pay', validators=[DataRequired()])
    hotel_expenses = fields.FloatField('hotel_expenses')
    fuel_expenses = fields.FloatField('fuel_expenses')
    fuel_gallons = fields.FloatField('fuel_gallons')
    total_miles = fields.FloatField('total_miles')
    total_hours = fields.FloatField('total_hours')

# App Engine ndb model form example
RouteForm = mf1(RouteEntryMain, FlaskForm, field_args={
    'route_date_start' : dict(validators=[DataRequired()],label="Start Date"),
    'route_date_end' : dict(validators=[DataRequired()],label="End Date"),
    'operator_name' : dict(validators=[DataRequired()]),
    'operator_pay' : dict(validators=[DataRequired()])
    #'example_name': dict(validators=[DataRequired()]),
    #'example_description': dict(validators=[DataRequired()]),
})

WeekForm = mf1(GrowWeek, FlaskForm, 
            field_args={
                'week_number' : dict(validators=[DataRequired()]),
                'year' : dict(validators=[DataRequired()])  })

PlantGrowSupplyForm = mf1(PlantGrowSupply, FlaskForm)

StopForm = mf1(RouteStops, FlaskForm, field_args={
    'stop_ship_to': dict(validators=[DataRequired()],label='Ship To'),
    'stop_load': dict(validators=[DataRequired()],label='Percent Load'),
    'stop_name':dict(label='Name'),'stop_zip':dict(label='Zip Code'),
    'stop_dist':dict(label='Distance'),'stop_pallets':dict(label='Num Pallets'),
    'stop_ret_carts':dict(label='Num Return Carts'),'stop_carts':dict(label='Num Carts')})
