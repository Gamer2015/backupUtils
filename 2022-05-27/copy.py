import os
import shutil
import functools
import argparse

 
parser = argparse.ArgumentParser(description='Copy files from source_directory to target_directory if it does not already exist or if the file in source_directory is newer.')
parser.add_argument('source_directory', help='source directory')
parser.add_argument('target_directory', help='target directory')
parser.add_argument("-i", "--ignore_file", default="ignore_patterns.txt", help='path to the file that contains the ignore rules')
parser.add_argument("-c", "--check", action='store_true', help="no files are copied if this option is selected")
args = parser.parse_args()


class Ignorer:
    def __init__(self):
        self.patterns = []

    def ignore_by_pattern(self, path, name):
        for pattern in self.patterns:
            including = pattern[0] == "!"
            if including:
                pattern = pattern[1:]

            match = len(shutil.ignore_patterns(pattern)(path, [name])) > 0
            if match:
                return including == False
        return False

    def ignore_by_mtime(self, source, target):
        if os.path.isfile(target) == False:
            return False 

        newer = int(os.path.getmtime(source)) > int(os.path.getmtime(target) + 1)
        if newer:
            print("source: %f: %s" % (os.path.getmtime(source), source))
            print("source: %f: %s" % (os.path.getmtime(target), target))
        return newer == False

    def ignore(self, source, target):
        path, name = os.path.split(source)
        if self.ignore_by_pattern(path, name): return True
        if self.ignore_by_mtime(source, target): return True
        return False


def run(): 
    if os.path.isfile(args.ignore_file) == False:
        print("Error: file does not exist: %s" % args.ignore_file)
        parser.print_help()
        return

    ignorer = Ignorer();
    with open(args.ignore_file,"r") as f:
        patterns = [line.split("#")[0].strip() for line in f.read().splitlines()]
        patterns = [pattern for pattern in patterns if len(pattern) > 0]
        patterns.reverse()
        ignorer.patterns = patterns

    copy = lambda source, target: shutil.copy2(source, target, follow_symlinks=False)
    makedirs = lambda name: os.makedirs(name, exist_ok=True)
    if args.check: # use dummy methods instead
        copy = lambda a,b: 0
        makedirs = lambda a: 0

    # delete files, (but not folders!)
    for root, dirs, files in os.walk(args.source_directory):
        relpath = os.path.relpath(root, args.source_directory)
        makedirs(os.path.join(args.target_directory, relpath))
        for filename in files:
            source = os.path.join(root, filename)
            target = os.path.normpath(os.path.join(args.target_directory, relpath, filename))
            if ignorer.ignore(source, target) == False:
                print("copy: %s -> %s" % (source, target))
                copy(source, target)

if __name__ == '__main__':
    run()






# def ignore_by_patterns(patterns, path, names):
#     ignored = []
#     for name in names:
#         filepath = os.path.join(path, name)
#         for pattern in patterns:
#             including = pattern[0] == "!"
#             if including:
#                 pattern = pattern[1:]

#             match = len(shutil.ignore_patterns(pattern)(path, [name])) > 0
#             if match:
#                 if including == False:
#                     ignored.append(name)
#                 break 
#     return ignored

# def ignore_by_modification_time(path, names):
#     relpath = os.path.relpath(path, args.source_directory)
#     ignored = []
#     for name in names:
#         source = os.path.join(args.source_directory, relpath, name)
#         target = os.path.join(args.target_directory, relpath, name)
#         if os.path.isfile(target) == False:
#             continue
        
#         newer = os.path.getmtime(source) > os.path.getmtime(target)
#         if newer == False:
#             ignored.append(name)

#     return ignored

# def ignore_finder(ignorers, path, names):
#     relpath = os.path.relpath(path, args.source_directory)
#     ignored = []
#     for ignorer in ignorers:
#         newIgnored = ignorer(path, names)
            
#         names = [name for name in names if name not in newIgnored]
#         ignored.extend(newIgnored)

#     for name in names: 
#         source = os.path.normpath(os.path.join(args.source_directory, relpath, name))
#         target = os.path.normpath(os.path.join(args.target_directory, relpath, name))
#         if os.path.isfile(source):
#             print('copy: %s -> %s' % (source, target))
#     return ignored
