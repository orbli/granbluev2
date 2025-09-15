import fs_configs
import get_personal_border
import get_crew
import datetime

def main():
    ts = datetime.datetime.now()
    fs_configs.get_configs()
    try:
        get_personal_border.get_personal_border(ts)
        get_crew.get_crew(ts)
        print('success')
    finally:
        fs_configs.set_cookie()

if __name__ == "__main__":
    main()
