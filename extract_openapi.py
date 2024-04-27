import json

import yaml

from app.main import app


if __name__ == "__main__":
    openapi = app.openapi()
    version = openapi.get("openapi", "unknown version")

    print(f"writing openapi spec v{version}")

    dir_file = "openapi.yaml"
    with open(dir_file, "w", encoding="utf8") as f:
        if dir_file.endswith(".json"):
            json.dump(openapi, f, indent=2, ensure_ascii=False)
        else:
            yaml.dump(openapi, f, sort_keys=False, allow_unicode=True)

    print(f"spec written to {dir_file}")
