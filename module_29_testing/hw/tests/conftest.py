import os, datetime, requests, pytest

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from ..flaskr.__init__ import create_app, db as _db
from ..flaskr.models import Client, Parking, Client_Parking

@pytest.fixture
def app():
    configa = {'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://'}
    _app = create_app(configa)

    with _app.app_context():
        tst_data = []
        tst_data.append(Client(name='Lenka', surname='Sereda', credit_card='9674263', car_number='j967ot'))
        tst_data.append(Parking(address='Курнатовского, 71', opened=True, count_places=55, count_available_places=24))
        tst_data.append(Client(name='Svetka', surname='Solovieva', credit_card='9878454', car_number='l853jh'))
        tst_data.append(Client(name='Voffka', surname='Chuprov', credit_card='', car_number='f841gg'))
        tst_data.append(Parking(address='Фрунзе, 10', opened=False, count_places=15, count_available_places=4))
        tst_data.append(Parking(address='Журавлёва, 15', opened=True, count_places=5, count_available_places=0))

        _db.create_all()
        _db.session.add_all(tst_data)
        _db.session.flush()
        c_p = []
        c_p.append(Client_Parking(client_id=tst_data[0].id, parking_id=tst_data[1].id,
                                       time_in=datetime.datetime.now()-datetime.timedelta(hours=1),
                                       time_out=datetime.datetime.now() ))
        c_p.append(Client_Parking(client_id=tst_data[3].id, parking_id=tst_data[1].id,
                                       time_in=datetime.datetime.now()-datetime.timedelta(hours=1),
                                       time_out=datetime.datetime.now() ))
        _db.session.add_all(c_p)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
