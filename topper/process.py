from operator import itemgetter


class Process:
    """
    Computation class providing top songs by country or by user, depending on mode
    """

    def __init__(self, mode):
        self.mode = mode  # the aggregation mode (agg_item or user)
        self.count_songs_aggregated = {}  # representation of count songs by agg_item or user

    def update_result(self, agg_item, sng_id):
        """
        Increment song id for the aggregation item
        :param agg_item: item of aggregation, a country or a user
        :param sng_id: song id to increment
        """
        if agg_item not in self.count_songs_aggregated:
            self.count_songs_aggregated.update({agg_item: {}})

        if sng_id not in self.count_songs_aggregated[agg_item]:
            self.count_songs_aggregated[agg_item].update({sng_id: 1})
        else:
            self.count_songs_aggregated[agg_item][sng_id] = self.count_songs_aggregated[agg_item][sng_id] + 1

    def reduce_days(self, list_days):
        """
        Group by data by day
        :param list_days: list(tuple()): list of data for each day
        :return: dict(): dictionary grouped by and aggregated
        """
        for day in list_days:
            for data in day:
                country, user_id, song_id = data
                if self.mode == 'user':
                    self.update_result(user_id, song_id)
                else:
                    self.update_result(country, song_id)
        return self.count_songs_aggregated

    def get_top50(self):
        """
        Format aggregated dict to get top 50 elements ordered for each entry
        :return: dict(key:list(tuple)
        """
        result = {}
        for country, data in self.count_songs_aggregated.items():

            # Sort songs and get only top 50
            tmp = []
            for song, nber in data.items():
                tmp.append((song, nber))
            country_sorted_50 = sorted(tmp, key=itemgetter(1), reverse=True)[:50]
            result.update({country: country_sorted_50})
        return result
