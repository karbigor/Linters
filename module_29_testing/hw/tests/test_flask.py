import json
import pytest
from ..flaskr.models import Client, Parking, Client_Parking


@pytest.mark.parametrize('getpoints', ['/clients', '/clients/1'])
def test_all_gets(client, getpoints) -> None:
    resp = client.get(getpoints)
    data = resp.status_code
    assert data == 200

def test_create_user(client) -> None:
    user_data = {"name": "Nikita", "surname": "Nesterenko", "credit_card": "9674263", 'car_number': 'j967ot'}
    resp = client.post("/clients", data=user_data)
    assert resp.status_code == 201

def test_create_parking(client) -> None:
    parking_data = {'address': 'Новобульварная, 119', 'opened': True, "count_places": 33, "count_available_places": 11}
    resp = client.post("/parkings", data=parking_data)
    assert resp.status_code == 201

@pytest.mark.parkings
@pytest.mark.parametrize('parks', [1, 2, 3])
def test_in_parking(client, db, parks) -> None:
    parking_data = {'parking': parks, 'client': 2}
    resp = db.session.query(Parking).where(Parking.id == parking_data['parking']).first()
    opened = resp.opened
    available = resp.count_available_places
    resp = client.post("/client_parkings", data=parking_data)
    if opened and available > 0:
        assert resp.status_code == 201
        resp = db.session.query(Parking).where(Parking.id == parking_data['parking']).first()
        assert resp.count_available_places == available - 1
    else:
#        print(json.loads(resp.data))
        assert resp.status_code == 400

@pytest.mark.parkings
@pytest.mark.parametrize('cli', [1, 3])
def test_off_parking(client, db, cli) -> None:
    parking_data = {'parking': 1, 'client': cli}
    resp = db.session.query(Parking).where(Parking.id == parking_data['parking']).first()
    available = resp.count_available_places
    cli_p = db.session.query(Client).where(Client.id == parking_data['client']).first()
    resp = client.delete("/client_parkings", data=parking_data)
    if cli_p.credit_card:
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['time_in'] < data['time_out']
        resp = db.session.query(Parking).where(Parking.id == parking_data['parking']).first()
        assert available + 1 == resp.count_available_places
    else:
        assert resp.status_code == 400
