from collections import UserDict
from datetime import datetime, date
import json


class Field:

    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if len(value) < 3:
            raise ValueError("The name is too short")
        self.__value = value


class Phone(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if not (len(value) >= 7 and len(value) <= 15):
            raise ValueError("The phone number should be 7 to 15 characters long and written with numbers")
        self.__value = value


class Birthday(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if value["month"] > 12 or value["day"] > 31:
            raise ValueError("The birthday date seems weird")
        self.__value = value


class Record:
    def __init__(self, name:Name, *phone_numbers:Phone):
        self.name = name
        self.phone_numbers = []
        self.birthday = None
        if phone_numbers:
            for i in phone_numbers:
                self.phone_numbers.append(i)

    def add_phone_number(self, phone_number:Phone):
        if phone_number not in self.phone_numbers:
            self.phone_numbers.append(phone_number)
            return f"Phone number {phone_number.value} was added to {self.name.value.capitalize()}"
        else:
            return f"Phone number {phone_number.value} already exists in{self.name.value.capitalize()}"

    def remove_phone_number(self, phone_number:Phone):
        if phone_number in self.phone_numbers:
            self.phone_numbers.remove(phone_number)
            return f"Phone number {phone_number.value} was removed from {self.name.value.capitalize()}"
        else:
            return f"Phone number {phone_number.value} was not found in {self.name.value.capitalize()}"

    def edit_phone_number(self, new_number:Phone, old_number:Phone=None):
        self.remove_phone_number(old_number)
        self.add_phone_number(new_number)

    def set_birthday(self, birthday:Birthday):
        self.birthday = birthday
    
    def days_to_birthday(self):
        bday_date =  date(date.today().year, self.birthday.value["month"], self.birthday.value["day"])
        today = date.today()
        if today > bday_date:
            bday_date = date(date.today().year + 1, self.birthday.value["month"], self.birthday.value["day"])
        difference = bday_date - today
        return f'Birthday coming in {difference.days} days\n'


class Addressbook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def to_dict(self):
        data = {}
        for name, record in self.data.items():
            data[str(name)] = {"phones": [str(phone.value) for phone in record.phone_numbers],
                               "birthday": str(None) if not record.birthday else [str(record.birthday.value["day"]), str(record.birthday.value["month"]), str(record.birthday.value["year"])]
                              }
        return data

    def from_dict(self, data):
        for name, value in data.items():
            self.add_record(Record(Name(name), *[Phone(phone) for phone in value["phones"]]))
            if value["birthday"] != "None":
                self.data[name].set_birthday(Birthday({"year":int(value["birthday"][2]), "month":int(value["birthday"][1]), "day":int(value["birthday"][0])}))

    def display_contact(self, name):
        output = f"---------------------------------------------------------\n{name.capitalize()}:\n"
        for phone in self.data[name].phone_numbers:
            output += f"{phone.value}\n"
        if self.data[name].birthday:
            output += self.data[name].days_to_birthday()
        return output
    
    def iterator(self, items_per_page, *args):
        start = 0
        keys = list(self.data.keys())
        while True:
            result = ""
            current_keys = keys[start:start + items_per_page]
            if not current_keys:
                break
            for name in current_keys:
                result += self.display_contact(name)
            yield result
            start += items_per_page
    
    def search(self, keyword, *args):
        result = ""
        for name in self.data.keys():
            content = str(self.display_contact(name)).lower()
            matched = content.find(keyword.lower())
            #print(content, "\n", matched)
            if matched != -1:
                result += self.display_contact(name)
        if result == "":
            result = "No matches\n" 
        return result

    def show_all(self, arg = None, *args):
        if arg:
            items_per_page = int(arg)
            result = "that was the last page \n"
            pg = self.iterator(items_per_page)
            for i in pg:
                print(i)
                input("Press Enter to see the next page\n>>>")
        else:
            result = ""
            for name in self.data.keys():
                result += self.display_contact(name)
        return result

    def load(self):
        try:
            with open("data.json", "r") as file:
                recovered_data = json.load(file)
            if recovered_data != {}:
                self.from_dict(recovered_data)
        except FileNotFoundError:
            print("data.json was not found")

    def save(self):
        converted_data = self.to_dict()
        with open("data.json", "w") as file:
            json.dump(converted_data, file)


addressbook = Addressbook()


def command_error(func):
    def inner(*args):
        try:
            return func(*args)
        except KeyError:
            return 'Unknown command, type "help" to see the list of commands'
        except IndexError:
            return 'IndexError occured'
        except TypeError:
            return 'TypeError occured'
        except ValueError:
            return 'ValueError occured'
    return inner

def greeting(*args):
    return "How can I help you?"

def help(*args):
    commands = [{"command": "hello", "description": "show greeting"},
                {"command": "help", "description": "show all available commands"},
                {"command": "add, name, phone_number", "description": "add a new contact"},
                {"command": "add birthday, name, day.month.year", "description": "add a birthday date to a contact"},
                {"command": "change, name, new_phone_number", "description": "change the phone number of an existing contact"},
                {"command": "phone, name", "description": "show the phone number of a contact"},
                {"command": "show all, number", "description": "show all contacts in console, number (optional) indicates the amount of contacts displayed per page"},
                {"command": "goodbye", "description": "exit Phonebook manager"},
                {"command": "close", "description": "exit Phonebook manager"},
                {"command": "exit", "description": "exit Phonebook manager"}]
    result = ""
    for item in commands:
        result += f'{item["command"]}: {item["description"]}\n'
    return result

def parcer(user_input):
    user_input += ","
    disected_input = user_input.lower().split(",")
    disected_input.remove('')
    results = list()
    for i in disected_input:
        results.append(i.lower().strip(' '))
    return results

def add(name, *args):
    #print(args)
    if name in addressbook.data.keys():
        result = str()
        for arg in args:            
            result += addressbook.data[name].add_phone_number(Phone(arg)) + "\n"
        return result
    name = Name(name)
    phones = [Phone(p) for p in args]
    record = Record(name, *phones)
    addressbook.add_record(record)
    return f"Contact added: {name.value.capitalize()}: {[phone.value for phone in phones]}"

def add_bday(name, date:str, *args):
    date = date.split(".")
    y = int(date[2])
    m = int(date[1])
    d = int(date[0])
    birthday = Birthday({"year":y, "month":m, "day":d})
    addressbook.data[name].set_birthday(birthday)
    return f"Birthday {birthday} was added to {name.capitalize()}"

def change(name, *args):
    if name in addressbook.data.keys():
        addressbook.data[name].phone_numbers = [Phone(p) for p in args]
        return f"Contact changed to {name.capitalize()}: {[(p) for p in args]}"
    return 'Contact not found'

def change_phone(name, old_phone, *new_phones):
    pass

def remove_phone(name, phone, *args):
    pass

def show_contact(*names):
    result_found = ""
    result_not = ""
    for name in names:
        if name in addressbook.data.keys():
            result_found += addressbook.display_contact(name)
        else: result_not += f"---------------------------------------------------------\n{name} not found\n"
    return f"{result_found}{result_not}"

# def iterator(items_per_page, *args):
#     start = 0
#     keys = list(addressbook.data.keys())
#     while True:
#         result = ""
#         current_keys = keys[start:start + items_per_page]
#         if not current_keys:
#             break
#         for name in current_keys:
#             result += addressbook.display_contact(name)
#         yield result
#         start += items_per_page

# def show_all(arg = None, *args):
#     if arg:
#         items_per_page = int(arg)
#         result = "that was the last page \n"
#         pg = addressbook.iterator(items_per_page)
#         for i in pg:
#             print(i)
#             input("Press Enter to see the next page\n>>>")
#     else:
#         result = ""
#         for name in addressbook.data.keys():
#             result += addressbook.display_contact(name)
#     return result

# def search(keyword, *args):
#     result = ""
#     for name in addressbook.data.keys():
#         content = str(addressbook.display_contact(name)).lower()
#         matched = content.find(keyword.lower())
#         #print(content, "\n", matched)
#         if matched != -1:
#             result += addressbook.display_contact(name)
#     if result == "":
#         result = "No matches\n" 
#     return result

@command_error
def handler(command, args):
    functions = {
                "hello": greeting,
                "help": help,
                "add": add,
                "add birthday": add_bday,
                "change": change,
                # "change phone": change_phone,
                # "remove phone": remove_phone,
                "phone": show_contact,
                "show all": addressbook.show_all,
                "search": addressbook.search
                }
    return functions[command](*args)

def main():
    print("Greetings, user! Phonebook manager online")
    addressbook.load()
    while True:
        user_input = parcer(input('Enter a command: \n>>> '))
        command = user_input[0]
        user_input.remove(command)
        args = [arg for arg in user_input]
        #print(user_input)
        if command in ("goodbye", "close", "exit"):
            print("Goodbye!")
            break
        result = handler(command, args)
        if result == "":
            result = "Seems like your list of contacts is empty. Try adding some" 
        print(result)
    addressbook.save()

main()