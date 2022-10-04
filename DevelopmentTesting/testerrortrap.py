from clsError import clsError

try: 
    raise clsError("Test")
except clsError as err:
    print (err)
except ValueError as err:
    print ("ValueError:",err)
except Exception as err:
    print ("Exception:",err)