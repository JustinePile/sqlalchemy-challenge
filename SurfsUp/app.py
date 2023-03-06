#################################################
#              Import Dependencies              #
#################################################
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
#                Database Setup                 #
#################################################

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
#                 Flask Setup                   #
#################################################

app = Flask(__name__)


#################################################
#                 Flask Routes                  #
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<p><b>Available Routes:</b><br/><br/></p>"
        f"Precipitation analysis for last 12 months of data:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of stations:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Dates and temperature observations of the most-active station for the previous year of data:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Returns a list of min, avg, and max temps for specified start or start/stop range in YYYY-MM-DD format:<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Finds the most recent date in the data set
    most_recent_date = session.query(Measurement.date).\
        group_by(Measurement.date).\
        order_by(Measurement.date.desc()).first()

    # Calcuates date one year prior from last date in dataset
    date = most_recent_date[0]
    date = dt.datetime.strptime(date, "%Y-%m-%d")
    one_year_ago_date = date - dt.timedelta(days=365)
    one_year_ago_date

    # Query for precipitation date from last 12 months
    last_12_mos = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_year_ago_date).all()

    # Close session to DB
    session.close()

    # Create a dictionary from the row data and append to a list
    precipitation_list = []
    for date, prcp in last_12_mos:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["preciptation"] = prcp
        precipitation_list.append(precip_dict)

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for all stations
    all_stations = session.query(Station.name).all()

    # Close session to DB
    session.close()

    # Create a list from the row data
    station_list = []
    for row in all_stations:
        station_list.append(row[0])

    return station_list

@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to find the most active stations (i.e. what stations have the most rows) 
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                       group_by(Measurement.station).\
                       order_by(func.count(Measurement.station).desc()).all()
    
    # Gets station ID and assigns it to variable first_station
    i=0
    for item in most_active_stations:
        while i < 1:
            most_active_station = (item[0])
            i += 1

    # Finds the most recent date in the data set
    most_recent_date = session.query(Measurement.date).\
        group_by(Measurement.date).\
        order_by(Measurement.date.desc()).first()

    # Calcuates date one year prior from last date in dataset
    date = most_recent_date[0]
    date = dt.datetime.strptime(date, "%Y-%m-%d")
    one_year_ago_date = date - dt.timedelta(days=365)
    one_year_ago_date

    # Query for dates and temperature observations of the most-active station for the previous year of data
    last_12_mos_most_active_station = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_year_ago_date).all()

    # Close session to DB
    session.close()

    # Create a dictionary from the row data and append to a list
    temp_list = []
    for date, tobs in last_12_mos_most_active_station:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    if end:
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    else:
        end_date = dt.datetime.now()

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    ranged_query = session.query(Station.name, \
                                func.min(Measurement.tobs), \
                                func.max(Measurement.tobs), \
                                func.avg(Measurement.tobs)).\
                                filter(Measurement.station == Station.station).\
                                filter(Measurement.date >= start_date).\
                                filter(Measurement.date <= end_date).\
                                group_by(Station.name).all()
                                
    # Close session to DB
    session.close()
    
    # Create a dictionary from the row data and append to a list
    data = []
    for name, min, max, avg in ranged_query:
        data_dict = {}
        data_dict["name"] = name
        data_dict["min"] = min
        data_dict["max"] = max
        data_dict["avg"] = avg
        data.append(data_dict)

    return jsonify(data)



#################################################
#                   Run Flask                   #
#################################################

if __name__ == '__main__':
    app.run(debug=True)
