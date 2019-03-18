from django.test import TestCase

# Create your tests here.


def add(kwargs):
    print(kwargs)


if __name__ == '__main__':
    d = {'1': 'a', '2': 'b'}
    add(d)
