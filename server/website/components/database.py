# DataBase --------------------------------------------------------------------------------------------------------------

def connectDB():
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi
    from urllib.parse import quote_plus

    password = "TinusViburnum6%&"
    db_password = quote_plus(password)
    uri = f"mongodb+srv://develop:{db_password}@cluster0.nosda.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    myclient = MongoClient(uri, server_api=ServerApi('1'))
    
    mydb = myclient["dBndvis"]

    return mydb

# TimeSeries ---------------------------------------------------------

# Polygons ---------------------------------------------------------
def addInPolygons(intersection, date, poligon_json):
    print("addInPolygons ---------------")
    mydb = connectDB()
    mycol = mydb["polygons"]
    intersection["date"] = date
    attributes = ["sig_pac_code", "fertilitzable", "use", "plotId", "area", "sr", "dryType", "zv", "municipaly", "campaign"] 
    # sr strontium
    for attr in attributes:
        intersection[attr] = poligon_json[attr]
    mycol.insert_one(intersection)


def getPolygon(sigpac, date):
    mydb = connectDB()
    mycol = mydb["polygons"]
    polygon = mycol.find_one({"sig_pac_code": sigpac,
                              "date": date}, {"_id": 0})

    return polygon


def returnPolygons(date):
    mydb = connectDB()
    mycol = mydb["polygons"]
    polygons = mycol.find({"date": date}, {"_id": 0})
    polygons_list = [pol for pol in polygons] 

    return polygons_list


"""
polygons
crear índex: id_camp i data 
no fer camp únic pq pot haver diferent en dates
mydb.users.createIndex({ "email": 1 }, { unique: false });

timeSeries
índex: id_camp i periode
"""

