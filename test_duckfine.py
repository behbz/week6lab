import unittest

from duckfine import DuckFine


class TestDuckFineInit(unittest.TestCase):
    def test_new_member_starts_with_zero_owed(self):
        duck = DuckFine(member_id=1)
        self.assertEqual(duck.total_owed, 0.0)

    def test_member_id_is_stored(self):
        duck = DuckFine(member_id=42)
        self.assertEqual(duck.member_id, 42)


class TestDuckFineCharge(unittest.TestCase):
    def setUp(self):
        self.duck = DuckFine(member_id=1)

    def test_zero_days_late_is_free(self):
        fee = self.duck.charge(0)
        self.assertEqual(fee, 0.0)

    def test_days_late_within_grace_period_is_free(self):
        fee = self.duck.charge(1)
        self.assertEqual(fee, 0.0)

    def test_days_late_exactly_at_grace_boundary_is_free(self):
        fee = self.duck.charge(DuckFine.GRACE_DAYS)
        self.assertEqual(fee, 0.0)

    def test_fine_grace_period_covers_first_two_days(self):
        # Brief: "the first two days late are forgiven" - literal 2, not DuckFine.GRACE_DAYS,
        # so a shortened grace period can't drag the expectation along with it.
        fee = self.duck.charge(2)
        self.assertEqual(fee, 0.0)

    def test_one_day_past_grace_charges_single_daily_fee(self):
        fee = self.duck.charge(DuckFine.GRACE_DAYS + 1)
        self.assertAlmostEqual(fee, DuckFine.DAILY_FEE)

    def test_multiple_days_past_grace_charges_proportional_fee(self):
        fee = self.duck.charge(DuckFine.GRACE_DAYS + 3)
        self.assertAlmostEqual(fee, 3 * DuckFine.DAILY_FEE)

    def test_deluxe_doubles_the_fee(self):
        normal_fee = self.duck.charge(DuckFine.GRACE_DAYS + 1)
        deluxe_duck = DuckFine(member_id=2)
        deluxe_fee = deluxe_duck.charge(DuckFine.GRACE_DAYS + 1, deluxe=True)
        self.assertAlmostEqual(deluxe_fee, normal_fee * 2)

    def test_fee_is_capped_at_max_fee(self):
        fee = self.duck.charge(days_late=100)
        self.assertEqual(fee, DuckFine.MAX_FEE)

    def test_deluxe_fee_is_capped_at_max_fee(self):
        fee = self.duck.charge(days_late=DuckFine.GRACE_DAYS + 6, deluxe=True)
        self.assertEqual(fee, DuckFine.MAX_FEE)

    def test_negative_days_late_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.duck.charge(-1)

    def test_charge_returns_the_computed_fee(self):
        fee = self.duck.charge(DuckFine.GRACE_DAYS + 2)
        self.assertEqual(fee, 2 * DuckFine.DAILY_FEE)

    def test_total_owed_accumulates_across_multiple_charges(self):
        self.duck.charge(DuckFine.GRACE_DAYS + 1)
        self.duck.charge(DuckFine.GRACE_DAYS + 1)
        self.assertAlmostEqual(self.duck.total_owed, 2 * DuckFine.DAILY_FEE)

    def test_total_owed_unaffected_by_charge_within_grace_period(self):
        self.duck.charge(1)
        self.assertEqual(self.duck.total_owed, 0.0)


if __name__ == "__main__":
    unittest.main()
