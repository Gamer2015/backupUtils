import os
import argparse

import datetime

parser = argparse.ArgumentParser(description='Delete files, but not folders, from delete_directory, that are older than the specified date.')
parser.add_argument('delete_directory', help='delete directory')
parser.add_argument("-Y", '--year', help='year')
parser.add_argument("-m", '--month', help='month')
parser.add_argument("-d", '--day', help='day')
args = parser.parse_args()

def input_int(prompt):
    val = None
    while val == None:
        try:
            year = int(input(prompt))
        except Exception as e:
            print(e)
    return val

def run():
    if os.path.isdir(args.delete_directory) == False:
        print("Error: directory does not exist: %s" % args.delete_directory)
        print("")
        parser.print_help()
        return

    now = datetime.datetime.now()
    year = args.year
    if year == None:
        year = input_int("year:")

    month = args.month
    if month == None:
        month = input_int("month:")

    day = args.day
    if day == None:
        day = input_int("day:")

    cleanup_date = datetime.datetime(year, month, day)
    print("deleting files that are older than: %s" % cleanup_date.isoformat())

    # delete files, (but not folders!)
    for root, dirs, files in os.walk(args.delete_directory):
        for name in files:
            filepath = os.path.join(root, name)
            modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            if modification_time < cleanup_date:
                print("deleting: %s" % filepath)
                os.remove(filepath)

if __name__ == '__main__':
    run()