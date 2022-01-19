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
            batch.update(doc_crew, {
                "name": guild["name"],
                "last_updated": t,
            })

            doc_fight = doc_crew.collection('records').document(fs_configs.teamraid)
            batch.update(doc_fight, {
                "records": firestore.ArrayUnion([{
                    "ranking": guild["ranking"],
                    "point": guild["point"],
                    "datetime": t,
                }])
            })
        batch.commit()
    print("end get_crew")