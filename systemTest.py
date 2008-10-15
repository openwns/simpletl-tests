#! /usr/bin/env python

# this is needed, so that the script can be called from everywhere
import os
import sys
base, tail = os.path.split(sys.argv[0])
os.chdir(base)

# Append the python sub-dir of WNS--main--x.y ...
sys.path.append(os.path.join('..', '..', '..', 'sandbox', 'default', 'lib', 'python2.4', 'site-packages'))

# ... because the module WNS unit test framework is located there.
import pywns.WNSUnit

testSuite1 = pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                    configFile = 'config.py',
                                    shortDescription = 'All kinds of Constanze traffic sent using SimpleTL with UDP/IP',
				    #runSimulations = False,
		                    #readProbes = True, # needed if "Expectation" is used below
                                    requireReferenceOutput = False,
                                    disabled = False, disabledReason = "")

### This makes some nice output graphs to show what the different traffic is like:
# /fast-wns-core -f long_run.py

# create a system test
testSuite = pywns.WNSUnit.TestSuite()
testSuite.addTest(testSuite1)

someExpectation = pywns.WNSUnit.Expectation("traffic.endToEnd.packet.incoming.delay_PDF.dat",
                                      ["probe.trials > 17000","probe.trials < 18000"],
                                      "dbg")
testSuite1.addTest(someExpectation)

if __name__ == '__main__':
    # This is only evaluated if the script is called by hand

    # if you need to change the verbosity do it here
    verbosity = 2

    pywns.WNSUnit.verbosity = verbosity

    # Create test runner
    testRunner = pywns.WNSUnit.TextTestRunner(verbosity=verbosity)

    # Finally, run the tests.
    testRunner.run(testSuite)
    #testRunner.run(testSuite1)
    #testRunner.run(testSuite2)

