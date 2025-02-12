class Medicine():
    count = 0

    def __init__(self, name, price, count):
        self.__name = name
        self.__price = float(price)
        self.__count = int(count)
        Medicine.count += 1
        self.__id = Medicine.count

    def set_name(self, name):
        self.__name = name

    def set_price(self, price):
        self.__price = price

    def set_count(self, count):
        self.__count = count

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_count(self):
        return self.__count

    def get_id(self):
        return self.__id

    def __str__(self):
        return f"{self.get_name()}, {self.get_id()}, {self.get_price()}, {self.get_count()}"

