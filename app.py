import numpy as np
import datetime

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
Base.prepare(engine, reflect=True)

# Save references to tables

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).all()

    session.close()

    # Create dictionary
    all_precip = []
    for station, date, prcp in results:
        prcp_dict = {}
        prcp_dict["station"] = station
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        all_precip.append(prcp_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into list
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temps():
    session = Session(engine)

    results = session.query(Measurement.tobs).filter(Measurement.date >= 2016-8-23).filter(Measurement.station == 'USC00519281').all()

    session.close()

    # Convert to list
    active_temps = list(np.ravel(results))

    return jsonify(active_temps)


@app.route("/api/v1.0/<start>")
def dated_temps(start):
    session = Session(engine)

    user_input = datetime.datetime.strptime(start, "%Y-%M-%d").date()

    results = session.query(Measurement.date, Measurement.tobs).all()

    # Lists to store session data
    dates = []
    temps = []

    # Move session data into lists
    for result in results:
        dates.append(datetime.datetime.strptime(Measurement.date, "%Y-%M-%d").date())
        temps.append(Measurement.tobs)

    session.close()

    # List to store min, max, avg temps
    start_temps = []

    for date in dates:
        
        if date >= user_input:
            temp_dict = {}
            temp_dict["Minimum Temperature"] = temps(func.min)
            temp_dict["Maximum Temperature"] = temps(func.max)
            temp_dict["Average Temperature"] = temps(func.avg)
            start_temps.append(temp_dict)
    
    return jsonify(start_temps)


# @app.route("/api/v1.0/<start>/<end>")
# def dated_temps(end):
#     session = Session(engine)

#     session.close()


if __name__ == '__main__':
    app.run(debug=True)