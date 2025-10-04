from ..flaskr.models import Client, Client_Parking, Parking
from .factories import ClientFactory, ParkingFactory

#Здесь можно создавать новые сущности через API, что вроде бы логично, однако придётся использовать объекты созданные
# фабрикой как словари, что, вроде моветон. Для альтернативы сделал создание сущностей прямо в базу.

def test_create_user_by_api(app, client):
    cli = ClientFactory()
    resp = client.post("/clients", data=cli.__dict__)
    assert resp.status_code == 201
    assert cli.id is not None

def test_create_user_by_db(db, app):
    client = ClientFactory()
    db.session.commit()
    assert client.id is not None
    cli = db.session.query(Client).all()
    assert len(cli) == 4


def test_create_parking_by_api(app, client):
    par = ParkingFactory()
    resp = client.post("/parkings", data=par.__dict__)
    assert resp.status_code == 201
    assert par.id is not None

def test_create_parking_by_db(client, db):
    parking = ParkingFactory()
    db.session.commit()
    assert parking.id is not None
    par = db.session.query(Parking).all()
    assert len(par) == 4


