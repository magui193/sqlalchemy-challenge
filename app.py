from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import datetime as dt
import numpy as np
import pandas as pd
from datetime import timedelta

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

#set classes
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#Flask
app = Flask(__name__)

#Route home
@app.route("/")
#def Home():
    #return(f"Available Routes:<br/>"
           #f"/api/v1.0/precipitation<br/>"
           #f"/api/v1.0/stations<br/>"
           #f"/api/v1.0/tobs<br/>"
           #f"/api/v1.0/temp/start/end")

def home():
    homepageHTML = (
        f"<h1>Welcome to the Hawaii Climate Analysis API!</h1>"
        f"<h2>Available API Endpoints:</h2><br/>"

        f"<h3>🌧 PRECIPITATION:</h3>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/><br/><br/><br/>"

        f"<h3>📡 STATIONS:</h3>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/><br/><br/><br/>"
        
        f"<h3>🌡 TEMPERATURE OBSERVATIONS:</h3>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/><br/><br/><br/>"

        f"<h3>📆 SPECIFIED START DATE:</h3>"
        f"/api/v1.0/temp/YYYY-MM-DD<br/><br/><br/><br/>"

        f"<h3>📆 SPECIFIED START DATE & END DATE:</h3>"
        f"/api/v1.0/temp/YYYY-MM-DD/YYYY-MM-DD"
    )
    return homepageHTML

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    first_date = recent_date - dt.timedelta(days=365)
    precipitation_results = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).order_by(Measurement.date).all())
    precipitation_results_dict = {}
    for result in precipitation_results:
        precipitation_results_dict[result[0]] = result[1]
    session.close()
    return jsonify(precipitation_results_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = (session.query(Measurement.station).filter(Measurement.station == Station.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all())
    stations_query_list = [station[0] for station in stations_query]
    session.close()
    return jsonify(stations_query_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = (session.query(Measurement.station).filter(Measurement.station == Station.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all())[0][0]
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    temperature_analysis_mas = (session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date > last_year).filter(Measurement.station == most_active_station).order_by(Measurement.date).all())
    temperature_list =[]
    for station, record_date, temp in temperature_analysis_mas:
        temperature_list.append({
            "date":record_date,
            "temp":temp
        })
    session.close()
    return jsonify(temperature_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start_and_end(start='YYYY-MM-DD', end='YYYY-MM-DD'):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)        
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 