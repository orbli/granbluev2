import datetime
from google.cloud import firestore

PROJECT = 'granblue-247222'
REGION = 'asia-northeast1'
SCHEDULER_JOB = 'cloud-run-crawler-scheduler-trigger'

db = firestore.Client(project=PROJECT)
cookie = ''
teamraid = ''
useragent = ''


def get_configs():
    """Derive the active raid from configs/history date ranges (public_config is
    retired - history is now the single source of truth for "which raid, when").
    Returns (active_raid_or_None, latest_event_end_or_None) and loads the
    cookie/useragent secrets from private_config into module globals."""
    now = datetime.datetime.now(datetime.timezone.utc)
    hist = db.collection('configs').document('history').get().to_dict() or {}
    global teamraid
    teamraid = None
    latest_end = None
    for key, val in hist.items():
        dates = val.get('date')
        if not isinstance(dates, list) or len(dates) < 2:
            continue
        start, end = dates[0], dates[1]
        if start <= now <= end:
            teamraid = key
        if latest_end is None or end > latest_end:
            latest_end = end
    print("active teamraid: %s" % teamraid)

    doc = db.collection('configs').document('private_config').get().to_dict()
    global cookie
    global useragent
    cookie = doc["cookie"]
    useragent = doc["useragent"]
    # don't log the cookie itself - it's the game session secret
    print("init cookie: %d chars" % len(cookie))
    print("init useragent: %s" % useragent)
    return teamraid, latest_end


def set_cookie():
    db.collection('configs').document('private_config').update({
        "cookie": cookie
    })
    print("store cookie: %d chars" % len(cookie))


def pause_scheduler():
    """Self-shutoff: pause the Cloud Scheduler trigger so the crawler stops
    firing (and stops costing money) once the event is over. Best-effort - needs
    the job service account to hold cloudscheduler.jobs.pause."""
    import google.auth
    import google.auth.transport.requests
    import requests
    try:
        creds, _ = google.auth.default()
        creds.refresh(google.auth.transport.requests.Request())
        url = ("https://cloudscheduler.googleapis.com/v1/projects/%s/locations/%s/jobs/%s:pause"
               % (PROJECT, REGION, SCHEDULER_JOB))
        r = requests.post(url,
                          headers={"Authorization": "Bearer %s" % creds.token},
                          timeout=30)
        print("pause_scheduler: HTTP %d %s" % (r.status_code, r.text[:200]))
    except Exception as e:
        print("pause_scheduler failed: %s" % e)
