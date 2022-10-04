from CMFormDescriptions import frmAltReadingFORM
import pprint

def update (description, key, value):
    description.update({key:value})
    return description

pp = pprint
pp.pprint(frmAltReadingFORM)

pp.pprint(update(
    update(frmAltReadingFORM,"name","new name"),
    "title",
    "new title"))
