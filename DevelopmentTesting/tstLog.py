import sys
import pprint

class clslog():
    def __init__(self,logfile=None) -> None:
        if logfile == None:
            logfile = "cmLog.txt"
        self.lf = open(logfile,"w")

    def log(self,**param):
        if cmLOG == True:
            caller = sys._getframe(2).f_code.co_name
            if caller == "<module>":
                caller = "__main__"
            funcname = sys._getframe(1).f_code.co_name
            self.lf.write("\n")
            self.lf.write("Caller <{caller}>: Module <{funcname}>\n".format(caller=caller,funcname=funcname))
            if len(param) != 0:
                self.lf.write("Parameters\n")
                for p in param:
                    self.lf.write("\t{p}\t{ty}\t".format(p=p, ty=type(param[p])))
                    pprint.pprint(param[p],stream=self.lf)

    def close(self):
        self.lf.close()

cmLOG = True
lg = clslog()

def someroutine(arg1,arg2,arg3,arg4):
    lg.log(arg1=arg1,arg2=arg2,arg3=arg3,arg4=arg4)
    nested()

    return True

def nested():
    lg.log()
    doublenested()

def doublenested():
    lg.log()

someroutine("test",1,{"a":1,"b":2},[0,1,2,3])
lg.close()
