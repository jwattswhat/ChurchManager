class clsChoicesList():
    separator = "-"

    def __init__(self):
        self.display = []
        self.fields = []
    def setseparator(self,separator):
        self.separator = separator

    def addchoice(self,fields):
        self.display.append(self.combinefields(fields))
        self.fields.append(fields)

    def getdisplay(self,n=0):
        return self.display[n]

    def getfields(self,n=0):
        return self.fields[n]

    def getfieldsbydisplay(self,display):
        for d in range(len(self.display)):
            if self.display[d] == display:
                return self.fields[d]
                break
        return None

    def combinefields(self,fields):
        combine = ""
        for f in fields:
            if combine != "":
                combine = combine + self.separator
            combine = combine + f
        return combine

    def getfieldcombine(self,n=0):
        combine = ""
        for f in self.fields[n]:
            if combine != "":
                combine = combine + self.separator
            combine = combine + f
        return combine

    def len(self):
        return len(self.display)

fields = [
    ["0"],
    ["1","Test"],
    ["2","Test","Test"],
    ["3","Test","Test","Test"]
]
l = clsChoicesList()

for i in range(len(fields)):
    l.addchoice(fields[i])

for i in range(l.len()):
    display = l.getdisplay(i)
    print (display)
    print (l.getfieldsbydisplay(display))
