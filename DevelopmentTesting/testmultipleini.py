class a:
    def init__a(self,text):
        print ("a - init")
        print (text)

class b:
    def init__b(self,text,value):
        print ("b - init")
        print (text,value)

class c(a,b):
    def __init__(self,text,value):
        super().init__a(text)
        super().init__b(text,value)

var = c("This is a test",123)
