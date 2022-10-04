class EE:
    pass

class OuterClass:
    def __init__(self):
        self.name = "John"
        self.ic = self.InnerClass(self)
    def clearname(self):
        self.name = ""

 
    class InnerClass(EE):
        def __init__(self, outerclass):
            self.oc = outerclass
  
        def setname(self,name):
            self.oc.name = name

        def callinnerclearname(self):
            self.oc.clearname()

o = OuterClass()
print (o.name)
o.ic.setname("Bill")
print (o.name)
o.ic.callinnerclearname()
print (o.name)
