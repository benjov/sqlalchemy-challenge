import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///DATA/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to the table
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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    
    # Perform a query to retrieve the data and precipitation scores
    sel = [Measurement.date, Measurement.prcp]
    Prc_DF = pd.DataFrame(session.query(*sel).\
                      filter(Measurement.date > '2016-08-23').\
                      order_by(Measurement.date.asc()).all())
    session.close()

    # Convert list of tuples into normal list
    Prc_DF_list = list(np.ravel(Prc_DF))

    return jsonify(Prc_DF_list)

#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.
    Stations_G = session.query(Measurement.station, func.count(Measurement.station)).\
                           group_by(Measurement.station).\
                           order_by(func.count(Measurement.station).desc())

    session.close()
    
    # Convert list of tuples into normal list
    Stations_G_list = list(np.ravel(Stations_G))

    return jsonify(Stations_G_list)

#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """query for the dates and temperature observations from a year from the last data point."""
    
    # Choose the station with the highest number of temperature observations.
    Temp_most_active = pd.DataFrame(session.query(Measurement.tobs).\
                                              filter(Measurement.date > '2016-08-23').\
                                              filter_by(station = 'USC00519281'))

    session.close()

    # Convert list of tuples into normal list
    Temp_most_active_list = list(np.ravel(Temp_most_active))

    return jsonify(Temp_most_active_list)

#################################################
@app.route("/api/v1.0/<start>/<end>")
def start(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
    # Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation
    sel = [Measurement.station, Station.name, Measurement.prcp, Station.latitude, Station.longitude, 
           Station.elevation, Measurement.tobs]
    start_date = start
    end_date = end
    Match_Data = session.query(*sel).filter(Measurement.station == Station.station).\
                           filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).\
                           order_by(Measurement.prcp.desc()).all()
    
    session.close()

    # Convert list of tuples into normal list
    Match_Data_list = list(np.ravel(Match_Data))

    return jsonify(Match_Data_list)


if __name__ == '__main__':
    app.run(debug=True)
