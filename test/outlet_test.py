import unittest
from unittest.mock import Mock
import asyncio
from xknx import XKNX, Outlet
from xknx.knx import Address, Telegram, TelegramType, DPTBinary


class TestOutlet(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    #
    # SYNC STATE
    #
    def test_sync_state(self):

        xknx = XKNX(self.loop, start=False)
        outlet = Outlet(xknx, "TestOutlet", group_address='1/2/3')
        outlet.sync_state()

        self.assertEqual(xknx.telegrams.qsize(), 1)

        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(Address('1/2/3'), TelegramType.GROUP_READ))


    #
    # TEST PROCESS
    #
    def test_process(self):
        xknx = XKNX(self.loop, start=False)
        outlet = Outlet(xknx, 'TestOutlet', group_address='1/2/3')

        self.assertEqual(outlet.state, False)

        telegram_on = Telegram()
        telegram_on.payload = DPTBinary(1)
        outlet.process(telegram_on)

        self.assertEqual(outlet.state, True)

        telegram_off = Telegram()
        telegram_off.payload = DPTBinary(0)
        outlet.process(telegram_off)

        self.assertEqual(outlet.state, False)


    def test_process_callback(self):
        # pylint: disable=no-self-use

        xknx = XKNX(self.loop, start=False)
        outlet = Outlet(xknx, 'TestOutlet', group_address='1/2/3')

        after_update_callback = Mock()
        outlet.after_update_callback = after_update_callback

        telegram = Telegram()
        telegram.payload = DPTBinary(1)
        outlet.process(telegram)

        after_update_callback.assert_called_with(outlet)


    #
    # TEST SET ON
    #
    def test_set_on(self):
        xknx = XKNX(self.loop, start=False)
        outlet = Outlet(xknx, 'TestOutlet', group_address='1/2/3')
        outlet.set_on()
        self.assertEqual(xknx.telegrams.qsize(), 1)
        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(Address('1/2/3'), payload=DPTBinary(1)))

    #
    # TEST SET OFF
    #
    def test_set_off(self):
        xknx = XKNX(self.loop, start=False)
        outlet = Outlet(xknx, 'TestOutlet', group_address='1/2/3')
        outlet.set_off()
        self.assertEqual(xknx.telegrams.qsize(), 1)
        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(Address('1/2/3'), payload=DPTBinary(0)))

    #
    # TEST DO
    #
    def test_do(self):
        xknx = XKNX(self.loop, start=False)
        outlet = Outlet(xknx, 'TestOutlet', group_address='1/2/3')
        outlet.do("on")
        self.assertTrue(outlet.state)
        outlet.do("off")
        self.assertFalse(outlet.state)

SUITE = unittest.TestLoader().loadTestsFromTestCase(TestOutlet)
unittest.TextTestRunner(verbosity=2).run(SUITE)
