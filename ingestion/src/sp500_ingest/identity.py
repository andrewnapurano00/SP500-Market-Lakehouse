"""Reviewed corporate-identity boundary from finalize_daily_population.py.

The SKYD endpoint was cross-checked against CBS/VIAC prices by the original
pipeline. The 2025-08-07 issuer boundary is explicit there and in the reviewed
membership intervals; it is not inferred from an index entry or ticker string.
"""
SKYD_BOUNDARY='2025-08-07'
SKYD_IDENTITIES={'CBS_PARAMOUNT_LEGACY','SKYD'}

def price_identity(ticker,day,requested_security_id):
    if ticker=='SKYD' and requested_security_id is not None:
        if requested_security_id not in SKYD_IDENTITIES:raise ValueError('Unexpected SKYD identity route')
        return 'CBS_PARAMOUNT_LEGACY' if str(day)[:10]<SKYD_BOUNDARY else 'SKYD'
    return requested_security_id
