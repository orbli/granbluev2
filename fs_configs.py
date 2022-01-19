from google.cloud import firestore

db = firestore.Client(project='granblue-247222')
cookie = ''
teamraid = ''
useragent = ''

def get_configs():
    doc = db.collection('configs').document('config').get().to_dict()
    global cookie
    global teamraid
    global useragent
    cookie = doc["cookie"]
    teamraid = doc["teamraid"]
    useragent = doc["useragent"]
    print("init cookie: %s" % cookie)
    print("init teamraid: %s" % teamraid)
    print("init useragent: %s" % useragent)


def set_cookie():
    db.collection('configs').document('config').update({
        "cookie": cookie
    })
    print("store cookie: %s" % cookie)
