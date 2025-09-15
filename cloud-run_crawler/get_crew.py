import fs_configs
import gbf_request
import json
from google.cloud import firestore

ranks = 5500

def get_crew(t):
    print("start get_crew")
    for i in range(ranks//10):
        i = i + 1
        if i % 50 == 0:
            print("Crawling %d" % i)
        batch = fs_configs.db.batch()
        url = "/rest/ranking/totalguild/detail/%d/0" % i
        resp = gbf_request.get(url)
        resj = json.loads(resp)
        for guild in resj["list"]:
            doc_crew = fs_configs.db.collection('crew').document(guild['id'])
            batch.set(doc_crew, {
                "name": guild["name"],
                "last_updated": t,
            }, merge=True)

            doc_fight = doc_crew.collection('records').document(fs_configs.teamraid)
            batch.set(doc_fight, {
                "records": firestore.ArrayUnion([{
                    "ranking": int(guild["ranking"]),
                    "point": int(guild["point"]),
                    "datetime": t,
                }])
            }, merge=True)
        batch.commit()
    print("end get_crew")