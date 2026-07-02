from google.cloud import firestore

db = firestore.Client(project='granblue-247222')
cookie = ''
teamraid = ''
useragent = ''

def get_configs():
    doc = db.collection('configs').document('public_config').get().to_dict()
    global teamraid
    teamraid = doc["teamraid"]
    print("init teamraid: %s" % teamraid)
    doc = db.collection('configs').document('private_config').get().to_dict()
    global cookie
    global useragent
    cookie = doc["cookie"]
    useragent = doc["useragent"]
    # don't log the cookie itself - it's the game session secret
    print("init cookie: %d chars" % len(cookie))
    print("init useragent: %s" % useragent)


def set_cookie():
    db.collection('configs').document('private_config').update({
        "cookie": cookie
    })
    print("store cookie: %d chars" % len(cookie))
