from collections import OrderedDict

def interpret(data):
    """Interprets uncompressed SQLite
    
    Parameters
    ----------
    input : data (byte array)
        The uncompressed data from the SQLite table.
        Decompression should be performed via snappy.

    Returns
    ------
    output : obj
        Usually a dictionary, but not exclusively.
    """

    segment = []
    stack = []
    curr = None
    FlagRemoveKey = False
    FlagOpenObject = False
    FlagCloseObject = False
    key = ""
    obj = None
    offset = 0
    while offset < len(data):
        segment = data[offset:offset+8]
        datatype = int.from_bytes(segment[4:8], "little")
        if datatype == 0xfff10000:
            curr = None
        elif datatype == 0xffff0000: # null
            curr = None
        elif datatype == 0xffff0001: # flag remove previously added key
            FlagRemoveKey = True
        elif datatype == 0xffff0002: # boolean
            curr = segment[0] == 1
        elif datatype == 0xffff0003: # int 32
            curr = int.from_bytes(segment[0:4], "little")
        elif datatype == 0xffff0004: # string
            ItemCount = int.from_bytes(segment[0:4], "little") & 0x00ffffff
            if segment[3] == 0x80: # UTF-8
                curr = bytearray(data[offset+8:offset+8+ItemCount]).decode("utf-8")
            else: # UTF-16
                ItemCount *= 2
                curr = bytearray(data[offset+8:offset+8+ItemCount]).decode("utf-16")
            offset += ItemCount
            if ItemCount % 8 != 0:
                offset += 8 - (ItemCount % 8)
        elif datatype == 0xffff0007: # array
            ItemCount = int.from_bytes(segment[0:4], "little")
            curr = { "FindKey": True, "Object": [] }
            FlagOpenObject = True
        elif datatype == 0xffff0008: # dictionary
            curr = { "FindKey": True, "Object": OrderedDict() }
            FlagOpenObject = True
        elif datatype == 0xffff0013: # flag end of array/dictionary
            curr = stack[-1]["Object"]
            stack.pop()
            FlagCloseObject = True
        else:
            try:
                # IEEE-754 64-bit floating-point
                curr = struct.unpack('<d', bytes(segment))[0]
            except:
                # fallback
                curr = ''.join("{:02X}".format(c) for c in reversed(segment))
        if curr != None or len(stack) > 0:
            if FlagOpenObject:
                stack.append(curr)
                FlagOpenObject = False
            else:
                if len(stack) > 0:
                    if FlagRemoveKey:
                        key = next(reversed(stack[-1]["Object"]))
                        stack[-1]["Object"].pop(key)
                        FlagRemoveKey = False
                    elif stack[-1]["FindKey"]:
                        key = str(curr)
                        if type(stack[-1]["Object"]) is OrderedDict:
                            stack[-1]["Object"][key] = None
                    else:
                        if FlagCloseObject:
                            key = next(reversed(stack[-1]["Object"]))
                            FlagCloseObject = False
                        if type(stack[-1]["Object"]) is OrderedDict:
                            stack[-1]["Object"][key] = curr
                        else:
                            stack[-1]["Object"].append(curr)
                    stack[-1]["FindKey"] = not stack[-1]["FindKey"]
                else:
                    obj = curr
        offset += 8
    return obj
