import Forms
from AccountForms import CreateUserForm, LoginForm, StaffLogin, ChangePassword, ResetPassword, UpdateUserForm
from AccountForms import CreateStaffForm, UpdateStaffForm
from User import User, StaffUser
from User_Form import ContactUs, Feedback, Booking
from Medicine import Medicine
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from Forms import FeedbackForm, BookingForm, ContactForm
from wtforms import Form, StringField, SelectField, TextAreaField, validators, IntegerField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
import matplotlib.pyplot as plt
from fpdf import FPDF
import shelve
import os
import datetime
from pathlib import Path
from fpdf.enums import XPos, YPos

app = Flask(__name__)

SECRET_KEY = os.urandom(24).hex()
app.config['SECRET_KEY'] = SECRET_KEY  # Replace with the generated secret key

# Pre-Created Staff Login Credentials

# staff1 = StaffUser('A12345', '123Admin!', 'Xavier Ong', 'T1234567A', 'xavier@gmail.com', '12345678', 'Admin')
# staff2 = StaffUser('B12345', '1NotAdmin!', 'Chloe Chua', 'T1234567B', 'chloe@gmail.com', '23455678', 'Practitioner')
# Note: Only admin users can delete accounts.

# Jing En's Code


# Helper Functions
def load_users():
    with shelve.open('users') as shelf:
        return shelf


def save_users(users):
    with shelve.open('users', 'w') as shelf:
        shelf.update(users)


def save_staff_users(users):
    with shelve.open('staff', 'w') as shelf:
        shelf.update(users)


def is_logged_in():  # User Login
    return 'user_email' in session


def is_staff_logged_in():  # Staff Login
    return 'staff_id' in session


users = load_users()


# App Routes
@app.route('/signup', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)
    if request.method == 'POST':
        if create_user_form.validate():
            with shelve.open('users', 'c') as shelf:
                existing_users = list(shelf.keys())  # Get all existing emails

                # Check if the new email already exists in the shelf
                if create_user_form.email.data in existing_users:
                    flash('This email address is already in use.')
                    return render_template('signup.html', form=create_user_form)

            db = shelve.open('storage.db', 'c')

            user = User(create_user_form.name.data,
                        create_user_form.nric.data, create_user_form.password.data,
                        create_user_form.email.data, create_user_form.number.data,
                        create_user_form.day.data, create_user_form.month.data,
                        create_user_form.year.data, create_user_form.street_name.data,
                        create_user_form.block_number.data, create_user_form.unit_number.data,
                        create_user_form.postal_code.data)

            users_dict = {}
            users_dict[create_user_form.email.data] = user
            save_users(users_dict)
            db.close()
            print('Account created successfully!')
            return redirect('/patient')
    return render_template('signup.html', form=create_user_form)


@app.route('/home')
def visitor_home():
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    user_email = session['user_email']

    with shelve.open('users') as shelf:
        if user_email in shelf:
            user = shelf[user_email]
            return render_template('Visitor_home.html', user=user)


@app.route('/editprofile', methods=['GET', 'POST'])
def edit_profile():
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    user_email = session['user_email']
    form = UpdateUserForm(request.form)

    # Pre-filling the form with data
    if request.method == 'GET':
        with shelve.open('users') as shelf:
            user = shelf.get(user_email)

        if user:
            form.name.data = user.get_name()
            form.nric.data = user.get_nric()
            form.email.data = user.get_email()
            form.number.data = user.get_number()
            dob = user.get_dob()
            form.day.data = dob.day
            form.month.data = str(dob.month)
            form.year.data = dob.year

            address_parts = user.get_address().split(' ')
            form.block_number.data = address_parts[1]
            form.street_name.data = ' '.join(address_parts[2:-2])
            form.unit_number.data = address_parts[-2]
            form.postal_code.data = address_parts[-1]

    # User submits form
    if request.method == 'POST' and form.validate():
        new_email = form.email.data

        with shelve.open('users', 'c') as shelf:
            existing_users = list(shelf.keys())  # Get all existing emails

            # Check if the new email already exists in the shelve, excluding the current user
            if new_email in existing_users and new_email != user_email:
                flash('This email address is already in use.', 'error')
                return render_template('EditProfile.html', form=form)

            user = shelf.get(user_email)
            if user:
                user.set_name(form.name.data)
                user.set_nric(form.nric.data)
                user.set_email(new_email)
                user.set_number(form.number.data)
                user.set_dob(datetime.date(form.year.data, int(form.month.data), form.day.data))

                address = f'Blk {form.block_number.data} {form.street_name.data} {form.unit_number.data} {form.postal_code.data}'
                user.set_address(address)

                if new_email != user_email:
                    # Remove the old email entry if email is being updated
                    del shelf[user_email]
                    shelf[new_email] = user
                    session['user_email'] = new_email
                else:
                    # If email has not changed, update existing entry
                    shelf[new_email] = user

        return redirect('/home')

    return render_template('EditProfile.html', form=form)


@app.route('/changepassword', methods=['GET', 'POST'])
def change_password():
    if not is_logged_in():
        return redirect('/login')

    form = ChangePassword(request.form)
    user_email = session['user_email']

    if request.method == 'POST':
        with shelve.open('users') as shelf:
            user = shelf[user_email]
            current_password = form.current_password.data
            new_password = form.new_password.data
            confirm_password = form.confirm_new_password.data

            if user.get_password() == current_password:
                if new_password == confirm_password:
                    user.set_password(new_password)  # update password
                    shelf[user_email] = user
                    return redirect('/home')
                else:
                    flash('New passwords do not match.')
                    return render_template('changePassword.html', form=form)
            else:
                flash('Current password is incorrect.')
                return render_template('changePassword.html', form=form)
    return render_template('changePassword.html', form=form)


@app.route('/patient', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with shelve.open('users') as shelf:
            if email in shelf:
                user = shelf[email]
                if user.get_password() == password:
                    # Successful login
                    session['user_email'] = user.get_email()  # begin session with user
                    return redirect('/home')   # enters homepage logged in
                else:
                    flash('Password entered is incorrect.')
                    return render_template('visitorlogin.html', form=form)
            else:
                flash('Email entered is not linked to any account.')
                return render_template('visitorlogin.html', form=form)

    return render_template('visitorlogin.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/patient')


# Staff Portal: Account Management


@app.route('/staff', methods=['GET', 'POST'])
def staff():
    form = StaffLogin(request.form)
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        password = request.form['password']
        with shelve.open('staff') as shelf:
            if staff_id in shelf:
                user = shelf[staff_id]
                if user.get_password() == password:
                    # Successful login
                    session['staff_id'] = user.get_staff_id()  # begin session using staff id
                    print(f"Redirecting to /portal with session staff_id: {session['staff_id']}")  # Debug print
                    return redirect('/portal')  # enters
                else:
                    flash('Password entered is incorrect.')
                    return render_template('stafflogin.html', form=form)
            else:
                flash('Staff ID does not exist.')
                return render_template('stafflogin.html', form=form)
    return render_template('stafflogin.html', form=form)


@app.route('/portal')
def staff_portal():
    staff_id = session['staff_id']

    with shelve.open('staff') as shelf:
        if staff_id in shelf:
            user = shelf[staff_id]
            return render_template('staff_dashboard.html', user=user)


@app.route('/staffEditProfile', methods=['GET', 'POST'])
def staff_edit_profile():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    staff_id = session['staff_id']
    form = UpdateStaffForm(request.form)

    # Pre-filling the form with data
    if request.method == 'GET':
        with shelve.open('staff') as shelf:
            user = shelf.get(staff_id)

        if user:
            form.name.data = user.get_name()
            form.nric.data = user.get_nric()
            form.email.data = user.get_email()
            form.number.data = user.get_number()

    # User submits form
    if request.method == 'POST' and form.validate():
        with shelve.open('staff', 'c') as shelf:
            user = shelf.get(staff_id)
            if user:
                user.set_name(form.name.data)
                user.set_nric(form.nric.data)
                user.set_email(form.email.data)
                user.set_number(form.number.data)
                shelf[staff_id] = user

        return redirect('/portal')

    return render_template('StaffEditProfile.html', form=form)


@app.route('/changeStaffPassword', methods=['GET', 'POST'])
def change_staff_password():
    if not is_staff_logged_in():
        return redirect('/staff')

    form = ChangePassword(request.form)
    staff_id = session['staff_id']

    if request.method == 'POST':
        with shelve.open('staff') as shelf:
            user = shelf[staff_id]
            current_password = form.current_password.data
            new_password = form.new_password.data
            confirm_password = form.confirm_new_password.data

            if user.get_password() == current_password:
                if new_password == confirm_password:
                    user.set_password(new_password)  # update password
                    shelf[staff_id] = user
                    return redirect('/portal')
                else:
                    flash('New passwords do not match.')
                    return render_template('changeStaffPassword.html', form=form)
            else:
                flash('Current password is incorrect.')
                return render_template('changeStaffPassword.html', form=form)
    return render_template('changeStaffPassword.html', form=form)


@app.route('/accountManagement')
def account_management():
    with shelve.open('users') as db:
        # Retrieve all users as a list of User objects
        patient = [user for user in db.values() if isinstance(user, User)]  # ensure only user objects are inside
        print(patient)
    with shelve.open('staff') as db:
        # Retrieve all users as a list of StaffUser objects
        staff_users = [user for user in db.values() if isinstance(user, StaffUser)]
    return render_template('account_storage.html', patient=patient, staff=staff_users)


# Staff Portal Account Management Features
@app.route('/accountManagement/createStaffUser', methods=['GET', 'POST'])
def create_staff_user():
    form = CreateStaffForm(request.form)
    if request.method == 'POST':
        if form.validate():
            with shelve.open('staff', 'c') as shelf:
                existing_users = list(shelf.keys())  # Get all existing staff id

                # Check if the new email already exists in the shelf
                if form.staff_id.data in existing_users:
                    flash('This staff ID is already in use.')
                    return render_template('createStaffUser.html', form=form)

            db = shelve.open('storage.db', 'c')

            user = StaffUser(form.staff_id.data, form.password.data,
                             form.name.data, form.nric.data,
                             form.email.data, form.number.data, form.role.data)
            users_dict = {}
            users_dict[form.staff_id.data] = user
            save_staff_users(users_dict)
            db.close()
            print('Account created successfully!')
            return redirect('/accountManagement')
    return render_template('createStaffUser.html', form=form)


@app.route('/deleteUser/<id>', methods=['POST'])
def delete_user(id):
    staff_id = session['staff_id']  # grab staff id of current staff user
    with shelve.open('staff') as db:  # check if current user is an admin
        user = db[staff_id]
        role = user.get_role()
        print(role)
    if role == 'Admin':
        shelf = shelve.open('users')
        del shelf[id]
        shelf.close()
        return redirect('/accountManagement')
    else:
        flash('Permission denied: Only admins can delete accounts.', 'error')
        return redirect(url_for('account_management'))


@app.route('/deleteStaffUser/<id>', methods=['POST'])
def delete_staff_user(id):
    staff_id = session['staff_id']  # grab staff id of current staff user
    with shelve.open('staff') as db:  # check if current user is an admin
        user = db[staff_id]
        role = user.get_role()
    if role == 'Admin':
        shelf = shelve.open('staff')
        del shelf[id]
        shelf.close()
        return redirect('/accountManagement')
    else:
        flash('Permission denied: Only admins can delete accounts.', 'error')
        return redirect(url_for('account_management'))


@app.route('/resetPassword/<id>', methods=['GET', 'POST'])
def reset_password(id):  # from staff portal
    form = ResetPassword(request.form)
    if request.method == 'POST':
        with shelve.open('users') as shelf:
            user = shelf[id]
            new_password = form.new_password.data
            confirm_password = form.confirm_new_password.data
            if new_password == confirm_password:
                user.set_password(new_password)  # update password
                shelf[id] = user
                return redirect('/accountManagement')
            else:
                flash('New passwords do not match.')
                return render_template('resetPassword.html', form=form, user_id=id)
    return render_template('resetPassword.html', form=form, user_id=id)


@app.route('/resetStaffPassword/<id>', methods=['GET', 'POST'])
def reset_staff_password(id):  # from staff portal
    staff_id = session['staff_id']  # grab staff id of current staff user
    with shelve.open('staff') as db:
        user = db[staff_id]
        role = user.get_role()
    if role == 'Admin' or role == 'IT Manager':  # ONLY ADMIN/IT MANAGER can reset staff passwords
        form = ResetPassword(request.form)
        if request.method == 'POST':
            with shelve.open('staff') as shelf:
                user = shelf[id]
                new_password = form.new_password.data
                confirm_password = form.confirm_new_password.data
                if new_password == confirm_password:
                    user.set_password(new_password)  # update password
                    shelf[id] = user
                    return redirect('/accountManagement')
                else:
                    flash('New passwords do not match.')
                    return render_template('resetPassword.html', form=form, user_id=id)
        return render_template('resetPassword.html', form=form, user_id=id)
    else:
        flash('Permission denied: Only admins or IT managers can reset passwords for Staff Users.', 'error')
        return redirect(url_for('account_management'))


@app.route('/staffLogout')
def staff_logout():
    session.pop('staff_id', None)
    return redirect('/staff')


@app.route('/')
def starting():
    return render_template('chooselogin.html')


# Alyssa's Code
@app.route('/home/feedback', methods=['GET', 'POST'])
def feedback():
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    feedback_form = FeedbackForm(request.form)
    email = session['user_email']

    # Open user db
    with shelve.open('users', 'c') as shelf:
        user = shelf[email]  # Get current user object

    if request.method == 'POST' and feedback_form.validate():
        feedback_dict = {}

        with shelve.open('storage.db', 'c') as db:
            feedback_dict = db.get('Feedback', {})

            # Get the current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            feedback = Feedback(feedback_form.full_name.data,
                                feedback_form.email.data, feedback_form.rate.data,
                                feedback_form.remarks.data, timestamp)
            feedback_id = str(feedback.get_email())
            feedback_dict[feedback_id] = feedback
            db['Feedback'] = feedback_dict

        return redirect(url_for('visitor_home'))

    return render_template('feedback.html', form=feedback_form)

@app.route('/home/contact', methods=['GET', 'POST'])
def contact():
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    contact_form = ContactForm(request.form)
    email = session['user_email']

    # Open user db
    with shelve.open('users', 'c') as shelf:
        user = shelf[email]  # Get current user object

    if request.method == 'POST' and contact_form.validate_on_submit():
        contact_dict = {}
        with shelve.open('storage.db', 'c') as db:
            contact_dict = db.get('Contact', {})

            # Get the current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            contact = ContactUs(contact_form.full_name.data, contact_form.email.data,
                                contact_form.Subject.data, contact_form.remarks.data, timestamp)
            contact_id = str(contact.get_email())
            contact_dict[contact_id] = contact
            db['Contact'] = contact_dict

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('visitor_home'))

    return render_template('contact.html', form=contact_form)

@app.route('/portal/forms_view')
def forms_view():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    view = request.args.get('view', 'feedback')
    with shelve.open('storage.db', 'r') as db:
        feedback_data = db.get('Feedback', {})
        contact_data = db.get('Contact', {})

    selected_view = 'contact' if view == 'contact' else 'feedback'
    submissions_data = contact_data.values() if view == 'contact' else feedback_data.values()

    # Convert class instances to dictionaries if needed
    submissions_data = [
        submission.__dict__ if hasattr(submission, '__dict__') else submission
        for submission in submissions_data
    ]

    # Debugging statements
    print(f"Selected view: {selected_view}")
    print(f"Submissions data: {list(submissions_data)}")

    return render_template('forms_view.html', selected_view=selected_view, submissions_data=submissions_data)


@app.route('/delete_feedback/<string:email>', methods=['POST'])
def delete_feedback(email):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('storage.db', 'c') as db:
        feedback_data = db.get('Feedback', {})
        if email in feedback_data:
            del feedback_data[email]
            db['Feedback'] = feedback_data
            flash('Feedback entry deleted successfully', 'success')
        else:
            flash('Feedback entry not found', 'danger')
    return redirect(url_for('forms_view', view='feedback'))

@app.route('/delete_contact/<string:email>', methods=['POST'])
def delete_contact(email):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('storage.db', 'c') as db:
        contact_data = db.get('Contact', {})
        if email in contact_data:
            del contact_data[email]
            db['Contact'] = contact_data
            flash('Contact entry deleted successfully', 'success')
        else:
            flash('Contact entry not found', 'danger')
    return redirect(url_for('forms_view', view='contact'))

@app.route('/portal/forms_view/reply_submission-<string:email>', methods=['POST'])
def reply_submission(email):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    reply = request.form['reply']
    staff_member = 'Staff Name'  # Replace with actual staff member's name or ID

    with shelve.open('storage.db', 'c') as db:
        contact_data = db.get('Contact', {})
        if email in contact_data:
            contact_entry = contact_data[email]
            if 'replies' not in contact_entry:
                contact_entry['replies'] = []
            contact_entry['replies'].append({'staff': staff_member, 'reply': reply})
            db['Contact'] = contact_data

    return redirect(url_for('forms_view', view='contact'))


# Reese's Code

# Booking Form
@app.route('/home/booking', methods=['GET', 'POST'])
def booking():
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    form = BookingForm(request.form)
    email = session['user_email']

    # Open user db
    with shelve.open('users', 'c') as shelf:
        user = shelf[email]  # Get current user object

    if request.method == 'POST' and form.validate_on_submit():
        # Bookings db
        db = shelve.open('bookings', 'c')
        try:
            booking_dict = db['booking']
        except:
            booking_dict = {}
            db['booking'] = booking_dict

        #Save booking information as an object
        name = user.get_name()
        email = user.get_email()
        phone = user.get_number()
        dob = user.get_dob()
        purpose = form.purpose.data
        date = form.date.data
        time = datetime.datetime.strptime(form.time.data, "%H%M").time()
        location = form.location.data
        remarks = form.remarks.data

        print(time, form.time.data)

        # Create object
        booking = Booking(name, email, phone, dob, purpose, date, time, location, remarks)
        booking_dict[booking.get_booking_id()] = booking
        db['booking'] = booking_dict
        db.close()

        for key in booking_dict:
            print(booking_dict[key])

        return redirect(url_for('visitor_home'))

    return render_template('Booking.html', form=form)

# Reschedule Form
@app.route('/home/records/reschedule-<int:id>', methods=['GET', 'POST'])
def reschedule(id):
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    reschedule_form = BookingForm(request.form)

    if request.method == 'POST' and reschedule_form.validate_on_submit():
        # Bookings db
        db = shelve.open('bookings', 'c')
        booking_dict = {}
        booking_dict = db['booking']

        #update booking information
        booking = booking_dict.get(id)
        booking.set_Purpose_of_visit(reschedule_form.purpose.data)
        booking.set_Location(reschedule_form.location.data)
        booking.set_Time_slot(datetime.datetime.strptime(reschedule_form.time.data, "%H%M").time())
        booking.set_Date_of_visit(reschedule_form.date.data)
        booking.set_remarks(reschedule_form.remarks.data)

        db['booking'] = booking_dict
        db.close()

        print(booking)

        return redirect(url_for('visitor_home'))
    else:
        # Bookings db
        db = shelve.open('bookings', 'c')
        booking_dict = {}
        booking_dict = db['booking']

        # retrieve booking information
        booking = booking_dict.get(id)
        reschedule_form.purpose.data = booking.get_Purpose_of_visit()
        reschedule_form.location.data = booking.get_Location()
        reschedule_form.time.data = booking.get_Time_slot()
        reschedule_form.date.data = booking.get_Date_of_visit()

    return render_template('Reschedule.html', form=reschedule_form)

# Load Visitor Bookings
@app.route('/home/records', methods=['GET'])
def view_bookings():
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    # Open user db
    email = session['user_email']
    with shelve.open('users', 'c') as shelf:
        user = shelf[email]  # Get current user object

    # Retrieve data from Booking Forms
    with shelve.open('bookings', 'c') as db:
        booking_dict = db['booking']

    booking_list = []
    date = datetime.datetime.today().date()
    time = datetime.datetime.today().time()

    for key in booking_dict:
        # Retrieve Booking Object
        booking_instance = booking_dict.get(key)
        print(booking_instance)
        # check that booking data belongs to user
        if booking_instance.get_email() == user.get_email():
            booking_list.append(booking_instance)

        # Sort by date
        booking_list = sorted(booking_list, key=lambda booking: booking.get_Date_of_visit())

    print(booking_list)

    return render_template('Visitor_Bookings.html', booking_list=booking_list, date=date, time=time)

# View Specifics (Link to Update, Delete and Retrieve MC)
@app.route('/home/records-<int:id>', methods=['GET'])
def retrieve_record(id):
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    # Retrieve data from Booking Forms
    booking_dict = {}
    with shelve.open('bookings', 'c') as db:
        booking_dict = db['booking']
        db.close()

    # Return specific instance
    booking_instance = booking_dict.get(id)

    # Export Variables
    today_date = datetime.datetime.today().date()
    today_time = datetime.datetime.today().date()
    button_criteria = datetime.timedelta(days=2)
    mc_criteria = datetime.timedelta(hours=1)

    return render_template('Visitor_Bookings_Specifics.html', info=booking_instance, date=today_date, time=today_time,
                           button_criteria=button_criteria, mc_criteria=mc_criteria)

# Cancel Booking
@app.route('/home/records/cancel-<int:id>', methods=['POST'])
def cancel_booking(id):
    if not is_logged_in():  # Check if user is logged in
        return redirect('/patient')

    with shelve.open('bookings', 'c') as db:
        booking_dict = db['booking']
        booking_dict.pop(id)
        db['booking'] = booking_dict
        db.close()

    return redirect(url_for('view_bookings'))

@app.route('/portal/appointments', methods=['GET'])
def retrieve_appointments():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    # Retrieve all booking data
    appointments_dict = {}
    db = shelve.open('bookings', 'c')
    try:
        appointments_dict = db['booking']
    except:
        db['booking'] = appointments_dict
    finally:
        db.close()

    appointments_list = []
    for key in appointments_dict:
        # Retrieve Booking Object
        appointment = appointments_dict.get(key)
        appointments_list.append(appointment)

    return render_template('appointments_view.html', appointments_list=appointments_list)

@app.route('/portal/inventory', methods=['GET', 'POST'])
def inventory():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    # Retrieve data from inventory Forms
    with shelve.open('inventory', 'c') as db:
        inventory_dict = db['inventory']

    inventory_list = []
    for key in inventory_dict:
        # retrieve medicine object
        med = inventory_dict.get(key)
        inventory_list.append(med)

    return render_template('inventory_view.html', inventory_list=inventory_list)

# Note for lecturer: This exact code works in all other files but in this iteration it might glitch
@app.route('/portal/inventory/add', methods=['GET', 'POST'])
def add_medicine():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    add = Forms.MedicineForm()
    inventory_dict = {}

    if request.method == 'POST' and add.validate_on_submit():
        # Create Object
        med = Medicine(add.name.data, add.price.data, add.count.data)

        # Update db
        db = shelve.open('inventory', 'c')
        try:
            inventory_dict = db['inventory']
        except:
            db['inventory'] = inventory_dict
        finally:
            inventory_dict[med.get_id()] = med
            db['inventory'] = inventory_dict
            db.close()

        return redirect(url_for('inventory'))

    return render_template('inventory_form.html', form=add)

@app.route('/portal/inventory/edit-<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    edit = Forms.MedicineForm()

    if request.method == 'POST' and edit.validate_on_submit():
        # Load data
        inventory_dict = {}
        db = shelve.open('inventory', 'c')
        inventory_dict = db['inventory']

        # update object
        medicine = inventory_dict.get(id)
        medicine.set_name(edit.name.data)
        medicine.set_count(edit.count.data)
        medicine.set_price(edit.price.data)

        # Update db
        db['inventory'] = inventory_dict
        db.close()

        # Redirect
        return redirect(url_for('inventory'))

    else:
        # Load db
        inventory_dict = {}
        db = shelve.open('inventory', 'c')
        inventory_dict = db['inventory']
        db.close()

        medicine = inventory_dict.get(id)
        edit.name.data = medicine.get_name()
        edit.price.data = medicine.get_price()
        edit.count.data = medicine.get_count()

        return render_template('inventory_form_e.html', form=edit)

# Remove Medicine
@app.route('/portal/inventory/remove-<int:id>', methods=['POST'])
def remove_medicine(id):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('inventory', 'c') as db:
        booking_dict = db['inventory']
        booking_dict.pop(id)
        db['inventory'] = booking_dict
        db.close()

        # Redirect
        return redirect(url_for('inventory'))

# Prescription Form
class PrescriptionForm(FlaskForm):
    medicine = SelectField('Medicine', [DataRequired()], choices=[])
    quantity = IntegerField('Quantity', validators=[NumberRange(min=1, max=5), DataRequired()], default=0, )
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit')


# restart prescription each session
prescription_data = {}

# add medicine into session storage
def add_p(id, quantity, name, price):
    prescription_data[int(id)] = [int(quantity), name, price]

def calculate_price(purpose, prescription):
    if purpose == "Medical Check Up":
        price = 20.00
    elif purpose == "Medical Test":
        base = 45.00
    elif purpose == "Health Screening":
        base = 100.00
    elif purpose == "Vaccination":
        base = 15.00

    for id in prescription:
        medicine = prescription.get(id)
        base += medicine[2]

    fee = base * 1.09

    return fee

@app.route('/portal/prescription-<int:id>', methods=['GET', 'POST'])
def Prescription(id):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    # Retrieve data from Inventories
    inventory_dict = {}
    db = shelve.open('inventory', 'c')
    try:
        inventory_dict = db['inventory']
    except:
        db['inventory'] = inventory_dict
    finally:
        db.close()

    # Retrieve all booking data
    appointments_dict = {}
    db = shelve.open('bookings', 'c')
    try:
        appointments_dict = db['booking']
    except:
        db['booking'] = appointments_dict
    finally:
        db.close()

    # Retrieve all booking data
    mc_dict = {}
    db = shelve.open('mc', 'c')
    try:
        mc_dict = db['mc']
    except:
        db['mc'] = mc_dict


    appointment = appointments_dict.get(id)
    medicines_list = []

    # populate medicine list
    for key in inventory_dict:
        medicine = inventory_dict.get(key)
        # Check if stock is still available
        if medicine.get_count() > 0:
            medicines_list.append(medicine)

    # Load Form
    form = PrescriptionForm()
    form.medicine.choices = [(m.get_id(), m.get_name()) for m in medicines_list]


    if request.method == 'POST' and form.validate_on_submit():
        # Add medicine to list of prescription
        if request.form['action'] == 'add':
            med_id = int(form.medicine.data)
            med_quantity = int(form.quantity.data)
            med_obj = inventory_dict.get(med_id)
            med_name = med_obj.get_name()
            med_price = med_obj.get_price()
            add_p(med_id, med_quantity, med_name, med_price)

        # Submit Prescription and Doctor's comment
        elif request.form['action'] == 'submit':
            # Update Medicine Quantity in Inventory
            for med_id in prescription_data:
                # Store object as variable
                medicine = inventory_dict.get(med_id)

                # Update count
                medicine.set_count(int(medicine.get_count()) - prescription_data[med_id][0])
                print(medicine.get_name(), medicine.get_count())

            # Calculate price
            price = calculate_price(appointment.get_Purpose_of_visit, prescription_data)

            # Export to MC Records
            mc_dict[appointment.get_booking_id()] = {'medicine': prescription_data,
                                                     'comment': form.comment.data,
                                                     'price': price}
            db = shelve.open('prescription', 'c')
            db['mc'] = mc_dict
            db.close()

            # Reset
            prescription_data.clear()

            return redirect('/portal')

    return render_template('doctor_page.html', form=form, medicines=prescription_data, appointment=appointment)


# Navo's code
@app.route('/createreport')
def create_report():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    return render_template('chart_report.html')

@app.route('/reportlist')
def report_list():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')
    return render_template('report_list.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    data = request.get_json()
    analyses = data.get('analyses', [])
    report_name = data.get('reportName', '').strip()
    description = data.get('description', '').strip()

    # Create a directory for Reports if it doesn't exist
    if not os.path.exists('Reports'):
        os.makedirs('Reports')
    if not os.path.exists('Charts'):
        os.makedirs('Charts')

    # Load data from shelve database
    with shelve.open('storage.db', 'r') as db:
        users = list(db['test'].keys())
        visits = [value[0] for value in db['test'].values()]
        locations = [value[1] for value in db['test'].values()]
        ratings = [value[2] for value in db['test'].values()]
        print(locations, analyses)
    chart_paths = []

    def create_pie_chart(data, labels, title, filename):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(data, labels=labels, autopct='%1.1f%%')
        ax.set_title(title)
        image_path = os.path.join('Charts', filename)
        fig.savefig(image_path)
        plt.close(fig)
        return image_path

    def create_bar_chart(x, y, title, xlabel, ylabel, filename):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x, y, color='skyblue')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        image_path = os.path.join('Charts', filename)
        fig.savefig(image_path)
        plt.close(fig)
        return image_path

    if 'location_users' in analyses:
        # Count occurrences of each location
        location_count = {location: locations.count(location) for location in set(locations)}
        labels = list(location_count.keys())
        data = list(location_count.values())
        chart_paths.append(create_pie_chart(data, labels, 'Distribution of Locations', 'location_users.png'))

    if 'num_visits' in analyses:
        chart_paths.append(create_bar_chart(users, visits, 'Distribution of Visits', 'Users', 'Number of Visits', 'num_visits.png'))

    if 'user_ratings' in analyses:
        chart_paths.append(create_bar_chart(users, ratings, 'Distribution of Ratings', 'Users', 'Ratings', 'user_ratings.png'))

    # Create PDF with report name
    print(report_name)
    pdf_filename = f"{report_name}.pdf"
    pdf_path = os.path.join('Reports', pdf_filename)
    pdf = FPDF()
    pdf.add_page()

    # Add description to the PDF if available
    if description:
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, description)
        pdf.ln(10)  # Add some space after the description

    # Add saved charts to the PDF
    for chart_path in chart_paths:
        pdf.image(chart_path, x=10, y=pdf.get_y(), w=180)
        pdf.ln(95)  # Add space for the next image, adjust this value as needed
        if pdf.get_y() + 95 > 297:  # Check if the next image would be outside the page (A4 size height is 297mm)
            pdf.add_page()

    pdf.output(pdf_path)

    # Save the path to shelve database
    with shelve.open('report_paths.db') as db:
        db[report_name] = pdf_path
        print(db[report_name])

    return jsonify({"success": True})

@app.route('/get_reports', methods=['GET'])
def get_reports():
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('report_paths.db') as db:
        reports = {key: db[key] for key in db}
        print(reports)
    return jsonify(reports)


@app.route('/download_report/<filename>')
def download_report(filename):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('report_paths.db') as db:
        pdf_path = db[filename]

    return send_file(pdf_path, as_attachment=True)


@app.route('/delete_report/<filename>', methods=['POST'])
def delete_report(filename):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('report_paths.db', 'c') as db:
        report_path = db[filename]
        os.remove(report_path)  # Remove the PDF file
        del db[filename]  # Remove the record from the shelve database
    return jsonify({'message': 'Report deleted successfully!'})

@app.route('/rename_report/<filename>', methods=['POST'])
def rename_report(filename):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    data = request.get_json()
    new_name = data.get('newName', '').strip()

    with shelve.open('report_paths.db', 'c') as db:
        if new_name in db:
            return jsonify({'message': 'A report with this name already exists. Please choose a different name.'}), 400

        if filename in db:
            pdf_path = db[filename]
            new_path = os.path.join('Reports', f"{new_name}.pdf")
            os.rename(pdf_path, new_path)  # Rename the file
            db[new_name] = new_path
            del db[filename]  # Remove the old record
            return jsonify({'message': 'Report renamed successfully!'})
        else:
            return jsonify({'message': 'Report not found.'}), 404

@app.route('/preview_report/<filename>', methods=['GET'])
def preview_report(filename):
    if not is_staff_logged_in():  # Check if user is logged in
        return redirect('/staff')

    with shelve.open('report_paths.db', 'r') as db:
        if filename not in db:
            return jsonify({'message': 'Report not found'}), 404
        report_path = db[filename]

    return send_file(report_path)
@app.route('/mc')
def generate_mc():
    class PDF(FPDF):
        def header(self):
            # Klynix logo at the top left corner
            self.image('static/klinyxlogo.png', 10, 5, 50)  # Adjust the size and position as needed

            self.set_y(25)
            # Title
            self.set_font('Helvetica', 'B', 20)

            # Using new_x and new_y instead of ln
            self.cell(0, 10, 'Klynix Medical Centre', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        def footer(self):
            # Page footer
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            # Use new_x and new_y instead of ln
            self.cell(0, 10, f'Page {self.page_no()}', 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

    # Create a PDF instance
    pdf = PDF()
    pdf.add_page()

    # Centralized content
    pdf.set_font('Helvetica', '', 12)
    pdf.set_y(33)  # Set Y position to where you want to start the content
    pdf.multi_cell(0, 10, '51 Edgefield plains, Singapore 123456\n', align='C')

    pdf.set_font('Helvetica', 'B', 16)
    # Use new_x and new_y instead of ln
    pdf.cell(0, 10, 'Medical Certificate', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    #doctor's signature image
    pdf.image('static/doctor sign.png', 93, 145, 20)

    # Retrieve data from Booking Forms
    booking_dict = {}
    with shelve.open('bookings', 'r') as db:
        booking_dict = db['booking']
        db.close()

    email = session['user_email']
    with shelve.open('users', 'r') as shelf:
        user = shelf[email]  # Get current user object

    # Return specific instance
    booking_instance = booking_dict.get(id)
    info = booking_instance

    name = info.get_name
    nric_number = user.get_nric()
    date = info.get_Date_of_visit()
    number = str(user.get_number())
    registration_number = number [::-1]

    pdf.set_font('Helvetica', '', 12)
    pdf.set_y(pdf.get_y() + 20)  # Adjust position explicitly
    pdf.multi_cell(0, 10, f'This is to certify that the individual known as {name} with the NRIC {nric_number} has '
                          f'undergone a medical examination on {date} by Dr. Mary Tan.'
                          f'\n\nThe examinee has been advised, for the sake of the individual\'s overall health, to take medical '
                          f'leave for a period of 2 days.\n\n\n\nCertified by Dr. Mary Tan,\nKlynix Medical Centre\n'
                          f'{registration_number}', align='C')

    # Determine the path to the Downloads folder
    downloads_folder = str(Path.home() / "Downloads")
    file_path = os.path.join(downloads_folder, 'medical_certificate.pdf')

    # Output the PDF to the Downloads folder
    pdf.output(file_path)

    # Optionally open the PDF file
    os.startfile(file_path)

    return send_file(file_path, as_attachment=True)

@app.route('/invoice')
def invoice_generator():
    class PDF(FPDF):
        def header(self):
            # Klynix logo at the top left corner
            self.image('static/klinyxlogo.png', 10, 0, 50)  # Adjust the size and position as needed

            # Title
            self.set_y(20)
            self.set_font('Helvetica', 'B', 20)
            self.cell(0, 10, 'Klynix Medical Centre', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

            # Subtitle
            self.set_font('Helvetica', '', 12)
            self.cell(82)
            self.cell(30, 10, 'INVOICE', new_x=XPos.RIGHT, new_y=YPos.TOP)

            # Move to the next line
            self.set_y(self.get_y() + 10)  # Adjust this value to move the telephone number downwards

        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-20)
            self.set_x(65)
            # Helvetica italic 8
            self.set_font('Helvetica', 'BI', 8)
            self.cell(30, 10, '51 Edgefield Plains, Singapore 541224. Tel: +123-456-7890', new_x=XPos.RIGHT,
                      new_y=YPos.TOP)

            self.set_y(-15)
            self.set_x(78)
            self.set_font('Helvetica', 'BI', 8)
            self.cell(30, 10, 'klynix@gmail.com. www.klynix.com', new_x=XPos.RIGHT, new_y=YPos.TOP)

    # Create instance of FPDF class
    pdf = PDF()

    # Add a page
    pdf.add_page()

    # Invoice Info
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_y(60)  # Set Y position for Invoice ID
    pdf.set_x(90)  # Set X position for Invoice ID
    pdf.cell(100, 10, f'Date: {datetime.now().strftime("%d %B, %Y")}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')

    # Reduce the font size for the date and adjust its position
    pdf.set_font('Helvetica', 'B', 10)  # Reduced font size to 10
    pdf.set_y(65)  # Set Y position for Date
    pdf.set_x(90)  # Set X position for Date
    pdf.cell(100, 10, f'Invoice No: 00000001', new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_y(60)  # Set Y position for Bill to label
    pdf.set_x(20)  # Set X position for Bill to label
    pdf.cell(100, 10, 'Bill to:', new_x=XPos.RIGHT, new_y=YPos.NEXT, align='L')

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_y(65)  # Set Y position for Bill to address
    pdf.set_x(20)  # Set X position for Bill to address
    pdf.cell(100, 10, 'Liceria & Co.', new_x=XPos.RIGHT, new_y=YPos.NEXT, align='L')

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_y(70)  # Set Y position for Bill to address
    pdf.set_x(20)  # Set X position for Bill to address
    pdf.cell(100, 10, '123 Anywhere St.,', new_x=XPos.RIGHT, new_y=YPos.NEXT, align='L')

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_y(75)  # Set Y position for Bill to address
    pdf.set_x(20)  # Set X position for Bill to address
    pdf.cell(100, 10, 'Any City, ST 12345', new_x=XPos.RIGHT, new_y=YPos.NEXT, align='L')

    # Table header
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_fill_color(164, 233, 237)
    pdf.set_y(120)  # Set Y position for the table
    pdf.set_x(20)
    pdf.cell(15, 10, 'Item', 1, fill=True)
    pdf.cell(85, 10, 'Description', 1, fill=True)
    pdf.cell(35, 10, 'Price', 1, fill=True)
    pdf.cell(35, 10, 'Amount', 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    # Table content
    with shelve.open('storage.db', 'r') as db:
        med_A = db['mc']['test']['medicine'][1]
        med_B = db['mc']['test']['medicine'][2]

    with shelve.open('inventory', 'r') as db:
        a_price = f"{db['inventory'][3].get_price():.2f}"
        med_A.append(a_price)
        b_price = f"{db['inventory'][1].get_price():.2f}"
        med_B.append(b_price)
        items = []
        items.append(med_A)
        items.append(med_B)
        print(items)

    pdf.set_font('Helvetica', '', 12)
    x = 0
    subtotal = 0
    for item in items:
        amount = item[2] * item[0]
        subtotal = subtotal + float(amount)
        x = x + 1
        pdf.set_x(20)
        pdf.cell(15, 10, str(x), 1)
        pdf.cell(85, 10, str(item[1]), 1)
        pdf.cell(35, 10, str(item[0]), 1)
        pdf.cell(35, 10, f'${str(item[2])}', 1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Total
    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(5)
    pdf.cell(120)
    pdf.cell(30, 10, 'Subtotal', 0)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(40)
    pdf.cell(120)
    pdf.cell(30, 10, f'${subtotal:.2f}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(5)
    pdf.cell(120)
    pdf.cell(30, 10, 'GST(9%)', 0)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(40)
    pdf.cell(120)
    pdf.cell(30, 10, f'${subtotal / 100 * 9:.2f}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    # Move down 10 units from the current position for the horizontal line
    pdf.set_y(pdf.get_y() + 5)  # Adjust the value to move the line down if necessary
    pdf.set_line_width(0.5)  # Set the width of the line
    pdf.line(120, pdf.get_y(), 180, pdf.get_y())

    # Adjust the Y position for the last 'Total Due' value
    pdf.set_y(pdf.get_y())  # Move the position down to avoid overlap
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_x(5)
    pdf.cell(120)
    pdf.cell(30, 10, 'Total Due', new_x=XPos.RIGHT, new_y=YPos.NEXT, align='L', border=0)

    # Adjust Y position for the last amount
    pdf.set_y(pdf.get_y() - 10)  # Move the position up for the amount
    pdf.set_x(40)
    pdf.cell(120)
    pdf.cell(30, 10, f'${subtotal:.2f}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    # Determine the path to the Downloads folder
    downloads_folder = str(Path.home() / "Downloads")
    file_path = os.path.join(downloads_folder, 'invoice.pdf')

    # Save the PDF to the Downloads folder
    pdf.output(file_path)

    # Optionally open the PDF file
    os.startfile(file_path)

    # Return the file as an attachment
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
