#!/usr/local/bin/python

def parse_config_file(configfile, configuration):
    mapping = ""
    debug_paths = ""
    optimized_paths = ""
    config_create = ""
    config_paths = ""

    for line in open(configfile, 'r'):
        if "DEPENDENCY_COLLECTOR_MAPPING_" + configuration in line:
            print("configuration mapping found")
            mapping = "PLEASE SET ME CORRECTLY"
        if "DEPENDENCY_COLLECTOR_CREATE_" + configuration in line:
            print("configuration create found")
            config_create = "PLEASE SET ME CORRECTLY"
        if "DEPENDENCY_COLLECTOR_PATHS_OPTIMIZED" in line:
            print("optimized paths found")
            optimized_paths = "PLEASE SET ME CORRECTLY"
        if "DEPENDENCY_COLLECTOR_PATHS_DEBUG" in line:
            print("debug paths found")
            debug_paths = "PLEASE SET ME CORRECTLY"

    if mapping.lower() == "debug":
        config_paths = debug_paths
    elif mapping.lower() == "release":
        config_paths = optimized_paths
    else:
        print("DependencyCollector: error: mapping of configuration not found in config file")
        exit()
    return(config_create,config_paths)

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
        print("DependencyCollector: error: input file does not exist")
        exit()
    if not os.path.isfile(args.configfile):
        print("DependencyCollector: error: config file does not exist")
        exit()

    (config_create, config_paths) = parse_config_file(args.configfile, args.configuration)

