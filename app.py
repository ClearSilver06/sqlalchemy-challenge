# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-08-23<br/>"
        f"/api/v1.0/2017-08-23/2016-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query precipitation data for the last 12 months
    latest_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (np.datetime64(latest_date) - np.timedelta64(365, 'D')).astype(str)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Create dictionary from row data and append list of precipitation
    all_precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_precipitation.append(prcp_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Query stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the most-active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Query dates and temperature observations for previous year
    latest_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (np.datetime64(latest_date) - np.timedelta64(365, 'D')).astype(str)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()

    # Create a list of temperature observations
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/2017-08-23")
def start():
    start_date = "2017-08-23"
    # Query for TMIN, TAVG, TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    temps = list(np.ravel(results))

    return jsonify({"start_date": start_date, "TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]})

@app.route("/api/v1.0/2017-08-23/2016-08-23")
def start_end():
    start_date = "2016-08-23"
    end_date = "2017-08-23"

    # Query for TMIN, TAVG, TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps = list(np.ravel(results))

    return jsonify({"start_date": start_date, "end_date": end_date, "TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]})

if __name__ == '__main__':
    app.run(debug=True)
