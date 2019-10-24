# This script is used to

import yang as ly
import logging
import argparse
import sys
import ijson
import json
#import sonic_yang as sy
from os import listdir
from os.path import isfile, join, splitext

#Globals vars
PASS = 0
FAIL = 1
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("YANG-TEST")
log.setLevel(logging.INFO)
log.addHandler(logging.NullHandler())

# Global functions
def printExceptionDetails():
    try:
        excType, excObj, traceBack = sys.exc_info()
        fileName = traceBack.tb_frame.f_code.co_filename
        lineNumber = traceBack.tb_lineno
        log.error(" Exception >{}< in {}:{}".format(excObj, fileName, lineNumber))
    except Exception as e:
        log.error(" Exception in printExceptionDetails")
    return

# class for YANG Model YangModelTesting
# Run function will run all the tests
# from a user given list.

class YangModelTesting:

    def __init__(self, tests, yangDir, jsonFile):
        self.defaultYANGFailure = {
            'Must': ['Must condition', 'not satisfied'],
            'InvalidValue': ['Invalid value'],
            'LeafRef': ['Leafref', 'non-existing'],
            'When': ['When condition', 'not satisfied'],
            'Pattern': ['pattern', 'does not satisfy']
        }

        self.ExceptionTests = {
            'WRONG_FAMILY_WITH_IP_PREFIX': {
                'desc': 'Configure Wrong family with ip-prefix for VLAN_Interface Table',
                'eStr': self.defaultYANGFailure['Must']
            },
            'DHCP_SERVER_INCORRECT_FORMAT': {
                'desc': 'Add dhcp_server which is not in correct ip-prefix format.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['dhcp_servers']
            },
            'VLAN_WITH_NON_EXIST_PORT': {
                'desc': 'Configure a member port in VLAN_MEMBER table which does not exist.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'VLAN_MEMEBER_WITH_NON_EXIST_VLAN': {
                'desc': 'Configure vlan-id in VLAN_MEMBER table which does not exist in VLAN  table.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'TAGGING_MODE_WRONG_VALUE': {
                'desc': 'Configure wrong value for tagging_mode.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['tagging_mode']
            },
            'INTERFACE_IP_PREFIX_EMPTY_STRING': {
                'desc': 'Configure empty string as ip-prefix in INTERFACE table.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['ip-prefix']
            },
            'ACL_RULE_UNDEFINED_PACKET_ACTION': {
                'desc': 'Configure undefined packet_action in ACL_RULE table.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['PACKET_ACTION']
            },
            'ACL_TABLE_UNDEFINED_TABLE_TYPE': {
                'desc': 'Configure undefined acl_table_type in ACL_TABLE table.',
                'eStr': self.defaultYANGFailure['InvalidValue'] + ['type']
            },
            'ACL_RULE_WITH_NON_EXIST_ACL_TABLE': {
                'desc': 'Configure non-existing ACL_TABLE in ACL_RULE.',
                'eStr': self.defaultYANGFailure['LeafRef']
            },
            'ACL_RULE_IP_TYPE_SRC_IPV6_MISMATCH': {
                'desc': 'Configure IP_TYPE as ipv4any and SRC_IPV6 in ACL_RULE.',
                'eStr': self.defaultYANGFailure['When'] + ['IP_TYPE']
            },
            'ACL_RULE_ARP_TYPE_DST_IPV6_MISMATCH': {
                'desc': 'Configure IP_TYPE as ARP and DST_IPV6 in ACL_RULE.',
                'eStr': self.defaultYANGFailure['When'] + ['IP_TYPE']
            },
            'ACL_RULE_WRONG_L4_SRC_PORT_RANGE': {
                'desc': 'Configure l4_src_port_range as 99999-99999 in ACL_RULE',
                'eStr': self.defaultYANGFailure['Pattern']
            },
            'ACL_RULE_ARP_TYPE_ICMPV6_CODE_MISMATCH': {
                'desc': 'Configure IP_TYPE as ARP and ICMPV6_CODE in ACL_RULE.',
                'eStr': self.defaultYANGFailure['When'] + ['IP_TYPE']
            },
            'ACL_RULE_WRONG_INNER_ETHER_TYPE': {
                'desc': 'Configure INNER_ETHER_TYPE as 0x080C in ACL_RULE.',
                'eStr': self.defaultYANGFailure['Pattern']
            }
        }

        self.tests = tests
        if (self.tests == None):
            self.tests = self.ExceptionTests.keys()
        self.yangDir = yangDir
        self.jsonFile = jsonFile
        self.testNum = 1
        # other class vars
        # self.ctx
        return

    """
        load all YANG models before test run
    """
    def loadYangModel(self, yangDir):
        try:
            # get all files
            yangFiles = [f for f in listdir(yangDir) if isfile(join(yangDir, f))]
            # get all yang files
            yangFiles = [f for f in yangFiles if splitext(f)[-1].lower()==".yang"]
            yangFiles = [f.split('.')[0] for f in yangFiles]
            # load yang mdoules
            self.ctx = ly.Context(yangDir)
            log.debug(yangFiles)
            for f in yangFiles:
                # load a module
                log.debug(f)
                m = self.ctx.get_module(f)
                if m is not None:
                    log.error("Could not get module: {}".format(m.name()))
                else:
                    m = self.ctx.load_module(f)
                    if m is not None:
                        log.info("module: {} is loaded successfully".format(m.name()))
                    else:
                        return
        except Exception as e:
            printExceptionDetails()
            raise e
        return

    """
        Run all tests from list self.tests
    """
    def run(self):
        try:
            self.loadYangModel(self.yangDir)
            ret = 0
            for test in self.tests:
                test = test.strip()
                if test in self.ExceptionTests:
                    self.runExceptionTest(test);
        except Exception as e:
            printExceptionDetails()
            raise e
        return ret

    """
        Get the JSON input based on func name
        and return jsonInput
    """
    def readJsonInput(self, test):
        try:
            # load test specific Dictionary, using Key = func
            # this is to avoid loading very large JSON in memory
            log.debug(" Read JSON Section: " + test)
            jInput = ""
            with open(self.jsonFile, 'rb') as f:
                jInst = ijson.items(f, test)
                for it in jInst:
                    jInput = jInput + json.dumps(it)
            log.debug(jInput)
        except Exception as e:
            printExceptionDetails()
        return jInput

    """
        Log the start of a test
    """
    def logStartTest(self, desc):
        log.info("\n------------------- Test "+ str(self.testNum) +\
        ": " + desc + "---------------------")
        self.testNum = self.testNum + 1
        return

    """
        Load Config Data and return Exception as String
    """
    def loadConfigData(self, jInput):
        s = ""
        try:
            node = self.ctx.parse_data_mem(jInput, ly.LYD_JSON, \
            ly.LYD_OPT_CONFIG | ly.LYD_OPT_STRICT)
        except Exception as e:
            s = str(e)
            log.debug(s)
        return s

    """
        Run Exception Test
    """
    def runExceptionTest(self, test):
        try:
            desc = self.ExceptionTests[test]['desc']
            self.logStartTest(desc)
            jInput = self.readJsonInput(test)
            # load the data, expect a exception with must condition failure
            s = self.loadConfigData(jInput)
            eStr = self.ExceptionTests[test]['eStr']
            log.debug(eStr)
            if (sum(1 for str in eStr if str not in s) == 0):
                log.info(desc + " Passed\n")
                return PASS
        except Exception as e:
            printExceptionDetails()
        log.info(desc + " Failed\n")
        return FAIL

# End of Class

"""
    Start Here
"""
def main():
    parser = argparse.ArgumentParser(description='Script to run YANG model tests',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog="""
Usage:
python yangModelTesting.py -h
""")
    parser.add_argument('-t', '--tests', type=str, \
    help='tests to run separated by comma')
    parser.add_argument('-f', '--json-file', type=str, \
    help='JSON input for tests ', required=True)
    parser.add_argument('-y', '--yang-dir', type=str, \
    help='Path to YANG models', required=True)
    parser.add_argument('-v', '--verbose-level', \
    help='Verbose mode', action='store_true')
    parser.add_argument('-l', '--list-tests', \
    help='list all tests', action='store_true')

    args = parser.parse_args()
    try:
        tests = args.tests
        jsonFile = args.json_file
        yangDir = args.yang_dir
        logLevel = args.verbose_level
        listTests = args.list_tests
        if logLevel:
            log.setLevel(logging.DEBUG)
        # Make a list
        if (tests):
            tests = tests.split(",")

        yTest = YangModelTesting(tests, yangDir, jsonFile)
        if (listTests):
            log.info(yTest.ExceptionTests.keys())
            sys.exit(0)

        ret = yTest.run()
        if ret == 0:
            log.info("All Test Passed")
        sys.exit(ret)

    except Exception as e:
        printExceptionDetails()
        sys.exit(1)

    return
if __name__ == '__main__':
    main()
