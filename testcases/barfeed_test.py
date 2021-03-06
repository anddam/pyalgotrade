# PyAlgoTrade
#
# Copyright 2011-2014 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

import unittest
import datetime

from pyalgotrade import barfeed
from pyalgotrade import bar
from pyalgotrade import dispatcher


def check_base_barfeed(testCase, barFeed, barsHaveAdjClose, isRealTime):
    called = {"called": True}

    def callback(dateTime, bars):
        called["called"] = True
        testCase.assertEquals(barFeed.getCurrentDateTime(), dateTime)

    testCase.assertEquals(barFeed.getCurrentDateTime(), None)
    testCase.assertEquals(barFeed.barsHaveAdjClose(), barsHaveAdjClose)
    if not barsHaveAdjClose:
        with testCase.assertRaisesRegexp(Exception, "The barfeed doesn't support adjusted close values.*"):
            barFeed.setUseAdjustedValues(True)
    testCase.assertEquals(barFeed.isRealTime(), isRealTime)

    d = dispatcher.Dispatcher()
    d.addSubject(barFeed)
    barFeed.getNewValuesEvent().subscribe(callback)
    d.run()

    testCase.assertEquals(called["called"], True)


class OptimizerBarFeedestCase(unittest.TestCase):
    def testDateTimesNotInOrder(self):
        bars = [
            bar.Bars({"orcl": bar.BasicBar(datetime.datetime(2001, 1, 2), 1, 1, 1, 1, 1, 1, bar.Frequency.DAY)}),
            bar.Bars({"orcl": bar.BasicBar(datetime.datetime(2001, 1, 1), 1, 1, 1, 1, 1, 1, bar.Frequency.DAY)}),
        ]
        f = barfeed.OptimizerBarFeed(bar.Frequency.DAY, ["orcl"], bars)
        with self.assertRaisesRegexp(Exception, "Bar date times are not in order.*"):
            for dt, b in f:
                pass

    def testBaseBarFeed(self):
        bars = [
            bar.Bars({"orcl": bar.BasicBar(datetime.datetime(2001, 1, 1), 1, 1, 1, 1, 1, 1, bar.Frequency.DAY)}),
            bar.Bars({"orcl": bar.BasicBar(datetime.datetime(2001, 1, 2), 1, 1, 1, 1, 1, 1, bar.Frequency.DAY)}),
        ]
        barFeed = barfeed.OptimizerBarFeed(bar.Frequency.DAY, ["orcl"], bars)
        check_base_barfeed(self, barFeed, True, False)

    def testBaseBarFeedNoAdjClose(self):
        bars = [
            bar.Bars({"orcl": bar.BasicBar(datetime.datetime(2001, 1, 1), 1, 1, 1, 1, 1, None, bar.Frequency.DAY)}),
            bar.Bars({"orcl": bar.BasicBar(datetime.datetime(2001, 1, 2), 1, 1, 1, 1, 1, None, bar.Frequency.DAY)}),
        ]
        barFeed = barfeed.OptimizerBarFeed(bar.Frequency.DAY, ["orcl"], bars)
        check_base_barfeed(self, barFeed, False, False)

    def testEmtpy(self):
        barFeed = barfeed.OptimizerBarFeed(bar.Frequency.DAY, ["orcl"], [])
        self.assertEquals(barFeed.barsHaveAdjClose(), False)

