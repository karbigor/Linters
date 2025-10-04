import datetime
import os

import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    # Создаём и конфигурируем приложеньку
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Если конфигурация не получена делаем по-своему (нормальный старт)
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///parkings.db'
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        # app.config.from_pyfile('config.py', silent=True)
    else:
        # Если конфигурация получена передаём в приложение (старт тестирования)
        app.config.from_mapping(test_config)

    # Если б/д отсутствует - создаём.
    new = False
    try:
        os.makedirs(app.instance_path)
        new = True
        print('Created.')
    except OSError as err:
        print(err)
        pass

    db.init_app(app)
    with app.app_context():
        from .models import Client, Client_Parking, Parking
        db.create_all()
        if new:
            start_data = [Client(name='Igor',
                                 surname='Karbushev',
                                 credit_card='7498269',
                                 car_number='g345hh'),
                          Client(name='Zarek',
                                 surname='Danelian',
                                 credit_card='9879856',
                                 car_number='a951ky'),
                          Parking(address='Ленина, 1',
                                  opened=True,
                                  count_places=35,
                                  count_available_places=34),
                          Parking(address='Бабушкина, 35',
                                  opened=True,
                                  count_places=63,
                                  count_available_places=62),
                          Client_Parking(client_id=2,
                                         parking_id=2,
                                         time_in=datetime.datetime.now()),
                          Client_Parking(client_id=1,
                                         parking_id=1,
                                         time_in=datetime.datetime.now())]
            db.session.add_all(start_data)
            db.session.commit()

    # a simple page that says hello

    @app.route('/clients')
    def clients():
        all_cli = db.session.query(Client).all()
        all_cli_json = []
        for cli in all_cli:
            all_cli_json.append(cli.to_json())

        return all_cli_json

    @app.route('/clients/<int:client_id>')
    def client(client_id):
        all_cli = db.session.query(Client).where(Client.id
                                                 == client_id).all()
        all_cli_json = []
        for cli in all_cli:
            all_cli_json.append(cli.to_json())
        return all_cli_json

    @app.route('/clients', methods=['POST'])
    def clients_post():
        data = request.form.to_dict()
        new_cli = Client(name=data['name'], surname=data['surname'],
                         credit_card=data['credit_card'],
                         car_number=data['car_number'])
        db.session.add(new_cli)
        db.session.commit()
        added_cli = db.session.query(Client).where(Client.id
                                                   == new_cli.id).first()
        return added_cli.to_json(), 201

    @app.route('/parkings', methods=['POST'])
    def parkings_post():
        data = request.form.to_dict()
        if 'opened' in data:
            data['opened'] = True
        else:
            data['opened'] = False
        new_park = Parking(address=data['address'],
                           opened=data['opened'],
                           count_places=data['count_places'],
                           count_available_places=data[
                               'count_available_places'])
        db.session.add(new_park)
        db.session.commit()
        added_park = db.session.query(Parking).where(Parking.id
                                                     == new_park.id).first()
        return added_park.to_json(), 201

    @app.route('/client_parkings', methods=['POST'])
    def client_parkings_post():
        data = request.form.to_dict()
        park = db.session.query(Parking).where(Parking.id
                                               == data['parking']).first()
        if not park.opened:
            return {'Ответ': 'Парковка закрыта.'}, 400
        if park.count_available_places <= 0:
            return {'Ответ': "Нет свободных мест на парковке."}, 400
        new_cli_park = Client_Parking(client_id=data['client'],
                                      parking_id=data['parking'],
                                      time_in=datetime.datetime.now())
        park.count_available_places -= 1
        db.session.add(new_cli_park)
        db.session.commit()

        added_cli_park = db.session.query(Client_Parking
                                          ).where(Client_Parking.id
                                                  == new_cli_park.id).first()
        return added_cli_park.to_json(), 201

    @app.route('/client_parkings', methods=['DELETE'])
    def client_parkings_delete():
        data = request.form.to_dict()
        cli = db.session.query(Client).where(Client.id
                                             == data['client']).first()
        if not cli.credit_card:
            return {'Ответ': 'Парковка на оплачена. Выезд запрещён.'}, 400
        park = db.session.query(Parking).where(Parking.id
                                               == data['parking']).first()
        cli_park = db.session.query(Client_Parking
                                    ).where(Client_Parking.parking_id
                                            == data['parking'],
                                            Client_Parking.client_id
                                            == data['client']).first()
        if cli_park:
            cli_park.time_out = datetime.datetime.now()
            park.count_available_places += 1
            db.session.commit()
        else:
            return {'Ответ': 'Нет такого клиента на этой парковке.'}, 400
        cli_park = db.session.query(Client_Parking
                                    ).where(Client_Parking.id == cli_park.id
                                            ).first()
        return cli_park.to_json(), 200

# Дополнительные эндпоинты для собственного удобства

    @app.route('/delmet', methods=['POST'])
    def delmet():
        data = request.form.to_dict()
        responce = requests.delete(f"{request.scheme}://{request.host}"
                                   f"/client_parkings", data=data)
        return responce.json(), responce.status_code

    @app.route('/all')
    def all():
        all_cli = db.session.query(Client).all()
        all_cli_json = []
        for cli in all_cli:
            all_cli_json.append(cli.to_json())

        all_park = db.session.query(Parking).all()
        all_park_json = []
        for park in all_park:
            all_park_json.append(park.to_json())

        all_park_cli = db.session.query(Client_Parking).all()
        all_park_cli_json = []
        for park_cli in all_park_cli:
            all_park_cli_json.append(park_cli.to_json())

        return {'clients': all_cli_json, 'parkings': all_park_json,
                'client-parkings': all_park_cli_json}, 200

    return app
