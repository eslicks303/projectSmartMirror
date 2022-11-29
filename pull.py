import mysql.connector
import json
import collections

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="test123",
        database="Mirror"
    )

    cursor = mydb.cursor()

    cursor.execute("SELECT * FROM mirrorSettings")

    row = cursor.fetchone()

    objects_list = []
    d = collections.OrderedDict()
    d["hours"] = [row[1], row[5], row[9]]
    d["minutes"] = [row[2], row[6], row[10]]
    d["seconds"] = [row[3], row[7], row[11]]
    d["toggles"] = [row[4], row[8], row[12]]
    d["layout"] = row[13]
    d["city"] = row[14]
    d["zip"] = row[15]
    d["name"] = row[16]
    d["device"] = row[17]
    d["link"] = row[18]
    d["accessToken"] = row[19]
    d["expiry"] = row[20]
    d["refreshToken"] = row[21]
    d["scopes"] = row[22]
    objects_list.append(d)

    j = json.dumps(objects_list)
    with open("data.js", "w") as f:
        f.write(j)

except mysql.connector.Error as e:
    print("Error reading the data", e)

finally:
    mydb.close()
    cursor.close()