"""Reference registry. One source of truth for notebooks, references.md and paper_catalog.csv.

verified = True means the bibliographic record was checked against at least one
independent index or the official publisher page through web search on VERIFIED_ON.
It does not mean every claim in a notebook was checked against the full text.
Entries with verified = False must be checked before anyone cites them.
"""

VERIFIED_ON = "2026-11-25"


def ref(key, kind, title, authors, year, venue, link, verified, source, contribution, status="current"):
    return {
        "key": key,
        "kind": kind,
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "link": link,
        "verified": verified,
        "source": source,
        "contribution": contribution,
        "status": status,
    }


REFS = {
    "kupiec1995": ref(
        "kupiec1995", "academic",
        "Techniques for verifying the accuracy of risk measurement models",
        "Kupiec, P. H.", 1995,
        "Finance and Economics Discussion Series 95-24, Board of Governors of the Federal Reserve System",
        "https://fraser.stlouisfed.org/title/1491/item/717921", True,
        "Fed FRASER and EconPapers records, web search " + VERIFIED_ON,
        "Introduces the proportion of failures likelihood ratio test for VaR exceptions and discusses its low power on short samples. The Journal of Derivatives version was not checked.",
    ),
    "christoffersen1998": ref(
        "christoffersen1998", "academic",
        "Evaluating interval forecasts",
        "Christoffersen, P. F.", 1998,
        "International Economic Review 39(4):841-862",
        "https://doi.org/10.2307/2527341", True,
        "RePEc IDEAS and EconPapers records, web search " + VERIFIED_ON,
        "Defines unconditional coverage, independence and conditional coverage tests for interval forecasts. VaR exceptions are a special case.",
    ),
    "artzner1999": ref(
        "artzner1999", "academic",
        "Coherent measures of risk",
        "Artzner, P., Delbaen, F., Eber, J.-M. and Heath, D.", 1999,
        "Mathematical Finance 9(3):203-228",
        "https://doi.org/10.1111/1467-9965.00068", True,
        "RePEc IDEAS and EconPapers records, web search " + VERIFIED_ON,
        "States the axioms of a coherent risk measure and discusses why quantile based measures such as VaR can fail subadditivity.",
    ),
    "acerbi2002": ref(
        "acerbi2002", "academic",
        "On the coherence of expected shortfall",
        "Acerbi, C. and Tasche, D.", 2002,
        "Journal of Banking & Finance 26(7):1487-1503",
        "https://econpapers.repec.org/RePEc:eee:jbfina:v:26:y:2002:i:7:p:1487-1503", True,
        "EconPapers and arXiv records, web search " + VERIFIED_ON,
        "Compares definitions of expected shortfall and shows which one is coherent for any loss distribution, including discrete ones.",
    ),
    "rockafellar2000": ref(
        "rockafellar2000", "academic",
        "Optimization of conditional value-at-risk",
        "Rockafellar, R. T. and Uryasev, S.", 2000,
        "Journal of Risk 2, pp. 21-42 (indexes disagree on the last page)",
        "https://www.risk.net/journal-risk/2161159/optimization-conditional-value-risk", True,
        "Risk.net, EconPapers and author PDF, web search " + VERIFIED_ON,
        "Introduces CVaR minimisation through linear programming. CVaR is the same quantity as ES for continuous losses.",
    ),
    "bollerslev1986": ref(
        "bollerslev1986", "academic",
        "Generalized autoregressive conditional heteroskedasticity",
        "Bollerslev, T.", 1986,
        "Journal of Econometrics 31(3):307-327",
        "https://doi.org/10.1016/0304-4076(86)90063-1", True,
        "Duke Scholars, RePEc IDEAS, web search " + VERIFIED_ON,
        "Defines the GARCH model for time varying variance. This repository uses it to generate synthetic returns with volatility clustering.",
    ),
    "nolde2017": ref(
        "nolde2017", "academic",
        "Elicitability and backtesting: Perspectives for banking regulation",
        "Nolde, N. and Ziegel, J. F.", 2017,
        "The Annals of Applied Statistics 11(4):1833-1874",
        "https://doi.org/10.1214/17-AOAS1041", True,
        "Project Euclid, web search " + VERIFIED_ON,
        "Compares traditional backtests with comparative backtests for VaR and ES, and discusses elicitability.",
    ),
    "acerbi2014": ref(
        "acerbi2014", "academic",
        "Backtesting expected shortfall",
        "Acerbi, C. and Szekely, B.", 2014,
        "Risk Magazine, December 2014, pp. 76-81",
        None, True,
        "Existence confirmed through the reference list of Nolde and Ziegel (2017). The article itself was not opened.",
        "Proposes ES backtest statistics. The Z1 diagnostic in this repository follows the idea in simplified form and is not their full test.",
    ),
    "lessmann2015": ref(
        "lessmann2015", "academic",
        "Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research",
        "Lessmann, S., Baesens, B., Seow, H.-V. and Thomas, L. C.", 2015,
        "European Journal of Operational Research 247(1):124-136",
        "https://doi.org/10.1016/j.ejor.2015.05.030", True,
        "RePEc IDEAS, dblp and library records, web search " + VERIFIED_ON,
        "Large benchmark of 41 classifiers on eight real credit scoring data sets, with several accuracy indicators and a financial impact view.",
    ),
    "gunnarsson2021": ref(
        "gunnarsson2021", "academic",
        "Deep learning for credit scoring: Do or don't?",
        "Gunnarsson, B. R., vanden Broucke, S., Baesens, B., Óskarsdóttir, M. and Lemahieu, W.", 2021,
        "European Journal of Operational Research 295(1):292-305",
        "https://doi.org/10.1016/j.ejor.2021.03.006", True,
        "RePEc IDEAS, dblp and library records, web search " + VERIFIED_ON,
        "Compares deep learning with conventional and ensemble credit scoring methods. The authors conclude deep learning looks inappropriate there and that XGBoost is preferred when classification performance is the main goal.",
    ),
    "bcbs_d424": ref(
        "bcbs_d424", "regulatory",
        "Basel III: Finalising post-crisis reforms (BCBS d424)",
        "Basel Committee on Banking Supervision", 2017,
        "Bank for International Settlements, 7 December 2017, consolidated into the Basel Framework",
        "https://www.bis.org/bcbs/publ/d424.htm", True,
        "BIS page, web search " + VERIFIED_ON,
        "Finalises the Basel III reforms, including the revised standardised approach for credit risk.",
        status="integrated into the consolidated Basel Framework",
    ),
    "bcbs_d457": ref(
        "bcbs_d457", "regulatory",
        "Minimum capital requirements for market risk (BCBS d457)",
        "Basel Committee on Banking Supervision", 2019,
        "Bank for International Settlements, 14 January 2019 (rev. February 2019), consolidated into the Basel Framework",
        "https://www.bis.org/bcbs/publ/d457.htm", True,
        "BIS page, web search " + VERIFIED_ON,
        "Revised market risk framework. The internal models approach uses expected shortfall, and the standard supersedes the January 2016 version (d352).",
        status="integrated into the consolidated Basel Framework",
    ),
    "ifrs9": ref(
        "ifrs9", "regulatory",
        "IFRS 9 Financial Instruments, Section 5.5 Impairment",
        "IASB, IFRS Foundation", 2014,
        "Effective for annual periods beginning on or after 1 January 2018",
        "https://www.ifrs.org/content/dam/ifrs/publications/html-standards/english/2026/issued/ifrs9-ie.html", True,
        "IFRS Foundation illustrative examples page and IASB staff paper, web search " + VERIFIED_ON + ". The link opens the illustrative examples that accompany the standard. Paragraph numbers were not checked.",
        "Sets the expected credit loss model: 12 month ECL when credit risk has not increased significantly, lifetime ECL after a significant increase, and lifetime ECL for credit impaired assets.",
    ),
    "iasb_pir2024": ref(
        "iasb_pir2024", "regulatory",
        "Post-implementation Review of IFRS 9 Impairment: summary of feedback and the IASB's responses",
        "IFRS Foundation Trustees, Due Process Oversight Committee staff paper", 2024,
        "Agenda reference 1C, June 2024",
        "https://cdn.ifrs.org/content/dam/ifrs/meetings/2024/june/dpoc/ap1c-pir-impairment.pdf", True,
        "IFRS Foundation document, web search " + VERIFIED_ON,
        "Recent official review of how the IFRS 9 impairment model works in practice. Useful for judgement areas such as staging.",
    ),
    "sr117": ref(
        "sr117", "regulatory",
        "SR 11-7: Supervisory Guidance on Model Risk Management",
        "Board of Governors of the Federal Reserve System and OCC", 2011,
        "4 April 2011 (OCC Bulletin 2011-12)",
        "https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm", True,
        "Federal Reserve page, web search " + VERIFIED_ON,
        "Long standing US guidance on model development, validation and governance. It has been superseded, see SR 26-2.",
        status="superseded by SR 26-2 (17 April 2026)",
    ),
    "sr262": ref(
        "sr262", "regulatory",
        "SR 26-2: Revised Guidance on Model Risk Management",
        "Federal Reserve, OCC and FDIC", 2026,
        "17 April 2026, supersedes SR 11-7 and SR 21-8",
        "https://www.federalreserve.gov/supervisionreg/srletters/sr2602.htm", True,
        "Federal Reserve page, fetched " + VERIFIED_ON,
        "Current US model risk guidance with a risk based approach. The letter says it is most relevant to organisations above 30 billion dollars in assets and states no effective date.",
    ),
    "hull_rmfi": ref(
        "hull_rmfi", "book",
        "Risk Management and Financial Institutions",
        "Hull, J. C.", None,
        "Wiley (edition not fixed in this repository)",
        None, False,
        "Not verified in the build environment.",
        "Standard textbook treatment of duration, convexity, VaR, ES and bank regulation.",
    ),
    "siddiqi2006": ref(
        "siddiqi2006", "book",
        "Credit Risk Scorecards: Developing and Implementing Intelligent Credit Scoring",
        "Siddiqi, N.", 2006,
        "Wiley",
        None, False,
        "Not verified in the build environment.",
        "Practitioner reference for weight of evidence binning, information value rules of thumb and score scaling.",
    ),
    "jorion_var": ref(
        "jorion_var", "book",
        "Value at Risk: The New Benchmark for Managing Financial Risk",
        "Jorion, P.", None,
        "McGraw-Hill (3rd edition, year not verified)",
        None, False,
        "Not verified in the build environment.",
        "Practitioner reference for historical, parametric and Monte Carlo VaR and for backtesting.",
    ),
}


# DOI records matched with the Crossref API on VERIFIED_ON. The check compared title, authors,
# journal, year, volume and issue. Page ranges were not compared for every record.
DOIS = {
    "kupiec1995": ("10.3905/jod.1995.407942", "DOI is the Journal of Derivatives version. The link in the registry is the Fed working paper."),
    "christoffersen1998": ("10.2307/2527341", ""),
    "artzner1999": ("10.1111/1467-9965.00068", ""),
    "acerbi2002": ("10.1016/S0378-4266(02)00283-2", ""),
    "rockafellar2000": ("10.21314/JOR.2000.038", "Crossref gives pages 21 to 41, registry says 21 to 42."),
    "bollerslev1986": ("10.1016/0304-4076(86)90063-1", ""),
    "nolde2017": ("10.1214/17-AOAS1041", "Crossref record shows no page range."),
    "lessmann2015": ("10.1016/j.ejor.2015.05.030", ""),
    "gunnarsson2021": ("10.1016/j.ejor.2021.03.006", ""),
}


def doi_of(key):
    return DOIS[key][0] if key in DOIS else ""


def doi_note(key):
    return DOIS[key][1] if key in DOIS else ""


def get(keys):
    """Return reference records for a list of keys."""
    return [REFS[key] for key in keys]


def link_text(record):
    if record["link"]:
        return record["link"]
    return "no link, verify before citing"


def verification_text(record):
    if record["verified"]:
        return "verified: " + record["source"]
    return "NOT VERIFIED: " + record["source"]
