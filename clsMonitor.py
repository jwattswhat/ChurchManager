from screeninfo import get_monitors
import pprint


class clsMonitor:
    fontsize = 1
    monitor = {}

    def __init__(self):
        for m in get_monitors():
            if m.is_primary:
                self.monitor.update(
                    {
                        "primary": {
                            "name": m.name,
                            "primary": m.is_primary,
                            "width": m.width,
                            "height": m.height,
                            "width_in": m.width_mm * 0.039,
                            "height_in": m.height_mm * 0.039,
                            "pixelsperinch": [
                                int(m.width / (m.width_mm * 0.039)),
                                int(m.height / (m.height_mm * 0.039)),
                            ],
                        }
                    }
                )
                pointsperinch = 0.013
                fontinches = self.fontsize * pointsperinch
                pixelinchesx = self.monitor["primary"]["pixelsperinch"][0]
                pixelinchesy = self.monitor["primary"]["pixelsperinch"][1]
                fontsizepixelsx = pixelinchesx * fontinches * self.fontsize
                fontsizepixelsy = pixelinchesy * fontinches * self.fontsize
                self.monitor["primary"]["fontsizepixelsx"] = fontsizepixelsx
                self.monitor["primary"]["fontsizepixelsy"] = fontsizepixelsy

    #        pprint.pprint(self.monitor)

    def getfontpixelsx(self, fontsize):
        return self.monitor["primary"]["fontsizepixelsx"] * fontsize

    def getfontpixelsy(self, fontsize):
        return self.monitor["primary"]["fontsizepixelsy"] * fontsize


PMON = clsMonitor()
