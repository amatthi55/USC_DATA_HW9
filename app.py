from flask import Flask, jsonify

import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc


#calc_temps function is used in the <start><end> endpoint

def calc_temps(start_date, end_date):
    
    #queries for temps in date range
    rows = session.query(Measurements.date, Measurements.tobs).filter(Measurements.date >= '{}'.format(start_date))\
            .filter(Measurements.date <= '{}'.format(end_date)).all()
    
    #create dataframe from queried data
    date, temp = zip(*rows)

    temp_DF = pd.DataFrame({'date':list(date),'temp':list(temp)})
    
    #find mean, min, max of temp data
    Mean = temp_DF['temp'].mean()
    Min = temp_DF['temp'].min()
    Max = temp_DF['temp'].max()

    Temp = {'TAVG': Mean, 'TMIN': Min,'TMAX': Max}

    return Temp




#boiler plate code to start database session and create table objects
engine = create_engine("sqlite:///hawaii.sqlite")
session = Session(engine)
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurements = Base.classes.measurements
Stations = Base.classes.stations

#Flask setup 

app = Flask(__name__)

#Flask routes 

@app.route("/")

def Welcome():
    return 'Welcome to Hawaii Climate API. Use extension api/v1.0/precipitation for last year of\
    precipitation data. Use extension api/v1.0/stations for a list of the weather stations in Hawaii. \
    Use extension api/v1.0/tobs for the last 12 months of temperature measurements. \
    Type api/v1.0/ and add a date in the format YYYY-MM-DD for all temp measurements from that day on.\
    For a range of temperature measurements type api/v1.0/YYYY-MM-DD/YYYY-MM-DD where the second date is\
    the end date.'

@app.route("/api/v1.0/precipitation")

def precip():
    #queries database for last year of precipitation data
    rows = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date > '2016-08-23').all()

    #turn data into dictionary form for jsonify function
    date, precip = zip(*rows)
    data_DF = pd.DataFrame({'date':list(date),'precip':list(precip)})
    data_dict = data_DF.to_dict(orient='records')

    return jsonify(data_dict)


@app.route("/api/v1.0/stations")

def stations():
    rows = session.query(Stations.station).all()

    station = zip(*rows)

    return jsonify(list(station))


@app.route("/api/v1.0/tobs")

def tobs():
    rows = session.query(Measurements.tobs)\
        .filter(Measurements.date > '2016-08-23').all()

    tobs = zip(*rows)

    return jsonify(list(tobs))


@app.route("/api/v1.0/<start>")

def tobs_start(start):

    #use calc_temps function to find all rainfall data (max,min,mean) since start date

    temp_range_dict = calc_temps(start, '2017-12-31')

    #change values in min,max,mean dictionary to floats so jsonify can turn dict into json
    for key in temp_range_dict:
        temp_range_dict[key] = float(temp_range_dict[key])
    return jsonify(temp_range_dict)


@app.route("/api/v1.0/<start>/<end>")

def tobs_range(start,end ):

    #use calc_temps function to find all rainfall data between start date and end date

    temp_range_dict = calc_temps(start,end)

    #change values in min,max,mean dictionary to floats so jsonify can turn dict into json
    for key in temp_range_dict:
        temp_range_dict[key] = float(temp_range_dict[key])
    return jsonify(temp_range_dict)        


if __name__ == "__main__":
    
    app.run(debug=True)