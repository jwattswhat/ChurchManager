"""Launch the ChurchManager setup wizard in safe preview or apply mode."""

import argparse

import wx

from setup_wizard import show_setup_wizard


def main(argv=None):
    """Run the graphical setup wizard; preview is the development default."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true",
        help="Allow the reviewed wizard plan to create a fresh local installation.",
    )
    args = parser.parse_args(argv)
    application = wx.App(False)
    try:
        show_setup_wizard(apply=args.apply)
    finally:
        application.Destroy()


if __name__ == "__main__":
    main()
