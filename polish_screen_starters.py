"""Apply the approved ChurchManager visual theme to every shipped screen."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FORMS = ROOT / "Forms"


def polish(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    root = data[next(iter(data))]
    root["FORM"]["theme"] = "churchmanager"
    path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    paths = sorted(FORMS.glob("*.json"))
    for path in paths:
        polish(path)
    print("Applied the ChurchManager theme to {} starter screens.".format(len(paths)))


if __name__ == "__main__":
    main()
