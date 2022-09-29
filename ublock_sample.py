import os
import json
import snappy
import sqlite3
import foxyjunk

def main():
    # path to the uBlock Origin SQLite database file within your profile
    sqlite_path = "/home/username/snap/firefox/common/.mozilla/firefox/9is368xq.default-release-1663319000999/storage/default/moz-extension+++25b74cbe-5f3f-4500-8dc5-412c855fcaec^userContextId=4294967295/idb/3647222921wleabcEoxlt-eengsairo.sqlite"
    with sqlite3.connect(sqlite_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT object_store_id, key, data FROM object_data WHERE ('' || key || '') LIKE '0mpdbmTupsbhf';")
        for row in cursor:
            file_name = "{}_{}.json".format(row[0], row[1].hex())
            file_name = os.path.join(os.path.dirname(__file__), file_name)
            data = snappy.decompress(row[2])
            obj = foxyjunk.interpret(data)
            with open(file_name, "w") as file:
                file.write(json.dumps(obj, indent=2))
                print(f"Saved {file_name}")

if __name__ == "__main__":
    main()
