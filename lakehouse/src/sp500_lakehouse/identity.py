"""Explicit effective-date price routing; never substitute successor prices."""
from sp500_ingest.identity import SKYD_BOUNDARY,SKYD_IDENTITIES

def route_prices_spark(prices,routes):
    """routes grain security_id/ticker_latest; returns reviewed security/date rows."""
    from pyspark.sql import functions as F
    routes=routes.select('security_id','ticker_latest').distinct()
    ambiguous=routes.groupBy('ticker_latest').agg(F.collect_set('security_id').alias('identities')).where(F.size('identities')>1).collect()
    for row in ambiguous:
        if row.ticker_latest!='SKYD' or set(row.identities)!=SKYD_IDENTITIES:
            raise ValueError('Historical ticker reuse requires a reviewed effective-date boundary: '+row.ticker_latest)
    frame=prices.join(routes,on='ticker_latest',how='inner')
    permitted=(F.col('ticker_latest')!='SKYD')|((F.col('security_id')=='CBS_PARAMOUNT_LEGACY')&(F.to_date('date')<F.lit(SKYD_BOUNDARY)))|((F.col('security_id')=='SKYD')&(F.to_date('date')>=F.lit(SKYD_BOUNDARY)))
    return frame.where(permitted)
