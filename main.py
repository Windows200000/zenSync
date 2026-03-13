import pycron
import os
import shutil
import psutil  # pip install psutil
from datetime import datetime

is_zen_running = False

def main() -> None:
    pc_id = "desktop"
    global is_zen_running
    is_zen_running = check_zen_running()
    print(is_zen_running)
    pycron.start()

@pycron.cron("* * * * * */5")
async def check_and_backup(timestamp: datetime):
    global is_zen_running
    main_profile = "mx9dcbsw.Default (release)"
    print(f"running at {timestamp}, zen_running: {is_zen_running}")
    if not is_zen_running:
        is_zen_running = check_zen_running()
        if is_zen_running:
            print("zen started")
    else:
        is_zen_running = check_zen_running()
        if not is_zen_running:
            print("zen stopped")
            copy_zen_appdata(main_profile)
            print("backup finished")
    

def check_zen_running(process_name: str = "zen.exe") -> bool:
    """Return True if zen.exe is running, else False."""
    for proc in psutil.process_iter(attrs=["name"]):
        try:
            if proc.info.get("name", "").lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Skip problematic processes [web:20]
    return False

def copy_zen_appdata(profile: str, backup_dir: str = "C:\\Users\\Arne\\OneDrive\\Desktop\\Coding\\zenSync") -> str:
    """
    Copy %APPDATA%/Zen to backup_root/Zen.
    Returns destination path. Creates directories as needed.
    """
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not set")

    src_dir = os.path.join(appdata, "Zen", "Profiles", profile)
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"Source folder not found: {src_dir}")

    backup_file = "zen-sessions.jsonlz4"

    src_sessions_json = os.path.join(src_dir, backup_file)
    if not os.path.isfile(src_sessions_json):
        raise FileNotFoundError(f"Sessions file not found: {src_sessions_json}")

    dst_sessions_json = os.path.join(backup_dir, backup_file)

    shutil.copy(src_sessions_json, dst_sessions_json)
    return dst_sessions_json

if __name__ == "__main__":
    main()
