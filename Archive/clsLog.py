import sys
import pprint
import datetime


class clslog:
    def __init__(self, logfile=None) -> None:
        if logfile == None:
            logfile = "Log.txt"
        self.lf = open(logfile, "w")
        now = datetime.datetime.now()
        self.lf.write(now.strftime(("%Y-%m-%d %H:%M:%S")))
        self.lf.write("\n\n")

    def log(self, **param):
        if cmLOG == True:
            caller = sys._getframe(2).f_code.co_name
            if caller == "<module>":
                caller = "__main__"
            funcname = sys._getframe(1).f_code.co_name
            self.lf.write("\n")
            self.lf.write(
                "Caller <{caller}>: Module <{funcname}>\n".format(
                    caller=caller, funcname=funcname
                )
            )
            if cmLOGPARAM == True:
                if len(param) != 0:
                    self.lf.write("Parameters\n")
                    for p in param:
                        self.lf.write("\t{p}\t{ty}\t".format(p=p, ty=type(param[p])))
                        pprint.pprint(param[p], stream=self.lf)

    def close(self):
        self.lf.close()


cmLOG = False
cmLOGPARAM = False
lg = clslog()
