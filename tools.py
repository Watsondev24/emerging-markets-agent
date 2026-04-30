# tools.py
# These are "stubbed" tools - they look like real data sources but return
# realistic fake data. In a real system you'd swap these out for calls to
# the World Bank API, GDELT news API, a regulatory database, etc.
#
# Each tool takes a market name (and optionally a sector) and returns a dict.

import random


def get_macro_indicators(market: str) -> dict:
    """
    Simulates fetching macroeconomic data for a market.
    Real version: World Bank API, IMF Data API, Trading Economics
    """
    # Realistic stub data keyed by market name
    data = {
        "indonesia": {
            "gdp_growth_pct": 5.1,
            "inflation_pct": 2.8,
            "currency": "IDR (Indonesian Rupiah)",
            "currency_stability": "Moderate - has depreciated ~5% vs USD over 2 years",
            "foreign_reserves_usd_bn": 144,
            "trade_balance": "Positive surplus driven by commodity exports",
            "middle_class_growth": "Expanding rapidly, ~52M households",
            "internet_penetration_pct": 77,
            "mobile_penetration_pct": 128,
            "source": "stub:world_bank"
        },
        "nigeria": {
            "gdp_growth_pct": 2.9,
            "inflation_pct": 28.9,
            "currency": "NGN (Naira)",
            "currency_stability": "High volatility - significant devaluation post-2023 reforms",
            "foreign_reserves_usd_bn": 33,
            "trade_balance": "Oil-dependent, vulnerable to commodity cycles",
            "middle_class_growth": "Under pressure due to inflation",
            "internet_penetration_pct": 55,
            "mobile_penetration_pct": 108,
            "source": "stub:world_bank"
        },
        "vietnam": {
            "gdp_growth_pct": 6.4,
            "inflation_pct": 3.5,
            "currency": "VND (Vietnamese Dong)",
            "currency_stability": "Relatively stable, managed float against USD",
            "foreign_reserves_usd_bn": 88,
            "trade_balance": "Strong manufacturing export surplus",
            "middle_class_growth": "One of fastest growing in SE Asia",
            "internet_penetration_pct": 79,
            "mobile_penetration_pct": 141,
            "source": "stub:world_bank"
        },
        "kenya": {
            "gdp_growth_pct": 5.0,
            "inflation_pct": 5.4,
            "currency": "KES (Kenyan Shilling)",
            "currency_stability": "Moderate - recovered after 2023 pressure",
            "foreign_reserves_usd_bn": 7.5,
            "trade_balance": "Deficit, offset by remittances and services",
            "middle_class_growth": "Urbanising quickly, Nairobi tech hub emerging",
            "internet_penetration_pct": 42,
            "mobile_penetration_pct": 119,
            "source": "stub:world_bank"
        },
        "ghana": {
            "gdp_growth_pct": 4.7,
            "inflation_pct": 23.1,
            "currency": "GHS (Ghanaian Cedi)",
            "currency_stability": "Recovering after 2022-23 debt crisis and IMF bailout",
            "foreign_reserves_usd_bn": 6.8,
            "trade_balance": "Gold and cocoa exports provide base",
            "middle_class_growth": "Modest, concentrated in Accra",
            "internet_penetration_pct": 58,
            "mobile_penetration_pct": 132,
            "source": "stub:world_bank"
        },
        "bangladesh": {
            "gdp_growth_pct": 5.8,
            "inflation_pct": 9.7,
            "currency": "BDT (Bangladeshi Taka)",
            "currency_stability": "Moderate pressure, forex reserves constrained",
            "foreign_reserves_usd_bn": 21,
            "trade_balance": "Garment exports dominant, remittances key",
            "middle_class_growth": "Growing rapidly off large population base",
            "internet_penetration_pct": 40,
            "mobile_penetration_pct": 109,
            "source": "stub:world_bank"
        },
    }

    # Normalise market name to lowercase for lookup
    key = market.lower().strip()

    if key in data:
        return data[key]

    # Generic fallback for markets not in our stub
    return {
        "gdp_growth_pct": round(random.uniform(2.5, 6.5), 1),
        "inflation_pct": round(random.uniform(3.0, 18.0), 1),
        "currency": f"Local currency of {market}",
        "currency_stability": "Data not available in stub - would query World Bank API",
        "foreign_reserves_usd_bn": round(random.uniform(5, 80), 1),
        "trade_balance": "Data not available in stub",
        "middle_class_growth": "Data not available in stub",
        "internet_penetration_pct": round(random.uniform(30, 80)),
        "mobile_penetration_pct": round(random.uniform(70, 140)),
        "source": "stub:fallback"
    }


def get_political_risk(market: str) -> dict:
    """
    Simulates fetching political risk and governance data.
    Real version: World Bank Governance Indicators, ICRG, Control Risks API
    """
    data = {
        "indonesia": {
            "political_stability_score": 65,   # out of 100, higher = more stable
            "governance_quality": "Moderate - democratic consolidation ongoing",
            "corruption_index": 34,             # Transparency International CPI (higher = cleaner)
            "regulatory_quality": "Improving but bureaucratic",
            "rule_of_law_score": 55,
            "recent_developments": [
                "Prabowo administration took office Oct 2024, continuity expected",
                "Resource nationalism trends in mining sector",
                "Anti-corruption drive ongoing under KPK"
            ],
            "sanctions_risk": "Low - no major international sanctions",
            "expropriation_risk": "Low to moderate",
            "source": "stub:world_bank_governance"
        },
        "nigeria": {
            "political_stability_score": 38,
            "governance_quality": "Weak - significant structural challenges",
            "corruption_index": 25,
            "regulatory_quality": "Poor, improving slowly under reform agenda",
            "rule_of_law_score": 33,
            "recent_developments": [
                "Tinubu government pursuing IMF-backed reforms including fuel subsidy removal",
                "Security concerns in north, Niger Delta",
                "Significant FX reform underway - naira float introduced"
            ],
            "sanctions_risk": "Low at country level, individual entity risk exists",
            "expropriation_risk": "Moderate",
            "source": "stub:world_bank_governance"
        },
        "vietnam": {
            "political_stability_score": 72,
            "governance_quality": "Strong by regional standards - single party stability",
            "corruption_index": 41,
            "regulatory_quality": "Improving, Doi Moi legacy of reform continues",
            "rule_of_law_score": 58,
            "recent_developments": [
                "Anti-corruption 'Blazing Furnace' campaign ongoing",
                "Leadership transition completed, policy continuity maintained",
                "Strong FDI inflows from supply chain diversification"
            ],
            "sanctions_risk": "Low",
            "expropriation_risk": "Low",
            "source": "stub:world_bank_governance"
        },
        "kenya": {
            "political_stability_score": 55,
            "governance_quality": "Moderate - multiparty democracy with periodic tension",
            "corruption_index": 31,
            "regulatory_quality": "Moderate, CBK and CMA are credible regulators",
            "rule_of_law_score": 50,
            "recent_developments": [
                "2024 protests led to cabinet reshuffles, political uncertainty elevated",
                "IMF programme ongoing, fiscal consolidation required",
                "Regional hub status for East Africa maintained"
            ],
            "sanctions_risk": "Low",
            "expropriation_risk": "Low to moderate",
            "source": "stub:world_bank_governance"
        },
        "ghana": {
            "political_stability_score": 62,
            "governance_quality": "Good by African standards - peaceful power transfers",
            "corruption_index": 43,
            "regulatory_quality": "Improving, BoG is respected regulator",
            "rule_of_law_score": 57,
            "recent_developments": [
                "John Mahama won Dec 2024 election, policy continuity expected",
                "IMF Extended Credit Facility programme on track",
                "Debt restructuring largely completed"
            ],
            "sanctions_risk": "Low",
            "expropriation_risk": "Low",
            "source": "stub:world_bank_governance"
        },
        "bangladesh": {
            "political_stability_score": 42,
            "governance_quality": "Transitional - interim government post-2024 revolution",
            "corruption_index": 24,
            "regulatory_quality": "Weak but Bangladesh Bank has credibility",
            "rule_of_law_score": 38,
            "recent_developments": [
                "Sheikh Hasina ousted Aug 2024, Yunus-led interim government in place",
                "Political uncertainty elevated in short term",
                "Garment sector and remittances provide economic anchor"
            ],
            "sanctions_risk": "Low",
            "expropriation_risk": "Moderate under current transition",
            "source": "stub:world_bank_governance"
        },
    }

    key = market.lower().strip()

    if key in data:
        return data[key]

    return {
        "political_stability_score": round(random.uniform(30, 70)),
        "governance_quality": "Data not available in stub",
        "corruption_index": round(random.uniform(20, 55)),
        "regulatory_quality": "Data not available in stub",
        "rule_of_law_score": round(random.uniform(30, 65)),
        "recent_developments": ["Stub data - would query GDELT / news APIs"],
        "sanctions_risk": "Requires manual check",
        "expropriation_risk": "Requires manual assessment",
        "source": "stub:fallback"
    }


def get_sector_data(market: str, sector: str) -> dict:
    """
    Simulates fetching sector-specific market data.
    Real version: GSMA Intelligence, Statista, CB Insights, sector-specific APIs
    """
    sector_lower = sector.lower()

    # Fintech / payments
    if any(kw in sector_lower for kw in ["fintech", "payment", "financial"]):
        return {
            "sector": "Fintech / Digital Payments",
            "market_size_usd_bn": _market_lookup(market, {
                "indonesia": 1.8, "nigeria": 1.2, "vietnam": 0.9,
                "kenya": 0.7, "ghana": 0.15, "bangladesh": 0.4
            }, default=0.3),
            "cagr_pct": _market_lookup(market, {
                "indonesia": 23, "nigeria": 18, "vietnam": 28,
                "kenya": 21, "ghana": 19, "bangladesh": 26
            }, default=20),
            "mobile_money_users_millions": _market_lookup(market, {
                "indonesia": 30, "nigeria": 45, "vietnam": 12,
                "kenya": 38, "ghana": 18, "bangladesh": 22
            }, default=10),
            "banked_population_pct": _market_lookup(market, {
                "indonesia": 52, "nigeria": 45, "vietnam": 69,
                "kenya": 58, "ghana": 61, "bangladesh": 53
            }, default=40),
            "key_players": _market_lookup(market, {
                "indonesia": ["GoPay", "OVO", "Dana", "BCA Mobile"],
                "nigeria": ["OPay", "Flutterwave", "Paystack", "Interswitch"],
                "vietnam": ["MoMo", "ZaloPay", "ViettelPay"],
                "kenya": ["M-Pesa (Safaricom)", "Airtel Money", "Equity Bank"],
                "ghana": ["MTN MoMo", "AirtelTigo Money", "Zeepay"],
                "bangladesh": ["bKash", "Nagad", "Rocket"]
            }, default=["Local incumbents", "Regional players"]),
            "key_growth_drivers": [
                "Large unbanked/underbanked population",
                "High mobile penetration vs low bank branch density",
                "Government push for digital financial inclusion",
                "Young, tech-savvy demographic"
            ],
            "source": "stub:gsma_statista"
        }

    # Telecoms / infrastructure
    elif any(kw in sector_lower for kw in ["teleco", "tower", "infrastructure", "network"]):
        return {
            "sector": "Telecoms Infrastructure",
            "tower_count": _market_lookup(market, {
                "indonesia": 98000, "nigeria": 45000, "vietnam": 62000,
                "kenya": 10000, "ghana": 7200, "bangladesh": 35000
            }, default=15000),
            "tower_sharing_ratio": "1.5x avg (opportunity to increase to 2.0x+)",
            "market_size_usd_bn": _market_lookup(market, {
                "indonesia": 3.2, "nigeria": 1.8, "vietnam": 2.1,
                "kenya": 0.6, "ghana": 0.3, "bangladesh": 0.9
            }, default=0.5),
            "cagr_pct": _market_lookup(market, {
                "indonesia": 8, "nigeria": 12, "vietnam": 11,
                "kenya": 9, "ghana": 10, "bangladesh": 13
            }, default=9),
            "key_players": ["IHS Towers", "American Tower Corp", "Helios Towers", "Local MNOs"],
            "key_growth_drivers": [
                "4G/5G rollout requires densification",
                "MNOs monetising tower assets via sale-leaseback",
                "Data demand growing 30%+ annually",
                "Rural coverage mandates from regulators"
            ],
            "source": "stub:towerxchange"
        }

    # E-commerce / retail
    elif any(kw in sector_lower for kw in ["ecommerce", "e-commerce", "retail", "digital retail"]):
        return {
            "sector": "E-commerce & Digital Retail",
            "market_size_usd_bn": _market_lookup(market, {
                "indonesia": 62, "nigeria": 12, "vietnam": 22,
                "kenya": 1.5, "ghana": 0.8, "bangladesh": 3.5
            }, default=2),
            "cagr_pct": _market_lookup(market, {
                "indonesia": 19, "nigeria": 22, "vietnam": 24,
                "kenya": 18, "ghana": 20, "bangladesh": 27
            }, default=20),
            "ecommerce_penetration_pct": _market_lookup(market, {
                "indonesia": 22, "nigeria": 8, "vietnam": 18,
                "kenya": 6, "ghana": 4, "bangladesh": 9
            }, default=7),
            "key_players": _market_lookup(market, {
                "indonesia": ["Tokopedia/TikTok Shop", "Shopee", "Lazada", "Bukalapak"],
                "nigeria": ["Jumia", "Konga", "Flutterwave Storefront"],
                "vietnam": ["Shopee", "Lazada", "Tiki", "Sendo"],
                "kenya": ["Jumia", "Kilimall", "Copia"],
                "ghana": ["Jumia", "Tonaton", "Reapp"],
                "bangladesh": ["Chaldal", "Shajgoj", "Pathao"]
            }, default=["Jumia (Africa)", "Shopee (Asia)", "Local players"]),
            "key_growth_drivers": [
                "Rising smartphone adoption",
                "Improved last-mile logistics",
                "Digital payments infrastructure maturing",
                "Covid-era online shopping habits retained"
            ],
            "source": "stub:statista_ecommerce"
        }

    # Energy / renewables
    elif any(kw in sector_lower for kw in ["energy", "renewable", "solar", "power"]):
        return {
            "sector": "Renewable Energy",
            "installed_capacity_gw": _market_lookup(market, {
                "indonesia": 13, "nigeria": 1.2, "vietnam": 21,
                "kenya": 2.9, "ghana": 0.8, "bangladesh": 0.9
            }, default=1),
            "market_size_usd_bn": _market_lookup(market, {
                "indonesia": 4.5, "nigeria": 2.0, "vietnam": 5.1,
                "kenya": 1.2, "ghana": 0.6, "bangladesh": 1.4
            }, default=0.8),
            "cagr_pct": _market_lookup(market, {
                "indonesia": 16, "nigeria": 24, "vietnam": 19,
                "kenya": 14, "ghana": 18, "bangladesh": 22
            }, default=17),
            "electrification_rate_pct": _market_lookup(market, {
                "indonesia": 99, "nigeria": 57, "vietnam": 99,
                "kenya": 75, "ghana": 88, "bangladesh": 95
            }, default=70),
            "key_players": ["Total Energies", "Scaling Solar (IFC)", "PowerGen", "Regional IPPs"],
            "key_growth_drivers": [
                "Grid reliability issues driving off-grid/mini-grid demand",
                "Falling solar panel costs making projects bankable",
                "Government renewable targets and feed-in tariffs",
                "Multilateral financing (AfDB, IFC, AIIB) available"
            ],
            "source": "stub:irena_data"
        }

    # Generic / lending / credit
    else:
        return {
            "sector": sector,
            "market_size_usd_bn": round(random.uniform(0.5, 5.0), 1),
            "cagr_pct": round(random.uniform(12, 28)),
            "penetration_pct": round(random.uniform(5, 35)),
            "key_players": ["Incumbent local players", "Regional challengers", "Global entrants"],
            "key_growth_drivers": [
                "Rising middle class and consumer spending",
                "Digital infrastructure improving access",
                "Regulatory environment gradually opening",
                "Demographic dividend (young population)"
            ],
            "source": "stub:generic"
        }


def get_regulatory_environment(market: str, sector: str) -> dict:
    """
    Simulates fetching regulatory and compliance data.
    Real version: LexisNexis, local bar association databases, regulatory body APIs
    """
    sector_lower = sector.lower()

    fdi_limits = {
        "indonesia": "Max 49-85% foreign ownership depending on sector (negative investment list)",
        "nigeria": "Generally 100% foreign ownership permitted, sector exceptions apply",
        "vietnam": "51-100% depending on sector; fintech may require local JV partner",
        "kenya": "Generally open to foreign investment, CBK approval required for financial services",
        "ghana": "Generally open; Bank of Ghana approval required for financial sector",
        "bangladesh": "100% FDI permitted in most sectors; Bangladesh Bank approval for financial services",
    }

    key = market.lower().strip()

    if "fintech" in sector_lower or "payment" in sector_lower:
        return {
            "fdi_ownership_limit": fdi_limits.get(key, "Requires local legal review"),
            "primary_regulator": _market_lookup(market, {
                "indonesia": "Bank Indonesia (BI) + OJK (Financial Services Authority)",
                "nigeria": "Central Bank of Nigeria (CBN)",
                "vietnam": "State Bank of Vietnam (SBV)",
                "kenya": "Central Bank of Kenya (CBK)",
                "ghana": "Bank of Ghana (BoG)",
                "bangladesh": "Bangladesh Bank + BFIU"
            }, default="Central Bank (requires local legal advice)"),
            "key_licences_required": [
                "Payment System Operator (PSO) licence",
                "Electronic Money Issuer (EMI) licence (if holding customer funds)",
                "AML/KYC registration",
                "Data protection registration"
            ],
            "data_localisation": _market_lookup(market, {
                "indonesia": "Required - data must be stored on local servers",
                "nigeria": "CBN requires local storage of Nigerian customer data",
                "vietnam": "Strict data localisation under Cybersecurity Law 2019",
                "kenya": "Data Protection Act 2019 - consent required, some localisation",
                "ghana": "Data Protection Act - moderate requirements",
                "bangladesh": "Emerging framework, local storage preferred"
            }, default="Requires local legal review"),
            "typical_licence_timeline_months": _market_lookup(market, {
                "indonesia": "12-18", "nigeria": "9-15", "vietnam": "12-24",
                "kenya": "6-12", "ghana": "6-12", "bangladesh": "12-18"
            }, default="12-18"),
            "recent_regulatory_changes": [
                "Open banking frameworks being developed across most markets",
                "CBDC pilots underway in several jurisdictions",
                "Tightening AML/CFT requirements post-FATF reviews"
            ],
            "source": "stub:regulatory_db"
        }

    elif "teleco" in sector_lower or "tower" in sector_lower:
        return {
            "fdi_ownership_limit": fdi_limits.get(key, "Requires local legal review"),
            "primary_regulator": _market_lookup(market, {
                "indonesia": "Ministry of Communication + BRTI",
                "nigeria": "Nigerian Communications Commission (NCC)",
                "vietnam": "Ministry of Information and Communications (MIC)",
                "kenya": "Communications Authority of Kenya (CA)",
                "ghana": "National Communications Authority (NCA)",
                "bangladesh": "Bangladesh Telecommunication Regulatory Commission (BTRC)"
            }, default="National Telecoms Regulator"),
            "key_licences_required": [
                "Tower/infrastructure provider registration",
                "Right-of-way approvals (municipal level)",
                "Environmental and building permits",
                "Frequency licence (if active equipment)"
            ],
            "data_localisation": "Not primary concern for passive tower infrastructure",
            "typical_licence_timeline_months": "6-12 for tower registration; site permits ongoing",
            "recent_regulatory_changes": [
                "Several markets mandating infrastructure sharing to reduce duplication",
                "5G spectrum allocation accelerating",
                "Some markets imposing local ownership requirements"
            ],
            "source": "stub:regulatory_db"
        }

    else:
        return {
            "fdi_ownership_limit": fdi_limits.get(key, "Requires local legal review"),
            "primary_regulator": "Sector regulator (requires local legal advice)",
            "key_licences_required": [
                "Business registration with companies registry",
                "Sector-specific operating licence",
                "Tax registration (VAT, corporate)",
                "Employment / work permit approvals"
            ],
            "data_localisation": "Emerging data protection laws in most markets - review required",
            "typical_licence_timeline_months": "6-18",
            "recent_regulatory_changes": [
                "Most markets actively courting FDI with improved frameworks",
                "Digital economy regulations evolving rapidly"
            ],
            "source": "stub:regulatory_db"
        }


# --- Helper ---

def _market_lookup(market: str, lookup: dict, default):
    """Helper to look up a value by normalised market name."""
    return lookup.get(market.lower().strip(), default)
