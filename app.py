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
def Home():
    return(f"Available Routes:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f"/api/v1.0/stations<br/>"
           f"/api/v1.0/tobs<br/>"
           f"/api/v1.0/temp/start/end")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    first_date = recent_date - dt.timedelta(days=365)
    precipitation_results = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).order_by(Measurement.date).all())
    return jsonify(precipitation_results)
 
@app.route("/api/v1.0/stations")
def stations ():
    session  = Session(engine)
    stations_results = session.query(Station.station, Station.name).all()
    return jsonify(stations_results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    first_date = recent_date - dt.timedelta(days=365)
    stations = (session.query(Measurement.station, func.count).filter(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
    best_station = ([stations[0]])
    tobs_stadistics = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs).filter(Measurement.station == best_station).all()
    best_station_tobs = session.query(Measurement.tobs).filter(Measurement.station == best_station).filter(Measurement.date >= first_date).all()
    return jsonify(best_station_tobs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start(start = none, end = none):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)        
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(results)

if __name__ == '__main__':
    app.run()
