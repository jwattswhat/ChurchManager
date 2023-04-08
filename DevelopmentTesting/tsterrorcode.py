
class errorcode(Exception):
    def __init__(self,number):
        errormessage = _error(number)


class CustomException(Exception):
    """ABC"""
    def __init__(self, *args):
        super().__init__(*args)
        self.__str__ = self._wrapper(self.__str__)
    def _wrapper(self, f):
        def _inner(*args, **kwargs):
            return self.__doc__ + '\n' + f(*args, **kwargs)
        return _inner


t = {"a":1,"b":2,"c":3}
k = input("key")
try:
    print (t[k])
except KeyError as e:
    print ("error",e)
else:
    print (t[k])