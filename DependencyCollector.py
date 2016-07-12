#!/usr/local/bin/python

OUTPUT_NAME = "DependencyCollector"
import logging
logging.basicConfig(level=logging.WARNING, format=OUTPUT_NAME + ' %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def parse_config_file(configfile, configuration):
    import configparser
    config = configparser.ConfigParser();

    config.read(configfile)
    mapping = config['DependencyCollector']['MAPPING_'+configuration]
    if not (mapping.lower() == "debug" or mapping.lower() == "release"):
        logger.error("mapping of configuration not found or incorrect in config file")
        exit()

    create = config.getboolean('DependencyCollector','CREATE_'+configuration)
    paths_string = config['DependencyCollector']['PATHS_'+mapping.upper()]
    paths = paths_string.split(';')
    blacklist = "";
    if config.has_option('DependencyCollector','BLACKLIST'):
        blacklist = config['DependencyCollector']['BLACKLIST']
        blacklist = blacklist.split(';')
    return(create,paths,blacklist)

def update_mode(infile, config_paths, config_blacklist):
    import glob
    import ntpath

    logger.debug("running update mode")
    dir = os.path.dirname(os.path.realpath(infile))
    existing_dlls = glob.glob(dir+"/*.ini")

    logger.debug("dll found in directory:" + str(existing_dlls))
    for dll in existing_dlls:
        dll_name = ntpath.basename(dll)
        logger.debug("searching for a newer version of " + dll)
        if dll_name not in config_blacklist:
            (newest_dll, mod_date) = search_for_newest_file(dll_name, config_paths)
            if mod_date < os.path.getmtime(dll):
                print("COPY FILE HERE!!")
        else:
            logger.debug(dll + " skipped because of blacklist")
    return

def create_mode(infile, config_paths, config_blacklist):
    import ntpath

    logger.debug("running create mode")
    path = os.path.dirname(os.path.realpath(infile))
    infile_name = ntpath.basename(infile)
    dlls = search_for_used_dlls(infile_name, path, [], config_blacklist)

    logger.debug("all dlls found:" + str(dlls))
    return


def search_for_used_dlls(infile, path, dll_list, blacklist):
    import re
    dll_regexp = re.compile(b'\.dll')
    logger.debug("analyzing: "+path + "/" + infile)
    # ifile = open(path + "/" + infile, 'rb', buffering=0)
    ifile = open(path + "/" + infile, 'rb')
    for line in ifile:
        iterator = dll_regexp.finditer(line)
        for match in iterator:
            pos = match.start()-1 # -1 because of the dot
            while pos > 0 and (line[pos-1:pos].isalnum() or line[pos-1:pos] == b"_" or line[pos-1:pos] == b"-"):
                pos = pos - 1
            if pos == match.start()-1: # check if position has changed
                continue

            dllname = line[pos:match.end()].decode()
            if dllname not in blacklist and dllname not in dll_list:
                dll_list.append(dllname)
                dll_list = search_for_used_dlls(dllname, path, dll_list, blacklist)

    ifile.close()
    logger.debug(infile + " uses dlls:" + str(dll_list))

    return dll_list

def search_for_newest_file(file, paths):
    import time

    newest_file = ""
    mod_date = ""
    for p in paths:
        if os.path.isfile(p + "/" + file) and (mod_date == "" or os.path.getmtime(p + "/" + file) < mod_date):
            mod_date = os.path.getmtime(p+ "/" + file)
            newest_file = p+ "/" + file
            logger.debug("newer dll found in " + p + "for " + file + " (date:" + time.ctime(mod_date) + ")")

    if newest_file == "":
        logger.warning("no dll found for " + file)

    return(newest_file, mod_date)

if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='searches for dependencies of an executable or library and'
                                                 'copies the dependencies to the corresponding directory')

    parser.add_argument('--infile', default='', metavar="inputfile",
                        help ="""executable or dependency which dependencies should be copied""",
                        required=True)
    parser.add_argument('--configfile', default='', metavar="configfile",
                        help ="""configuration file of the dependencycollector""", required=True)
    parser.add_argument('--configuration', default='', metavar='configuration',
                        help = """current build configuration (Release|Debug|...)""", required=True)
    parser.add_argument('--debug', action="store_true",
                        help="""enable debug messages""")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if not os.path.isfile(args.infile):
        logger.error("input file does not exist:" + args.infile)
        exit()
    if not os.path.isfile(args.configfile):
        logger.error("config file does not exist" + args.configfile)
        exit()

    (config_create, config_paths, config_blacklist) = parse_config_file(args.configfile, args.configuration)

    logger.debug("running create mode:" + str(config_create))
    logger.debug("using paths:" + str(config_paths))
    logger.debug("using blacklist:" + str(config_blacklist))

    if config_create == True:
        create_mode(args.infile, config_paths, config_blacklist)
    elif config_create == False:
        update_mode(args.infile, config_paths, config_blacklist)
    else:
        logger.error("create mode unkown")
        exit()