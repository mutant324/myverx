#!/usr/bin/env python
# стандартный manage.py из джанги, я его не трогал почти
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myverx.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "не найден джанго, сделай pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
