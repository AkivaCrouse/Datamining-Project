######################################################################################################################
"""
Title: Data Enrichment - Google Trends API
Authors: Akiva Crouse, Ohad Ben Tzvi and Roni Reuven
Date: 26/07/2021
"""
######################################################################################################################

import pandas as pd
from pytrends.request import TrendReq


def get_top_ten_regions(tag):
    """
    Gets a tag and returned the top 10 regions in which this tag is searched on Google
    Parameters
    ----------
    tag: string tag which came from an article

    Returns: DataFrame of top 10 regions in which it was searched
    -------
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[tag])
    interest_by_region_df = pytrend.interest_by_region()
    return interest_by_region_df.sort_values(by=tag, ascending=False).head(10)


def main():
    print(get_top_ten_regions('Blockchain'))
    pass


if __name__ == '__main__':
    main()
