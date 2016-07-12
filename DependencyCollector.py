#!/usr/local/bin/python

OUTPUT_NAME = "DependencyCollector"
ERROR_MSG = OUTPUT_NAME + ": ERROR: "
WARNING_MSG = OUTPUT_NAME + ": WARNING: "

def parse_config_file(configfile, configuration):
    import configparser
    config = configparser.ConfigParser();

    config.read(configfile)
    mapping = config['DependencyCollector']['MAPPING_'+configuration]
    if not (mapping.lower() == "debug" or mapping.lower() == "release"):
        print(ERROR_MSG + " mapping of configuration not found or incorrect in config file")
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

    print("update mode")
    dir = os.path.dirname(os.path.realpath(infile))
    existing_dlls = glob.glob(dir+"/*.ini")

    print("existing dlls:" + str(existing_dlls))
    for dll in existing_dlls:
        dll_name = ntpath.basename(dll)
        if dll_name not in config_blacklist:
            (newest_dll, mod_date) = search_for_newest_file(dll_name, config_paths)
            if mod_date < os.path.getmtime(dll):
                print("COPY FILE HERE!!")
    return

def create_mode(infile, config_paths, config_blacklist):
    print("create mode")
    return

def search_for_newest_file(file, paths):
    newest_file = ""
    mod_date = ""
    for p in paths:
        print(p + "/" + file)
        if os.path.isfile(p+ "/" + file):
            if mod_date == "" or os.path.getmtime(p+ "/" + file) < mod_date:
                mod_date = os.path.getmtime(p+ "/" + file)
                newest_file = p+ "/" + file
    if newest_file == "":
        print(WARNING_MSG + ": no dll found for " + file)

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

    args = parser.parse_args()

    if not os.path.isfile(args.infile):
        print(ERROR_MSG + "input file does not exist")
        exit()
    if not os.path.isfile(args.configfile):
        print(ERROR_MSG + "config file does not exist")
        exit()

    (config_create, config_paths, config_blacklist) = parse_config_file(args.configfile, args.configuration)

    print("config_create:" + str(config_create))
    if config_create == True:
        create_mode(args.infile, config_paths, config_blacklist)
    elif config_create == False:
        update_mode(args.infile, config_paths, config_blacklist)
    else:
        print(ERROR_MSG + "create mode unkown")
        exit()