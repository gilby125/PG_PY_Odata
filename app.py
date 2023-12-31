from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import datetime
import argparse
import psycopg2

app = Flask(__name__)
api = Api(app)

parser = argparse.ArgumentParser(description='Process database connection and table name.')
parser.add_argument('--db_connection', type=str, help='Database connection string')
parser.add_argument('--table_name', type=str, help='Table name')
args = parser.parse_args()

app.config["SQLALCHEMY_DATABASE_URI"] = args.db_connection
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class FlightData(db.Model):
    __tablename__ = args.table_name
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.String, unique=True, nullable=False)
    flyFrom = db.Column(db.String)
    flyTo = db.Column(db.String)

    def as_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            result[c.name] = value
        return result


for table in args.table_name.split(','):
    class_name = table.title().replace('_', '') + 'Data'
    locals()[class_name] = type(class_name, (db.Model,), {'__tablename__': table})


class FlightDataResource(Resource):
    def get(self, flight_id=None):
        if flight_id:
            flight_data = FlightData.query.get(flight_id)
            if flight_data:
                return flight_data.as_dict()
            else:
                return {"error": "Flight data not found"}, 404
        else:
            flights = FlightData.query.all()
            return [flight.as_dict() for flight in flights]

    def post(self):
        flight_data = FlightData(**request.json)
        db.session.add(flight_data)
        db.session.commit()
        return flight_data.as_dict(), 201


api.add_resource(FlightDataResource, "/odata/flight_data", "/odata/flight_data/<int:flight_id>")

if __name__ == "__main__":
    app.run(debug=True)
