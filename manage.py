#!/usr/bin/env python
"""Utility CLI para o Django."""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django não foi encontrado. Verifique se o ambiente virtual está ativado."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
