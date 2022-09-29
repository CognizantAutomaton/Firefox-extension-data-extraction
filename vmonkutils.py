import snappy
import sqlite3
import foxyjunk
from collections import OrderedDict

def retrieve_userscript_data(sqlite_path, retrieval_key, retrieval_method):
    metadata = OrderedDict()
    userscript = ""
    data = dict()
    with sqlite3.connect(sqlite_path) as conn:
        # retrieve userscript meta data to find corresponding userscript suffix
        # in violentmonkey, all meta data keys start with 0tds
        cursor = conn.cursor()
        cursor.execute("SELECT key,data FROM object_data WHERE ('' || key || '') LIKE '0tds;%';")
        suffix = ""
        bytes = None
        decoded_key = ""
        decoded_suffix = ""
        for row in cursor:
            if len(suffix) > 0:
                break
            decoded_key = row[0].decode()
            if ";" in decoded_key:
                decoded_suffix = decoded_key.split(";")[1]
                bytes = snappy.decompress(row[1])
                metadata = foxyjunk.interpret(bytes)
                if type(metadata) is OrderedDict and metadata["meta"] != None and type(metadata["meta"]) is OrderedDict:
                    if retrieval_method == "namespace" and metadata["meta"]["namespace"] != None:
                        if metadata["meta"]["namespace"] == retrieval_key:
                            suffix = decoded_suffix
                    elif retrieval_method == "userscript_name" and metadata["meta"]["name"] != None:
                        if metadata["meta"]["name"] == retrieval_key:
                            suffix = decoded_suffix
        if len(suffix) == 0:
            if retrieval_method == "namespace":
                raise Exception(f"Cannot find userscript namespace '{retrieval_key}'")
            elif retrieval_method == "userscript_name":
                raise Exception(f"Cannot find userscript named '{retrieval_key}'")
        else:
            # use suffix obtained from above to retrieve userscript body
            # in violentmonkey, all userscript body keys start with 0dpef
            cursor.execute(f"SELECT data FROM object_data WHERE ('' || key || '') LIKE '0dpef;{suffix}';")
            for row in cursor:
                bytes = row[0]
            bytes = snappy.decompress(bytes)
            userscript = foxyjunk.interpret(bytes)
            # use suffix obtained from above to retrieve stored values for the userscript
            # in violentmonkey, all stored value keys start with 0wbm
            cursor.execute(f"SELECT data FROM object_data WHERE ('' || key || '') LIKE '0wbm;{suffix}';")
            for row in cursor:
                bytes = row[0]
            bytes = snappy.decompress(bytes)
            data = foxyjunk.interpret(bytes)
    return [metadata, userscript, data]

def get_data_by_namespace(sqlite_path, namespace):
    return retrieve_userscript_data(sqlite_path, namespace, "namespace")

def get_data_by_userscript_name(sqlite_path, userscript_name):
    return retrieve_userscript_data(sqlite_path, userscript_name, "userscript_name")