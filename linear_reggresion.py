import warnings
import pandas as pd
import numpy as np
import MySQLdb
import datetime
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()


db = MySQLdb.connect(host="localhost", user="root", passwd="", db="erode_solar")
cur = db.cursor()


df = pd.read_csv("path for dataset")
df = df.fillna(0)
print(df.describe())


cols_X = [0, 1, 2, 3, 4]
cols_Y_temp = [5]
cols_Y_ghi = [6]

X = df[df.columns[cols_X]].apply(pd.to_numeric, errors='coerce').values
Y_temp = df[df.columns[cols_Y_temp]].apply(pd.to_numeric, errors='coerce').values
Y_ghi = df[df.columns[cols_Y_ghi]].apply(pd.to_numeric, errors='coerce').values


x_train, x_test, y_temp_train, y_temp_test = train_test_split(X, Y_temp, random_state=42)
_, _, y_ghi_train, y_ghi_test = train_test_split(X, Y_ghi, random_state=42)


lr_temp = LinearRegression()
lr_ghi = LinearRegression()

lr_temp.fit(x_train, y_temp_train)
lr_ghi.fit(x_train, y_ghi_train)

print("Models trained successfully. Starting prediction loop...")

while True:

    nextTime = datetime.datetime.now() + datetime.timedelta(minutes=10)
    now_numeric = list(map(int, [nextTime.year, nextTime.month, nextTime.day, nextTime.hour, nextTime.minute]))


    temp_prediction = lr_temp.predict([now_numeric])[0][0]
    ghi_prediction = lr_ghi.predict([now_numeric])[0][0]


    f = 0.18 * 7.4322 * ghi_prediction
    insi = temp_prediction - 25
    midd = 0.95 * insi
    power = f * midd


    time_now_str = nextTime.strftime("%Y-%m-%d %H:%M")
    power_float = float(power)
    temp_float = float(temp_prediction)
    ghi_float = float(ghi_prediction)

    print(f"Time: {time_now_str}")
    print(f"Temperature: {temp_float:.2f} °C")
    print(f"GHI: {ghi_float:.2f} W/m²")
    print(f"Power: {power_float:.2f} W")


    sql_query = """INSERT INTO power_prediction (time_updated, Temperature, GHI, power) VALUES (%s, %s, %s, %s)"""
    values = (time_now_str, temp_float, ghi_float, power_float)

    try:
        print("Writing to the database...")
        cur.execute(sql_query, values)
        db.commit()
        print("Write complete")
    except Exception as e:
        db.rollback()
        print("We have a problem:", e)

    time.sleep(1) 
