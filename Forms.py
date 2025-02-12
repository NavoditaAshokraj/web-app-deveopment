from wtforms import Form, StringField, SelectField, TextAreaField, IntegerField, DateField, FloatField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Email
from flask_wtf import FlaskForm


class FeedbackForm(FlaskForm):
    full_name = StringField('Full Name', [Length(min=1, max=150), DataRequired()])
    email = StringField('Email Address', [Length(min=1, max=150), DataRequired(), Email()])
    rate = IntegerField('Rating', validators=[NumberRange(min=1, max=5)], default=0)
    remarks = TextAreaField('Message', [Optional()])

class BookingForm(FlaskForm):
    purpose = SelectField(
        'Purpose of visit',
        choices=[
            ('Medical Check Up', 'Medical Check Up'),
            ('Medical Test', 'Medical Test'),
            ('Health Screening', 'Health Screening'),
            ('Vaccination', 'Vaccination')
        ],
        validators=[DataRequired()]
    )
    date = DateField('Date of visit', format='%Y-%m-%d', validators=[DataRequired()])
    time = SelectField('Time slot', [DataRequired()], choices=[
            ('0900', '9:00 AM - 10:00 AM'),
            ('1000', '10:00 AM - 11:00 AM'),
            ('1100', '11:00 AM - 12:00 PM'),
            ('1300', '1:00 PM - 2:00 PM'),
            ('1400', '2:00 PM - 3:00 PM')])
    location = SelectField('Location',[DataRequired()], choices=[
            ('Yishun', 'Yishun'),
            ('Punggol', 'Punggol'),
            ('Bukit Panjang', 'Bukit Panjang')])
    remarks = TextAreaField('Comments', [Optional()])

class ContactForm(FlaskForm):
    full_name = StringField('Full Name', [Length(min=1, max=150), DataRequired()])
    email = StringField('Email Address', [Length(min=1, max=150), DataRequired(), Email()])
    Subject = SelectField(
        'Subject',
        choices=[
            ('General Enquiry', 'General Enquiry'),
            ('Corporate Enquiry', 'Corporate Enquiry')
        ],
        validators=[Optional()]
    )
    remarks = TextAreaField('Message', [Optional()])

class MedicineForm(FlaskForm):
    name = StringField('Name', [Length(min=1, max=150), DataRequired()])
    price = FloatField('Price', validators=[NumberRange(min=1, max=5)], default=0)
    count = IntegerField('Count', validators=[NumberRange(min=1, max=100)], default=0)
