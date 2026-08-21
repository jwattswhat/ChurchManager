"""Start development ChurchManager without opening a console window."""

from pathlib import Path
import os
import sys
import traceback


ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def show_startup_error(error):
    """Display a useful GUI error when the development runtime cannot start."""
    import wx

    app = wx.App(False)
    wx.MessageBox(
        "ChurchManager could not start. Verify the development runtime and review "
        f"the support error log.\n\n{error}",
        "ChurchManager Startup Failed",
        wx.OK | wx.ICON_ERROR,
    )
    app.Destroy()


try:
    import JSForm
    from development_boundary import assert_development_isolation

    assert_development_isolation(JSForm)
    from cm import main

    raise SystemExit(main(["--server", "127.0.0.1", "--user", "church", "--test"]))
except SystemExit:
    raise
except Exception as startup_error:
    try:
        from churchmanager_error_support import configure_churchmanager_error_reporting

        configure_churchmanager_error_reporting()
        JSForm.report_exception(startup_error, operation="application.startup")
    except Exception:
        traceback.print_exc()
    show_startup_error(startup_error)
