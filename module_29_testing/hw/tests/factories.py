import factory
import factory.fuzzy as fuzzy
import random


from ..flaskr.__init__ import create_app, db as _db
from ..flaskr.models import Client, Parking, Client_Parking

class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = _db.session

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    if random.random() < 0.5:
        credit_card = factory.Faker('credit_card_number')
    else:
        credit_card = ''
    car_number = factory.Faker('license_plate')


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = _db.session

    address = factory.Faker('address')
    opened = factory.Faker('pybool')
    count_places = factory.Faker('random_int', min=10, max=100)
    count_available_places = factory.Faker('random_int', min=0, max=count_places)
