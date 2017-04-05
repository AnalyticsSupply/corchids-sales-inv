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

from application.models import GrowWeek,PlantGrowSupply


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


WeekForm = mf1(GrowWeek, FlaskForm, 
            field_args={
                'week_number' : dict(validators=[DataRequired()]),
                'year' : dict(validators=[DataRequired()])  })

PlantGrowSupplyForm = mf1(PlantGrowSupply, FlaskForm)

