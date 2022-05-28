import os
import shutil
import functools
import argparse

 
parser = argparse.ArgumentParser(description='Copy files from source_directory to target_directory if it does not already exist or if the file in source_directory is newer.')
parser.add_argument('source_directory', help='source directory')
parser.add_argument('target_directory', help='target directory')
parser.add_argument("-i", "--ignore", default="ignore_patterns.txt", help='path to the file that contains the ignore rules')
parser.add_argument("-c", "--check", action='store_true', help="no files are copied if this option is selected")
args = parser.parse_args()


def ignore_by_patterns(patterns, path, names):
    ignored = []
    for name in names:
        filepath = os.path.join(path, name)
        for pattern in patterns:
            including = pattern[0] == "!"
            if including:
                pattern = pattern[1:]

            match = len(shutil.ignore_patterns(pattern)(path, [name])) > 0
            if match:
                if including == False:
                    ignored.append(name)
                break 
    return ignored

def ignore_by_modification_time(path, names):
    relpath = os.path.relpath(path, args.source_directory)
    ignored = []
    for name in names:
        source = os.path.join(args.source_directory, relpath, name)
        target = os.path.join(args.target_directory, relpath, name)
        if os.path.isfile(target) == False:
            continue
        
        newer = os.path.getmtime(source) > os.path.getmtime(target)
        if newer == False:
            ignored.append(name)

    return ignored

def ignore_finder(ignorers, path, names):
    relpath = os.path.relpath(path, args.source_directory)
    ignored = []
    for ignorer in ignorers:
        newIgnored = ignorer(path, names)
            
        names = [name for name in names if name not in newIgnored]
        ignored.extend(newIgnored)

    for name in names: 
        source = os.path.normpath(os.path.join(args.source_directory, relpath, name))
        target = os.path.normpath(os.path.join(args.target_directory, relpath, name))
        if os.path.isfile(source):
            print('copy: %s -> %s' % (source, target))
    return ignored

def ignore(source, target):


def run(): 
    if os.path.isfile(args.ignore) == False:
        print("Error: file does not exist: %s" % args.ignore)
        parser.print_help()
        return

    f = open(args.ignore,"r")
    patterns = [line.split("#")[0].strip() for line in f.read().splitlines()]
    patterns = [pattern for pattern in patterns if len(pattern) > 0]
    patterns.reverse()
    
    prepared_ignore_by_patterns=functools.partial(ignore_by_patterns, patterns)

    prepared_ignore_finder = functools.partial(ignore_finder, [
        prepared_ignore_by_patterns,
        ignore_by_modification_time
    ])

    copy = shutil.copy2
    makedirs = os.makedirs
    if args.check:
        copy = lambda a,b: 0

    if args.check:
        makedirs = lambda a: 0

    # delete files, (but not folders!)
    for root, dirs, files in os.walk(args.source_directory):
        relpath = os.path.relpath(root, args.source_directory)
        for filename in files:
            source = os.path.normpath(os.path.join(args.source_directory, relpath, filename))
            target = os.path.normpath(os.path.join(args.target_directory, relpath, filename))

            if ignore(source, target) == False:
                copy(source, target)
            print("source: %s" % source)
            print("target: %s" % target)
    return
    # copy files
    shutil.copytree(args.source_directory, args.target_directory, copy_function=copyFunction, ignore=prepared_ignore_finder, dirs_exist_ok=True)
    print("done!")

if __name__ == '__main__':
    run()