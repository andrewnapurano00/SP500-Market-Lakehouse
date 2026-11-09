--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: analyst_estimates_annual; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.analyst_estimates_annual (
    symbol text,
    date date,
    "estimatedRevenueLow" bigint,
    "estimatedRevenueHigh" bigint,
    "estimatedRevenueAvg" bigint,
    "estimatedEbitdaLow" bigint,
    "estimatedEbitdaHigh" bigint,
    "estimatedEbitdaAvg" bigint,
    "estimatedEbitLow" bigint,
    "estimatedEbitHigh" bigint,
    "estimatedEbitAvg" bigint,
    "estimatedNetIncomeLow" bigint,
    "estimatedNetIncomeHigh" bigint,
    "estimatedNetIncomeAvg" double precision,
    "estimatedSgaExpenseLow" bigint,
    "estimatedSgaExpenseHigh" bigint,
    "estimatedSgaExpenseAvg" bigint,
    "estimatedEpsAvg" double precision,
    "estimatedEpsHigh" double precision,
    "estimatedEpsLow" double precision,
    "numberAnalystEstimatedRevenue" bigint,
    "numberAnalystsEstimatedEps" bigint,
    ticker text,
    estimate_period_type text,
    date_start date,
    date_end date,
    ingested_at timestamp without time zone
);


--
-- Name: balance_sheets_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.balance_sheets_q (
    symbol text,
    date timestamp without time zone,
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    reportedcurrency text,
    cik text,
    fillingdate text,
    accepteddate text,
    calendaryear text,
    period text,
    cashandcashequivalents double precision,
    shortterminvestments double precision,
    cashandshortterminvestments double precision,
    netreceivables double precision,
    inventory double precision,
    othercurrentassets double precision,
    totalcurrentassets double precision,
    propertyplantequipmentnet double precision,
    goodwill double precision,
    intangibleassets bigint,
    goodwillandintangibleassets double precision,
    longterminvestments double precision,
    taxassets double precision,
    othernoncurrentassets double precision,
    totalnoncurrentassets double precision,
    otherassets double precision,
    totalassets double precision,
    accountpayables double precision,
    shorttermdebt double precision,
    taxpayables double precision,
    deferredrevenue double precision,
    othercurrentliabilities double precision,
    totalcurrentliabilities double precision,
    longtermdebt double precision,
    deferredrevenuenoncurrent double precision,
    deferredtaxliabilitiesnoncurrent double precision,
    othernoncurrentliabilities double precision,
    totalnoncurrentliabilities double precision,
    otherliabilities double precision,
    capitalleaseobligations bigint,
    totalliabilities double precision,
    preferredstock double precision,
    commonstock double precision,
    retainedearnings double precision,
    accumulatedothercomprehensiveincomeloss double precision,
    othertotalstockholdersequity double precision,
    totalstockholdersequity double precision,
    totalequity double precision,
    totalliabilitiesandstockholdersequity double precision,
    minorityinterest double precision,
    totalliabilitiesandtotalequity double precision,
    totalinvestments double precision,
    totaldebt double precision,
    netdebt double precision,
    link text,
    finallink text,
    cashandcashequivalents_yoy double precision,
    shortterminvestments_yoy double precision,
    cashandshortterminvestments_yoy double precision,
    netreceivables_yoy double precision,
    inventory_yoy double precision,
    othercurrentassets_yoy double precision,
    totalcurrentassets_yoy double precision,
    propertyplantequipmentnet_yoy double precision,
    longterminvestments_yoy double precision,
    totalnoncurrentassets_yoy double precision,
    totalassets_yoy double precision,
    accountpayables_yoy double precision,
    shorttermdebt_yoy double precision,
    totalcurrentliabilities_yoy double precision,
    longtermdebt_yoy double precision,
    totalnoncurrentliabilities_yoy double precision,
    totalliabilities_yoy double precision,
    commonstock_yoy double precision,
    retainedearnings_yoy double precision,
    totalstockholdersequity_yoy double precision,
    totalequity_yoy double precision,
    totaldebt_yoy double precision,
    netdebt_yoy double precision,
    current_ratio double precision,
    quick_ratio double precision,
    cash_ratio double precision,
    working_capital double precision,
    working_capital_to_assets double precision,
    inventory_to_current double precision,
    debt_to_equity double precision,
    debt_to_assets double precision,
    net_debt_to_equity double precision,
    liabilities_to_assets double precision,
    equity_ratio double precision,
    lt_debt_to_capital double precision,
    total_debt_to_capital double precision,
    total_debt double precision,
    net_debt double precision,
    total_assets double precision,
    total_equity double precision,
    total_liabilities double precision,
    total_current_assets double precision,
    total_current_liabilities double precision,
    cash_and_st_investments double precision,
    financialleverage double precision,
    financialleverage_avg4q double precision,
    financialleverage_yoy double precision,
    debttoequity double precision,
    liabilitiestoequity double precision,
    debttoassets double precision,
    netdebttoequity double precision,
    book_value double precision,
    book_value_yoy_growth double precision,
    book_value_3y_growth double precision,
    asset_yoy_growth double precision,
    asset_3y_growth double precision,
    book_value_growth_yoy double precision,
    book_value_growth_3y double precision,
    three_year_book_value_growth double precision,
    asset_growth_yoy double precision,
    asset_growth_3y double precision,
    three_year_asset_growth double precision,
    avg_total_assets double precision,
    avg_total_equity double precision,
    average_total_assets double precision,
    average_total_equity double precision,
    accounting_reconciliation_failed boolean,
    availability_proxy boolean,
    cik_normalized text,
    data_available_at timestamp with time zone,
    ingested_at timestamp with time zone,
    pit_revision_uncertain boolean,
    source_family text,
    source_notebook text,
    source_row_id text,
    source_symbol text,
    source_version text
);


--
-- Name: cashflow_statements_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cashflow_statements_q (
    symbol text,
    date timestamp without time zone,
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    reportedcurrency text,
    cik text,
    fillingdate text,
    accepteddate text,
    calendaryear text,
    period text,
    netincome double precision,
    depreciationandamortization double precision,
    deferredincometax double precision,
    stockbasedcompensation double precision,
    changeinworkingcapital double precision,
    accountsreceivables double precision,
    inventory double precision,
    accountspayables double precision,
    otherworkingcapital double precision,
    othernoncashitems double precision,
    netcashprovidedbyoperatingactivities double precision,
    investmentsinpropertyplantandequipment double precision,
    acquisitionsnet double precision,
    purchasesofinvestments double precision,
    salesmaturitiesofinvestments double precision,
    otherinvestingactivites double precision,
    netcashusedforinvestingactivites double precision,
    debtrepayment double precision,
    commonstockissued double precision,
    commonstockrepurchased double precision,
    dividendspaid double precision,
    otherfinancingactivites double precision,
    netcashusedprovidedbyfinancingactivities double precision,
    effectofforexchangesoncash double precision,
    netchangeincash double precision,
    cashatendofperiod double precision,
    cashatbeginningofperiod double precision,
    operatingcashflow double precision,
    capitalexpenditure double precision,
    freecashflow double precision,
    operatingcashflow_ttm double precision,
    freecashflow_ttm double precision,
    investingcashflow_ttm bigint,
    operatingcashflow_ttm_growth double precision,
    freecashflow_ttm_growth double precision,
    investingcashflow_ttm_growth double precision,
    operatingcashflow_q_yoy double precision,
    freecashflow_q_yoy double precision,
    investingcashflow_q_yoy double precision,
    link text,
    finallink text,
    operatingcashflow_ttm_yoy_growth double precision,
    operatingcashflow_ttm_3y_growth double precision,
    freecashflow_ttm_yoy_growth double precision,
    freecashflow_ttm_3y_growth double precision,
    investingcashflow_ttm_yoy_growth double precision,
    investingcashflow_ttm_3y_growth double precision,
    operating_cashflow_ttm_yoy_growth double precision,
    operating_cashflow_ttm_3y_growth double precision,
    free_cashflow_ttm_yoy_growth double precision,
    free_cashflow_ttm_3y_growth double precision,
    accounting_reconciliation_failed boolean,
    availability_proxy boolean,
    cf_mode text,
    cf_semantics_available_at timestamp with time zone,
    cf_semantics_verified boolean,
    cik_normalized text,
    commonstockissued_ttm double precision,
    commonstockrepurchased_ttm double precision,
    data_available_at timestamp with time zone,
    dividendspaid_ttm double precision,
    fcf_derived boolean,
    fcf_reconciliation_failed boolean,
    ingested_at timestamp with time zone,
    ocf_alias_mismatch boolean,
    pit_revision_uncertain boolean,
    source_family text,
    source_notebook text,
    source_row_id text,
    source_symbol text,
    source_version text,
    ttm_available_at timestamp with time zone,
    ttm_source_ids text,
    ttm_valid boolean,
    ttm_accounting_reconciliation_failed boolean
);


--
-- Name: earnings_surprises_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.earnings_surprises_q (
    symbol character varying(16),
    date date,
    eps_est double precision,
    eps_actual double precision,
    surprise_abs double precision,
    surprise_pct double precision,
    beat_flag integer,
    date_start date,
    date_end date
);


--
-- Name: enterprise_values_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enterprise_values_q (
    symbol text,
    date timestamp without time zone,
    enterprisevalue double precision,
    stockprice double precision,
    numberofshares double precision,
    marketcapitalization double precision,
    minuscashandcashequivalents double precision,
    addtotaldebt double precision,
    accounting_reconciliation_failed boolean,
    cik_normalized text,
    data_available_at timestamp with time zone,
    ingested_at timestamp with time zone,
    pit_revision_uncertain boolean,
    source_family text,
    source_notebook text,
    source_row_id text,
    source_symbol text,
    source_version text,
    observation_close_at timestamp with time zone,
    availability_unknown boolean
);


--
-- Name: factor_definition_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.factor_definition_registry (
    factor_id text,
    family text,
    numerator_fields text,
    denominator_fields text,
    upstream_notebooks text,
    upstream_tables text,
    formula text,
    direction text,
    version text,
    money_floor_absolute double precision,
    eps_floor_absolute double precision,
    materiality_fraction double precision,
    min_peers bigint,
    currency_policy text,
    revision_policy text,
    audit_only_fields text
);


--
-- Name: factor_quality_long; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.factor_quality_long (
    security_id text,
    month_end timestamp without time zone,
    factor_id text,
    missing_reason text,
    n_valid bigint,
    n_eligible_applicable bigint,
    sector_coverage double precision,
    score_missing_reason text,
    outlier_flag boolean,
    peer_group_used text,
    version text
);


--
-- Name: fundamental_cleaning_threshold_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fundamental_cleaning_threshold_audit (
    peer_group text,
    factor_id text,
    month_end timestamp without time zone,
    fit_observations bigint,
    fit_end timestamp without time zone,
    low double precision,
    high double precision
);


--
-- Name: fundamental_extension_capabilities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fundamental_extension_capabilities (
    metric text,
    available boolean,
    status text,
    version text
);


--
-- Name: fundamental_raw_payload_manifest; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fundamental_raw_payload_manifest (
    batch_id text,
    source_family text,
    source_notebook text,
    payload_path text,
    payload_sha256 text
);


--
-- Name: fundamental_source_lineage; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fundamental_source_lineage (
    security_id text,
    month_end timestamp without time zone,
    family text,
    source_row_id text,
    ttm_source_ids text,
    available_at timestamp with time zone,
    ttm_available_at timestamp with time zone,
    ttm_used boolean,
    lag4_source_ids text,
    lag12_source_ids text,
    feature_cutoff_at timestamp with time zone,
    source_notebook text
);


--
-- Name: income_statements_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.income_statements_q (
    symbol text,
    date timestamp without time zone,
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    reportedcurrency text,
    cik text,
    fillingdate timestamp without time zone,
    accepteddate timestamp without time zone,
    calendaryear text,
    period text,
    revenue double precision,
    costofrevenue double precision,
    grossprofit double precision,
    grossprofitratio double precision,
    researchanddevelopmentexpenses bigint,
    generalandadministrativeexpenses double precision,
    sellingandmarketingexpenses double precision,
    sellinggeneralandadministrativeexpenses double precision,
    otherexpenses double precision,
    operatingexpenses double precision,
    costandexpenses double precision,
    interestincome double precision,
    interestexpense double precision,
    depreciationandamortization double precision,
    ebitda double precision,
    ebitdaratio double precision,
    operatingincome double precision,
    operatingincomeratio double precision,
    totalotherincomeexpensesnet double precision,
    incomebeforetax double precision,
    incomebeforetaxratio double precision,
    incometaxexpense double precision,
    netincome double precision,
    netincomeratio double precision,
    eps double precision,
    epsdiluted double precision,
    weightedaverageshsout double precision,
    weightedaverageshsoutdil double precision,
    link text,
    finallink text,
    revenue_ttm double precision,
    netincome_ttm double precision,
    operatingincome_ttm double precision,
    revenue_ttm_growth double precision,
    netincome_ttm_growth double precision,
    operatingincome_ttm_growth double precision,
    revenue_q_yoy double precision,
    netincome_q_yoy double precision,
    operatingincome_q_yoy double precision,
    costofrevenue_ttm double precision,
    grossprofit_ttm double precision,
    researchanddevelopmentexpenses_ttm double precision,
    interestincome_ttm double precision,
    interestexpense_ttm double precision,
    depreciationandamortization_ttm double precision,
    ebitda_ttm double precision,
    incomebeforetax_ttm double precision,
    incometaxexpense_ttm double precision,
    ebitda_margin_ttm double precision,
    gross_margin_ttm double precision,
    net_margin_ttm double precision,
    operating_margin_ttm double precision,
    rd_as_pct_revenue_ttm double precision,
    interest_coverage_ttm double precision,
    revenue_yoy_growth double precision,
    net_income_yoy_growth double precision,
    operating_income_yoy_growth double precision,
    revenue_3y_growth double precision,
    three_year_revenue_growth double precision,
    net_income_3y_growth double precision,
    three_year_net_income_growth double precision,
    accounting_reconciliation_failed boolean,
    availability_proxy boolean,
    cik_normalized text,
    data_available_at timestamp with time zone,
    ebitda_ttm_growth double precision,
    eps_approximation boolean,
    eps_ttm double precision,
    epsdiluted_ttm double precision,
    ingested_at timestamp with time zone,
    pit_revision_uncertain boolean,
    source_family text,
    source_notebook text,
    source_row_id text,
    source_symbol text,
    source_version text,
    ttm_available_at timestamp with time zone,
    ttm_source_ids text,
    ttm_valid boolean
);


--
-- Name: key_metrics_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.key_metrics_q (
    symbol text,
    date date,
    "calendarYear" text,
    period text,
    "revenuePerShare" double precision,
    "netIncomePerShare" double precision,
    "operatingCashFlowPerShare" double precision,
    "freeCashFlowPerShare" double precision,
    "cashPerShare" double precision,
    "bookValuePerShare" double precision,
    "tangibleBookValuePerShare" double precision,
    "shareholdersEquityPerShare" double precision,
    "interestDebtPerShare" double precision,
    "marketCap" double precision,
    "enterpriseValue" double precision,
    "peRatio" double precision,
    "priceToSalesRatio" double precision,
    pocfratio double precision,
    "pfcfRatio" double precision,
    "pbRatio" double precision,
    "ptbRatio" double precision,
    "evToSales" double precision,
    "enterpriseValueOverEBITDA" double precision,
    "evToOperatingCashFlow" double precision,
    "evToFreeCashFlow" double precision,
    "earningsYield" double precision,
    "freeCashFlowYield" double precision,
    "debtToEquity" double precision,
    "debtToAssets" double precision,
    "netDebtToEBITDA" double precision,
    "currentRatio" double precision,
    "interestCoverage" double precision,
    "incomeQuality" double precision,
    "dividendYield" double precision,
    "payoutRatio" double precision,
    "salesGeneralAndAdministrativeToRevenue" double precision,
    "researchAndDdevelopementToRevenue" double precision,
    "intangiblesToTotalAssets" double precision,
    "capexToOperatingCashFlow" double precision,
    "capexToRevenue" double precision,
    "capexToDepreciation" double precision,
    "stockBasedCompensationToRevenue" double precision,
    "grahamNumber" double precision,
    roic double precision,
    "returnOnTangibleAssets" double precision,
    "grahamNetNet" double precision,
    "workingCapital" double precision,
    "tangibleAssetValue" double precision,
    "netCurrentAssetValue" double precision,
    "investedCapital" double precision,
    "averageReceivables" double precision,
    "averagePayables" double precision,
    "averageInventory" double precision,
    "daysSalesOutstanding" double precision,
    "daysPayablesOutstanding" double precision,
    "daysOfInventoryOnHand" double precision,
    "receivablesTurnover" double precision,
    "payablesTurnover" double precision,
    "inventoryTurnover" double precision,
    roe double precision,
    "capexPerShare" double precision,
    ticker text,
    date_start date,
    date_end date
);


--
-- Name: macro_cross_asset_features_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.macro_cross_asset_features_daily (
    date date NOT NULL,
    dollar_source_date date,
    dollar_adj_close double precision,
    dollar_return_21d double precision,
    dollar_return_63d double precision,
    dollar_return_126d double precision,
    dollar_return_252d double precision,
    dollar_realized_vol_21d double precision,
    dollar_realized_vol_63d double precision,
    dollar_price_to_sma200 double precision,
    dollar_drawdown_252d double precision,
    gold_source_date date,
    gold_adj_close double precision,
    gold_return_21d double precision,
    gold_return_63d double precision,
    gold_return_126d double precision,
    gold_return_252d double precision,
    gold_realized_vol_21d double precision,
    gold_realized_vol_63d double precision,
    gold_price_to_sma200 double precision,
    gold_drawdown_252d double precision,
    high_yield_source_date date,
    high_yield_adj_close double precision,
    high_yield_return_21d double precision,
    high_yield_return_63d double precision,
    high_yield_return_126d double precision,
    high_yield_return_252d double precision,
    high_yield_realized_vol_21d double precision,
    high_yield_realized_vol_63d double precision,
    high_yield_price_to_sma200 double precision,
    high_yield_drawdown_252d double precision,
    investment_grade_source_date date,
    investment_grade_adj_close double precision,
    investment_grade_return_21d double precision,
    investment_grade_return_63d double precision,
    investment_grade_return_126d double precision,
    investment_grade_return_252d double precision,
    investment_grade_realized_vol_21d double precision,
    investment_grade_realized_vol_63d double precision,
    investment_grade_price_to_sma200 double precision,
    investment_grade_drawdown_252d double precision,
    market_source_date date,
    market_adj_close double precision,
    market_return_21d double precision,
    market_return_63d double precision,
    market_return_126d double precision,
    market_return_252d double precision,
    market_realized_vol_21d double precision,
    market_realized_vol_63d double precision,
    market_price_to_sma200 double precision,
    market_drawdown_252d double precision,
    oil_source_date date,
    oil_adj_close double precision,
    oil_return_21d double precision,
    oil_return_63d double precision,
    oil_return_126d double precision,
    oil_return_252d double precision,
    oil_realized_vol_21d double precision,
    oil_realized_vol_63d double precision,
    oil_price_to_sma200 double precision,
    oil_drawdown_252d double precision,
    treasury_10y_source_date date,
    treasury_10y_yield_pct double precision,
    treasury_10y_change_21d_bp double precision,
    treasury_10y_change_63d_bp double precision,
    treasury_2y_source_date date,
    treasury_2y_yield_pct double precision,
    treasury_2y_change_21d_bp double precision,
    treasury_2y_change_63d_bp double precision,
    treasury_30y_source_date date,
    treasury_30y_yield_pct double precision,
    treasury_30y_change_21d_bp double precision,
    treasury_30y_change_63d_bp double precision,
    treasury_3m_source_date date,
    treasury_3m_yield_pct double precision,
    treasury_3m_change_21d_bp double precision,
    treasury_3m_change_63d_bp double precision,
    treasury_intermediate_source_date date,
    treasury_intermediate_adj_close double precision,
    treasury_intermediate_return_21d double precision,
    treasury_intermediate_return_63d double precision,
    treasury_intermediate_return_126d double precision,
    treasury_intermediate_return_252d double precision,
    treasury_intermediate_realized_vol_21d double precision,
    treasury_intermediate_realized_vol_63d double precision,
    treasury_intermediate_price_to_sma200 double precision,
    treasury_intermediate_drawdown_252d double precision,
    treasury_long_source_date date,
    treasury_long_adj_close double precision,
    treasury_long_return_21d double precision,
    treasury_long_return_63d double precision,
    treasury_long_return_126d double precision,
    treasury_long_return_252d double precision,
    treasury_long_realized_vol_21d double precision,
    treasury_long_realized_vol_63d double precision,
    treasury_long_price_to_sma200 double precision,
    treasury_long_drawdown_252d double precision,
    volatility_proxy_source_date date,
    volatility_proxy_adj_close double precision,
    volatility_proxy_return_21d double precision,
    volatility_proxy_return_63d double precision,
    volatility_proxy_return_126d double precision,
    volatility_proxy_return_252d double precision,
    volatility_proxy_realized_vol_21d double precision,
    volatility_proxy_realized_vol_63d double precision,
    volatility_proxy_price_to_sma200 double precision,
    volatility_proxy_drawdown_252d double precision,
    curve_10y_2y_pp double precision,
    curve_10y_3m_pp double precision,
    credit_hyg_minus_lqd_return_21d double precision,
    gold_minus_oil_return_21d double precision,
    credit_hyg_minus_lqd_return_63d double precision,
    gold_minus_oil_return_63d double precision,
    vix_source_date date,
    vix_level double precision,
    vix_change_1d_points double precision,
    vix_change_1d_fraction double precision,
    vix_change_5d_points double precision,
    vix_change_5d_fraction double precision,
    vix_change_21d_points double precision,
    vix_change_21d_fraction double precision,
    vix_change_63d_points double precision,
    vix_change_63d_fraction double precision,
    vix_mean_21d double precision,
    vix_vs_mean_21d double precision,
    vix_mean_63d double precision,
    vix_vs_mean_63d double precision,
    vix_percentile_252d double precision
);


--
-- Name: macro_cross_asset_observations_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.macro_cross_asset_observations_daily (
    date date NOT NULL,
    observation_date date,
    series text NOT NULL,
    value double precision
);


--
-- Name: market_caps_d; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.market_caps_d (
    symbol text,
    date timestamp without time zone,
    marketcap double precision,
    accounting_reconciliation_failed boolean,
    cik_normalized text,
    data_available_at timestamp with time zone,
    ingested_at timestamp with time zone,
    pit_revision_uncertain boolean,
    source_family text,
    source_notebook text,
    source_row_id text,
    source_symbol text,
    source_version text
);


--
-- Name: market_sector_macro_features_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.market_sector_macro_features_daily (
    date timestamp without time zone,
    sp500_close real,
    sp500_ret_20d real,
    sp500_ret_30d real,
    sp500_ret_60d real,
    sp500_ret_120d real,
    sp500_ret_180d real,
    sp500_ret_252d real,
    sp500_ret_360d real,
    sp500_realized_vol_20d real,
    sp500_realized_vol_60d real,
    sp500_realized_vol_252d real,
    sp500_price_vs_sma_50 real,
    sp500_price_vs_sma_200 real,
    sp500_drawdown_252d real,
    technology_close real,
    technology_ret_20d real,
    technology_ret_30d real,
    technology_ret_60d real,
    technology_ret_120d real,
    technology_ret_180d real,
    technology_ret_252d real,
    technology_ret_360d real,
    technology_realized_vol_20d real,
    technology_realized_vol_60d real,
    technology_realized_vol_252d real,
    technology_price_vs_sma_50 real,
    technology_price_vs_sma_200 real,
    technology_drawdown_252d real,
    financials_close real,
    financials_ret_20d real,
    financials_ret_30d real,
    financials_ret_60d real,
    financials_ret_120d real,
    financials_ret_180d real,
    financials_ret_252d real,
    financials_ret_360d real,
    financials_realized_vol_20d real,
    financials_realized_vol_60d real,
    financials_realized_vol_252d real,
    financials_price_vs_sma_50 real,
    financials_price_vs_sma_200 real,
    financials_drawdown_252d real,
    healthcare_close real,
    healthcare_ret_20d real,
    healthcare_ret_30d real,
    healthcare_ret_60d real,
    healthcare_ret_120d real,
    healthcare_ret_180d real,
    healthcare_ret_252d real,
    healthcare_ret_360d real,
    healthcare_realized_vol_20d real,
    healthcare_realized_vol_60d real,
    healthcare_realized_vol_252d real,
    healthcare_price_vs_sma_50 real,
    healthcare_price_vs_sma_200 real,
    healthcare_drawdown_252d real,
    consumer_discretionary_close real,
    consumer_discretionary_ret_20d real,
    consumer_discretionary_ret_30d real,
    consumer_discretionary_ret_60d real,
    consumer_discretionary_ret_120d real,
    consumer_discretionary_ret_180d real,
    consumer_discretionary_ret_252d real,
    consumer_discretionary_ret_360d real,
    consumer_discretionary_realized_vol_20d real,
    consumer_discretionary_realized_vol_60d real,
    consumer_discretionary_realized_vol_252d real,
    consumer_discretionary_price_vs_sma_50 real,
    consumer_discretionary_price_vs_sma_200 real,
    consumer_discretionary_drawdown_252d real,
    consumer_staples_close real,
    consumer_staples_ret_20d real,
    consumer_staples_ret_30d real,
    consumer_staples_ret_60d real,
    consumer_staples_ret_120d real,
    consumer_staples_ret_180d real,
    consumer_staples_ret_252d real,
    consumer_staples_ret_360d real,
    consumer_staples_realized_vol_20d real,
    consumer_staples_realized_vol_60d real,
    consumer_staples_realized_vol_252d real,
    consumer_staples_price_vs_sma_50 real,
    consumer_staples_price_vs_sma_200 real,
    consumer_staples_drawdown_252d real,
    industrials_close real,
    industrials_ret_20d real,
    industrials_ret_30d real,
    industrials_ret_60d real,
    industrials_ret_120d real,
    industrials_ret_180d real,
    industrials_ret_252d real,
    industrials_ret_360d real,
    industrials_realized_vol_20d real,
    industrials_realized_vol_60d real,
    industrials_realized_vol_252d real,
    industrials_price_vs_sma_50 real,
    industrials_price_vs_sma_200 real,
    industrials_drawdown_252d real,
    energy_close real,
    energy_ret_20d real,
    energy_ret_30d real,
    energy_ret_60d real,
    energy_ret_120d real,
    energy_ret_180d real,
    energy_ret_252d real,
    energy_ret_360d real,
    energy_realized_vol_20d real,
    energy_realized_vol_60d real,
    energy_realized_vol_252d real,
    energy_price_vs_sma_50 real,
    energy_price_vs_sma_200 real,
    energy_drawdown_252d real,
    utilities_close real,
    utilities_ret_20d real,
    utilities_ret_30d real,
    utilities_ret_60d real,
    utilities_ret_120d real,
    utilities_ret_180d real,
    utilities_ret_252d real,
    utilities_ret_360d real,
    utilities_realized_vol_20d real,
    utilities_realized_vol_60d real,
    utilities_realized_vol_252d real,
    utilities_price_vs_sma_50 real,
    utilities_price_vs_sma_200 real,
    utilities_drawdown_252d real,
    real_estate_close real,
    real_estate_ret_20d real,
    real_estate_ret_30d real,
    real_estate_ret_60d real,
    real_estate_ret_120d real,
    real_estate_ret_180d real,
    real_estate_ret_252d real,
    real_estate_ret_360d real,
    real_estate_realized_vol_20d real,
    real_estate_realized_vol_60d real,
    real_estate_realized_vol_252d real,
    real_estate_price_vs_sma_50 real,
    real_estate_price_vs_sma_200 real,
    real_estate_drawdown_252d real,
    materials_close real,
    materials_ret_20d real,
    materials_ret_30d real,
    materials_ret_60d real,
    materials_ret_120d real,
    materials_ret_180d real,
    materials_ret_252d real,
    materials_ret_360d real,
    materials_realized_vol_20d real,
    materials_realized_vol_60d real,
    materials_realized_vol_252d real,
    materials_price_vs_sma_50 real,
    materials_price_vs_sma_200 real,
    materials_drawdown_252d real,
    communication_services_close real,
    communication_services_ret_20d real,
    communication_services_ret_30d real,
    communication_services_ret_60d real,
    communication_services_ret_120d real,
    communication_services_ret_180d real,
    communication_services_ret_252d real,
    communication_services_ret_360d real,
    communication_services_realized_vol_20d real,
    communication_services_realized_vol_60d real,
    communication_services_realized_vol_252d real,
    communication_services_price_vs_sma_50 real,
    communication_services_price_vs_sma_200 real,
    communication_services_drawdown_252d real,
    gold_price real,
    gold_ret_20d real,
    gold_ret_30d real,
    gold_ret_60d real,
    gold_ret_120d real,
    gold_ret_180d real,
    gold_ret_252d real,
    gold_ret_360d real,
    wti_oil_price_proxy real,
    wti_oil_ret_20d real,
    wti_oil_ret_30d real,
    wti_oil_ret_60d real,
    wti_oil_ret_120d real,
    wti_oil_ret_180d real,
    wti_oil_ret_252d real,
    wti_oil_ret_360d real,
    dxy_level_proxy real,
    dxy_ret_20d real,
    dxy_ret_30d real,
    dxy_ret_60d real,
    dxy_ret_120d real,
    dxy_ret_180d real,
    dxy_ret_252d real,
    dxy_ret_360d real,
    vix_proxy_level real,
    vix_proxy_change_20d real,
    vix_proxy_change_60d real,
    vix_proxy_change_120d real,
    vix_proxy_ma_20d real,
    vix_proxy_ma_60d real,
    vix_proxy_vs_ma_60d real,
    vix_proxy_percentile_252d real,
    treasury_3m_proxy_close real,
    treasury_3m_proxy_ret_20d real,
    treasury_3m_proxy_ret_30d real,
    treasury_3m_proxy_ret_60d real,
    treasury_3m_proxy_ret_120d real,
    treasury_3m_proxy_ret_180d real,
    treasury_3m_proxy_ret_252d real,
    treasury_3m_proxy_ret_360d real,
    treasury_10y_proxy_close real,
    treasury_10y_proxy_ret_20d real,
    treasury_10y_proxy_ret_30d real,
    treasury_10y_proxy_ret_60d real,
    treasury_10y_proxy_ret_120d real,
    treasury_10y_proxy_ret_180d real,
    treasury_10y_proxy_ret_252d real,
    treasury_10y_proxy_ret_360d real,
    treasury_30y_proxy_close real,
    treasury_30y_proxy_ret_20d real,
    treasury_30y_proxy_ret_30d real,
    treasury_30y_proxy_ret_60d real,
    treasury_30y_proxy_ret_120d real,
    treasury_30y_proxy_ret_180d real,
    treasury_30y_proxy_ret_252d real,
    treasury_30y_proxy_ret_360d real,
    treasury_10y_vs_3m_proxy_ratio real,
    treasury_30y_vs_3m_proxy_ratio real,
    treasury_10y_proxy_change_60d real,
    treasury_30y_proxy_change_60d real,
    week_end timestamp without time zone
);


--
-- Name: market_sector_macro_features_weekly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.market_sector_macro_features_weekly (
    date timestamp without time zone,
    sp500_close real,
    sp500_ret_20d real,
    sp500_ret_30d real,
    sp500_ret_60d real,
    sp500_ret_120d real,
    sp500_ret_180d real,
    sp500_ret_252d real,
    sp500_ret_360d real,
    sp500_realized_vol_20d real,
    sp500_realized_vol_60d real,
    sp500_realized_vol_252d real,
    sp500_price_vs_sma_50 real,
    sp500_price_vs_sma_200 real,
    sp500_drawdown_252d real,
    technology_close real,
    technology_ret_20d real,
    technology_ret_30d real,
    technology_ret_60d real,
    technology_ret_120d real,
    technology_ret_180d real,
    technology_ret_252d real,
    technology_ret_360d real,
    technology_realized_vol_20d real,
    technology_realized_vol_60d real,
    technology_realized_vol_252d real,
    technology_price_vs_sma_50 real,
    technology_price_vs_sma_200 real,
    technology_drawdown_252d real,
    financials_close real,
    financials_ret_20d real,
    financials_ret_30d real,
    financials_ret_60d real,
    financials_ret_120d real,
    financials_ret_180d real,
    financials_ret_252d real,
    financials_ret_360d real,
    financials_realized_vol_20d real,
    financials_realized_vol_60d real,
    financials_realized_vol_252d real,
    financials_price_vs_sma_50 real,
    financials_price_vs_sma_200 real,
    financials_drawdown_252d real,
    healthcare_close real,
    healthcare_ret_20d real,
    healthcare_ret_30d real,
    healthcare_ret_60d real,
    healthcare_ret_120d real,
    healthcare_ret_180d real,
    healthcare_ret_252d real,
    healthcare_ret_360d real,
    healthcare_realized_vol_20d real,
    healthcare_realized_vol_60d real,
    healthcare_realized_vol_252d real,
    healthcare_price_vs_sma_50 real,
    healthcare_price_vs_sma_200 real,
    healthcare_drawdown_252d real,
    consumer_discretionary_close real,
    consumer_discretionary_ret_20d real,
    consumer_discretionary_ret_30d real,
    consumer_discretionary_ret_60d real,
    consumer_discretionary_ret_120d real,
    consumer_discretionary_ret_180d real,
    consumer_discretionary_ret_252d real,
    consumer_discretionary_ret_360d real,
    consumer_discretionary_realized_vol_20d real,
    consumer_discretionary_realized_vol_60d real,
    consumer_discretionary_realized_vol_252d real,
    consumer_discretionary_price_vs_sma_50 real,
    consumer_discretionary_price_vs_sma_200 real,
    consumer_discretionary_drawdown_252d real,
    consumer_staples_close real,
    consumer_staples_ret_20d real,
    consumer_staples_ret_30d real,
    consumer_staples_ret_60d real,
    consumer_staples_ret_120d real,
    consumer_staples_ret_180d real,
    consumer_staples_ret_252d real,
    consumer_staples_ret_360d real,
    consumer_staples_realized_vol_20d real,
    consumer_staples_realized_vol_60d real,
    consumer_staples_realized_vol_252d real,
    consumer_staples_price_vs_sma_50 real,
    consumer_staples_price_vs_sma_200 real,
    consumer_staples_drawdown_252d real,
    industrials_close real,
    industrials_ret_20d real,
    industrials_ret_30d real,
    industrials_ret_60d real,
    industrials_ret_120d real,
    industrials_ret_180d real,
    industrials_ret_252d real,
    industrials_ret_360d real,
    industrials_realized_vol_20d real,
    industrials_realized_vol_60d real,
    industrials_realized_vol_252d real,
    industrials_price_vs_sma_50 real,
    industrials_price_vs_sma_200 real,
    industrials_drawdown_252d real,
    energy_close real,
    energy_ret_20d real,
    energy_ret_30d real,
    energy_ret_60d real,
    energy_ret_120d real,
    energy_ret_180d real,
    energy_ret_252d real,
    energy_ret_360d real,
    energy_realized_vol_20d real,
    energy_realized_vol_60d real,
    energy_realized_vol_252d real,
    energy_price_vs_sma_50 real,
    energy_price_vs_sma_200 real,
    energy_drawdown_252d real,
    utilities_close real,
    utilities_ret_20d real,
    utilities_ret_30d real,
    utilities_ret_60d real,
    utilities_ret_120d real,
    utilities_ret_180d real,
    utilities_ret_252d real,
    utilities_ret_360d real,
    utilities_realized_vol_20d real,
    utilities_realized_vol_60d real,
    utilities_realized_vol_252d real,
    utilities_price_vs_sma_50 real,
    utilities_price_vs_sma_200 real,
    utilities_drawdown_252d real,
    real_estate_close real,
    real_estate_ret_20d real,
    real_estate_ret_30d real,
    real_estate_ret_60d real,
    real_estate_ret_120d real,
    real_estate_ret_180d real,
    real_estate_ret_252d real,
    real_estate_ret_360d real,
    real_estate_realized_vol_20d real,
    real_estate_realized_vol_60d real,
    real_estate_realized_vol_252d real,
    real_estate_price_vs_sma_50 real,
    real_estate_price_vs_sma_200 real,
    real_estate_drawdown_252d real,
    materials_close real,
    materials_ret_20d real,
    materials_ret_30d real,
    materials_ret_60d real,
    materials_ret_120d real,
    materials_ret_180d real,
    materials_ret_252d real,
    materials_ret_360d real,
    materials_realized_vol_20d real,
    materials_realized_vol_60d real,
    materials_realized_vol_252d real,
    materials_price_vs_sma_50 real,
    materials_price_vs_sma_200 real,
    materials_drawdown_252d real,
    communication_services_close real,
    communication_services_ret_20d real,
    communication_services_ret_30d real,
    communication_services_ret_60d real,
    communication_services_ret_120d real,
    communication_services_ret_180d real,
    communication_services_ret_252d real,
    communication_services_ret_360d real,
    communication_services_realized_vol_20d real,
    communication_services_realized_vol_60d real,
    communication_services_realized_vol_252d real,
    communication_services_price_vs_sma_50 real,
    communication_services_price_vs_sma_200 real,
    communication_services_drawdown_252d real,
    gold_price real,
    gold_ret_20d real,
    gold_ret_30d real,
    gold_ret_60d real,
    gold_ret_120d real,
    gold_ret_180d real,
    gold_ret_252d real,
    gold_ret_360d real,
    wti_oil_price_proxy real,
    wti_oil_ret_20d real,
    wti_oil_ret_30d real,
    wti_oil_ret_60d real,
    wti_oil_ret_120d real,
    wti_oil_ret_180d real,
    wti_oil_ret_252d real,
    wti_oil_ret_360d real,
    dxy_level_proxy real,
    dxy_ret_20d real,
    dxy_ret_30d real,
    dxy_ret_60d real,
    dxy_ret_120d real,
    dxy_ret_180d real,
    dxy_ret_252d real,
    dxy_ret_360d real,
    vix_proxy_level real,
    vix_proxy_change_20d real,
    vix_proxy_change_60d real,
    vix_proxy_change_120d real,
    vix_proxy_ma_20d real,
    vix_proxy_ma_60d real,
    vix_proxy_vs_ma_60d real,
    vix_proxy_percentile_252d real,
    treasury_3m_proxy_close real,
    treasury_3m_proxy_ret_20d real,
    treasury_3m_proxy_ret_30d real,
    treasury_3m_proxy_ret_60d real,
    treasury_3m_proxy_ret_120d real,
    treasury_3m_proxy_ret_180d real,
    treasury_3m_proxy_ret_252d real,
    treasury_3m_proxy_ret_360d real,
    treasury_10y_proxy_close real,
    treasury_10y_proxy_ret_20d real,
    treasury_10y_proxy_ret_30d real,
    treasury_10y_proxy_ret_60d real,
    treasury_10y_proxy_ret_120d real,
    treasury_10y_proxy_ret_180d real,
    treasury_10y_proxy_ret_252d real,
    treasury_10y_proxy_ret_360d real,
    treasury_30y_proxy_close real,
    treasury_30y_proxy_ret_20d real,
    treasury_30y_proxy_ret_30d real,
    treasury_30y_proxy_ret_60d real,
    treasury_30y_proxy_ret_120d real,
    treasury_30y_proxy_ret_180d real,
    treasury_30y_proxy_ret_252d real,
    treasury_30y_proxy_ret_360d real,
    treasury_10y_vs_3m_proxy_ratio real,
    treasury_30y_vs_3m_proxy_ratio real,
    treasury_10y_proxy_change_60d real,
    treasury_30y_proxy_change_60d real,
    week_end timestamp without time zone
);


--
-- Name: rates_momentum_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rates_momentum_daily (
    date date NOT NULL,
    t_1m double precision,
    t_6m double precision,
    t_12m double precision
);


--
-- Name: ratios_annual; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ratios_annual (
    symbol character varying(32),
    date date,
    "calendarYear" character varying(32),
    period character varying(32),
    "currentRatio" double precision,
    "quickRatio" double precision,
    "cashRatio" double precision,
    "daysOfSalesOutstanding" double precision,
    "daysOfInventoryOutstanding" double precision,
    "operatingCycle" double precision,
    "daysOfPayablesOutstanding" double precision,
    "cashConversionCycle" double precision,
    "grossProfitMargin" double precision,
    "operatingProfitMargin" double precision,
    "pretaxProfitMargin" double precision,
    "netProfitMargin" double precision,
    "effectiveTaxRate" double precision,
    "returnOnAssets" double precision,
    "returnOnEquity" double precision,
    "returnOnCapitalEmployed" double precision,
    "netIncomePerEBT" double precision,
    "ebtPerEbit" double precision,
    "ebitPerRevenue" double precision,
    "debtRatio" double precision,
    "debtEquityRatio" double precision,
    "longTermDebtToCapitalization" double precision,
    "totalDebtToCapitalization" double precision,
    "interestCoverage" double precision,
    "cashFlowToDebtRatio" double precision,
    "companyEquityMultiplier" double precision,
    "receivablesTurnover" double precision,
    "payablesTurnover" double precision,
    "inventoryTurnover" double precision,
    "fixedAssetTurnover" double precision,
    "assetTurnover" double precision,
    "operatingCashFlowPerShare" double precision,
    "freeCashFlowPerShare" double precision,
    "cashPerShare" double precision,
    "payoutRatio" double precision,
    "operatingCashFlowSalesRatio" double precision,
    "freeCashFlowOperatingCashFlowRatio" double precision,
    "cashFlowCoverageRatios" double precision,
    "shortTermCoverageRatios" double precision,
    "capitalExpenditureCoverageRatio" double precision,
    "dividendPaidAndCapexCoverageRatio" double precision,
    "dividendPayoutRatio" double precision,
    "priceBookValueRatio" double precision,
    "priceToBookRatio" double precision,
    "priceToSalesRatio" double precision,
    "priceEarningsRatio" double precision,
    "priceToFreeCashFlowsRatio" double precision,
    "priceToOperatingCashFlowsRatio" double precision,
    "priceCashFlowRatio" double precision,
    "priceEarningsToGrowthRatio" double precision,
    "priceSalesRatio" double precision,
    "dividendYield" double precision,
    "enterpriseValueMultiple" double precision,
    "priceFairValue" double precision,
    date_start date,
    date_end date,
    ingested_at timestamp without time zone
);


--
-- Name: ratios_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ratios_q (
    symbol text,
    date date,
    "calendarYear" text,
    period text,
    "currentRatio" double precision,
    "quickRatio" double precision,
    "cashRatio" double precision,
    "daysOfSalesOutstanding" double precision,
    "daysOfInventoryOutstanding" double precision,
    "operatingCycle" double precision,
    "daysOfPayablesOutstanding" double precision,
    "cashConversionCycle" double precision,
    "grossProfitMargin" double precision,
    "operatingProfitMargin" double precision,
    "pretaxProfitMargin" double precision,
    "netProfitMargin" double precision,
    "effectiveTaxRate" double precision,
    "returnOnAssets" double precision,
    "returnOnEquity" double precision,
    "returnOnCapitalEmployed" double precision,
    "netIncomePerEBT" double precision,
    "ebtPerEbit" double precision,
    "ebitPerRevenue" double precision,
    "debtRatio" double precision,
    "debtEquityRatio" double precision,
    "longTermDebtToCapitalization" double precision,
    "totalDebtToCapitalization" double precision,
    "interestCoverage" double precision,
    "cashFlowToDebtRatio" double precision,
    "companyEquityMultiplier" double precision,
    "receivablesTurnover" double precision,
    "payablesTurnover" double precision,
    "inventoryTurnover" double precision,
    "fixedAssetTurnover" double precision,
    "assetTurnover" double precision,
    "operatingCashFlowPerShare" double precision,
    "freeCashFlowPerShare" double precision,
    "cashPerShare" double precision,
    "payoutRatio" double precision,
    "operatingCashFlowSalesRatio" double precision,
    "freeCashFlowOperatingCashFlowRatio" double precision,
    "cashFlowCoverageRatios" double precision,
    "shortTermCoverageRatios" double precision,
    "capitalExpenditureCoverageRatio" double precision,
    "dividendPaidAndCapexCoverageRatio" double precision,
    "dividendPayoutRatio" double precision,
    "priceBookValueRatio" double precision,
    "priceToBookRatio" double precision,
    "priceToSalesRatio" double precision,
    "priceEarningsRatio" double precision,
    "priceToFreeCashFlowsRatio" double precision,
    "priceToOperatingCashFlowsRatio" double precision,
    "priceCashFlowRatio" double precision,
    "priceEarningsToGrowthRatio" double precision,
    "priceSalesRatio" double precision,
    "dividendYield" double precision,
    "enterpriseValueMultiple" double precision,
    "priceFairValue" double precision,
    ticker text,
    date_start date,
    date_end date
);


--
-- Name: realized_vol_d; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.realized_vol_d (
    symbol text,
    date timestamp without time zone,
    vol_1m_ann double precision,
    vol_6m_ann double precision,
    vol_12m_ann double precision
);


--
-- Name: sector_etf_prices_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sector_etf_prices_daily (
    date date,
    proxy_ticker text,
    adj_close double precision,
    volume bigint
);


--
-- Name: sector_factor_applicability_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sector_factor_applicability_registry (
    sector text,
    financial_subtype text,
    factor_id text,
    applicable boolean,
    substitute_factor_id text,
    preferred_peer_group text,
    direction text,
    scoring_method text,
    null_policy text,
    min_peer_count bigint,
    version text
);


--
-- Name: sector_technical_proxy_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sector_technical_proxy_map (
    sector text,
    proxy_ticker text,
    classification_basis text,
    proxy_note text
);


--
-- Name: sector_technicals_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sector_technicals_daily (
    date date,
    sector text,
    proxy_ticker text,
    proxy_source_date date,
    sector_return_21d double precision,
    sector_return_63d double precision,
    sector_return_126d double precision,
    sector_return_252d double precision,
    sector_momentum_12_1 double precision,
    sector_realized_vol_21d double precision,
    sector_realized_vol_63d double precision,
    sector_price_to_sma50 double precision,
    sector_price_to_sma200 double precision,
    sector_drawdown_252d double precision,
    sector_excess_market_return_21d double precision,
    sector_excess_market_return_63d double precision,
    sector_excess_market_return_126d double precision,
    sector_strength_rank_63d double precision
);


--
-- Name: sp500_beta_12m_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_beta_12m_daily (
    date date NOT NULL,
    ticker_latest character varying(16) NOT NULL,
    beta_12m double precision
);


--
-- Name: sp500_capped_portfolio_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_capped_portfolio_audit (
    portfolio_prediction_id text,
    source_prediction_id text,
    portfolio_policy text,
    signal_date timestamp without time zone,
    model text,
    scenario text,
    phase text,
    ticker text,
    feature_row_id text,
    policy_rank bigint,
    weight double precision,
    equal_weight double precision,
    portfolio_contribution double precision,
    allocation_explanation text,
    allocation_explanation_method text,
    score_explanation_provenance text
);


--
-- Name: sp500_model_feature_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_model_feature_audit (
    signal_date timestamp without time zone,
    ticker text,
    technical_date timestamp without time zone,
    return_5d double precision,
    return_21d double precision,
    return_63d double precision,
    return_126d double precision,
    return_252d double precision,
    momentum_12_1 double precision,
    momentum_acceleration double precision,
    reversal_5d double precision,
    reversal_21d double precision,
    realized_vol_21d double precision,
    realized_vol_63d double precision,
    downside_vol_63d double precision,
    vol_ratio_21_63 double precision,
    return_skew_63d double precision,
    return_kurtosis_63d double precision,
    max_drawdown_63d double precision,
    max_drawdown_252d double precision,
    ulcer_index_63d double precision,
    price_to_sma20 double precision,
    price_to_sma50 double precision,
    price_to_sma200 double precision,
    sma50_to_sma200 double precision,
    trend_r2_63d double precision,
    price_position_252d double precision,
    relative_volume_20d double precision,
    volume_trend_21_63 double precision,
    signed_volume_pressure_21d double precision,
    return_volume_corr_63d double precision,
    log_dollar_volume_21d double precision,
    amihud_illiquidity_21d double precision,
    macro_available_date timestamp without time zone,
    dollar_source_date timestamp without time zone,
    dollar_adj_close double precision,
    dollar_return_21d double precision,
    dollar_return_63d double precision,
    dollar_return_126d double precision,
    dollar_return_252d double precision,
    dollar_realized_vol_21d double precision,
    dollar_realized_vol_63d double precision,
    dollar_price_to_sma200 double precision,
    dollar_drawdown_252d double precision,
    gold_source_date timestamp without time zone,
    gold_adj_close double precision,
    gold_return_21d double precision,
    gold_return_63d double precision,
    gold_return_126d double precision,
    gold_return_252d double precision,
    gold_realized_vol_21d double precision,
    gold_realized_vol_63d double precision,
    gold_price_to_sma200 double precision,
    gold_drawdown_252d double precision,
    high_yield_source_date timestamp without time zone,
    high_yield_adj_close double precision,
    high_yield_return_21d double precision,
    high_yield_return_63d double precision,
    high_yield_return_126d double precision,
    high_yield_return_252d double precision,
    high_yield_realized_vol_21d double precision,
    high_yield_realized_vol_63d double precision,
    high_yield_price_to_sma200 double precision,
    high_yield_drawdown_252d double precision,
    investment_grade_source_date timestamp without time zone,
    investment_grade_adj_close double precision,
    investment_grade_return_21d double precision,
    investment_grade_return_63d double precision,
    investment_grade_return_126d double precision,
    investment_grade_return_252d double precision,
    investment_grade_realized_vol_21d double precision,
    investment_grade_realized_vol_63d double precision,
    investment_grade_price_to_sma200 double precision,
    investment_grade_drawdown_252d double precision,
    market_source_date timestamp without time zone,
    market_adj_close double precision,
    market_return_21d double precision,
    market_return_63d double precision,
    market_return_126d double precision,
    market_return_252d double precision,
    market_realized_vol_21d double precision,
    market_realized_vol_63d double precision,
    market_price_to_sma200 double precision,
    market_drawdown_252d double precision,
    oil_source_date timestamp without time zone,
    oil_adj_close double precision,
    oil_return_21d double precision,
    oil_return_63d double precision,
    oil_return_126d double precision,
    oil_return_252d double precision,
    oil_realized_vol_21d double precision,
    oil_realized_vol_63d double precision,
    oil_price_to_sma200 double precision,
    oil_drawdown_252d double precision,
    treasury_10y_source_date timestamp without time zone,
    treasury_10y_yield_pct double precision,
    treasury_10y_change_21d_bp double precision,
    treasury_10y_change_63d_bp double precision,
    treasury_2y_source_date timestamp without time zone,
    treasury_2y_yield_pct double precision,
    treasury_2y_change_21d_bp double precision,
    treasury_2y_change_63d_bp double precision,
    treasury_30y_source_date timestamp without time zone,
    treasury_30y_yield_pct double precision,
    treasury_30y_change_21d_bp double precision,
    treasury_30y_change_63d_bp double precision,
    treasury_3m_source_date timestamp without time zone,
    treasury_3m_yield_pct double precision,
    treasury_3m_change_21d_bp double precision,
    treasury_3m_change_63d_bp double precision,
    treasury_intermediate_source_date timestamp without time zone,
    treasury_intermediate_adj_close double precision,
    treasury_intermediate_return_21d double precision,
    treasury_intermediate_return_63d double precision,
    treasury_intermediate_return_126d double precision,
    treasury_intermediate_return_252d double precision,
    treasury_intermediate_realized_vol_21d double precision,
    treasury_intermediate_realized_vol_63d double precision,
    treasury_intermediate_price_to_sma200 double precision,
    treasury_intermediate_drawdown_252d double precision,
    treasury_long_source_date timestamp without time zone,
    treasury_long_adj_close double precision,
    treasury_long_return_21d double precision,
    treasury_long_return_63d double precision,
    treasury_long_return_126d double precision,
    treasury_long_return_252d double precision,
    treasury_long_realized_vol_21d double precision,
    treasury_long_realized_vol_63d double precision,
    treasury_long_price_to_sma200 double precision,
    treasury_long_drawdown_252d double precision,
    volatility_proxy_source_date timestamp without time zone,
    volatility_proxy_adj_close double precision,
    volatility_proxy_return_21d double precision,
    volatility_proxy_return_63d double precision,
    volatility_proxy_return_126d double precision,
    volatility_proxy_return_252d double precision,
    volatility_proxy_realized_vol_21d double precision,
    volatility_proxy_realized_vol_63d double precision,
    volatility_proxy_price_to_sma200 double precision,
    volatility_proxy_drawdown_252d double precision,
    curve_10y_2y_pp double precision,
    curve_10y_3m_pp double precision,
    credit_hyg_minus_lqd_return_21d double precision,
    gold_minus_oil_return_21d double precision,
    credit_hyg_minus_lqd_return_63d double precision,
    gold_minus_oil_return_63d double precision,
    vix_source_date timestamp without time zone,
    vix_level double precision,
    vix_change_1d_points double precision,
    vix_change_1d_fraction double precision,
    vix_change_5d_points double precision,
    vix_change_5d_fraction double precision,
    vix_change_21d_points double precision,
    vix_change_21d_fraction double precision,
    vix_change_63d_points double precision,
    vix_change_63d_fraction double precision,
    vix_mean_21d double precision,
    vix_vs_mean_21d double precision,
    vix_mean_63d double precision,
    vix_vs_mean_63d double precision,
    vix_percentile_252d double precision,
    sector text,
    sector_technical_date timestamp without time zone,
    proxy_ticker text,
    proxy_source_date timestamp without time zone,
    sector_return_21d double precision,
    sector_return_63d double precision,
    sector_return_126d double precision,
    sector_return_252d double precision,
    sector_momentum_12_1 double precision,
    sector_realized_vol_21d double precision,
    sector_realized_vol_63d double precision,
    sector_price_to_sma50 double precision,
    sector_price_to_sma200 double precision,
    sector_drawdown_252d double precision,
    sector_excess_market_return_21d double precision,
    sector_excess_market_return_63d double precision,
    sector_excess_market_return_126d double precision,
    sector_strength_rank_63d double precision,
    stock_excess_sector_return_21d double precision,
    stock_excess_sector_return_63d double precision,
    stock_to_sector_vol_ratio_63d double precision,
    security_id text,
    ticker_latest text,
    month_end timestamp without time zone,
    financial_subtype text,
    peer_group_used text,
    quality_coverage_pct double precision,
    debt_free boolean,
    nonpositive_equity boolean,
    no_interest_expense boolean,
    growth_unavailable_negative_base boolean,
    growth_unavailable_small_base boolean,
    pit_revision_uncertain boolean,
    sector_classification_retrospective boolean,
    revenue_growth_yoy_raw double precision,
    revenue_growth_yoy_clean double precision,
    revenue_growth_yoy_sector_score double precision,
    revenue_growth_yoy_applicable boolean,
    revenue_cagr_3y_raw double precision,
    revenue_cagr_3y_clean double precision,
    revenue_cagr_3y_sector_score double precision,
    revenue_cagr_3y_applicable boolean,
    eps_growth_yoy_raw double precision,
    eps_growth_yoy_clean double precision,
    eps_growth_yoy_sector_score double precision,
    eps_growth_yoy_applicable boolean,
    net_income_growth_3y_raw double precision,
    net_income_growth_3y_clean double precision,
    net_income_growth_3y_sector_score double precision,
    net_income_growth_3y_applicable boolean,
    ebitda_growth_yoy_raw double precision,
    ebitda_growth_yoy_clean double precision,
    ebitda_growth_yoy_sector_score double precision,
    ebitda_growth_yoy_applicable boolean,
    ocf_growth_yoy_raw double precision,
    ocf_growth_yoy_clean double precision,
    ocf_growth_yoy_sector_score double precision,
    ocf_growth_yoy_applicable boolean,
    fcf_growth_3y_raw double precision,
    fcf_growth_3y_clean double precision,
    fcf_growth_3y_sector_score double precision,
    fcf_growth_3y_applicable boolean,
    gross_margin_raw double precision,
    gross_margin_clean double precision,
    gross_margin_sector_score double precision,
    gross_margin_applicable boolean,
    ebitda_margin_raw double precision,
    ebitda_margin_clean double precision,
    ebitda_margin_sector_score double precision,
    ebitda_margin_applicable boolean,
    operating_margin_raw double precision,
    operating_margin_clean double precision,
    operating_margin_sector_score double precision,
    operating_margin_applicable boolean,
    net_margin_raw double precision,
    net_margin_clean double precision,
    net_margin_sector_score double precision,
    net_margin_applicable boolean,
    roe_raw double precision,
    roe_clean double precision,
    roe_sector_score double precision,
    roe_applicable boolean,
    roic_raw double precision,
    roic_clean double precision,
    roic_sector_score double precision,
    roic_applicable boolean,
    fcf_margin_raw double precision,
    fcf_margin_clean double precision,
    fcf_margin_sector_score double precision,
    fcf_margin_applicable boolean,
    earnings_yield_raw double precision,
    earnings_yield_clean double precision,
    earnings_yield_sector_score double precision,
    earnings_yield_applicable boolean,
    sales_yield_raw double precision,
    sales_yield_clean double precision,
    sales_yield_sector_score double precision,
    sales_yield_applicable boolean,
    ebitda_ev_yield_raw double precision,
    ebitda_ev_yield_clean double precision,
    ebitda_ev_yield_sector_score double precision,
    ebitda_ev_yield_applicable boolean,
    fcf_yield_raw double precision,
    fcf_yield_clean double precision,
    fcf_yield_sector_score double precision,
    fcf_yield_applicable boolean,
    book_to_market_raw double precision,
    book_to_market_clean double precision,
    book_to_market_sector_score double precision,
    book_to_market_applicable boolean,
    ocf_yield_raw double precision,
    ocf_yield_clean double precision,
    ocf_yield_sector_score double precision,
    ocf_yield_applicable boolean,
    net_shareholder_yield_raw double precision,
    net_shareholder_yield_clean double precision,
    net_shareholder_yield_sector_score double precision,
    net_shareholder_yield_applicable boolean,
    debt_to_equity_raw double precision,
    debt_to_equity_clean double precision,
    debt_to_equity_sector_score double precision,
    debt_to_equity_applicable boolean,
    debt_to_assets_raw double precision,
    debt_to_assets_clean double precision,
    debt_to_assets_sector_score double precision,
    debt_to_assets_applicable boolean,
    net_debt_to_ebitda_raw double precision,
    net_debt_to_ebitda_clean double precision,
    net_debt_to_ebitda_sector_score double precision,
    net_debt_to_ebitda_applicable boolean,
    interest_coverage_raw double precision,
    interest_coverage_clean double precision,
    interest_coverage_sector_score double precision,
    interest_coverage_applicable boolean,
    cash_to_assets_raw double precision,
    cash_to_assets_clean double precision,
    cash_to_assets_sector_score double precision,
    cash_to_assets_applicable boolean,
    current_ratio_raw double precision,
    current_ratio_clean double precision,
    current_ratio_sector_score double precision,
    current_ratio_applicable boolean,
    ocf_to_debt_raw double precision,
    ocf_to_debt_clean double precision,
    ocf_to_debt_sector_score double precision,
    ocf_to_debt_applicable boolean,
    roa_raw double precision,
    roa_clean double precision,
    roa_sector_score double precision,
    roa_applicable boolean,
    equity_to_assets_raw double precision,
    equity_to_assets_clean double precision,
    equity_to_assets_sector_score double precision,
    equity_to_assets_applicable boolean,
    growth_composite double precision,
    growth_factor_count bigint,
    profitability_composite double precision,
    profitability_factor_count bigint,
    valuation_composite double precision,
    valuation_factor_count bigint,
    balance_sheet_composite double precision,
    balance_sheet_factor_count bigint,
    feature_row_id text
);


--
-- Name: sp500_model_prediction_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_model_prediction_audit (
    signal_date timestamp without time zone,
    ticker text,
    sector text,
    next_month_return double precision,
    benchmark_return double precision,
    target_top20 double precision,
    probability double precision,
    selected boolean,
    model text,
    training_target text,
    run_id text,
    scenario text,
    phase text,
    training_signal_end timestamp without time zone,
    training_outcome_end timestamp without time zone,
    attribution_baseline_log_odds double precision,
    attribution_method text,
    feature_row_id text,
    prediction_id text,
    prediction_rank bigint,
    candidate_count bigint,
    selection_cutoff_probability double precision,
    probability_above_selection_cutoff double precision,
    explanation_evidence_json text,
    evidence_summary text,
    weight double precision,
    rank double precision,
    actual_outperform_voo double precision,
    actual_target double precision,
    predicted_class_0_5 boolean,
    classification_correct_0_5 double precision,
    selection_outcome text,
    brier_error double precision,
    portfolio_contribution double precision,
    return_month timestamp without time zone,
    llm_explanation text,
    llm_explanation_status text,
    llm_explanation_id text,
    llm_model text,
    llm_prompt_version text,
    llm_generated_at timestamp with time zone,
    model_feature_count bigint,
    model_input_features_json text,
    dominant_positive_driver text,
    dominant_positive_block text,
    dominant_negative_driver text,
    dominant_negative_block text
);


--
-- Name: sp500_capped_model_audit_dataset; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.sp500_capped_model_audit_dataset AS
 SELECT a.signal_date,
    a.ticker,
    a.sector,
    a.next_month_return,
    a.benchmark_return,
    a.target_top20,
    a.probability,
    a.selected,
    a.model,
    a.training_target,
    a.run_id,
    a.scenario,
    a.phase,
    a.training_signal_end,
    a.training_outcome_end,
    a.attribution_baseline_log_odds,
    a.attribution_method,
    a.feature_row_id,
    a.prediction_id,
    a.prediction_rank,
    a.candidate_count,
    a.selection_cutoff_probability,
    a.probability_above_selection_cutoff,
    a.explanation_evidence_json,
    a.evidence_summary,
    a.rank,
    a.actual_outperform_voo,
    a.actual_target,
    a.predicted_class_0_5,
    a.classification_correct_0_5,
    a.selection_outcome,
    a.brier_error,
    a.return_month,
    a.llm_explanation,
    a.llm_explanation_status,
    a.llm_explanation_id,
    a.llm_model,
    a.llm_prompt_version,
    a.llm_generated_at,
    a.model_feature_count,
    a.model_input_features_json,
    a.dominant_positive_driver,
    a.dominant_positive_block,
    a.dominant_negative_driver,
    a.dominant_negative_block,
    p.portfolio_prediction_id,
    p.source_prediction_id,
    p.portfolio_policy,
    p.policy_rank,
    p.weight,
    p.equal_weight,
    p.portfolio_contribution,
    p.allocation_explanation,
    p.allocation_explanation_method,
    p.score_explanation_provenance,
    f.technical_date,
    f.return_5d,
    f.return_21d,
    f.return_63d,
    f.return_126d,
    f.return_252d,
    f.momentum_12_1,
    f.momentum_acceleration,
    f.reversal_5d,
    f.reversal_21d,
    f.realized_vol_21d,
    f.realized_vol_63d,
    f.downside_vol_63d,
    f.vol_ratio_21_63,
    f.return_skew_63d,
    f.return_kurtosis_63d,
    f.max_drawdown_63d,
    f.max_drawdown_252d,
    f.ulcer_index_63d,
    f.price_to_sma20,
    f.price_to_sma50,
    f.price_to_sma200,
    f.sma50_to_sma200,
    f.trend_r2_63d,
    f.price_position_252d,
    f.relative_volume_20d,
    f.volume_trend_21_63,
    f.signed_volume_pressure_21d,
    f.return_volume_corr_63d,
    f.log_dollar_volume_21d,
    f.amihud_illiquidity_21d,
    f.macro_available_date,
    f.dollar_source_date,
    f.dollar_adj_close,
    f.dollar_return_21d,
    f.dollar_return_63d,
    f.dollar_return_126d,
    f.dollar_return_252d,
    f.dollar_realized_vol_21d,
    f.dollar_realized_vol_63d,
    f.dollar_price_to_sma200,
    f.dollar_drawdown_252d,
    f.gold_source_date,
    f.gold_adj_close,
    f.gold_return_21d,
    f.gold_return_63d,
    f.gold_return_126d,
    f.gold_return_252d,
    f.gold_realized_vol_21d,
    f.gold_realized_vol_63d,
    f.gold_price_to_sma200,
    f.gold_drawdown_252d,
    f.high_yield_source_date,
    f.high_yield_adj_close,
    f.high_yield_return_21d,
    f.high_yield_return_63d,
    f.high_yield_return_126d,
    f.high_yield_return_252d,
    f.high_yield_realized_vol_21d,
    f.high_yield_realized_vol_63d,
    f.high_yield_price_to_sma200,
    f.high_yield_drawdown_252d,
    f.investment_grade_source_date,
    f.investment_grade_adj_close,
    f.investment_grade_return_21d,
    f.investment_grade_return_63d,
    f.investment_grade_return_126d,
    f.investment_grade_return_252d,
    f.investment_grade_realized_vol_21d,
    f.investment_grade_realized_vol_63d,
    f.investment_grade_price_to_sma200,
    f.investment_grade_drawdown_252d,
    f.market_source_date,
    f.market_adj_close,
    f.market_return_21d,
    f.market_return_63d,
    f.market_return_126d,
    f.market_return_252d,
    f.market_realized_vol_21d,
    f.market_realized_vol_63d,
    f.market_price_to_sma200,
    f.market_drawdown_252d,
    f.oil_source_date,
    f.oil_adj_close,
    f.oil_return_21d,
    f.oil_return_63d,
    f.oil_return_126d,
    f.oil_return_252d,
    f.oil_realized_vol_21d,
    f.oil_realized_vol_63d,
    f.oil_price_to_sma200,
    f.oil_drawdown_252d,
    f.treasury_10y_source_date,
    f.treasury_10y_yield_pct,
    f.treasury_10y_change_21d_bp,
    f.treasury_10y_change_63d_bp,
    f.treasury_2y_source_date,
    f.treasury_2y_yield_pct,
    f.treasury_2y_change_21d_bp,
    f.treasury_2y_change_63d_bp,
    f.treasury_30y_source_date,
    f.treasury_30y_yield_pct,
    f.treasury_30y_change_21d_bp,
    f.treasury_30y_change_63d_bp,
    f.treasury_3m_source_date,
    f.treasury_3m_yield_pct,
    f.treasury_3m_change_21d_bp,
    f.treasury_3m_change_63d_bp,
    f.treasury_intermediate_source_date,
    f.treasury_intermediate_adj_close,
    f.treasury_intermediate_return_21d,
    f.treasury_intermediate_return_63d,
    f.treasury_intermediate_return_126d,
    f.treasury_intermediate_return_252d,
    f.treasury_intermediate_realized_vol_21d,
    f.treasury_intermediate_realized_vol_63d,
    f.treasury_intermediate_price_to_sma200,
    f.treasury_intermediate_drawdown_252d,
    f.treasury_long_source_date,
    f.treasury_long_adj_close,
    f.treasury_long_return_21d,
    f.treasury_long_return_63d,
    f.treasury_long_return_126d,
    f.treasury_long_return_252d,
    f.treasury_long_realized_vol_21d,
    f.treasury_long_realized_vol_63d,
    f.treasury_long_price_to_sma200,
    f.treasury_long_drawdown_252d,
    f.volatility_proxy_source_date,
    f.volatility_proxy_adj_close,
    f.volatility_proxy_return_21d,
    f.volatility_proxy_return_63d,
    f.volatility_proxy_return_126d,
    f.volatility_proxy_return_252d,
    f.volatility_proxy_realized_vol_21d,
    f.volatility_proxy_realized_vol_63d,
    f.volatility_proxy_price_to_sma200,
    f.volatility_proxy_drawdown_252d,
    f.curve_10y_2y_pp,
    f.curve_10y_3m_pp,
    f.credit_hyg_minus_lqd_return_21d,
    f.gold_minus_oil_return_21d,
    f.credit_hyg_minus_lqd_return_63d,
    f.gold_minus_oil_return_63d,
    f.vix_source_date,
    f.vix_level,
    f.vix_change_1d_points,
    f.vix_change_1d_fraction,
    f.vix_change_5d_points,
    f.vix_change_5d_fraction,
    f.vix_change_21d_points,
    f.vix_change_21d_fraction,
    f.vix_change_63d_points,
    f.vix_change_63d_fraction,
    f.vix_mean_21d,
    f.vix_vs_mean_21d,
    f.vix_mean_63d,
    f.vix_vs_mean_63d,
    f.vix_percentile_252d,
    f.sector_technical_date,
    f.proxy_ticker,
    f.proxy_source_date,
    f.sector_return_21d,
    f.sector_return_63d,
    f.sector_return_126d,
    f.sector_return_252d,
    f.sector_momentum_12_1,
    f.sector_realized_vol_21d,
    f.sector_realized_vol_63d,
    f.sector_price_to_sma50,
    f.sector_price_to_sma200,
    f.sector_drawdown_252d,
    f.sector_excess_market_return_21d,
    f.sector_excess_market_return_63d,
    f.sector_excess_market_return_126d,
    f.sector_strength_rank_63d,
    f.stock_excess_sector_return_21d,
    f.stock_excess_sector_return_63d,
    f.stock_to_sector_vol_ratio_63d,
    f.security_id,
    f.ticker_latest,
    f.month_end,
    f.financial_subtype,
    f.peer_group_used,
    f.quality_coverage_pct,
    f.debt_free,
    f.nonpositive_equity,
    f.no_interest_expense,
    f.growth_unavailable_negative_base,
    f.growth_unavailable_small_base,
    f.pit_revision_uncertain,
    f.sector_classification_retrospective,
    f.revenue_growth_yoy_raw,
    f.revenue_growth_yoy_clean,
    f.revenue_growth_yoy_sector_score,
    f.revenue_growth_yoy_applicable,
    f.revenue_cagr_3y_raw,
    f.revenue_cagr_3y_clean,
    f.revenue_cagr_3y_sector_score,
    f.revenue_cagr_3y_applicable,
    f.eps_growth_yoy_raw,
    f.eps_growth_yoy_clean,
    f.eps_growth_yoy_sector_score,
    f.eps_growth_yoy_applicable,
    f.net_income_growth_3y_raw,
    f.net_income_growth_3y_clean,
    f.net_income_growth_3y_sector_score,
    f.net_income_growth_3y_applicable,
    f.ebitda_growth_yoy_raw,
    f.ebitda_growth_yoy_clean,
    f.ebitda_growth_yoy_sector_score,
    f.ebitda_growth_yoy_applicable,
    f.ocf_growth_yoy_raw,
    f.ocf_growth_yoy_clean,
    f.ocf_growth_yoy_sector_score,
    f.ocf_growth_yoy_applicable,
    f.fcf_growth_3y_raw,
    f.fcf_growth_3y_clean,
    f.fcf_growth_3y_sector_score,
    f.fcf_growth_3y_applicable,
    f.gross_margin_raw,
    f.gross_margin_clean,
    f.gross_margin_sector_score,
    f.gross_margin_applicable,
    f.ebitda_margin_raw,
    f.ebitda_margin_clean,
    f.ebitda_margin_sector_score,
    f.ebitda_margin_applicable,
    f.operating_margin_raw,
    f.operating_margin_clean,
    f.operating_margin_sector_score,
    f.operating_margin_applicable,
    f.net_margin_raw,
    f.net_margin_clean,
    f.net_margin_sector_score,
    f.net_margin_applicable,
    f.roe_raw,
    f.roe_clean,
    f.roe_sector_score,
    f.roe_applicable,
    f.roic_raw,
    f.roic_clean,
    f.roic_sector_score,
    f.roic_applicable,
    f.fcf_margin_raw,
    f.fcf_margin_clean,
    f.fcf_margin_sector_score,
    f.fcf_margin_applicable,
    f.earnings_yield_raw,
    f.earnings_yield_clean,
    f.earnings_yield_sector_score,
    f.earnings_yield_applicable,
    f.sales_yield_raw,
    f.sales_yield_clean,
    f.sales_yield_sector_score,
    f.sales_yield_applicable,
    f.ebitda_ev_yield_raw,
    f.ebitda_ev_yield_clean,
    f.ebitda_ev_yield_sector_score,
    f.ebitda_ev_yield_applicable,
    f.fcf_yield_raw,
    f.fcf_yield_clean,
    f.fcf_yield_sector_score,
    f.fcf_yield_applicable,
    f.book_to_market_raw,
    f.book_to_market_clean,
    f.book_to_market_sector_score,
    f.book_to_market_applicable,
    f.ocf_yield_raw,
    f.ocf_yield_clean,
    f.ocf_yield_sector_score,
    f.ocf_yield_applicable,
    f.net_shareholder_yield_raw,
    f.net_shareholder_yield_clean,
    f.net_shareholder_yield_sector_score,
    f.net_shareholder_yield_applicable,
    f.debt_to_equity_raw,
    f.debt_to_equity_clean,
    f.debt_to_equity_sector_score,
    f.debt_to_equity_applicable,
    f.debt_to_assets_raw,
    f.debt_to_assets_clean,
    f.debt_to_assets_sector_score,
    f.debt_to_assets_applicable,
    f.net_debt_to_ebitda_raw,
    f.net_debt_to_ebitda_clean,
    f.net_debt_to_ebitda_sector_score,
    f.net_debt_to_ebitda_applicable,
    f.interest_coverage_raw,
    f.interest_coverage_clean,
    f.interest_coverage_sector_score,
    f.interest_coverage_applicable,
    f.cash_to_assets_raw,
    f.cash_to_assets_clean,
    f.cash_to_assets_sector_score,
    f.cash_to_assets_applicable,
    f.current_ratio_raw,
    f.current_ratio_clean,
    f.current_ratio_sector_score,
    f.current_ratio_applicable,
    f.ocf_to_debt_raw,
    f.ocf_to_debt_clean,
    f.ocf_to_debt_sector_score,
    f.ocf_to_debt_applicable,
    f.roa_raw,
    f.roa_clean,
    f.roa_sector_score,
    f.roa_applicable,
    f.equity_to_assets_raw,
    f.equity_to_assets_clean,
    f.equity_to_assets_sector_score,
    f.equity_to_assets_applicable,
    f.growth_composite,
    f.growth_factor_count,
    f.profitability_composite,
    f.profitability_factor_count,
    f.valuation_composite,
    f.valuation_factor_count,
    f.balance_sheet_composite,
    f.balance_sheet_factor_count
   FROM ((public.sp500_capped_portfolio_audit p
     JOIN public.sp500_model_prediction_audit a ON ((a.prediction_id = p.source_prediction_id)))
     JOIN public.sp500_model_feature_audit f ON ((f.feature_row_id = a.feature_row_id)));


--
-- Name: sp500_daily_technicals_ml; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_daily_technicals_ml (
    date date NOT NULL,
    ticker_latest text NOT NULL,
    return_5d double precision,
    return_21d double precision,
    return_63d double precision,
    return_126d double precision,
    return_252d double precision,
    momentum_12_1 double precision,
    momentum_acceleration double precision,
    reversal_5d double precision,
    reversal_21d double precision,
    realized_vol_21d double precision,
    realized_vol_63d double precision,
    downside_vol_63d double precision,
    vol_ratio_21_63 double precision,
    return_skew_63d double precision,
    return_kurtosis_63d double precision,
    max_drawdown_63d double precision,
    max_drawdown_252d double precision,
    ulcer_index_63d double precision,
    price_to_sma20 double precision,
    price_to_sma50 double precision,
    price_to_sma200 double precision,
    sma50_to_sma200 double precision,
    trend_r2_63d double precision,
    price_position_252d double precision,
    relative_volume_20d double precision,
    volume_trend_21_63 double precision,
    signed_volume_pressure_21d double precision,
    return_volume_corr_63d double precision,
    log_dollar_volume_21d double precision,
    amihud_illiquidity_21d double precision
);


--
-- Name: sp500_long_latest_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_long_latest_profiles (
    date date NOT NULL,
    ticker character varying(16) NOT NULL,
    latest_ticker character varying(16),
    company_name character varying(256),
    sector character varying(64),
    currency character varying(8),
    is_actively_trading boolean,
    cik character varying(16)
);


--
-- Name: sp500_market_momentum_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_market_momentum_daily (
    date date NOT NULL,
    mkt_1m double precision,
    mkt_6m double precision,
    mkt_12m double precision
);


--
-- Name: sp500_model_attribution_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_model_attribution_audit (
    prediction_id text,
    feature text,
    feature_block text,
    model_input double precision,
    contribution_log_odds double precision,
    coefficient double precision
);


--
-- Name: sp500_model_audit_dataset; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.sp500_model_audit_dataset AS
 SELECT p.signal_date,
    p.ticker,
    p.sector,
    p.next_month_return,
    p.benchmark_return,
    p.target_top20,
    p.probability,
    p.selected,
    p.model,
    p.training_target,
    p.run_id,
    p.scenario,
    p.phase,
    p.training_signal_end,
    p.training_outcome_end,
    p.attribution_baseline_log_odds,
    p.attribution_method,
    p.feature_row_id,
    p.prediction_id,
    p.prediction_rank,
    p.candidate_count,
    p.selection_cutoff_probability,
    p.probability_above_selection_cutoff,
    p.explanation_evidence_json,
    p.evidence_summary,
    p.weight,
    p.rank,
    p.actual_outperform_voo,
    p.actual_target,
    p.predicted_class_0_5,
    p.classification_correct_0_5,
    p.selection_outcome,
    p.brier_error,
    p.portfolio_contribution,
    p.return_month,
    p.llm_explanation,
    p.llm_explanation_status,
    p.llm_explanation_id,
    p.llm_model,
    p.llm_prompt_version,
    p.llm_generated_at,
    p.model_feature_count,
    p.model_input_features_json,
    p.dominant_positive_driver,
    p.dominant_positive_block,
    p.dominant_negative_driver,
    p.dominant_negative_block,
    f.technical_date,
    f.return_5d,
    f.return_21d,
    f.return_63d,
    f.return_126d,
    f.return_252d,
    f.momentum_12_1,
    f.momentum_acceleration,
    f.reversal_5d,
    f.reversal_21d,
    f.realized_vol_21d,
    f.realized_vol_63d,
    f.downside_vol_63d,
    f.vol_ratio_21_63,
    f.return_skew_63d,
    f.return_kurtosis_63d,
    f.max_drawdown_63d,
    f.max_drawdown_252d,
    f.ulcer_index_63d,
    f.price_to_sma20,
    f.price_to_sma50,
    f.price_to_sma200,
    f.sma50_to_sma200,
    f.trend_r2_63d,
    f.price_position_252d,
    f.relative_volume_20d,
    f.volume_trend_21_63,
    f.signed_volume_pressure_21d,
    f.return_volume_corr_63d,
    f.log_dollar_volume_21d,
    f.amihud_illiquidity_21d,
    f.macro_available_date,
    f.dollar_source_date,
    f.dollar_adj_close,
    f.dollar_return_21d,
    f.dollar_return_63d,
    f.dollar_return_126d,
    f.dollar_return_252d,
    f.dollar_realized_vol_21d,
    f.dollar_realized_vol_63d,
    f.dollar_price_to_sma200,
    f.dollar_drawdown_252d,
    f.gold_source_date,
    f.gold_adj_close,
    f.gold_return_21d,
    f.gold_return_63d,
    f.gold_return_126d,
    f.gold_return_252d,
    f.gold_realized_vol_21d,
    f.gold_realized_vol_63d,
    f.gold_price_to_sma200,
    f.gold_drawdown_252d,
    f.high_yield_source_date,
    f.high_yield_adj_close,
    f.high_yield_return_21d,
    f.high_yield_return_63d,
    f.high_yield_return_126d,
    f.high_yield_return_252d,
    f.high_yield_realized_vol_21d,
    f.high_yield_realized_vol_63d,
    f.high_yield_price_to_sma200,
    f.high_yield_drawdown_252d,
    f.investment_grade_source_date,
    f.investment_grade_adj_close,
    f.investment_grade_return_21d,
    f.investment_grade_return_63d,
    f.investment_grade_return_126d,
    f.investment_grade_return_252d,
    f.investment_grade_realized_vol_21d,
    f.investment_grade_realized_vol_63d,
    f.investment_grade_price_to_sma200,
    f.investment_grade_drawdown_252d,
    f.market_source_date,
    f.market_adj_close,
    f.market_return_21d,
    f.market_return_63d,
    f.market_return_126d,
    f.market_return_252d,
    f.market_realized_vol_21d,
    f.market_realized_vol_63d,
    f.market_price_to_sma200,
    f.market_drawdown_252d,
    f.oil_source_date,
    f.oil_adj_close,
    f.oil_return_21d,
    f.oil_return_63d,
    f.oil_return_126d,
    f.oil_return_252d,
    f.oil_realized_vol_21d,
    f.oil_realized_vol_63d,
    f.oil_price_to_sma200,
    f.oil_drawdown_252d,
    f.treasury_10y_source_date,
    f.treasury_10y_yield_pct,
    f.treasury_10y_change_21d_bp,
    f.treasury_10y_change_63d_bp,
    f.treasury_2y_source_date,
    f.treasury_2y_yield_pct,
    f.treasury_2y_change_21d_bp,
    f.treasury_2y_change_63d_bp,
    f.treasury_30y_source_date,
    f.treasury_30y_yield_pct,
    f.treasury_30y_change_21d_bp,
    f.treasury_30y_change_63d_bp,
    f.treasury_3m_source_date,
    f.treasury_3m_yield_pct,
    f.treasury_3m_change_21d_bp,
    f.treasury_3m_change_63d_bp,
    f.treasury_intermediate_source_date,
    f.treasury_intermediate_adj_close,
    f.treasury_intermediate_return_21d,
    f.treasury_intermediate_return_63d,
    f.treasury_intermediate_return_126d,
    f.treasury_intermediate_return_252d,
    f.treasury_intermediate_realized_vol_21d,
    f.treasury_intermediate_realized_vol_63d,
    f.treasury_intermediate_price_to_sma200,
    f.treasury_intermediate_drawdown_252d,
    f.treasury_long_source_date,
    f.treasury_long_adj_close,
    f.treasury_long_return_21d,
    f.treasury_long_return_63d,
    f.treasury_long_return_126d,
    f.treasury_long_return_252d,
    f.treasury_long_realized_vol_21d,
    f.treasury_long_realized_vol_63d,
    f.treasury_long_price_to_sma200,
    f.treasury_long_drawdown_252d,
    f.volatility_proxy_source_date,
    f.volatility_proxy_adj_close,
    f.volatility_proxy_return_21d,
    f.volatility_proxy_return_63d,
    f.volatility_proxy_return_126d,
    f.volatility_proxy_return_252d,
    f.volatility_proxy_realized_vol_21d,
    f.volatility_proxy_realized_vol_63d,
    f.volatility_proxy_price_to_sma200,
    f.volatility_proxy_drawdown_252d,
    f.curve_10y_2y_pp,
    f.curve_10y_3m_pp,
    f.credit_hyg_minus_lqd_return_21d,
    f.gold_minus_oil_return_21d,
    f.credit_hyg_minus_lqd_return_63d,
    f.gold_minus_oil_return_63d,
    f.vix_source_date,
    f.vix_level,
    f.vix_change_1d_points,
    f.vix_change_1d_fraction,
    f.vix_change_5d_points,
    f.vix_change_5d_fraction,
    f.vix_change_21d_points,
    f.vix_change_21d_fraction,
    f.vix_change_63d_points,
    f.vix_change_63d_fraction,
    f.vix_mean_21d,
    f.vix_vs_mean_21d,
    f.vix_mean_63d,
    f.vix_vs_mean_63d,
    f.vix_percentile_252d,
    f.sector_technical_date,
    f.proxy_ticker,
    f.proxy_source_date,
    f.sector_return_21d,
    f.sector_return_63d,
    f.sector_return_126d,
    f.sector_return_252d,
    f.sector_momentum_12_1,
    f.sector_realized_vol_21d,
    f.sector_realized_vol_63d,
    f.sector_price_to_sma50,
    f.sector_price_to_sma200,
    f.sector_drawdown_252d,
    f.sector_excess_market_return_21d,
    f.sector_excess_market_return_63d,
    f.sector_excess_market_return_126d,
    f.sector_strength_rank_63d,
    f.stock_excess_sector_return_21d,
    f.stock_excess_sector_return_63d,
    f.stock_to_sector_vol_ratio_63d,
    f.security_id,
    f.ticker_latest,
    f.month_end,
    f.financial_subtype,
    f.peer_group_used,
    f.quality_coverage_pct,
    f.debt_free,
    f.nonpositive_equity,
    f.no_interest_expense,
    f.growth_unavailable_negative_base,
    f.growth_unavailable_small_base,
    f.pit_revision_uncertain,
    f.sector_classification_retrospective,
    f.revenue_growth_yoy_raw,
    f.revenue_growth_yoy_clean,
    f.revenue_growth_yoy_sector_score,
    f.revenue_growth_yoy_applicable,
    f.revenue_cagr_3y_raw,
    f.revenue_cagr_3y_clean,
    f.revenue_cagr_3y_sector_score,
    f.revenue_cagr_3y_applicable,
    f.eps_growth_yoy_raw,
    f.eps_growth_yoy_clean,
    f.eps_growth_yoy_sector_score,
    f.eps_growth_yoy_applicable,
    f.net_income_growth_3y_raw,
    f.net_income_growth_3y_clean,
    f.net_income_growth_3y_sector_score,
    f.net_income_growth_3y_applicable,
    f.ebitda_growth_yoy_raw,
    f.ebitda_growth_yoy_clean,
    f.ebitda_growth_yoy_sector_score,
    f.ebitda_growth_yoy_applicable,
    f.ocf_growth_yoy_raw,
    f.ocf_growth_yoy_clean,
    f.ocf_growth_yoy_sector_score,
    f.ocf_growth_yoy_applicable,
    f.fcf_growth_3y_raw,
    f.fcf_growth_3y_clean,
    f.fcf_growth_3y_sector_score,
    f.fcf_growth_3y_applicable,
    f.gross_margin_raw,
    f.gross_margin_clean,
    f.gross_margin_sector_score,
    f.gross_margin_applicable,
    f.ebitda_margin_raw,
    f.ebitda_margin_clean,
    f.ebitda_margin_sector_score,
    f.ebitda_margin_applicable,
    f.operating_margin_raw,
    f.operating_margin_clean,
    f.operating_margin_sector_score,
    f.operating_margin_applicable,
    f.net_margin_raw,
    f.net_margin_clean,
    f.net_margin_sector_score,
    f.net_margin_applicable,
    f.roe_raw,
    f.roe_clean,
    f.roe_sector_score,
    f.roe_applicable,
    f.roic_raw,
    f.roic_clean,
    f.roic_sector_score,
    f.roic_applicable,
    f.fcf_margin_raw,
    f.fcf_margin_clean,
    f.fcf_margin_sector_score,
    f.fcf_margin_applicable,
    f.earnings_yield_raw,
    f.earnings_yield_clean,
    f.earnings_yield_sector_score,
    f.earnings_yield_applicable,
    f.sales_yield_raw,
    f.sales_yield_clean,
    f.sales_yield_sector_score,
    f.sales_yield_applicable,
    f.ebitda_ev_yield_raw,
    f.ebitda_ev_yield_clean,
    f.ebitda_ev_yield_sector_score,
    f.ebitda_ev_yield_applicable,
    f.fcf_yield_raw,
    f.fcf_yield_clean,
    f.fcf_yield_sector_score,
    f.fcf_yield_applicable,
    f.book_to_market_raw,
    f.book_to_market_clean,
    f.book_to_market_sector_score,
    f.book_to_market_applicable,
    f.ocf_yield_raw,
    f.ocf_yield_clean,
    f.ocf_yield_sector_score,
    f.ocf_yield_applicable,
    f.net_shareholder_yield_raw,
    f.net_shareholder_yield_clean,
    f.net_shareholder_yield_sector_score,
    f.net_shareholder_yield_applicable,
    f.debt_to_equity_raw,
    f.debt_to_equity_clean,
    f.debt_to_equity_sector_score,
    f.debt_to_equity_applicable,
    f.debt_to_assets_raw,
    f.debt_to_assets_clean,
    f.debt_to_assets_sector_score,
    f.debt_to_assets_applicable,
    f.net_debt_to_ebitda_raw,
    f.net_debt_to_ebitda_clean,
    f.net_debt_to_ebitda_sector_score,
    f.net_debt_to_ebitda_applicable,
    f.interest_coverage_raw,
    f.interest_coverage_clean,
    f.interest_coverage_sector_score,
    f.interest_coverage_applicable,
    f.cash_to_assets_raw,
    f.cash_to_assets_clean,
    f.cash_to_assets_sector_score,
    f.cash_to_assets_applicable,
    f.current_ratio_raw,
    f.current_ratio_clean,
    f.current_ratio_sector_score,
    f.current_ratio_applicable,
    f.ocf_to_debt_raw,
    f.ocf_to_debt_clean,
    f.ocf_to_debt_sector_score,
    f.ocf_to_debt_applicable,
    f.roa_raw,
    f.roa_clean,
    f.roa_sector_score,
    f.roa_applicable,
    f.equity_to_assets_raw,
    f.equity_to_assets_clean,
    f.equity_to_assets_sector_score,
    f.equity_to_assets_applicable,
    f.growth_composite,
    f.growth_factor_count,
    f.profitability_composite,
    f.profitability_factor_count,
    f.valuation_composite,
    f.valuation_factor_count,
    f.balance_sheet_composite,
    f.balance_sheet_factor_count
   FROM (public.sp500_model_prediction_audit p
     JOIN public.sp500_model_feature_audit f USING (feature_row_id));


--
-- Name: sp500_monthly_fundamental_features; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_monthly_fundamental_features (
    security_id text,
    ticker_latest text,
    cik text,
    month_end timestamp without time zone,
    feature_cutoff_at timestamp with time zone,
    sector_clean text,
    industry text,
    financial_subtype text,
    is_sp500_member boolean,
    peer_group_used text,
    score_fallback_used boolean,
    sector_classification_retrospective boolean,
    industry_classification_retrospective boolean,
    pit_revision_uncertain boolean,
    sector_score_version text,
    reported_currency text,
    market_currency text,
    market_currency_inferred_from_profile boolean,
    enterprise_value_method text,
    market_route_verified boolean,
    enterprise_value_vendor_unverified double precision,
    enterprise_value_vendor_usable boolean,
    eps_approximation boolean,
    common_income_attribution_proxy boolean,
    excess_cash_proxy boolean,
    tax_rate_proxy double precision,
    tax_proxy_fit_end timestamp without time zone,
    identity_cik_verified boolean,
    debt_free boolean,
    nonpositive_equity boolean,
    no_interest_expense boolean,
    income_accounting_reconciliation_failed boolean,
    bs_accounting_reconciliation_failed boolean,
    cf_accounting_or_semantics_failed boolean,
    net_debt_definition_discrepancy boolean,
    income_stale boolean,
    income_ttm_complete boolean,
    cf_stale boolean,
    cf_ttm_complete boolean,
    bs_stale boolean,
    market_cap_stale boolean,
    ev_stale boolean,
    bs_opening_source_row_id text,
    bs_opening_available_at timestamp with time zone,
    revenue_ttm double precision,
    grossprofit_ttm double precision,
    ebitda_ttm double precision,
    operatingincome_ttm double precision,
    netincome_ttm double precision,
    interestexpense_ttm double precision,
    incomebeforetax_ttm double precision,
    incometaxexpense_ttm double precision,
    epsdiluted_ttm double precision,
    eps_ttm double precision,
    operatingcashflow_ttm double precision,
    freecashflow_ttm double precision,
    dividendspaid_ttm double precision,
    commonstockrepurchased_ttm double precision,
    commonstockissued_ttm double precision,
    assets double precision,
    equity double precision,
    cash double precision,
    current_assets double precision,
    current_liabilities double precision,
    debt double precision,
    common_equity double precision,
    net_debt double precision,
    average_common_equity double precision,
    average_assets double precision,
    average_invested_capital double precision,
    market_cap double precision,
    enterprise_value double precision,
    net_shareholder_cash_ttm double precision,
    latest_income_fiscal_end timestamp without time zone,
    latest_cf_fiscal_end timestamp without time zone,
    latest_bs_fiscal_end timestamp without time zone,
    market_cap_asof_date timestamp without time zone,
    enterprise_value_asof_date timestamp without time zone,
    fundamental_age_days double precision,
    net_income_ttm double precision,
    ocf_ttm double precision,
    fcf_ttm double precision,
    accepted_timestamp_timezone_assumed text,
    latest_filing_accepted_at timestamp with time zone,
    revenue_growth_yoy_raw double precision,
    revenue_growth_yoy_missing_reason text,
    revenue_growth_yoy_applicable boolean,
    revenue_cagr_3y_raw double precision,
    revenue_cagr_3y_missing_reason text,
    revenue_cagr_3y_applicable boolean,
    eps_growth_yoy_raw double precision,
    eps_growth_yoy_missing_reason text,
    eps_growth_yoy_applicable boolean,
    net_income_growth_3y_raw double precision,
    net_income_growth_3y_missing_reason text,
    net_income_growth_3y_applicable boolean,
    ebitda_growth_yoy_raw double precision,
    ebitda_growth_yoy_missing_reason text,
    ebitda_growth_yoy_applicable boolean,
    ocf_growth_yoy_raw double precision,
    ocf_growth_yoy_missing_reason text,
    ocf_growth_yoy_applicable boolean,
    fcf_growth_3y_raw double precision,
    fcf_growth_3y_missing_reason text,
    fcf_growth_3y_applicable boolean,
    gross_margin_raw double precision,
    gross_margin_missing_reason text,
    gross_margin_applicable boolean,
    ebitda_margin_raw double precision,
    ebitda_margin_missing_reason text,
    ebitda_margin_applicable boolean,
    operating_margin_raw double precision,
    operating_margin_missing_reason text,
    operating_margin_applicable boolean,
    net_margin_raw double precision,
    net_margin_missing_reason text,
    net_margin_applicable boolean,
    roe_raw double precision,
    roe_missing_reason text,
    roe_applicable boolean,
    roic_raw double precision,
    roic_missing_reason text,
    roic_applicable boolean,
    fcf_margin_raw double precision,
    fcf_margin_missing_reason text,
    fcf_margin_applicable boolean,
    earnings_yield_raw double precision,
    earnings_yield_missing_reason text,
    earnings_yield_applicable boolean,
    sales_yield_raw double precision,
    sales_yield_missing_reason text,
    sales_yield_applicable boolean,
    ebitda_ev_yield_raw double precision,
    ebitda_ev_yield_missing_reason text,
    ebitda_ev_yield_applicable boolean,
    fcf_yield_raw double precision,
    fcf_yield_missing_reason text,
    fcf_yield_applicable boolean,
    book_to_market_raw double precision,
    book_to_market_missing_reason text,
    book_to_market_applicable boolean,
    ocf_yield_raw double precision,
    ocf_yield_missing_reason text,
    ocf_yield_applicable boolean,
    net_shareholder_yield_raw double precision,
    net_shareholder_yield_missing_reason text,
    net_shareholder_yield_applicable boolean,
    debt_to_equity_raw double precision,
    debt_to_equity_missing_reason text,
    debt_to_equity_applicable boolean,
    debt_to_assets_raw double precision,
    debt_to_assets_missing_reason text,
    debt_to_assets_applicable boolean,
    net_debt_to_ebitda_raw double precision,
    net_debt_to_ebitda_missing_reason text,
    net_debt_to_ebitda_applicable boolean,
    interest_coverage_raw double precision,
    interest_coverage_missing_reason text,
    interest_coverage_applicable boolean,
    cash_to_assets_raw double precision,
    cash_to_assets_missing_reason text,
    cash_to_assets_applicable boolean,
    current_ratio_raw double precision,
    current_ratio_missing_reason text,
    current_ratio_applicable boolean,
    ocf_to_debt_raw double precision,
    ocf_to_debt_missing_reason text,
    ocf_to_debt_applicable boolean,
    roa_raw double precision,
    roa_missing_reason text,
    roa_applicable boolean,
    equity_to_assets_raw double precision,
    equity_to_assets_missing_reason text,
    equity_to_assets_applicable boolean,
    income_source_row_id text,
    income_available_at timestamp with time zone,
    income_fiscal_period_end timestamp without time zone,
    income_fiscal_age_days double precision,
    income_available_age_days double precision,
    income_availability_proxy boolean,
    cf_source_row_id text,
    cf_available_at timestamp with time zone,
    cf_fiscal_period_end timestamp without time zone,
    cf_fiscal_age_days double precision,
    cf_available_age_days double precision,
    cf_availability_proxy boolean,
    bs_source_row_id text,
    bs_available_at timestamp with time zone,
    bs_fiscal_period_end timestamp without time zone,
    bs_fiscal_age_days double precision,
    bs_available_age_days double precision,
    bs_availability_proxy boolean,
    market_cap_source_row_id text,
    market_cap_available_at timestamp with time zone,
    market_cap_fiscal_period_end timestamp without time zone,
    market_cap_fiscal_age_days double precision,
    market_cap_available_age_days double precision,
    market_cap_availability_proxy boolean,
    ev_source_row_id text,
    ev_available_at timestamp with time zone,
    ev_fiscal_period_end timestamp without time zone,
    ev_fiscal_age_days double precision,
    ev_available_age_days double precision,
    ev_availability_proxy boolean,
    fcf_ttm_for_margin double precision,
    ev_vendor_observation_date timestamp without time zone,
    ev_vendor_source_row_id text,
    ev_availability_unknown boolean,
    revenue_growth_yoy_clean double precision,
    revenue_growth_yoy_outlier_flag boolean,
    revenue_growth_yoy_sector_score double precision,
    revenue_cagr_3y_clean double precision,
    revenue_cagr_3y_outlier_flag boolean,
    revenue_cagr_3y_sector_score double precision,
    eps_growth_yoy_clean double precision,
    eps_growth_yoy_outlier_flag boolean,
    eps_growth_yoy_sector_score double precision,
    net_income_growth_3y_clean double precision,
    net_income_growth_3y_outlier_flag boolean,
    net_income_growth_3y_sector_score double precision,
    ebitda_growth_yoy_clean double precision,
    ebitda_growth_yoy_outlier_flag boolean,
    ebitda_growth_yoy_sector_score double precision,
    ocf_growth_yoy_clean double precision,
    ocf_growth_yoy_outlier_flag boolean,
    ocf_growth_yoy_sector_score double precision,
    fcf_growth_3y_clean double precision,
    fcf_growth_3y_outlier_flag boolean,
    fcf_growth_3y_sector_score double precision,
    gross_margin_clean double precision,
    gross_margin_outlier_flag boolean,
    gross_margin_sector_score double precision,
    ebitda_margin_clean double precision,
    ebitda_margin_outlier_flag boolean,
    ebitda_margin_sector_score double precision,
    operating_margin_clean double precision,
    operating_margin_outlier_flag boolean,
    operating_margin_sector_score double precision,
    net_margin_clean double precision,
    net_margin_outlier_flag boolean,
    net_margin_sector_score double precision,
    roe_clean double precision,
    roe_outlier_flag boolean,
    roe_sector_score double precision,
    roic_clean double precision,
    roic_outlier_flag boolean,
    roic_sector_score double precision,
    fcf_margin_clean double precision,
    fcf_margin_outlier_flag boolean,
    fcf_margin_sector_score double precision,
    earnings_yield_clean double precision,
    earnings_yield_outlier_flag boolean,
    earnings_yield_sector_score double precision,
    sales_yield_clean double precision,
    sales_yield_outlier_flag boolean,
    sales_yield_sector_score double precision,
    ebitda_ev_yield_clean double precision,
    ebitda_ev_yield_outlier_flag boolean,
    ebitda_ev_yield_sector_score double precision,
    fcf_yield_clean double precision,
    fcf_yield_outlier_flag boolean,
    fcf_yield_sector_score double precision,
    book_to_market_clean double precision,
    book_to_market_outlier_flag boolean,
    book_to_market_sector_score double precision,
    ocf_yield_clean double precision,
    ocf_yield_outlier_flag boolean,
    ocf_yield_sector_score double precision,
    net_shareholder_yield_clean double precision,
    net_shareholder_yield_outlier_flag boolean,
    net_shareholder_yield_sector_score double precision,
    debt_to_equity_clean double precision,
    debt_to_equity_outlier_flag boolean,
    debt_to_equity_sector_score double precision,
    debt_to_assets_clean double precision,
    debt_to_assets_outlier_flag boolean,
    debt_to_assets_sector_score double precision,
    net_debt_to_ebitda_clean double precision,
    net_debt_to_ebitda_outlier_flag boolean,
    net_debt_to_ebitda_sector_score double precision,
    interest_coverage_clean double precision,
    interest_coverage_outlier_flag boolean,
    interest_coverage_sector_score double precision,
    cash_to_assets_clean double precision,
    cash_to_assets_outlier_flag boolean,
    cash_to_assets_sector_score double precision,
    current_ratio_clean double precision,
    current_ratio_outlier_flag boolean,
    current_ratio_sector_score double precision,
    ocf_to_debt_clean double precision,
    ocf_to_debt_outlier_flag boolean,
    ocf_to_debt_sector_score double precision,
    roa_clean double precision,
    roa_outlier_flag boolean,
    roa_sector_score double precision,
    equity_to_assets_clean double precision,
    equity_to_assets_outlier_flag boolean,
    equity_to_assets_sector_score double precision,
    growth_factor_count bigint,
    growth_composite double precision,
    profitability_factor_count bigint,
    profitability_composite double precision,
    valuation_factor_count bigint,
    valuation_composite double precision,
    balance_sheet_factor_count bigint,
    balance_sheet_composite double precision,
    quality_coverage_pct double precision,
    growth_unavailable_negative_base boolean,
    growth_unavailable_small_base boolean
);


--
-- Name: sp500_monthly_population; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_monthly_population (
    week_end date,
    ticker_latest text,
    security_id text,
    historical_ticker text,
    sector text,
    api_lookup_ticker text,
    mapping_status text,
    price_status text,
    observed_sessions bigint,
    expected_sessions bigint
);


--
-- Name: sp500_population_daily_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_population_daily_audit (
    date date,
    security_id text,
    ticker text,
    historical_ticker text,
    latest_ticker text,
    api_lookup_ticker text,
    mapping_status text,
    corporate_successor_ticker text,
    company_name text,
    sector text,
    currency text,
    cik text,
    is_actively_trading boolean,
    source_membership_key text
);


--
-- Name: sp500_prices_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_prices_daily (
    date date NOT NULL,
    ticker_latest character varying(16) NOT NULL,
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    adj_close double precision,
    volume bigint
);


--
-- Name: sp500_prices_technicals_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_prices_technicals_daily (
    date date NOT NULL,
    ticker_latest character varying(16) NOT NULL,
    adj_close double precision,
    ret_30d double precision,
    ret_180d double precision,
    ret_360d double precision,
    rsi_14 double precision,
    rsi_9 double precision,
    rsi_3 double precision,
    sma_50 double precision,
    sma_100 double precision,
    sma_200 double precision,
    bb_lower double precision,
    bb_middle double precision,
    bb_upper double precision,
    bb_bandwidth double precision,
    bb_percent double precision
);


--
-- Name: sp500_quarterly_snapshots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_quarterly_snapshots (
    week_end date NOT NULL,
    ticker_latest character varying(16) NOT NULL,
    adj_close_week_last double precision,
    adj_close_week_avg double precision,
    volume_week_sum bigint,
    dollar_vol_week_avgp double precision,
    ret_week double precision,
    ret_week_fwd1 double precision,
    median_ret_fwd1 double precision,
    target_gt_median integer
);


--
-- Name: sp500_stock_technical_features_daily_v2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_stock_technical_features_daily_v2 (
    date timestamp without time zone,
    open real,
    high real,
    low real,
    close real,
    adj_close real,
    volume bigint,
    ticker_latest text,
    daily_return real,
    ret_5d real,
    ret_10d real,
    ret_20d real,
    ret_30d real,
    ret_60d real,
    ret_90d real,
    ret_120d real,
    ret_180d real,
    ret_252d real,
    ret_360d real,
    momentum_accel_20d_vs_120d real,
    momentum_accel_30d_vs_180d real,
    momentum_accel_60d_vs_180d real,
    momentum_accel_60d_vs_252d real,
    momentum_accel_120d_vs_252d real,
    rsi_14 real,
    rsi_9 real,
    rsi_3 real,
    rsi_14_overbought_flag integer,
    rsi_14_oversold_flag integer,
    rsi_3_overbought_flag integer,
    rsi_3_oversold_flag integer,
    sma_20 real,
    price_vs_sma_20 real,
    sma_50 real,
    price_vs_sma_50 real,
    sma_100 real,
    price_vs_sma_100 real,
    sma_200 real,
    price_vs_sma_200 real,
    sma_20_vs_sma_50 real,
    sma_50_vs_sma_100 real,
    sma_50_vs_sma_200 real,
    sma_100_vs_sma_200 real,
    sma_20_slope_20d real,
    sma_50_slope_20d real,
    sma_100_slope_20d real,
    sma_200_slope_20d real,
    macd_12_26 real,
    macd_signal_9 real,
    macd_hist real,
    macd_hist_positive_flag integer,
    bb_middle real,
    bb_upper real,
    bb_lower real,
    bb_percent real,
    bb_bandwidth real,
    price_vs_bb_upper real,
    price_vs_bb_lower real,
    dist_from_3m_high real,
    dist_from_3m_low real,
    dist_from_6m_high real,
    dist_from_6m_low real,
    dist_from_52w_high real,
    dist_from_52w_low real,
    drawdown_3m real,
    max_drawdown_3m real,
    drawdown_6m real,
    max_drawdown_6m real,
    drawdown_12m real,
    max_drawdown_12m real,
    drawdown_252d real,
    max_drawdown_252d real,
    realized_vol_20d real,
    realized_vol_60d real,
    realized_vol_120d real,
    realized_vol_252d real,
    vol_20d_minus_vol_60d real,
    vol_60d_minus_vol_252d real,
    vol_20d_div_vol_252d real,
    vol_60d_div_vol_252d real,
    downside_return real,
    downside_vol_20d real,
    downside_vol_60d real,
    downside_vol_120d real,
    downside_vol_252d real,
    dollar_volume double precision,
    avg_volume_20d bigint,
    avg_dollar_volume_20d double precision,
    avg_volume_60d bigint,
    avg_dollar_volume_60d double precision,
    avg_volume_252d bigint,
    avg_dollar_volume_252d double precision,
    volume_ratio_20d_vs_60d real,
    volume_ratio_20d_vs_252d real,
    volume_ratio_60d_vs_252d real,
    sp500_daily_return real,
    macro_source_date timestamp without time zone,
    sp500_ret_5d real,
    sp500_ret_10d real,
    sp500_ret_20d real,
    sp500_ret_30d real,
    sp500_ret_60d real,
    sp500_ret_90d real,
    sp500_ret_120d real,
    sp500_ret_180d real,
    sp500_ret_252d real,
    sp500_ret_360d real,
    technology_ret_20d real,
    technology_ret_30d real,
    technology_ret_60d real,
    technology_ret_120d real,
    technology_ret_180d real,
    technology_ret_252d real,
    technology_ret_360d real,
    financials_ret_20d real,
    financials_ret_30d real,
    financials_ret_60d real,
    financials_ret_120d real,
    financials_ret_180d real,
    financials_ret_252d real,
    financials_ret_360d real,
    healthcare_ret_20d real,
    healthcare_ret_30d real,
    healthcare_ret_60d real,
    healthcare_ret_120d real,
    healthcare_ret_180d real,
    healthcare_ret_252d real,
    healthcare_ret_360d real,
    consumer_discretionary_ret_20d real,
    consumer_discretionary_ret_30d real,
    consumer_discretionary_ret_60d real,
    consumer_discretionary_ret_120d real,
    consumer_discretionary_ret_180d real,
    consumer_discretionary_ret_252d real,
    consumer_discretionary_ret_360d real,
    consumer_staples_ret_20d real,
    consumer_staples_ret_30d real,
    consumer_staples_ret_60d real,
    consumer_staples_ret_120d real,
    consumer_staples_ret_180d real,
    consumer_staples_ret_252d real,
    consumer_staples_ret_360d real,
    industrials_ret_20d real,
    industrials_ret_30d real,
    industrials_ret_60d real,
    industrials_ret_120d real,
    industrials_ret_180d real,
    industrials_ret_252d real,
    industrials_ret_360d real,
    energy_ret_20d real,
    energy_ret_30d real,
    energy_ret_60d real,
    energy_ret_120d real,
    energy_ret_180d real,
    energy_ret_252d real,
    energy_ret_360d real,
    utilities_ret_20d real,
    utilities_ret_30d real,
    utilities_ret_60d real,
    utilities_ret_120d real,
    utilities_ret_180d real,
    utilities_ret_252d real,
    utilities_ret_360d real,
    real_estate_ret_20d real,
    real_estate_ret_30d real,
    real_estate_ret_60d real,
    real_estate_ret_120d real,
    real_estate_ret_180d real,
    real_estate_ret_252d real,
    real_estate_ret_360d real,
    materials_ret_20d real,
    materials_ret_30d real,
    materials_ret_60d real,
    materials_ret_120d real,
    materials_ret_180d real,
    materials_ret_252d real,
    materials_ret_360d real,
    communication_services_ret_20d real,
    communication_services_ret_30d real,
    communication_services_ret_60d real,
    communication_services_ret_120d real,
    communication_services_ret_180d real,
    communication_services_ret_252d real,
    communication_services_ret_360d real,
    macro_match_lag_days integer,
    rel_ret_5d_sp500 real,
    rel_ret_10d_sp500 real,
    rel_ret_20d_sp500 real,
    rel_ret_30d_sp500 real,
    rel_ret_60d_sp500 real,
    rel_ret_90d_sp500 real,
    rel_ret_120d_sp500 real,
    rel_ret_180d_sp500 real,
    rel_ret_252d_sp500 real,
    rel_ret_360d_sp500 real,
    beta_60d real,
    beta_120d real,
    beta_252d real,
    sector_clean text,
    sector_key text,
    sector_benchmark_ret_20d real,
    rel_ret_20d_sector real,
    sector_benchmark_ret_30d real,
    rel_ret_30d_sector real,
    sector_benchmark_ret_60d real,
    rel_ret_60d_sector real,
    sector_benchmark_ret_120d real,
    rel_ret_120d_sector real,
    sector_benchmark_ret_180d real,
    rel_ret_180d_sector real,
    sector_benchmark_ret_252d real,
    rel_ret_252d_sector real,
    sector_benchmark_ret_360d real,
    rel_ret_360d_sector real,
    week_end timestamp without time zone
);


--
-- Name: sp500_weekly_rollups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp500_weekly_rollups (
    week_end date NOT NULL,
    ticker_latest character varying(16) NOT NULL,
    adj_close_week_last double precision,
    adj_close_week_avg double precision,
    volume_week_sum bigint,
    dollar_vol_week_avgp double precision,
    ret_week double precision,
    ret_week_fwd1 double precision,
    median_ret_fwd1 double precision,
    target_gt_median integer
);


--
-- Name: stg_analyst_estimates_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stg_analyst_estimates_q (
    symbol text,
    date timestamp without time zone,
    symbol_x text,
    estimatedrevenuelow bigint,
    estimatedrevenuehigh bigint,
    estimatedrevenueavg bigint,
    estimatedebitdalow bigint,
    estimatedebitdahigh bigint,
    estimatedebitdaavg bigint,
    estimatedebitlow bigint,
    estimatedebithigh bigint,
    estimatedebitavg bigint,
    estimatednetincomelow bigint,
    estimatednetincomehigh bigint,
    estimatednetincomeavg double precision,
    estimatedsgaexpenselow bigint,
    estimatedsgaexpensehigh bigint,
    estimatedsgaexpenseavg bigint,
    estimatedepsavg double precision,
    estimatedepshigh double precision,
    estimatedepslow double precision,
    numberanalystestimatedrevenue bigint,
    numberanalystsestimatedeps bigint,
    symbol_y text,
    date_start timestamp without time zone,
    date_end timestamp without time zone
);


--
-- Name: stg_balance_sheets_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stg_balance_sheets_q (
    symbol text,
    date timestamp without time zone,
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    reportedcurrency text,
    cik text,
    fillingdate text,
    accepteddate text,
    calendaryear text,
    period text,
    cashandcashequivalents bigint,
    shortterminvestments bigint,
    cashandshortterminvestments bigint,
    netreceivables bigint,
    inventory bigint,
    othercurrentassets bigint,
    totalcurrentassets bigint,
    propertyplantequipmentnet bigint,
    goodwill bigint,
    intangibleassets bigint,
    goodwillandintangibleassets bigint,
    longterminvestments bigint,
    taxassets double precision,
    othernoncurrentassets bigint,
    totalnoncurrentassets bigint,
    otherassets double precision,
    totalassets bigint,
    accountpayables double precision,
    shorttermdebt bigint,
    taxpayables double precision,
    deferredrevenue double precision,
    othercurrentliabilities bigint,
    totalcurrentliabilities bigint,
    longtermdebt bigint,
    deferredrevenuenoncurrent double precision,
    deferredtaxliabilitiesnoncurrent double precision,
    othernoncurrentliabilities bigint,
    totalnoncurrentliabilities bigint,
    otherliabilities double precision,
    capitalleaseobligations bigint,
    totalliabilities bigint,
    preferredstock double precision,
    commonstock bigint,
    retainedearnings bigint,
    accumulatedothercomprehensiveincomeloss double precision,
    othertotalstockholdersequity double precision,
    totalstockholdersequity bigint,
    totalequity bigint,
    totalliabilitiesandstockholdersequity bigint,
    minorityinterest bigint,
    totalliabilitiesandtotalequity bigint,
    totalinvestments bigint,
    totaldebt bigint,
    netdebt double precision,
    link text,
    finallink text,
    cashandcashequivalents_yoy double precision,
    shortterminvestments_yoy double precision,
    cashandshortterminvestments_yoy double precision,
    netreceivables_yoy double precision,
    inventory_yoy double precision,
    othercurrentassets_yoy double precision,
    totalcurrentassets_yoy double precision,
    propertyplantequipmentnet_yoy double precision,
    longterminvestments_yoy double precision,
    totalnoncurrentassets_yoy double precision,
    totalassets_yoy double precision,
    accountpayables_yoy double precision,
    shorttermdebt_yoy double precision,
    totalcurrentliabilities_yoy double precision,
    longtermdebt_yoy double precision,
    totalnoncurrentliabilities_yoy double precision,
    totalliabilities_yoy double precision,
    commonstock_yoy double precision,
    retainedearnings_yoy double precision,
    totalstockholdersequity_yoy double precision,
    totalequity_yoy double precision,
    totaldebt_yoy double precision,
    netdebt_yoy double precision,
    current_ratio double precision,
    quick_ratio double precision,
    cash_ratio double precision,
    working_capital double precision,
    working_capital_to_assets double precision,
    inventory_to_current double precision,
    debt_to_equity double precision,
    debt_to_assets double precision,
    net_debt_to_equity double precision,
    liabilities_to_assets double precision,
    equity_ratio double precision,
    lt_debt_to_capital double precision,
    total_debt_to_capital double precision,
    total_debt double precision,
    net_debt double precision,
    total_assets double precision,
    total_equity double precision,
    total_liabilities double precision,
    total_current_assets double precision,
    total_current_liabilities double precision,
    cash_and_st_investments double precision,
    financialleverage double precision,
    financialleverage_avg4q double precision,
    financialleverage_yoy double precision,
    debttoequity double precision,
    liabilitiestoequity double precision,
    debttoassets double precision,
    netdebttoequity double precision
);


--
-- Name: stg_enterprise_values_q; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stg_enterprise_values_q (
    symbol text,
    date timestamp without time zone,
    enterprisevalue double precision,
    stockprice double precision,
    numberofshares double precision,
    marketcapitalization double precision,
    minuscashandcashequivalents bigint,
    addtotaldebt bigint
);


--
-- Name: stg_market_caps_d; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stg_market_caps_d (
    symbol text,
    date timestamp without time zone,
    marketcap double precision
);


--
-- Name: stg_realized_vol_d; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stg_realized_vol_d (
    symbol text,
    date timestamp without time zone,
    vol_1m_ann double precision,
    vol_6m_ann double precision,
    vol_12m_ann double precision
);


--
-- Name: v_sp500_daily_features; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_sp500_daily_features AS
 SELECT f.date,
    f.ticker_latest,
    f.adj_close,
    f.ret_30d,
    f.ret_180d,
    f.ret_360d,
    f.rsi_14,
    f.rsi_9,
    f.rsi_3,
    f.sma_50,
    f.sma_100,
    f.sma_200,
    f.bb_lower,
    f.bb_middle,
    f.bb_upper,
    f.bb_bandwidth,
    f.bb_percent,
    b.beta_12m,
    m.mkt_1m,
    m.mkt_6m,
    m.mkt_12m,
    (f.ret_30d - m.mkt_1m) AS rel_mom_1m,
    (f.ret_180d - m.mkt_6m) AS rel_mom_6m,
    (f.ret_360d - m.mkt_12m) AS rel_mom_12m
   FROM ((public.sp500_prices_technicals_daily f
     LEFT JOIN public.sp500_beta_12m_daily b ON (((b.date = f.date) AND ((b.ticker_latest)::text = (f.ticker_latest)::text))))
     LEFT JOIN public.sp500_market_momentum_daily m ON ((m.date = f.date)));


--
-- Name: v_sp500_ml_quarterly_base_technical; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_sp500_ml_quarterly_base_technical AS
 WITH valid_snapshots AS (
         SELECT sp500_quarterly_snapshots.week_end
           FROM public.sp500_quarterly_snapshots
          GROUP BY sp500_quarterly_snapshots.week_end
         HAVING (count(DISTINCT sp500_quarterly_snapshots.ticker_latest) >= 3)
        ), base AS (
         SELECT sp500_quarterly_snapshots.week_end,
            sp500_quarterly_snapshots.ticker_latest,
            sp500_quarterly_snapshots.adj_close_week_last,
            sp500_quarterly_snapshots.adj_close_week_avg,
            sp500_quarterly_snapshots.volume_week_sum,
            sp500_quarterly_snapshots.dollar_vol_week_avgp,
            sp500_quarterly_snapshots.ret_week,
            sp500_quarterly_snapshots.ret_week_fwd1,
            sp500_quarterly_snapshots.median_ret_fwd1,
            sp500_quarterly_snapshots.target_gt_median
           FROM public.sp500_quarterly_snapshots
          WHERE ((sp500_quarterly_snapshots.week_end IN ( SELECT valid_snapshots.week_end
                   FROM valid_snapshots)) AND (sp500_quarterly_snapshots.week_end <= '2026-01-01'::date))
        )
 SELECT b.week_end,
    b.ticker_latest,
    b.adj_close_week_last,
    b.adj_close_week_avg,
    b.volume_week_sum,
    b.dollar_vol_week_avgp,
    b.ret_week,
    b.ret_week_fwd1,
    b.median_ret_fwd1,
    b.target_gt_median,
    t.date AS technical_date,
    t.ret_30d,
    t.ret_180d,
    t.ret_360d,
    t.rsi_14,
    t.rsi_9,
    t.rsi_3,
        CASE
            WHEN ((t.sma_50 IS NOT NULL) AND (t.sma_50 <> (0)::double precision)) THEN ((t.adj_close / t.sma_50) - (1)::double precision)
            ELSE NULL::double precision
        END AS price_vs_sma_50,
        CASE
            WHEN ((t.sma_100 IS NOT NULL) AND (t.sma_100 <> (0)::double precision)) THEN ((t.adj_close / t.sma_100) - (1)::double precision)
            ELSE NULL::double precision
        END AS price_vs_sma_100,
        CASE
            WHEN ((t.sma_200 IS NOT NULL) AND (t.sma_200 <> (0)::double precision)) THEN ((t.adj_close / t.sma_200) - (1)::double precision)
            ELSE NULL::double precision
        END AS price_vs_sma_200,
        CASE
            WHEN ((t.sma_200 IS NOT NULL) AND (t.sma_200 <> (0)::double precision)) THEN ((t.sma_50 / t.sma_200) - (1)::double precision)
            ELSE NULL::double precision
        END AS sma_50_vs_sma_200,
    t.bb_percent,
    t.bb_bandwidth
   FROM (base b
     LEFT JOIN LATERAL ( SELECT d.date,
            d.adj_close,
            d.ret_30d,
            d.ret_180d,
            d.ret_360d,
            d.rsi_14,
            d.rsi_9,
            d.rsi_3,
            d.sma_50,
            d.sma_100,
            d.sma_200,
            d.bb_percent,
            d.bb_bandwidth
           FROM public.sp500_prices_technicals_daily d
          WHERE (((d.ticker_latest)::text = (b.ticker_latest)::text) AND (d.date <= b.week_end))
          ORDER BY d.date DESC
         LIMIT 1) t ON (true))
  ORDER BY b.week_end, b.ticker_latest;


--
-- Name: v_sp500_sector_clean; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_sp500_sector_clean AS
 SELECT DISTINCT ticker,
    COALESCE(NULLIF(btrim((sector)::text), ''::text), 'Other'::text) AS sector_clean
   FROM public.sp500_long_latest_profiles;


--
-- Name: vix_momentum_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vix_momentum_daily (
    date date NOT NULL,
    v_1m double precision,
    v_6m double precision,
    v_12m double precision
);


--
-- Name: voo_quarterley_returns; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.voo_quarterley_returns (
    quarter_end date,
    last_trading_day date,
    voo_adj_close double precision,
    ret_voo_fwd1 double precision
);


--
-- Name: voo_weekly_returns; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.voo_weekly_returns (
    week_end date,
    ret_voo_fwd1 double precision
);


--
-- Name: voo_weekly_returns_stg; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.voo_weekly_returns_stg (
    week_end date,
    voo_px double precision,
    ret_voo double precision
);


--
-- Name: balance_sheets_q balance_sheets_q_symbol_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.balance_sheets_q
    ADD CONSTRAINT balance_sheets_q_symbol_date_key UNIQUE (symbol, date);


--
-- Name: cashflow_statements_q cashflow_statements_q_symbol_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cashflow_statements_q
    ADD CONSTRAINT cashflow_statements_q_symbol_date_key UNIQUE (symbol, date);


--
-- Name: enterprise_values_q enterprise_values_q_symbol_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enterprise_values_q
    ADD CONSTRAINT enterprise_values_q_symbol_date_key UNIQUE (symbol, date);


--
-- Name: income_statements_q income_statements_q_symbol_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.income_statements_q
    ADD CONSTRAINT income_statements_q_symbol_date_key UNIQUE (symbol, date);


--
-- Name: macro_cross_asset_features_daily macro_cross_asset_features_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.macro_cross_asset_features_daily
    ADD CONSTRAINT macro_cross_asset_features_daily_pkey PRIMARY KEY (date);


--
-- Name: macro_cross_asset_observations_daily macro_cross_asset_observations_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.macro_cross_asset_observations_daily
    ADD CONSTRAINT macro_cross_asset_observations_daily_pkey PRIMARY KEY (date, series);


--
-- Name: market_caps_d market_caps_d_symbol_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.market_caps_d
    ADD CONSTRAINT market_caps_d_symbol_date_key UNIQUE (symbol, date);


--
-- Name: sp500_long_latest_profiles pk_sp500_long_latest_profiles; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_long_latest_profiles
    ADD CONSTRAINT pk_sp500_long_latest_profiles PRIMARY KEY (date, ticker);


--
-- Name: rates_momentum_daily rates_momentum_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rates_momentum_daily
    ADD CONSTRAINT rates_momentum_daily_pkey PRIMARY KEY (date);


--
-- Name: realized_vol_d realized_vol_d_symbol_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.realized_vol_d
    ADD CONSTRAINT realized_vol_d_symbol_date_key UNIQUE (symbol, date);


--
-- Name: sp500_beta_12m_daily sp500_beta_12m_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_beta_12m_daily
    ADD CONSTRAINT sp500_beta_12m_daily_pkey PRIMARY KEY (date, ticker_latest);


--
-- Name: sp500_daily_technicals_ml sp500_daily_technicals_ml_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_daily_technicals_ml
    ADD CONSTRAINT sp500_daily_technicals_ml_pkey PRIMARY KEY (date, ticker_latest);


--
-- Name: sp500_market_momentum_daily sp500_market_momentum_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_market_momentum_daily
    ADD CONSTRAINT sp500_market_momentum_daily_pkey PRIMARY KEY (date);


--
-- Name: sp500_prices_daily sp500_prices_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_prices_daily
    ADD CONSTRAINT sp500_prices_daily_pkey PRIMARY KEY (date, ticker_latest);


--
-- Name: sp500_prices_technicals_daily sp500_prices_technicals_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_prices_technicals_daily
    ADD CONSTRAINT sp500_prices_technicals_daily_pkey PRIMARY KEY (date, ticker_latest);


--
-- Name: sp500_quarterly_snapshots sp500_quarterly_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_quarterly_snapshots
    ADD CONSTRAINT sp500_quarterly_snapshots_pkey PRIMARY KEY (week_end, ticker_latest);


--
-- Name: sp500_weekly_rollups sp500_weekly_rollups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp500_weekly_rollups
    ADD CONSTRAINT sp500_weekly_rollups_pkey PRIMARY KEY (week_end, ticker_latest);


--
-- Name: vix_momentum_daily vix_momentum_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vix_momentum_daily
    ADD CONSTRAINT vix_momentum_daily_pkey PRIMARY KEY (date);


--
-- Name: analyst_estimates_annual_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX analyst_estimates_annual_date_idx ON public.analyst_estimates_annual USING btree (date);


--
-- Name: analyst_estimates_annual_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX analyst_estimates_annual_symbol_idx ON public.analyst_estimates_annual USING btree (symbol);


--
-- Name: analyst_estimates_annual_window_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX analyst_estimates_annual_window_idx ON public.analyst_estimates_annual USING btree (symbol, date_start, date_end);


--
-- Name: balance_sheets_q_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX balance_sheets_q_date_idx ON public.balance_sheets_q USING btree (date);


--
-- Name: balance_sheets_q_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX balance_sheets_q_fund_v1_key ON public.balance_sheets_q USING btree (symbol, date);


--
-- Name: balance_sheets_q_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX balance_sheets_q_symbol_idx ON public.balance_sheets_q USING btree (symbol);


--
-- Name: capped_portfolio_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX capped_portfolio_date ON public.sp500_capped_portfolio_audit USING btree (signal_date, scenario);


--
-- Name: capped_portfolio_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX capped_portfolio_key ON public.sp500_capped_portfolio_audit USING btree (portfolio_prediction_id);


--
-- Name: cashflow_statements_q_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cashflow_statements_q_date_idx ON public.cashflow_statements_q USING btree (date);


--
-- Name: cashflow_statements_q_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX cashflow_statements_q_fund_v1_key ON public.cashflow_statements_q USING btree (symbol, date);


--
-- Name: cashflow_statements_q_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cashflow_statements_q_symbol_idx ON public.cashflow_statements_q USING btree (symbol);


--
-- Name: enterprise_values_q_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX enterprise_values_q_date_idx ON public.enterprise_values_q USING btree (date);


--
-- Name: enterprise_values_q_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX enterprise_values_q_fund_v1_key ON public.enterprise_values_q USING btree (symbol, date);


--
-- Name: enterprise_values_q_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX enterprise_values_q_symbol_idx ON public.enterprise_values_q USING btree (symbol);


--
-- Name: factor_definition_registry_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX factor_definition_registry_fund_v1_key ON public.factor_definition_registry USING btree (factor_id);


--
-- Name: factor_quality_long_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX factor_quality_long_fund_v1_key ON public.factor_quality_long USING btree (security_id, month_end, factor_id);


--
-- Name: fundamental_cleaning_threshold_audit_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX fundamental_cleaning_threshold_audit_fund_v1_key ON public.fundamental_cleaning_threshold_audit USING btree (peer_group, factor_id, month_end);


--
-- Name: fundamental_extension_capabilities_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX fundamental_extension_capabilities_fund_v1_key ON public.fundamental_extension_capabilities USING btree (metric);


--
-- Name: fundamental_raw_payload_manifest_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX fundamental_raw_payload_manifest_fund_v1_key ON public.fundamental_raw_payload_manifest USING btree (batch_id, payload_path);


--
-- Name: fundamental_source_lineage_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX fundamental_source_lineage_fund_v1_key ON public.fundamental_source_lineage USING btree (security_id, month_end, family);


--
-- Name: idx_market_sector_macro_features_daily_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_market_sector_macro_features_daily_date ON public.market_sector_macro_features_daily USING btree (date);


--
-- Name: idx_market_sector_macro_features_daily_week_end; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_market_sector_macro_features_daily_week_end ON public.market_sector_macro_features_daily USING btree (week_end);


--
-- Name: idx_market_sector_macro_features_weekly_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_market_sector_macro_features_weekly_date ON public.market_sector_macro_features_weekly USING btree (date);


--
-- Name: idx_market_sector_macro_features_weekly_week_end; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_market_sector_macro_features_weekly_week_end ON public.market_sector_macro_features_weekly USING btree (week_end);


--
-- Name: idx_sp500_long_latest_profiles_cik; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sp500_long_latest_profiles_cik ON public.sp500_long_latest_profiles USING btree (cik);


--
-- Name: idx_sp500_long_latest_profiles_latest; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sp500_long_latest_profiles_latest ON public.sp500_long_latest_profiles USING btree (latest_ticker);


--
-- Name: idx_sp500_stock_technical_features_daily_v2_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sp500_stock_technical_features_daily_v2_date ON public.sp500_stock_technical_features_daily_v2 USING btree (date);


--
-- Name: idx_sp500_stock_technical_features_daily_v2_sector_clean; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sp500_stock_technical_features_daily_v2_sector_clean ON public.sp500_stock_technical_features_daily_v2 USING btree (sector_clean);


--
-- Name: idx_sp500_stock_technical_features_daily_v2_ticker_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sp500_stock_technical_features_daily_v2_ticker_date ON public.sp500_stock_technical_features_daily_v2 USING btree (ticker_latest, date);


--
-- Name: idx_sp500_stock_technical_features_daily_v2_week_end; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sp500_stock_technical_features_daily_v2_week_end ON public.sp500_stock_technical_features_daily_v2 USING btree (week_end);


--
-- Name: income_statements_q_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX income_statements_q_date_idx ON public.income_statements_q USING btree (date);


--
-- Name: income_statements_q_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX income_statements_q_fund_v1_key ON public.income_statements_q USING btree (symbol, date);


--
-- Name: income_statements_q_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX income_statements_q_symbol_idx ON public.income_statements_q USING btree (symbol);


--
-- Name: ix_earnings_surprises_q_sym_date; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_earnings_surprises_q_sym_date ON public.earnings_surprises_q USING btree (symbol, date);


--
-- Name: ix_ratios_annual_symbol_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ratios_annual_symbol_date ON public.ratios_annual USING btree (symbol, date);


--
-- Name: market_caps_d_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX market_caps_d_date_idx ON public.market_caps_d USING btree (date);


--
-- Name: market_caps_d_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX market_caps_d_fund_v1_key ON public.market_caps_d USING btree (symbol, date);


--
-- Name: market_caps_d_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX market_caps_d_symbol_idx ON public.market_caps_d USING btree (symbol);


--
-- Name: model_prediction_audit_date_model; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX model_prediction_audit_date_model ON public.sp500_model_prediction_audit USING btree (signal_date, model, scenario);


--
-- Name: model_prediction_audit_feature; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX model_prediction_audit_feature ON public.sp500_model_prediction_audit USING btree (feature_row_id);


--
-- Name: realized_vol_d_date_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX realized_vol_d_date_idx ON public.realized_vol_d USING btree (date);


--
-- Name: realized_vol_d_symbol_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX realized_vol_d_symbol_idx ON public.realized_vol_d USING btree (symbol);


--
-- Name: sector_etf_prices_daily_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sector_etf_prices_daily_key ON public.sector_etf_prices_daily USING btree (date, proxy_ticker);


--
-- Name: sector_factor_applicability_registry_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sector_factor_applicability_registry_fund_v1_key ON public.sector_factor_applicability_registry USING btree (sector, financial_subtype, factor_id);


--
-- Name: sector_technical_proxy_map_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sector_technical_proxy_map_key ON public.sector_technical_proxy_map USING btree (sector);


--
-- Name: sector_technicals_daily_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sector_technicals_daily_key ON public.sector_technicals_daily USING btree (date, sector);


--
-- Name: sp500_daily_technicals_ml_date_ticker_latest_uidx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_daily_technicals_ml_date_ticker_latest_uidx ON public.sp500_daily_technicals_ml USING btree (date, ticker_latest);


--
-- Name: sp500_model_attribution_audit_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_model_attribution_audit_key ON public.sp500_model_attribution_audit USING btree (prediction_id, feature);


--
-- Name: sp500_model_feature_audit_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_model_feature_audit_key ON public.sp500_model_feature_audit USING btree (feature_row_id);


--
-- Name: sp500_model_prediction_audit_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_model_prediction_audit_key ON public.sp500_model_prediction_audit USING btree (prediction_id);


--
-- Name: sp500_monthly_fundamental_features_fund_v1_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_monthly_fundamental_features_fund_v1_key ON public.sp500_monthly_fundamental_features USING btree (security_id, month_end);


--
-- Name: sp500_monthly_population_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_monthly_population_key ON public.sp500_monthly_population USING btree (week_end, ticker_latest);


--
-- Name: sp500_population_daily_audit_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX sp500_population_daily_audit_key ON public.sp500_population_daily_audit USING btree (date, security_id);


--
-- Name: ux_ratios_annual_symbol_date_period; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ux_ratios_annual_symbol_date_period ON public.ratios_annual USING btree (symbol, date, period);


--
-- PostgreSQL database dump complete
--
