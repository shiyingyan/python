# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age


class PersonManager:
    def __init__(self, person):
        self._person = person

    def __enter__(self):
        print(self._person)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._person = None

    def person(self):
        return self._person


def print_hi(person):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {person}')  # Press Ctrl+F8 to toggle the breakpoint.
    print(str(p))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    p = Person('xiaohong', 15)
    print(str(p))
    print_hi(p)

    with PersonManager(p) as pm:
        print('with pm', pm.person())
    print(pm.person())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
