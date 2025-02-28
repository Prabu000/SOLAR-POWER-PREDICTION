import warnings
import pandas as pd
import numpy as np
import MySQLdb
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import datetime
import time


warnings.filterwarnings("ignore", category=DeprecationWarning)


db_params = {
    "host": "localhost",
    "user": "root",
    "passwd": "",
    "db": "svm"
}


df = pd.read_csv("path for dataset")


df = df.fillna(0)


X = df.iloc[:, :5].values  
Y_temp = df.iloc[:, 5].values  
Y_ghi = df.iloc[:, 6].values  


x_train, x_test, y_temp_train, y_temp_test = train_test_split(X, Y_temp, test_size=0.1, random_state=42)
_, _, y_ghi_train, y_ghi_test = train_test_split(X, Y_ghi, test_size=0.1, random_state=42)


rfc1 = RandomForestRegressor()
rfc2 = RandomForestRegressor()

rfc1.fit(x_train, y_temp_train)
rfc2.fit(x_train, y_ghi_train)


y_temp_pred = rfc1.predict(x_test)
y_ghi_pred = rfc2.predict(x_test)

print("Temperature Prediction Metrics:")
print(f"Mean Absolute Error: {mean_absolute_error(y_temp_test, y_temp_pred)}")
print(f"Mean Squared Error: {mean_squared_error(y_temp_test, y_temp_pred)}")
print(f"R-squared: {r2_score(y_temp_test, y_temp_pred)}")

print("GHI Prediction Metrics:")
print(f"Mean Absolute Error: {mean_absolute_error(y_ghi_test, y_ghi_pred)}")
print(f"Mean Squared Error: {mean_squared_error(y_ghi_test, y_ghi_pred)}")
print(f"R-squared: {r2_score(y_ghi_test, y_ghi_pred)}")


print("Starting continuous prediction loop... Press Ctrl+C to stop.")
try:
    while True:

        next_time = datetime.datetime.now() + datetime.timedelta(minutes=10)
        next_time_features = [next_time.year, next_time.month, next_time.day, next_time.hour, next_time.minute]


        temp_pred = rfc1.predict([next_time_features])[0]
        ghi_pred = rfc2.predict([next_time_features])[0]


        f = 0.18 * 7.4322 * ghi_pred
        power = f * (0.95 * (temp_pred - 25))

        print(f"\nPredictions at {next_time.strftime('%Y-%m-%d %H:%M:%S')}:")
        print(f"Temperature: {temp_pred:.2f} °C")
        print(f"GHI: {ghi_pred:.2f} W/m²")
        print(f"Power: {power:.2f} W")

        try:
            db = MySQLdb.connect(**db_params)
            cur = db.cursor()

            sql = """INSERT INTO power_prediction (time_updated, Temperature, GHI, power)
                     VALUES (%s, %s, %s, %s)"""
            cur.execute(sql, (next_time.strftime("%Y-%m-%d %H:%M:%S"), temp_pred, ghi_pred, power))
            db.commit()
            print("Data successfully written to the database.")
        except MySQLdb.Error as e:
            print("Database error:", e)
            db.rollback()
        finally:
            if cur:
                cur.close()
            if db:
                db.close()


        time.sleep(1)

except KeyboardInterrupt:
    print("\nPrediction loop stopped by the user.")
