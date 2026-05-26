import ctypes
import os
import shutil
import sys
import threading


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    except Exception as e:
        print(f"[ERROR] 无法提升至管理员权限: {e}")
        os.system("pause")
        sys.exit(1)


def printLock(message):
    with print_lock:
        print(message)


def deleteFilesWithExtension(directory, extension):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                filePath = os.path.join(root, file)
                try:
                    printLock(f"Deleting: {filePath}")
                    os.remove(filePath)
                    printLock(f"Deleted: {filePath}")
                except OSError as e:
                    printLock(f"Error while deleting\n{filePath}\n{e}")


def deleteDirectory(directory):
    try:
        printLock(f"Deleting: {directory}")
        shutil.rmtree(directory)
        printLock(f"Deleted: {directory}")
    except Exception as e:
        printLock(f"Error deleting {directory}:\n{e}")


systemDrive = os.environ.get("systemdrive")
winDir = os.environ.get("windir")
userProfile = os.environ.get("userprofile")
systemDrive += "\\"

filesDict = {
    systemDrive: [".tmp", "._mp", ".log", ".gid", ".chk", ".old"],
    winDir: [".bak"],
}

directoriesDict = {
    systemDrive: ["recycled"],
    winDir: ["prefetch", "temp"],
    userProfile: [
        "cookies",
        "recent",
        "Local Settings\\Temporary Internet Files",
        "Local Settings\\Temp",
    ],
}

print_lock = threading.Lock()


if __name__ == "__main__":
    if not is_admin():
        print("[WARNING] 当前未以管理员权限运行")
        print("[WARNING] 部分系统缓存目录需要管理员权限才能清理")
        print()
        print("  请选择:")
        print("    1. 以管理员身份重新运行")
        print("    2. 退出程序")
        print()
        choice = input("  请输入选项 (1/2): ").strip()
        if choice == "1":
            print("[INFO] 正在请求管理员权限...")
            run_as_admin()
            sys.exit(0)
        else:
            print("[INFO] 用户选择退出，程序结束")
            os.system("pause")
            sys.exit(0)

    print("[INFO] 已获取管理员权限，开始清理...")

    threads = []

    diry = os.path.join(winDir, "SoftwareDistribution", "Download")
    t = threading.Thread(target=deleteDirectory, args=(diry,))
    threads.append(t)

    for path, exts in filesDict.items():
        for ext in exts:
            t = threading.Thread(target=deleteFilesWithExtension, args=(path, ext))
            threads.append(t)

    for path, directs in directoriesDict.items():
        for direct in directs:
            full_path = os.path.join(path, direct)
            t = threading.Thread(target=deleteDirectory, args=(full_path,))
            threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("Success free C space")
    os.system("pause")
