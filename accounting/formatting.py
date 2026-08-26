"""Consistent display formatting for accounting values."""

def money(value, symbol=False):
    text = "{:,.2f}".format(value)
    return "$" + text if symbol else text
