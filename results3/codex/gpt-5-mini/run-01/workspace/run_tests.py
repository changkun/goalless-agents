import sys
from proj_info import cli


def test_version():
    rc = cli.main(['--version'])
    if rc != 0:
        print('FAIL: return code', rc)
        return 1
    print('OK: version printed')
    return 0

if __name__ == '__main__':
    sys.exit(test_version())
