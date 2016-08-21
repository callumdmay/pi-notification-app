#!/usr/bin/env python
# Configuration manager.  Creates and manages application configurations.  Adds new config parameters on the fly

# core python libraries
###########################################################

import ConfigParser
import sys
from optparse import OptionParser
import datetime
import logging
import os
import stat


# peripheral libraries
###########################################################

# internal libraries and modules
###########################################################

# Configuration object

class Configuration(object):
    def __init__(self, default_filepath):
        """ read in the default template and set up the object"""

        object.__init__(self)

        try:
            configFile = open(default_filepath)
        except Exception as e:
            logging.critical(
                "Error opening default config file - {}.  Will exit application  Details:{}".format(default_filepath, e))
            sys.exit(1)

        # load the default config
        params = ConfigParser.SafeConfigParser(allow_no_value=True)
        params.readfp(configFile)

        # convert it into a Configuration format.  The data format is "type, default, scope".  If it's blank, defaults are str,"",user
        for section in params.sections():
            t = Section()
            setattr(self, section, t)
            for param, value in params.items(section):
                # logging.debug("adding section: {} parameter: {} value:  {}".format(section, param, value))
                if not value:
                    setattr(getattr(self, section), str(param), set_param("string", "", "user"))

                else:
                    # parse the param string, formatting and cleaning as you go.  then put it into the object
                    templist = value.split("|")[:3]
                    for i, string in enumerate(templist):
                        templist[i] = string.strip()
                    category, default, scope = tuple(templist)
                    setattr(getattr(self, section), str(param), set_param(category, default, scope))

    def load(self, filepath, scope="system"):
        # load a file of settings and fill the config object
        try:
            configFile = open(filepath)
        except Exception as e:
            logging.critical("Error opening config file - {}.  Will exit application  Details:{}".format(filepath, e))
            sys.exit(1)

        # load the config into params
        params = ConfigParser.SafeConfigParser(allow_no_value=True)
        params.readfp(configFile)

        # create repository for errors
        errors = list()

        # load it into the config object.
        # If it's blank, defaults are str,"",user
        for section in params.sections():
            # record if section is not in config
            if not hasattr(self, section):
                errors.append(dict(file=str(filepath), section=section, param="None", type="missing object section",
                                   desc="section not in object"))
                logging.error("Config file section ({}, {}) not in config object".format(filepath, section))
                continue

            # now look at the individual params
            # check for param errors: permission, type, ?
            config_section = getattr(self, section)
            for param, value in params.items(section):
                # does the param exist in the object?
                if not hasattr(config_section, param):
                    errors.append(dict(file=str(filepath), section=section, param=param, type="missing object param",
                                       desc="param not in object"))
                    logging.error(
                        "Config file param ({}, {}, {}) not in config object".format(filepath, section, param))
                    continue
                # the param exists.  get it and check permissions
                config_param = getattr(config_section, param)
                # scope.  system is a complete override, otherwise has to match exactly
                if scope != "system":
                    if config_param.scope.strip() != scope:
                        errors.append(dict(file=str(filepath), section=section, param=param, type="scope",
                                           desc="scope error param: {} argument: {}".format(config_param.scope,
                                                                                            scope)))
                        logging.error(
                            "Config file scope error ({}, {}, {},  param scope: {} argument: {}".format(filepath,
                                                                                                        section, param,
                                                                                                        config_param.scope,
                                                                                                        scope))
                        continue

                # TODO check for type

                # now set the parameter if there is one
                if len(value) > 0:
                    logging.debug(
                        "setting config object parameter.  Section: {} Parameter: {} Value:  {}".format(section, param,
                                                                                                        value))
                    # logging.debug("setting config object parameter {}, {}, {}".format( section, param, value))
                    setattr(config_section, param, set_param_obj(config_param, value))
                else:
                    logging.debug(
                        "Empty config object parameter.  Section: {} Parameter: {} Value: {}".format(section, param,
                                                                                                     value))
        return errors

    def check(self, filepath, permis_filter=""):
        # check a config file of settings and return a dict of problems
        logging.info("Checking config file {}".format(filepath))
        try:
            configFile = open(filepath)
        except Exception as e:
            logging.critical("Error opening config file - {}.  Will exit application  Details:{}".format(filepath, e))
            sys.exit(1)

        # load the config into params
        params = ConfigParser.SafeConfigParser(allow_no_value=True)
        params.readfp(configFile)

        # create repository for errors
        errors = list()

        # 1st check the config file against the config parser object
        logging.info("Checking config file against config object ...")
        for section in params.sections():
            # record if section is not in config
            if not hasattr(self, section):
                errors.append(dict(file=str(filepath), section=section, param="None", type="missing object section",
                                   desc="section not in object"))
                logging.error("Config file section ({}, {}) not in config object".format(filepath, section))
                continue

            # now look at the individual params
            # check for presence, type, ?
            config_section = getattr(self, section)
            for param, value in params.items(section):
                # does the param exist in the object?
                if not hasattr(config_section, param):
                    errors.append(dict(file=str(filepath), section=section, param=param, type="missing object param",
                                       desc="param not in object"))
                    logging.error(
                        "Configfile param ({}, {}, {}) not in config object".format(filepath, section, param))
                    continue
                # the param exists.  get it and check type
                config_param = getattr(config_section, param)
                # can't check an empty param for type
                if len(value) == 0:
                    logging.error(
                        "Empty Configfile parameter.  Can't check for type.  Section: {} Parameter: {}".format(section,
                                                                                                               param,
                                                                                                               value))
                    errors.append(dict(file=str(filepath), section=section, param=param, type="no value",
                                       desc="Param has no value, can't check for type"))
                else:
                    # try a cast related to param type
                    if check_param_type(config_param, value) == False:
                        logging.error(
                            "Parameter type error in Configfile. Section:{} Parameter:{} Value:{} Type:{}".format(
                                section, param, value, config_param.param_type))
                        errors.append(dict(file=str(filepath), section=section, param=param, type="wrong type",
                                           desc="Param cannot be converted to required type-{}".format(
                                               config_param.param_type)))
                    else:
                        # good parameter
                        logging.debug(
                            "Configfile Parameter is ok. Section:{} Parameter:{} Value:{} Type:{}".format(
                                section, param, value, config_param.param_type))

        # last, check for missing sections and parameters in config file
        logging.info("Checking config object against config file")
        for section, parameters in vars(self).iteritems():
            if not params.has_section(section):
                errors.append(
                    dict(file=str(filepath), section=section, param=param, type="missing config section",
                         desc="section not in config file"))
                logging.error("Configfile section missing ({}, {})".format(filepath, section))
                continue
            config_section = getattr(self, section)
            for param, value in vars(parameters).iteritems():
                config_param = getattr(config_section, param)
                # log any parameter that's in the object but not in the config file, and is not filtered out
                if not params.has_option(section, param) and (
                        config_param.scope in permis_filter or "system" in permis_filter):
                    errors.append(
                        dict(file=str(filepath), section=section, param=param, type="missing config param",
                             desc="parameter not in config file"))
                    logging.error("Configfile parameter missing ({}, {}, {}, {}, {})".format(filepath, section, param,
                                                                                             config_param.param_type,
                                                                                             config_param.scope))
                else:
                    logging.debug(
                        "Parameter is in config file. Section:{} Parameter:{} Value:{} Type:{}".format(
                            section, param, value, config_param.param_type))

        return errors


# configuration parameters
class int_param(int):
    def __init__(self, value=0):
        self.scope = ""
        int.__init__(self, value)
    @property
    def param_type(self):
        return "int_param"


class str_param(str):
    def __init__(self, value=""):
        self.scope = ""
        str.__init__(self, value)
    @property
    def param_type(self):
        return "str_param"


class bool_param(int):
    def __new__(self, value=0):
        if value.strip().lower() == "false":
            value = 0
        else:
            value = 1
        return int.__new__(self, value)

    def __init__(self, value=0):
        if value.strip().lower() == "false":
            value = 0
        else:
            value = 1
        self.scope = ""
        int.__init__(self, value)

    def __str__(self):
        if self == 1:
            return 'True'
        else:
            return 'False'

    @property
    def param_type(self):
        return "bool_param"


class float_param(float):
    def __init__(self, value=0.0):
        self.scope = ""
        float.__init__(self, value)
    @property
    def param_type(self):
        return "float_param"


class tuple_param(tuple):
    def __new__(typ, itr):
        i = eval(itr)
        if i is None:
            seq = [None,]
        else:
            seq = [x for x in eval(itr)]
        scope = ""
        return tuple.__new__(typ, seq)

    @property
    def param_type(self):
        return "tuple_param"


class Section:
    pass


def set_param(category, value, scope):
    if category == "integer":
        t = int_param(value)
    elif category == "floating":
        t = float_param(value)
    elif category == "boolean":
        t = bool_param(value)
    elif category == "tuple":
        t = tuple_param(value)
    else:
        t = str_param(value)
    t.scope = scope
    return t


def set_param_obj(param_obj, value):
    scope = param_obj.scope
    if param_obj.param_type == "int_param":
        t = int_param(value)
    elif param_obj.param_type == "float_param":
        t = float_param(value)
    elif param_obj.param_type == "bool_param":
        t = bool_param(value)
    elif param_obj.param_type == "tuple_param":
        t = tuple_param(value)
    else:
        t = str_param(value)
    t.scope = scope
    return t

def check_param_type(param_obj, value):
    #return True if value can be successfully casted as param_obj
    try:
        if param_obj.param_type == "int_param":
            int(value)
        elif param_obj.param_type == "float_param":
            float(value)
        elif param_obj.param_type == "bool_param":
            return value.lower() in ("true", "false","0","1")
        else:
            pass
    except ValueError:
        return False
    return True


def set_up_logging(loglvl, console_logging_enabled):
    # set up logging
    logger = logging.getLogger('')
    logger.setLevel(loglvl)
    # modules

    # add a rotating loghandler.  it will log to DEBUG or INFO
    Logfolderpath = "/log/coldsnap_log/"
    # if the directory doesn't exist, create it
    if not os.path.exists(Logfolderpath):
        try:
            os.makedirs(Logfolderpath)
            os.chmod(Logfolderpath, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH)
        except OSError as exception:
            logger.critical('Failed to create Log folder root directory  Error = {0}'.format(exception.errno))

    Rotations = 20
    Logfilename = 'modemperfR.log'
    rotatelogh = logging.handlers.RotatingFileHandler(Logfolderpath + '/' + Logfilename, mode='a', maxBytes=1000000,
                                                      backupCount=Rotations, encoding=None, delay=0)
    rotatelogh.setLevel(logging.DEBUG if loglvl == logging.DEBUG else logging.INFO)

    formatter = logging.Formatter('%(asctime)s\t%(threadName)s\t%(funcName)s:%(lineno)d\t%(levelname)s\t%(message)s')
    # tell the handler to use this format and add to root handler
    rotatelogh.setFormatter(formatter)
    logger.addHandler(rotatelogh)

    # now add a console logger if  enabled
    if console_logging_enabled:
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(loglvl)
        # set a format which is simpler for console use
        if options.service:
            formatter = logging.Formatter('%(lineno)-5d %(levelname)-8s %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s %(funcName)-16s:%(lineno)-5d %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logger.addHandler(console)

    ## logger.addHandler(t)

    ##        # set up  filters
    ##        console.addFilter(NomodbusFilter())
    ##        logger.addFilter(NomodbusFilter())
    else:
        # logging disabled so add log it
        logger.info("Console logging disabled")

    # modules
    t = logging.getLogger('requests.packages.urllib3.connectionpool')
    t.setLevel(logging.WARNING)

    return logger


def build_parse_options():
    # parse the command line
    parser = OptionParser()

    # logging
    parser.add_option("--noconsolelog", action='store_false', dest="console_logging_enabled", default=True,
                      help="Turn console logging OFF (default = on)")  # log flag
    parser.add_option("-I", '--info', dest='loglvl', action='store_const', const=logging.INFO, default=logging.INFO,
                      help="Log Info and higher i.e. no DEBUG (this is the default)")
    parser.add_option("-W", '--warning', dest='loglvl', action='store_const', const=logging.WARNING, default=logging.INFO,
                      help="Log Warning and higher.  Default = INFO")
    parser.add_option("-D", '--debug', dest='loglvl', action='store_const', const=logging.DEBUG, default=logging.INFO,
                      help="Log Debug and higher i.e. EVERYTHING.  Default = INFO")
    parser.add_option("-C", '--critical', dest='loglvl', action='store_const', const=logging.CRITICAL, default=logging.INFO,
                      help="Log Critical and higher.  Default = INFO")

    # test run parameters
    parser.add_option("--loop", type="int", dest="loop", default=1,
                      help="Repeat or loop the test this quantity (default = 1)")
    parser.add_option("-d", "--delay", type="float", dest="delay", default=5,
                      help="Delay between tests in minutes.  default = 5 minutes")
    parser.add_option("-R", "--run_constantly", action='store_true', dest="run_constantly", default=False,
                      help="Monitor constantly i.e. loop tests forever (default = False, only test for --loop loops")
    parser.add_option('--noservice', action="store_false", dest='service', default=True,
                      help='Run as an app, not service. Default = no, run as service')
    parser.add_option('--systemconfig', action="store_true", dest='system_config', default=False,
                      help='Use Coldsnap system configuration. Default = no, use command line parameters')

    # test targets and options
    parser.add_option("--ping-target", type="str", dest="ping_target", default="8.8.8.8",
                      help="Network target to ping (default = 8.8.8.8 - google).  Try goaglo.com for a forced failure")
    parser.add_option("--no-ping", action='store_false', dest="ping_enabled", default=True,
                      help="do *NOT* ping (default = *DO* ping)")
    parser.add_option("--no-modem", action='store_false', dest="modem_enabled", default=True,
                      help="do *NOT* check the modem (default = *DO* check modem)")

    (options, args) = parser.parse_args()

    return (options)


def mainroutine():
    # testing stub and entry point for standalone routine
    # global Config

    # some housekeeping so this will work on Windows
    ##        import os,sys,inspect
    ##        cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
    ##        if cmd_folder not in sys.path:
    ##                sys.path.insert(0, cmd_folder)
    ##                logger.debug('adding folder to sys.path')

    # parse the command line
    parser = OptionParser()
    parser.add_option("-f",'--configfile', dest='configfile', default = "camserver.cfg", help="Choose this config file for processing. (use abs path)")
    # parser.add_option("-n", '--notest', dest='test', action='store_const', const=False, default=True,
    #                   help="Take routine out of test mode and run full production")
    parser.add_option("-i", '--info', dest='loglvl', action='store_const', const=logging.INFO, default=logging.DEBUG,
                      help="Set logging to INFO (default = DEBUG)")
    parser.add_option( '--filter', dest='filter', default='system', help="Filter processing with scope (default = user)")

    (options, args) = parser.parse_args()

    # set up logging
    logger = logging.getLogger('')
    logger.setLevel(options.loglvl)
    # logger.debug('entering main()')
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(options.loglvl)
    formatter = logging.Formatter('%(asctime)s %(threadName)-14s %(funcName)s:%(lineno)-5d %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info("Options: {}".format(options))

    default_config_file = os.path.join(os.getcwd(), "default.cfg")

    t = Configuration(default_config_file)

    system_config_file = os.path.join(os.getcwd(), "camserver.cfg")
    #errors = t.load(system_config_file)
    errors = t.check(system_config_file)
    print "errors: {}".format(len(errors))

    user_config_file = os.path.join(os.getcwd(), "coldsnap_config.cfg")
    #user_errors = t.load(user_config_file, scope="user")
    user_errors = t.check(user_config_file, permis_filter = options.filter)
    #user_errors = t.check(user_config_file, permis_filter="user")
    print "errors: {}".format(len(user_errors))

    pass


##    logger.debug(dir())
##    logger.debug(globals())
##    logger.debug(locals())

def main():
    try:
        mainroutine()
    except KeyboardInterrupt:
        print('\nCancelling...')


#####################################################################
#
# MAIN
#
######################################################################

if __name__ == '__main__':
    main()
