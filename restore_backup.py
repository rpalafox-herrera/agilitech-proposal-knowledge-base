"""Restore to a new local folder. Stop the app first; use trusted backups only."""
import argparse
from kb.backups import restore_backup

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', help='Downloaded backup ZIP')
    parser.add_argument('--destination', required=True, help='NEW local data directory')
    args = parser.parse_args()
    count = restore_backup(args.archive, args.destination)
    print(f'Restored {count} documents. Set AGILITECH_DATA_DIR to {args.destination} before starting the app.')
    print('This backup restores originals locally. Unset Firebase/Supabase environment variables for this restored copy.')
