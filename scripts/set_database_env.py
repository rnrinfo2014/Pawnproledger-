#!/usr/bin/env python3
"""
Set DATABASE_URL in .env safely.

Usage:
  python scripts/set_database_env.py '<DATABASE_URL>'
or interactive:
  python scripts/set_database_env.py

This script will:
 - Back up existing .env to .env.bak.YYYYMMDD_HHMMSS
 - Write a new .env with DATABASE_URL=<provided url>
 - Preserve other lines from previous .env if present (unless overwritten)

Note: After running this, restart your FastAPI server so it picks up the new env.
"""

import os
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_PATH = os.path.join(ROOT, '.env')


def read_existing_env():
    if not os.path.exists(ENV_PATH):
        return {}
    data = {}
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.strip().startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                data[k.strip()] = v.strip().strip('"')
    return data


def write_env(values: dict):
    # Merge with existing but overwrite keys in values
    existing = read_existing_env()
    merged = {**existing, **values}

    # Backup existing
    if os.path.exists(ENV_PATH):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak = ENV_PATH + f'.bak.{ts}'
        os.replace(ENV_PATH, bak)
        print(f'Backed up existing .env to {bak}')

    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        for k, v in merged.items():
            f.write(f'{k}={v}\n')

    print(f'Wrote new .env at {ENV_PATH}')


def main():
    if len(sys.argv) >= 2:
        db_url = sys.argv[1]
    else:
        print('Enter the full Render DATABASE_URL (postgresql://...):')
        db_url = input().strip()

    if not db_url:
        print('No DATABASE_URL provided. Exiting.')
        sys.exit(1)

    # Basic validation
    if not db_url.startswith('postgres'):
        print('Warning: DATABASE_URL does not look like a Postgres URL.')
        confirm = input('Continue anyway? (y/n): ').lower()
        if confirm != 'y':
            print('Aborted')
            sys.exit(1)

    write_env({'DATABASE_URL': db_url})
    print('\nNext steps:')
    print(' 1) Restart your server so the app picks up the new DATABASE_URL:')
    print('    python run_server.py')
    print(" 2) Run the 5-day test: python comprehensive_5day_test.py")


if __name__ == '__main__':
    main()
