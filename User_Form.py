from User import User

class Feedback(User):
    def __init__(self, full_name, email, rate, remarks, timestamp):
        super().__init__(full_name=full_name, email=email)
        self.__rate = rate
        self.__remarks = remarks
        self.__timestamp = timestamp

    def set_rate(self, rate):
        self.__rate = rate

    def set_remarks(self, remarks):
        self.__remarks = remarks

    def get_rate(self):
        return self.__rate

    def get_remarks(self):
        return self.__remarks
    # Add getters for the timestamp if needed
    def get_timestamp(self):
        return self.__timestamp


# User Inheritance not working
class Booking():
    count = 0

    def __init__(self, full_name, email, number, dob, purpose, date, time_slot, location, remarks):
        self.__name = full_name
        self.__email = email
        self.__number = number
        self.__dob = dob
        self.__Purpose_of_visit = purpose
        self.__Date_of_visit = date
        self.__Time_slot = time_slot
        self.__Location = location
        self.__remarks = remarks
        Booking.count += 1
        self.__booking_id = Booking.count

    def set_Purpose_of_visit(self, purpose):
        self.__Purpose_of_visit = purpose

    def set_Date_of_visit(self, date):
        self.__Date_of_visit = date

    def set_Time_slot(self, time_slot):
        self.__Time_slot = time_slot

    def set_Location(self, location):
        self.__Location = location

    def set_remarks(self, remarks):
        self.__remarks = remarks

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_number(self):
        return self.__number

    def get_dob(self):
        return self.__dob

    def get_Purpose_of_visit(self):
        return self.__Purpose_of_visit

    def get_Date_of_visit(self):
        return self.__Date_of_visit

    def get_Time_slot(self):
        return self.__Time_slot

    def get_Location(self):
        return self.__Location

    def get_remarks(self):
        return self.__remarks

    def get_booking_id(self):
        return self.__booking_id

    def _str_(self):
        return f"{self.get_name()}, {self.get_email()}, {self.get_number()}, {self.get_booking_id()}, " \
               f"{self.get_Purpose_of_visit()}, {self.get_Date_of_visit()}, {self.get_Time_slot()}, {self.get_Location()}"


class ContactUs(User):
    def __init__(self, full_name, email, subject, remarks, timestamp):
        super().__init__(full_name=full_name, email=email)
        self.__Subject = subject
        self.__remarks = remarks
        self.__timestamp = timestamp

    def set_Subject(self, subject):
        self.__Subject = subject

    def set_remarks(self, remarks):
        self.__remarks = remarks

    def get_Subject(self):
        return self.__Subject

    def get_remarks(self):
        return self.__remarks

    # Add getters for the timestamp if needed
    def get_timestamp(self):
        return self.__timestamp