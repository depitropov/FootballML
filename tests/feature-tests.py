import unittest
import pandas as pd
import numpy as np
import os
from DataManagement import features


class TestFeatures(unittest.TestCase):

    class daoMock:
        def get_matches_without_features(self, table_name):
            dir = os.path.dirname(os.path.abspath(__file__))
            resources_dir = os.path.join(dir, 'resources')
            file = os.path.join(resources_dir, 'FeaturesTest.csv')
            result = pd.read_csv(file)
            result.date = result.date.astype(pd.Timestamp)

            return result

    def test_feature_calculation(self):
        feature_calculator = features.FeatureCalculator()
        dao = self.daoMock()
        df = dao.get_matches_without_features("temp")
        result = feature_calculator.calculate_features(df, 'home', 0)
        assert (result.home_half_time_draws == 4.000)
        assert (result.home_half_time_wins == 5.000)
        assert (result.home_full_time_draws == 2.000)
        assert (result.home_full_time_wins == 5.000)
        assert (result.home_scored_first_half == 6.000)
        assert (result.home_scored_second_half == 7.000)
        assert (result.home_recovery_percentage == 0.0)
        assert (result.home_turn_around_percentage == 1.00)
        assert (result.home_average_odds == 2.194)
        assert(result.home_lose_draws == 0.00)
        assert(result.home_win_draws == 1.00)
        assert(result.home_side_half_time_wins == 3.000)
        assert(result.home_side_full_time_wins == 2.000)
        assert(result.home_side_half_time_draws == 2.000)
        assert(result.home_side_full_time_draws == 1.000)
        assert(result.home_side_scored_first_half == 4.000)
        assert(result.home_side_scored_second_half == 3.000)
        assert np.isnan(result.home_side_recovery_percentage)
        assert(result.home_side_turn_around_percentage == 0.3333333333333333)
        assert(result.home_side_average_odds == 1.6599999999999997)
        assert(result.home_side_lose_draws == 0.00)
        assert(result.home_side_win_draws == 0.00)

    def test_feature_manager(self):

        class daoMock:
            @staticmethod
            def get_matches_without_features(table_name):
                dir = os.path.dirname(os.path.abspath(__file__))
                resources_dir = os.path.join(dir, 'resources')
                file = os.path.join(resources_dir, 'PreviousMatchesTest.csv')
                matches = pd.read_csv(file)
                matches.date = pd.to_datetime(matches.date, format='%Y-%m-%d %H:%M:%S')
                return matches

            @staticmethod
            def write_features(result, table_name):
                return result

        feature_calculator = features.FeatureCalculator()
        feature_manager = features.FeatureManager(daoMock, feature_calculator, 'temp_table', 10)
        result = feature_manager.generate_features().loc[0.0, :]
        print(result)
        assert (result.home_half_time_draws == 4.000)
        assert (result.home_half_time_wins == 5.000)
        assert (result.home_full_time_draws == 2.000)
        assert (result.home_full_time_wins == 5.000)
        assert (result.home_scored_first_half == 6.000)
        assert (result.home_scored_second_half == 7.000)
        assert (result.home_recovery_percentage == 0.0)
        assert (result.home_turn_around_percentage == 1.00)
        assert (result.home_average_odds == 2.194)
        assert(result.home_lose_draws == 0.00)
        assert(result.home_win_draws == 1.00)
        assert(result.home_side_half_time_wins == 3.000)
        assert(result.home_side_full_time_wins == 2.000)
        assert(result.home_side_half_time_draws == 2.000)
        assert(result.home_side_full_time_draws == 1.000)
        assert(result.home_side_scored_first_half == 4.000)
        assert(result.home_side_scored_second_half == 3.000)
        assert np.isnan(result.home_side_recovery_percentage)
        assert(result.home_side_turn_around_percentage == 0.3333333333333333)
        assert(result.home_side_average_odds == 1.6599999999999997)
        assert(result.home_side_lose_draws == 0.00)
        assert(result.home_side_win_draws == 0.00)


if __name__ == '__main__':
    unittest.main()
