import datetime


class User:
    def __init__(self, full_name, nric=None, password=None, email=None, number=None, day=1, month=1, year=1900, street_name=None, block_number=None,
                 unit_number=None, postal_code=None):
        self.__name = full_name
        self.__nric = nric
        self.__password = password
        self.__email = email
        self.__number = number
        self.__dob = datetime.date(int(year), int(month), int(day))
        self.__street_name = street_name
        self.__block_number = block_number
        self.__unit_number = unit_number
        self.__address = 'Blk ' + str(block_number) + ' ' + str(street_name) + ' ' + str(unit_number) + ' ' + str(postal_code)

    def get_name(self):
        return self.__name

    def get_nric(self):
        return self.__nric

    def get_password(self):
        return self.__password

    def get_email(self):
        return self.__email

    def get_number(self):
        return self.__number

    def get_dob(self):
        return self.__dob

    def get_address(self):
        return self.__address

    def set_name(self, name):
        self.__name = name

    def set_nric(self, nric):
        self.__nric = nric

    def set_password(self, password):
        self.__password = password

    def set_email(self, email):
        self.__email = email

    def set_number(self, number):
        self.__number = number

    def set_dob(self, dob):
        self.__dob = dob

    def set_address(self, address):
        self.__address = address


class StaffUser:
    def __init__(self, staff_id, password, name, nric, email, number, role):
        self.__staff_id = staff_id
        self.__password = password
        self.__name = name
        self.__nric = nric
        self.__email = email
        self.__number = number
        self.__role = role

    def get_staff_id(self):
        return self.__staff_id

    def get_password(self):
        return self.__password

    def get_name(self):
        return self.__name

    def get_nric(self):
        return self.__nric

    def get_email(self):
        return self.__email

    def get_number(self):
        return self.__number

    def get_role(self):
        return self.__role

    def set_staff_id(self, staff_id):
        self.__staff_id = staff_id

    def set_password(self, password):
        self.__password = password

    def set_name(self, name):
        self.__name = name

    def set_nric(self, nric):
        self.__nric = nric

    def set_email(self, email):
        self.__email = email

    def set_number(self, number):
        self.__number = number

    def set_role(self, role):
        self.__role = role


