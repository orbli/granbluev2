import fs_configs
import get_personal_border
import get_crew
# from google.cloud import firestore
import datetime
# import googlecloudprofiler

# try:
#     googlecloudprofiler.start(
#         service='crawler-profiler',
#         service_version='1.0.1',
#         verbose=3,
#         project_id='granblue-247222',
#     )
# except (ValueError, NotImplementedError) as exc:
#     print(exc)  # Handle errors here

def crawling(request):
    ts = datetime.datetime.now()
    fs_configs.get_configs()
    try:
        get_personal_border.get_personal_border(ts)
        get_crew.get_crew(ts)
        return 'success'
    finally:
        fs_configs.set_cookie()