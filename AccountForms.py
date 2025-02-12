from wtforms import Form, StringField, IntegerField, RadioField, SelectField, TextAreaField, \
    validators, PasswordField, SubmitField, ValidationError
import calendar, re

# ALl forms for Account Management


def custom_email_validator(form, field):
    email_validator = validators.Email(message="Invalid email address.")
    try:
        email_validator(form, field)
    except ValidationError:
        raise ValidationError("Please enter a valid email address.")


def is_numeric(form, field):
    if not field.data.isdigit():
        raise ValidationError(f'Must contain only numbers.')
    return is_numeric


def is_alnum(form, field):
    if not field.data.isalnum():
        raise ValidationError(f'Must contain only alphanumeric.')
    return is_alnum


def length_validator(min_length, max_length):
    def _length_validator(form, field):
        if not (min_length <= len(field.data) <= max_length):
            if min_length == max_length:
                raise ValidationError(f'Must be {min_length} characters long.')
            else:
                raise ValidationError(f'Must be between {min_length} and {max_length} characters long.')
    return _length_validator


def strong_password_validator(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError("Must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Must contain at least one special character.")


class CreateUserForm(Form):
    name = StringField('Full Name', [length_validator(1, 150), validators.DataRequired()])
    nric = StringField('NRIC', [length_validator(9, 9), validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired(),
                                                     strong_password_validator])
    confirm = PasswordField('Confirm Password', validators=[validators.EqualTo('password', 'Password mismatch')])
    email = StringField('Email Address', validators=[validators.DataRequired(), custom_email_validator])
    number = StringField('Mobile No.', validators=[length_validator(8, 8), validators.DataRequired(),
                                                   is_numeric])
    day = IntegerField('Day', validators=[validators.DataRequired(), validators.NumberRange(min=1, max=31)])
    month = SelectField('Month', choices=[(str(i), calendar.month_name[i]) for i in range(1, 13)])
    year = IntegerField('Year', validators=[validators.DataRequired(), validators.NumberRange(min=1900, max=2024)])
    street_name = StringField('Street Address', validators=[validators.DataRequired()])
    block_number = StringField('Block/House No.', validators=[validators.DataRequired(), is_alnum])
    unit_number = StringField('Unit No.', validators=[validators.DataRequired(), length_validator(1, 10)])
    postal_code = StringField('Postal Code', validators=[validators.DataRequired(), length_validator(6, 6),
                                                         is_numeric])


class LoginForm(Form):
    email = StringField('Email Address', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    submit = SubmitField('Login')


class StaffLogin(Form):
    staff_id = StringField('Staff ID')
    password = PasswordField('Password')
    submit = SubmitField('Login')


class UpdateUserForm(Form):
    name = StringField('Full Name', [length_validator(1, 150), validators.DataRequired()])
    nric = StringField('NRIC', [length_validator(9, 9), validators.DataRequired()])
    email = StringField('Email Address', validators=[validators.DataRequired(), custom_email_validator])
    number = StringField('Mobile No.', validators=[length_validator(8, 8), validators.DataRequired(),
                                                   is_numeric])
    day = IntegerField('Day', validators=[validators.DataRequired(), validators.NumberRange(min=1, max=31)])
    month = SelectField('Month', choices=[(str(i), calendar.month_name[i]) for i in range(1, 13)])
    year = IntegerField('Year', validators=[validators.DataRequired(), validators.NumberRange(min=1900, max=2024)])
    street_name = StringField('Street Address', validators=[validators.DataRequired()])
    block_number = StringField('Block/House No.', validators=[validators.DataRequired(), is_alnum])
    unit_number = StringField('Unit No.', validators=[validators.DataRequired(), length_validator(1, 10)])
    postal_code = StringField('Postal Code', validators=[validators.DataRequired(), length_validator(6, 6),
                                                         is_numeric])


class ChangePassword(Form):
    current_password = PasswordField('Current Password', validators=[validators.DataRequired()])
    new_password = PasswordField('New Password', validators=[validators.DataRequired(), strong_password_validator])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('new_password')
    ])
    submit = SubmitField('Change Password')


class ResetPassword(Form):  # does not require current password
    new_password = PasswordField('New Password', validators=[validators.DataRequired(), strong_password_validator])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('new_password')
    ])
    submit = SubmitField('Change Password')


class UpdateStaffForm(Form):
    name = StringField('Full Name', [length_validator(1, 150), validators.DataRequired()])
    nric = StringField('NRIC', [length_validator(9, 9), validators.DataRequired()])
    email = StringField('Email Address', validators=[validators.DataRequired(), custom_email_validator])
    number = StringField('Mobile No.', validators=[length_validator(8, 8), validators.DataRequired(),
                                                   is_numeric])


class CreateStaffForm(Form):
    staff_id = StringField('Staff ID', [length_validator(6, 6), validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired(),
                                                     strong_password_validator])
    confirm = PasswordField('Confirm Password', validators=[validators.EqualTo('password', 'Password mismatch')])
    name = StringField('Full Name', [length_validator(1, 150), validators.DataRequired()])
    nric = StringField('NRIC', [length_validator(9, 9), validators.DataRequired()])
    email = StringField('Email Address', validators=[validators.DataRequired(), custom_email_validator])
    number = StringField('Mobile No.', validators=[length_validator(8, 8), validators.DataRequired(),
                                                   is_numeric])
    role = SelectField('Staff Role', choices=['Practitioner', 'Receptionist', 'Analyst', 'IT Manager'])
    # Practitioner: Appointments, Inventory
    # Receptionist: Appointments, Helpdesk
    # Analyst: Reports
    # Manager: Accounts
