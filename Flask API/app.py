# Import the dependencies.
import pandas as pd
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

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///hawaii.sqlite")    

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(bind=engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available routes."""
    return (
        f"This website is an API for climate analysis of Hawaii.<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"/api/v1.0/tobs<br/><br/>"
        r"/api/v1.0/2010-01-01 to input start date<br/>"
        r"/api/v1.0/2010-01-01/2017-08-23 to input start and end dates <br/><br/>"
    )

# Return precipitation and date for the last year.
@app.route("/api/v1.0/precipitation")
def precipitation():

    prev_year_start = datetime.date(2017, 8, 23) - datetime.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
    filter(Measurement.date >= prev_year_start).\
    order_by(Measurement.date).\
    all()

    session.close()

    df = pd.DataFrame(results)
    data = df.to_dict(orient="records")
    return(jsonify(data))


# Return list of stations.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    df = pd.DataFrame(results).to_dict(orient="records")
    return(jsonify(df))


# Query dates and temperature observations of most active station for previous year.
# Return list of tobs for previous year.
@app.route("/api/v1.0/tobs")
def temp_observations():

    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).\
    all()

    top_station = most_active[0]
    top_id = top_station[0]

    prev_year_start = datetime.date(2017, 8, 23) - datetime.timedelta(days=365)
     
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == top_id).\
    filter(Measurement.date >= prev_year_start).all()

    session.close()

    df = pd.DataFrame(results).to_dict(orient="records")
    return(jsonify(df))


# Return min temp, avg temp, max temp for specified date ranges
@app.route("/api/v1.0/<start_date>")
def tobs_start(start_date):

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()

    session.close()

    min_temp, max_temp, avg_temp = results[0]
    start_date_results = {
        "min_temp": min_temp,
        "max_temp": max_temp,
        "avg_temp": avg_temp
    }

    df = pd.DataFrame([start_date_results])
    return(jsonify(df.to_dict(orient="records")))


@app.route("/api/v1.0/<start_date>/<end_date>")
def tobs_start_end(start_date, end_date):

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).\
    order_by(Measurement.date.asc()).all()

    session.close()

    min_temp, max_temp, avg_temp = results[0]
    date_range_results = {
        "min_temp": min_temp,
        "max_temp": max_temp,
        "avg_temp": avg_temp
    }

    df = pd.DataFrame([date_range_results])
    return(jsonify(df.to_dict(orient="records")))


if __name__ == '__main__':
    app.run(debug=True)