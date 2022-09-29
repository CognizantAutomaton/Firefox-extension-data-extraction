import vmonkutils

def main():
    # path to the Violentmonkey SQLite database file within your profile
    sqlite_path = "/home/username/snap/firefox/common/.mozilla/firefox/9is368xq.default-release-1663319000999/storage/default/moz-extension+++95b600ba-c9ca-48f3-9086-f71968e53054^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
    userscript_info = vmonkutils.get_data_by_userscript_name(sqlite_path, "your userscript name") # the @name field of the userscript metadata
    #userscript_info = vmonkutils.get_data_by_namespace(sqlite_path, "your userscript namespace") # the @namespace field of the userscript metadata
    print(userscript_info)

if __name__ == "__main__":
    main()
