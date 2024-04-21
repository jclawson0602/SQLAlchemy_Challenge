# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

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
measurement = Base.classes.measurement
station = Base.classes.station

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
def homepage():
    return(
    f"Welcome to our Climate API!<br/>"
    f"Please see below for our available routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end>"
)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculates the date 12 months prior to the most recent date of precipitation data
    most_recent_date = dt.date(2017,8,23)
    last_year_precipitation_date = most_recent_date - dt.timedelta(days=365)
    
    # Finds the date and precipitation for the last 12 months of data
    precipitation_query = session.query(measurement.date, measurement.prcp).filter(measurement.date <= most_recent_date).\
        filter(measurement.date >= last_year_precipitation_date)
    
    # Stores date and precipitation data in a list of dictionaries with date as the keys and precipitation as the values 
    precipitation_list = []
    for record in precipitation_query:
        prcp_dict = {record.date : record.prcp}
        precipitation_list.append(prcp_dict)    
    
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    # Returns all stations in the dataset
    all_stations = session.query(station.name).all()
    all_stations = list(np.ravel(all_stations))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Finds the most active station based on record counts
    most_active_station = session.query(measurement.station, func.count(measurement.station)).\
                group_by(measurement.station).order_by(func.count(measurement.station).desc())
    
    # Stores all stations retrieved from most_active_station into a list
    total_station_list = [station for station in most_active_station]
    
    # Calculates the date 12 months prior to the most recent date of the most active station
    most_recent_temp_date = dt.date(2017,8,18)
    last_year_temp_date = most_recent_temp_date - dt.timedelta(days=365)
    
    # Queries the date and temperature observations for the most-active station for the previous year
    most_active_station_query = session.query(measurement.date, measurement.tobs).filter(measurement.station == total_station_list[0][0]).\
                filter(measurement.date >= last_year_temp_date).filter(measurement.date <= most_recent_temp_date)
    
    # Appends temperature observations retrieved in most_active_station_query into a list
    temp_observations = []
    for temps in most_active_station_query:
        temp_observations.append(temps.tobs)
    
    return jsonify(temp_observations)

@app.route("/api/v1.0/<start>")
def temp_calcs_start(start):
    # Creates our session for this route to link our Python to the hawaii DB
    session = Session(engine)
    
    # Calculates the min, max, and average of temperatures for dates after the specified start date provided by the user
    temp_calcs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start)
    
    # Closes session
    session.close()
    
    # Stores temperature observations in a list
    temps_list = [temps for temps in temp_calcs]
    temps_list = list(np.ravel(temps_list))
    
    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_calcs_start_end(start, end):
    # Creates our session for this route to link our Python to the hawaii DB
    session = Session(engine)
    
    # Calculates the min, max, and average of temperatures for dates between the specified start and end dates provided by the user
    temp_calcs_2 = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end)

    # Closes session
    session.close()
    
    # Stores temperature observations in a list of tuples and converts them into a normal list
    temps_list_2 = [temps for temps in temp_calcs_2]
    temps_list_2 = list(np.ravel(temps_list_2))

    return jsonify(temps_list_2)

session.close()

if __name__ == "__main__":
    app.run(debug=True, port = 5001)
        