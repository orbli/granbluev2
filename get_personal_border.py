import json
import gbf_request
import fs_configs
from google.cloud import firestore

ranks = [2000]
ranks.extend(range(5000, 300000, 5000))

def get_personal_border(t):
    print("start get_personal_border")

    rt = {}
    for v in ranks:
        pageno = v / 10
        url = "/rest_ranking_user/detail/%d/0" % pageno
        resp = gbf_request.get(url)
        resj = json.loads(resp)
        for player in resj["list"]:
            if player["rank"] == str(v):
                rt[player["rank"]] = int(player["point"])
                break
        rt["datetime"] = t

    print("personal_border entry:", rt)
    doc = fs_configs.db.collection('personal_border').document(fs_configs.teamraid)
    doc.update({'records': firestore.ArrayUnion([rt])})

    print("end get_personal_border")