import subprocess
import sys
import os


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return subprocess.call(f'{dir_path}/scripts/claimed ' + ' '.join(sys.argv[1:]), shell=True)


if __name__ == '__main__':
    main()
