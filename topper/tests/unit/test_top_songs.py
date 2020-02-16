import unittest

from topper.process import Process


class TestTopProcess(unittest.TestCase):
    def setUp(self):
        self.process = Process(mode='country')

    def test_update_result(self):
        self.assertEqual({}, self.process.count_songs_aggregated)
        # 1 song occurs twice in FR
        self.process.update_result('FR', 819736552)
        self.process.update_result('FR', 819736552)
        self.assertDictEqual({'FR': {819736552: 2}}, self.process.count_songs_aggregated)

        # Another song FR
        self.process.update_result('FR', 12)
        self.assertDictEqual({'FR': {819736552: 2, 12: 1}}, self.process.count_songs_aggregated)

        # Same first song FR
        self.process.update_result('FR', 819736552)
        self.assertDictEqual({'FR': {819736552: 3, 12: 1}}, self.process.count_songs_aggregated)

        # 1 song occurs 4 times in GB
        self.process.update_result('GB', 12)
        self.process.update_result('GB', 12)
        self.process.update_result('GB', 12)
        self.process.update_result('GB', 12)
        self.assertDictEqual({'FR': {819736552: 3, 12: 1}, 'GB': {12: 4}}, self.process.count_songs_aggregated)

    def test_reduce_days(self):
        input_ = [[('FR', 14, 12)], [('FR', 3, 12)]]
        result = self.process.reduce_days(input_)
        self.assertDictEqual({'FR': {12: 2}}, result)

    def test_get_top50(self):
        dict_count_country_songs = {'FR': {14: 1, 819736552: 3, 12: 1}, 'GB': {12: 4}}
        self.process.count_songs_aggregated = dict_count_country_songs

        result = self.process.get_top50()
        self.assertEqual({'FR': [(819736552, 3), (14, 1), (12, 1)], 'GB': [(12, 4)]}, result)


if __name__ == '__main__':
    unittest.main()
