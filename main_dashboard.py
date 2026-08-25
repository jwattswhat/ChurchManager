"""Brand and configure ChurchManager's compact daily-work dashboard."""

import io

import wx


def _church_identity(connection):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT Church, Logo FROM tblChurch "
            "WHERE ID > 0 "
            "ORDER BY CASE WHEN Logo IS NULL OR OCTET_LENGTH(Logo)=0 "
            "THEN 1 ELSE 0 END, ID LIMIT 1"
        )
        return cursor.fetchone() or ("ChurchManager", None)
    finally:
        cursor.close()


def apply_congregation_branding(main_form, connection):
    """Display the first configured congregation name and logo prominently."""
    church_name, logo_bytes = _church_identity(connection)
    name = main_form.CONTROLID["lblChurchName"]
    name.SetLabel(church_name or "ChurchManager")
    name_font = name.GetFont()
    name_font.SetWeight(wx.FONTWEIGHT_BOLD)
    name_font.SetPointSize(name_font.GetPointSize() + 2)
    name.SetFont(name_font)
    name.Wrap(name.GetSize().width)
    name.SetMinSize((name.GetSize().width, name.GetBestSize().height))

    placeholder = main_form.CONTROLID["lblChurchLogo"]
    if not logo_bytes:
        placeholder.SetLabel("No church logo\nChurch Information can add one.")
        return None
    image = wx.Image(io.BytesIO(bytes(logo_bytes)))
    if not image.IsOk():
        placeholder.SetLabel("Church logo unavailable")
        return None
    maximum = placeholder.FromDIP((120, 72))
    width = min(placeholder.GetSize().width, maximum.width)
    height = min(placeholder.GetSize().height, maximum.height)
    scale = min(width / image.GetWidth(), height / image.GetHeight())
    image.Rescale(
        max(1, int(image.GetWidth() * scale)),
        max(1, int(image.GetHeight() * scale)),
        wx.IMAGE_QUALITY_HIGH,
    )
    bitmap = wx.StaticBitmap(placeholder.GetParent(), wx.ID_ANY, wx.Bitmap(image))
    bitmap.SetToolTip(church_name or "Church logo")
    containing_sizer = placeholder.GetContainingSizer()
    if containing_sizer is not None:
        containing_sizer.Replace(placeholder, bitmap)
    placeholder.Hide()
    placeholder.GetParent().Layout()
    return bitmap


def fit_dashboard_window(main_form):
    """Fit the dashboard client area exactly and suppress needless scroll bars."""
    sizer = main_form.FORM.GetSizer()
    if sizer is None:
        return
    desired = sizer.GetMinSize()
    main_form.FRAME.SetClientSize(desired)
    if isinstance(main_form.FORM, wx.ScrolledWindow):
        main_form.FORM.SetVirtualSize(desired)
        main_form.FORM.SetScrollRate(0, 0)
        main_form.FORM.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_NEVER)
    main_form.FRAME.Center(wx.BOTH)
