import fs_configs
import get_personal_border
import get_crew
import datetime
import os

def main():
    ts = datetime.datetime.now()
    fs_configs.get_configs()
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
