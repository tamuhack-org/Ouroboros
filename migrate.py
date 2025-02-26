import re
import subprocess


def install_requirements(filename="./hiss/requirements.txt"):
    with open(filename, "r") as f:
        for line in f.readlines():
            if len(line) < 2 or line.startswith("#"):
                continue
            package = re.sub(r"[\s=].*$", "", line, flags=re.IGNORECASE)
            subprocess.run(f"uv add {package}", shell=True)


if __name__ == "__main__":
    install_requirements()
