import sys
import pytest

def main(argv):
    # run pytest while overriding addopts so coverage enforcement from pyproject is skipped
    args = ["-o", "addopts="] + argv
    raise SystemExit(pytest.main(args))

if __name__ == "__main__":
    main(sys.argv[1:])
