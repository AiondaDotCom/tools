#!/usr/bin/python
# -*- coding: utf-8 -*-

##
# File:     helperUnitTest.py
# Author:   arwk
# Github:   https://github.com/AiondaDotCom/tools
# Created:  25.10.17
# Modified: 25.10.17
##

import helper as hlp

import unittest

class TestUM(unittest.TestCase):

    def setUp(self):
        pass

    def testDecimalToTimedelta(self):
        """
        Test decimalToTimedelta & timedeltaToDecimal
        """
        for h in range(0,24):
            for m in range(0,60):
                timedelta = hlp.hoursMinutesToTimedelta(h, m)
                newTimedelta = hlp.decimalToTimedelta(hlp.timedeltaToDecimal(timedelta))
                #print h, m, timedelta, newTimedelta

                #print timedelta, newTimedelta, timedelta == newTimedelta
                self.assertEqual(timedelta, newTimedelta)

    # Test roundToNearest()


if __name__ == '__main__':
    unittest.main()
