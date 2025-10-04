from typing import Any, Dict

from .__init__ import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50), nullable=False)
    car_number = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"Клиент {self.name} {self.surname}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Parking(db.Model):
    __tablename__ = "parkings"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, nullable=False)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Парковка {self.address}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Client_Parking(db.Model):
    __tablename__ = "client_parking"
    __table_args__ = (
        db.UniqueConstraint("client_id", "parking_id",
                name="unique_client_parking"),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    client = db.relationship("Client", backref="client_parking")
    parking_id = db.Column(db.Integer, db.ForeignKey("parkings.id"))
    parking = db.relationship("Parking", backref="client_parking")
    time_in = db.Column(db.DateTime, nullable=False)
    time_out = db.Column(db.DateTime)

    def __repr__(self):
        return f"Клиент-Парковка {self.client_id} {self.parking_id}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
