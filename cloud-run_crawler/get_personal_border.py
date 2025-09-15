import json
import gbf_request
import fs_configs
from google.cloud import firestore

ranks = [2000]
ranks.extend(range(5000, 370001, 5000))

def get_personal_border(t):
    print("start get_personal_border")

    rt = {}
    for v in ranks:
        pageno = v / 10
        url = "/rest_ranking_user/detail/%d/0" % pageno
        try:
            resp = gbf_request.get(url)
            resj = json.loads(resp)
            for player in resj["list"]:
                if player["rank"] == str(v):
                    rt[player["rank"]] = int(player["point"])
                    break
            rt["datetime"] = t
        except Exception as e:
            print(json.dump({"error":str(e),"resp":resp}))
            raise e

    doc = fs_configs.db.collection('personal_border').document(fs_configs.teamraid)
    doc.set({'records': firestore.ArrayUnion([rt])}, merge=True)

    print("end get_personal_border")