#!/usr/local/bin/python
import logging
OUTPUT_NAME = "DependencyCollector"

logging.basicConfig(level=logging.INFO, format=OUTPUT_NAME +
                    ' %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def parse_config_file(configfile, conftype):
    import configparser
    config = configparser.ConfigParser()

    config.read(configfile)
    if config.has_option('DependencyCollector', 'MAPPING_'+conftype.upper()):
        mapping = config['DependencyCollector']['MAPPING_'+conftype.upper()]
    else:
        logger.error("mapping not found in the configuration file (MAPPING_" +
                     conftype.upper()+")")
        exit()
    if not (mapping.lower() == "debug" or mapping.lower() == "release"):
        logger.error("mapping of configuration is not correct" +
                     ", it has to be Release or Debug")
        exit()

    if config.has_option('DependencyCollector', 'CREATE_' + conftype.upper()):
        create = config.getboolean('DependencyCollector',
                                   'CREATE_' + conftype.upper())
    else:
        logger.warning("CREATE flag for configratuion not found in config " +
                       "(CREATE_" + conftype.upper() +
                       ") automatically using create method")

    paths_string = config['DependencyCollector']['PATHS_'+mapping.upper()]
    paths = paths_string.split(';')
    for p in paths:
        if not os.path.isdir(p):
            logger.warning("paths in config file: " + p + " does not exist")
    blacklist = []
    if config.has_option('DependencyCollector', 'BLACKLIST'):
        blacklist = config['DependencyCollector']['BLACKLIST']
        blacklist = blacklist.split(';')
    blacklist_lower = []
    for b in blacklist:
        blacklist_lower.append(b.lower())
    conf = {'create': create, 'paths': paths, 'blacklist': blacklist_lower}
    return conf


def update_mode(infile, conf):
    import glob
    import ntpath
    import time

    logger.debug("running update mode")
    dir = os.path.dirname(os.path.realpath(infile))
    existing_dlls = glob.glob(dir+"/*.dll")

    logger.debug("dll found in directory:" + str(existing_dlls))
    for dll in existing_dlls:
        dll_name = ntpath.basename(dll)
        logger.debug("searching for a newer version of " + dll + "("+time.ctime(os.path.getmtime(dll))+")")
        if dll_name.lower() not in conf['blacklist']:
            (newest_dll, mod_date) = search_for_newest_file(dll_name,
                                                            conf['paths'])
            if newest_dll != "" and mod_date > os.path.getmtime(dll):
                copy_dll(newest_dll, dir)
            else:
                logger.debug("not copying dll because local file is newer")
        else:
            logger.debug(dll + " skipped because of blacklist")
    return


def create_mode(infile, conf):
    import ntpath

    logger.debug("running create mode")
    path = os.path.dirname(os.path.realpath(infile))
    infile_name = ntpath.basename(infile)
    dlls = search_for_used_dlls(infile_name, path, [], conf)
    logger.debug("all dlls found:" + str(dlls))


    return


def search_for_used_dlls(infile, path, dll_list, conf):
    import re
    dll_regexp = re.compile(b'\.dll')
    logger.debug("analyzing: "+os.path.join(path,infile))
    ifile = open(os.path.join(path,infile), 'rb')
    for line in ifile:
        iterator = dll_regexp.finditer(line)
        for match in iterator:
            pos = match.start()
            while pos > 0 and (line[pos - 1:pos].isalnum() or
                               line[pos - 1:pos] == b"_" or
                               line[pos - 1:pos] == b"-"):
                pos = pos - 1
            if pos == match.start():  # check if position has changed
                continue

            dllname = line[pos:match.end()].decode()

            if not dllname.lower() in conf['blacklist'] \
                    and not dllname.lower() in dll_list:
                (dllpath, mod_date) = \
                    search_for_newest_file(dllname, conf['paths'])
                if dllpath == "":
                    logger.warning(dllname + " not found")
                else:
                    if os.path.dirname(dllpath) != conf['localpath']:
                        copy_dll(dllpath, path)
                    dll_list.append(dllname.lower())
                    dll_list = \
                        search_for_used_dlls(dllname, path, dll_list, conf)

    ifile.close()
    logger.debug(infile + " uses dlls:" + str(dll_list))

    return dll_list


def copy_dll(dllpath, targetpath):
    import shutil
    logger.info("copying " + dllpath + " to " + targetpath)
    try:
        shutil.copy(dllpath, targetpath)
    except OSError as error:
        logger.error("unable to copy " + dllpath + " to " +
                     targetpath + "(" + str(error) + ")")
    except:
        logger.error("unable to copy " + dllpath + " to " + targetpath)
    return


def search_for_newest_file(file, paths):
    import time

    newest_file = ""
    mod_date = ""
    for p in paths:
        fullpath = os.path.join(p, file)
        if os.path.isfile(fullpath) and \
                (mod_date == "" or
                 os.path.getmtime(fullpath) < mod_date):
            mod_date = os.path.getmtime(fullpath)
            newest_file = fullpath
            logger.debug("newest dll found in " + p + " for " + file +
                         " (date:" + time.ctime(mod_date) + ")")

    if newest_file == "":
        logger.warning("no dll found for " + file)

    return(newest_file, mod_date)

if __name__ == "__main__":
    import argparse
    import configparser
    import os

    parser = argparse.ArgumentParser(
       description='searches for dependencies of an executable or library and'
                   'copies the dependencies to the corresponding directory')

    parser.add_argument('--infile', default='', metavar="inputfile",
                        help="""executable or dependency which dependencies
                        should be copied""",
                        required=True)
    parser.add_argument('--configfile', default='', metavar="configfile",
                        help="""configuration file of the
                        dependencycollector""", required=True)
    parser.add_argument('--configuration', default='', metavar='configuration',
                        help="""current build configuration
                        (Release|Debug|...)""", required=True)
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

    logger.info("called with file:" + args.infile + " and configuration " + args.configuration)
    conf = parse_config_file(args.configfile, args.configuration)
    conf['localpath'] = os.path.dirname(os.path.realpath(args.infile))
    conf['paths'].append(os.path.dirname(os.path.realpath(args.infile))) # adding local path

    logger.debug("running create mode:" + str(conf['create']))
    logger.debug("using paths:" + str(conf['paths']))
    logger.debug("using blacklist:" + str(conf['blacklist']))

    if conf['create'] is True:
        create_mode(args.infile, conf)
        logger.debug("resetting create flag")
        config = configparser.ConfigParser()
        config.read(args.configfile)
        config['DependencyCollector']['CREATE_' + args.configuration.upper()] = "False"
        with open(args.configfile, 'w') as configfile:
            config.write(configfile)

    elif conf['create'] is False:
        update_mode(args.infile, conf)
    else:
        logger.error("create mode unkown")
        exit()

    logger.info("finished")
