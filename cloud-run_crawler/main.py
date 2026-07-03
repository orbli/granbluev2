import fs_configs
import get_personal_border
import get_crew
import datetime
import os

def main():
    ts = datetime.datetime.now(datetime.timezone.utc)
    active, latest_end = fs_configs.get_configs()

    if active is None:
        # now() is outside every event's [start, end] window - don't crawl. This
        # alone stops the expensive per-page writes when no event is running.
        if latest_end is not None and ts > latest_end + datetime.timedelta(hours=1):
            # >1h past the last event's end: turn ourselves off so we stop firing.
            print("event ended >1h ago; pausing scheduler")
            fs_configs.pause_scheduler()
        else:
            print("no active raid; skipping crawl")
        return

    task_index = int(os.environ.get("CLOUD_RUN_TASK_INDEX", 0))
    try:
        if task_index == 0:
            get_personal_border.get_personal_border(ts)
        elif task_index == 1:
            get_crew.get_crew(ts)
        print('success')
    finally:
        fs_configs.set_cookie()

if __name__ == "__main__":
    main()
