from unittest import TestCase
from stocks.platform import StockTradingPlatform
from datetime import datetime
from gen_test_sets import TestSets
from stocks.trade import Trade

test_sets = TestSets()
SAMPLE_DATE = datetime.strptime('1/1/2022 1:00:00', '%d/%m/%Y %H:%M:%S')


class TestStockTradingPlatform(TestCase):

    @staticmethod
    def __trades_equal(trade_1: Trade, trade_2: Trade) -> bool:
        return trade_1.name == trade_2.name and trade_1.price == trade_2.price \
               and trade_1.quantity == trade_2.quantity and trade_1.time == trade_2.time

    def test_log_bad_stock(self):
        sut = StockTradingPlatform()
        try:
            sut.logTransaction(["UCL Bank", 1, 1, SAMPLE_DATE])
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "Invalid Stock Name: UCL Bank")
        except:
            self.assertFalse(True)

    def test_log_bad_stock_value(self):
        sut = StockTradingPlatform()
        try:
            sut.logTransaction(["HSBA", 0, 1, SAMPLE_DATE])
        except ValueError as e:
            self.assertEqual("Invalid Stock Price: 0", e.args[0])
        except:
            self.assertFalse(True)

    def test_log_bad_quantity(self):
        sut = StockTradingPlatform()
        try:
            sut.logTransaction(["HSBA", 100, 0, SAMPLE_DATE])
        except ValueError as e:
            self.assertEqual("Invalid Stock Quantity: 0", e.args[0])
        except:
            self.assertFalse(True)

    def test_log_insert_first(self):
        sut = StockTradingPlatform()
        t = ["HSBA", 100, 2, SAMPLE_DATE]

        sut.logTransaction(t)

        result = sut.sortedTransactions("HSBA")

        self.assertEqual(len(result), 1)
        self.assertTrue(self.__trades_equal(result[0], Trade(*t)))

    def test_log_many_of_one(self):
        # This generates 100 trades for HSBA with a min value of 100 and a max value of 100000
        # It is guaranteed that at least one trade exists with a value of 100 and one exists with a value of 100000
        sut, test_trades = test_sets.platform_gen_many_same_stock(stock="HSBA", low=100, high=100000)

        trade_list = sut.sortedTransactions("HSBA")

        # Assert right number of trades were inserted
        self.assertEqual(len(test_trades), len(trade_list))

        # Assert trade with correct minimum value was inserted
        self.assertEqual(sut.minTransactions("HSBA")[0].get_trade_val(), 100)

        # Assert trade with correct maximum value was inserted
        self.assertEqual(sut.maxTransactions("HSBA")[0].get_trade_val(), 100000)

    def test_log_one_of_each(self):
        sut = StockTradingPlatform()

        for stock in sut.STOCKS:
            sut.logTransaction(test_sets.gen_one_trade(stock, 1000, 100000))

        for stock in sut.STOCKS:
            self.assertEqual(len(sut.sortedTransactions(stock)), 1)

    def test_log(self):
        sut = StockTradingPlatform()

        sut.logTransaction(["London Stock Exchange Group",
                            1000, 5,
                            datetime.strptime("2020-02-25T22:00:15", "%Y-%m-%dT%H:%M:%S")])

        self.assertTrue(True)

    def test_log_all_same_trade_val(self):
        sut, trades = test_sets.platform_gen_many_same_val(250)

        for stock in sut.STOCKS:
            self.assertEqual(sut.minTransactions(stock), sut.maxTransactions(stock))

    def test_log_some_conflicts(self):
        trades1 = test_sets.trade_gen_many_same_value(550)
        trades2 = test_sets.trade_gen_many(min_val=1000, max_val=100000)
        sut = StockTradingPlatform()

        for trade in trades1 + trades2:
            sut.logTransaction(trade)

        total_len = 0
        for stock in sut.STOCKS:
            total_len += len(sut.sortedTransactions(stock))

        self.assertEqual(total_len, len(trades1) + len(trades2))

    def test_sorted_transactions_empty(self):
        sut = StockTradingPlatform()

        result = sut.sortedTransactions("HSBA")

        self.assertEqual(result, [])

    def test_sorted_one(self):
        t = test_sets.gen_one_trade("HSBA", 100, 100)
        sut = StockTradingPlatform()
        sut.logTransaction(t)

        result = sut.sortedTransactions("HSBA")

        self.assertTrue(self.__trades_equal(result[0], Trade(*t)))

    def test_sorted_many(self):
        sut, trades = test_sets.platform_gen_many_same_stock("HSBA")
        trades.sort(key=lambda x: x[1] * x[2])

        sorted_trades = sut.sortedTransactions("HSBA")

        for index, trade in enumerate(trades):
            self.assertTrue(self.__trades_equal(sorted_trades[index], Trade(*trade)))

    def test_sorted_all_one_val(self):
        sut, _ = test_sets.platform_gen_many_same_val(500)

        trade_list = sut.sortedTransactions("HSBA")

        # Essentially, just make sure nothing breaks
        for trade in trade_list:
            self.assertEqual(trade.get_trade_val(), 500)

    def test_min_transactions_none(self):
        sut = StockTradingPlatform()

        min_t = sut.minTransactions("HSBA")

        self.assertEqual([], min_t)

    def test_min_transactions_all_same(self):
        sut, _ = test_sets.platform_gen_many_same_val(5000)

        min_trades = sut.minTransactions("HSBA")

        for trade in min_trades:
            self.assertEqual(trade.get_trade_val(), 5000)

    def test_min_transactions(self):
        sut, _ = test_sets.platform_gen_many_same_stock(low=100, high=100000, stock="HSBA")

        min_set = sut.minTransactions("HSBA")

        self.assertEqual(100, min_set[0].get_trade_val())

    def test_min_transactions_one(self):
        sut = StockTradingPlatform()
        t = ["HSBA", 500, 2, SAMPLE_DATE]
        sut.logTransaction(t)

        min_set = sut.minTransactions("HSBA")

        self.assertEqual(len(min_set), 1)
        self.assertTrue(self.__trades_equal(min_set[0], Trade(*t)))

    def test_min_bad_name(self):
        sut = StockTradingPlatform()

        try:
            sut.minTransactions("UCL Bank")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "minTransactions: Invalid Stock Name: UCL Bank")
        except:
            self.assertFalse(True)

    def test_max_transactions_none(self):
        sut = StockTradingPlatform()

        max_t = sut.minTransactions("HSBA")

        self.assertEqual([], max_t)

    def test_max_transactions_all_same(self):
        sut, _ = test_sets.platform_gen_many_same_val(5000)

        max_trades = sut.maxTransactions("HSBA")

        for trade in max_trades:
            self.assertEqual(trade.get_trade_val(), 5000)

    def test_max_transactions(self):
        sut, _ = test_sets.platform_gen_many_same_stock(low=100, high=100000, stock="HSBA")

        max_set = sut.maxTransactions("HSBA")

        self.assertEqual(100000, max_set[0].get_trade_val())

    def test_max_transactions_one(self):
        sut = StockTradingPlatform()
        t = ["HSBA", 500, 2, SAMPLE_DATE]
        sut.logTransaction(t)

        max_set = sut.minTransactions("HSBA")

        self.assertEqual(len(max_set), 1)
        self.assertTrue(self.__trades_equal(max_set[0], Trade(*t)))

    def test_max_bad_name(self):
        sut = StockTradingPlatform()

        try:
            sut.maxTransactions("UCL Bank")
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "maxTransactions: Invalid Stock Name: UCL Bank")
        except:
            self.assertFalse(True)

    def test_floor_transactions_empty(self):
        sut = StockTradingPlatform()#

        floor = sut.floorTransactions("HSBA", 100)

        self.assertEqual(floor, [])

    def test_floor_below_min(self):
        sut, _ = test_sets.platform_gen_many_same_stock("HSBA", low=100)

        floor = sut.floorTransactions("HSBA", 99)

        self.assertEqual([], floor)

    def test_floor_above_max(self):
        sut, _ = test_sets.platform_gen_many_same_stock("HSBA", high=100000)

        floor = sut.floorTransactions("HSBA", 100001)

        self.assertEqual(floor[0].get_trade_val(), 100000)

    def test_floor_equal_min(self):
        sut, _ = test_sets.platform_gen_many_same_stock("HSBA", low=100)

        floor = sut.floorTransactions("HSBA", 100)

        self.assertEqual(100, floor[0].get_trade_val())

    def test_floor_bad_name(self):
        sut = StockTradingPlatform()

        try:
            sut.floorTransactions("UCL Bank", 200)
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "floorTransactions: Invalid Stock Name: UCL Bank")
        except:
            self.assertFalse(True)

    def test_ceiling_transactions_empty(self):
        sut = StockTradingPlatform()  #

        ceiling = sut.ceilingTransactions("HSBA", 100)

        self.assertEqual(ceiling, [])

    def test_ceiling_above_max(self):
        sut, _ = test_sets.platform_gen_many_same_stock("HSBA", high=100000)

        ceiling = sut.ceilingTransactions("HSBA", 100001)

        self.assertEqual([], ceiling)

    def test_ceiling_below_min(self):
        sut, _ = test_sets.platform_gen_many_same_stock("HSBA", low=100)

        ceiling = sut.ceilingTransactions("HSBA", 99)

        self.assertEqual(ceiling[0].get_trade_val(), 100)

    def test_ceiling_equal_max(self):
        sut, _ = test_sets.platform_gen_many_same_stock("HSBA", high=100000)

        ceiling = sut.floorTransactions("HSBA", 100000)

        self.assertEqual(100000, ceiling[0].get_trade_val())

    def test_ceiling_bad_name(self):
        sut = StockTradingPlatform()

        try:
            sut.ceilingTransactions("UCL Bank", 200)
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "ceilingTransactions: Invalid Stock Name: UCL Bank")
        except:
            self.assertFalse(True)

    def test_range_bad_range(self):
        sut = StockTradingPlatform()

        try:
            sut.rangeTransactions("HSBA", fromValue=101, toValue=99)
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "rangeTransactions: Invalid Range Bounds: fromValue: 101 toValue: 99")
        except:
            self.assertFalse(True)

    def test_range_inclusive_below(self):
        sut = StockTradingPlatform()
        sut.logTransaction(["HSBA", 100, 2, SAMPLE_DATE])
        sut.logTransaction(["HSBA", 500, 3, SAMPLE_DATE])
        sut.logTransaction(["HSBA", 1000, 4, SAMPLE_DATE])

        range_set = sut.rangeTransactions("HSBA", 200, 300)

        self.assertEqual(1, len(range_set))
        self.assertTrue(self.__trades_equal(range_set[0], Trade(*["HSBA", 100, 2, SAMPLE_DATE])))

    def test_range_inclusive_above(self):
        sut = StockTradingPlatform()
        sut.logTransaction(["HSBA", 100, 2, SAMPLE_DATE])
        sut.logTransaction(["HSBA", 500, 3, SAMPLE_DATE])
        sut.logTransaction(["HSBA", 1000, 4, SAMPLE_DATE])

        range_set = sut.rangeTransactions("HSBA", 2000, 4000)

        self.assertEqual(1, len(range_set))
        self.assertTrue(self.__trades_equal(range_set[0], Trade(*["HSBA", 1000, 4, SAMPLE_DATE])))

    def test_range_equal_to_stock(self):
        sut = StockTradingPlatform()
        sut.logTransaction(["HSBA", 100, 2, SAMPLE_DATE])
        sut.logTransaction(["HSBA", 500, 3, SAMPLE_DATE])
        sut.logTransaction(["HSBA", 1000, 4, SAMPLE_DATE])

        range_set = sut.rangeTransactions("HSBA", 1500, 1500)

        self.assertEqual(1, len(range_set))
        self.assertTrue(self.__trades_equal(range_set[0], Trade(*["HSBA", 500, 3, SAMPLE_DATE])))

    def test_range_bad_name(self):
        sut = StockTradingPlatform()

        try:
            sut.rangeTransactions("UCL Bank", 200, 500)
            self.assertFalse(True)
        except ValueError as e:
            self.assertEqual(e.args[0], "rangeTransactions: Invalid Stock Name: UCL Bank")
        except:
            self.assertFalse(True)

