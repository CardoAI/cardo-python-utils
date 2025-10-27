"""
This module contains choices used also in ESMA reports.

Choices structure:
Example: OVRD = 1, "Overdraft or Working Capital"
    OVRD -> ESMA code for the choice, to be used in reports
    1 -> value stored in database
    "Overdraft or Working Capital" -> human-readable name, used for display purposes

Exceptions:
    There might be cases in which multiple choices are mapped to the same ESMA code.
    In this case, some characters are added at the end of the ESMA code to differentiate it.
    Example:
        GUAR_G1 = 40, "Guarantee"
        GUAR_G2 = 41, "Government Guarantee"
    In such cases, only the part before the underscore (GUAR) (or the first 4 letters) is used in reports.
"""


from python_utils.choices import ChoiceEnum


class FinancialCreditAssetFinancingPurposeChoices(ChoiceEnum):
    # Corporate
    OVRD = 1, "Overdraft or Working Capital"
    EQPI = 2, "New Plant and Equipment Investment"
    INFT = 3, "New Information Technology Investment"
    RFBR = 4, "Refurbishment of Existing Plant, Equipment, or Technology"
    MGAQ = 5, "Merger and Acquisition"
    OEXP = 6, "Other Expansionary Purpose"

    # Consumer
    TUIT = 7, "Tuition"
    LEXP = 8, "Living Expenses"
    MDCL = 9, "Medical"
    HIMP = 10, "Home Improvement"
    APFR = 11, "Appliance or Furniture"
    TRVL = 12, "Travel"
    DCON = 13, "Debt Consolidation"
    NCAR = 14, "New Car"
    UCAR = 15, "Used Car"
    OTHV = 16, "Other Vehicle"
    EQUP = 17, "Equipment"
    PROP = 18, "Property"
    OTHR = 100, "Other"


class InterestRateTypeChoices(ChoiceEnum):
    FLIF = 1, "Floating rate underlying exposure (for life)"
    FINX = 2, "Floating rate underlying exposure linked to one index that will revert to another index in the future"
    FXRL = 3, "Fixed rate underlying exposure (for life)"
    FXPR = 4, "Fixed with future periodic resets"
    FLCF = 5, "Fixed rate underlying exposure with compulsory future switch to floating"
    FLFL = 6, "Floating rate underlying exposure with floor"
    CAPP = 7, "Floating rate underlying exposure with cap)"
    FLCA = 8, "Floating rate underlying exposure with both floor and cap"
    DISC = 9, "Discount"
    SWIC = 10, "Switch Optionality"
    OBLS = 11, "Obligor Swapped"
    MODE = 12, "Modular"
    OTHR = 13, "Other"
    FXRT = 14, "Fixed Rate"


class SeniorityChoices(ChoiceEnum):
    SNDB = 1, "Senior Debt"
    MZZD = 2, "Mezzanine Debt"
    JUND = 3, "Junior Debt"
    SBOD = 4, "Subordinated Debt"
    OTHR = 10, "Other"


class Basel3SegmentChoices(ChoiceEnum):
    CORP = 1, "Corporate"
    SMEX = 2, "Small and Medium Enterprise Treated as Corporate"
    RETL = 3, "Retail"
    OTHR = 10, "Other"


class EmploymentStatusChoices(ChoiceEnum):
    EMRS = 1, "Employed - Private Sector"
    EMBL = 2, "Employed - Public Sector"
    EMUK = 3, "Employed - Sector Unknown"
    UNEM = 4, "Unemployed"
    SFEM = 5, "Self-employed"
    STNT = 6, "Student"
    PNNR = 7, "Pensioner"
    NOEM = 8, "No Employment, Obligor is Legal Entity"
    OTHR = 10, "Other"


class PrimaryIncomeTypeChoices(ChoiceEnum):
    GRAN = 1, "Gross annual income"
    NITS = 2, "Net annual income (net of tax and social security)"
    NITX = 3, "Net annual income (net of tax only)"
    NTIN = 4, "Net annual income (net of social security only)"
    ENIS = 5, "Estimated net annual income (net of tax and social security)"
    EITX = 6, "Estimated net annual income (net of tax only)"
    EISS = 7, "Estimated net annual income (net of social security only)"
    DSPL = 8, "Disposable Income"
    CORP = 9, "Borrower is legal entity"
    OTHR = 10, "Other"


class PrimaryIncomeVerificationChoices(ChoiceEnum):
    SCRT = 1, "Self-certified no Checks"
    SCNF = 2, "Self-certified with Affordability Confirmation"
    VRFD = 3, "Verified"
    NVRF = 4, "Non-Verified Income or Fast Track"
    SCRG = 5, "Credit Bureau Information or Scoring"
    OTHR = 10, "Other"


class RecoverySourceChoices(ChoiceEnum):
    LCOL = 1, "Liquidation of Collateral"
    EGAR = 2, "Enforcement of Guarantees"
    ALEN = 3, "Additional Lending"
    CASR = 4, "Cash Recoveries"
    MIXD = 5, "Mixed"
    OTHR = 10, "Other"


class RealEstateAssetClassChoices(ChoiceEnum):
    OTRE_R1 = 30, "Other Real Estate"
    OTRE_R2 = 31, "Hospitality"
    OTHR_R1 = 32, "Plot of land"
    OTHR_R2 = 33, "Agricultural"
    OTHR_R3 = 34, "Ancillary units"
    CBLD_R1 = 35, "Retail"
    CBLD_R2 = 36, "Office"
    IBLD = 37, "Industrial"
    RBLD = 38, "Residential"
    OTRA = 39, "Other Real Estate Assets"
    PUBX = 91, "Public"
    SSTR = 92, "Self Storage"
    MULF = 93, "Multifamily"
    LEIS = 94, "Leisure"


class GuaranteeAssetClassChoices(ChoiceEnum):
    GUAR_G1 = 40, "Personal Guarantee"
    GUAR_G2 = 41, "Government Guarantee"
    GUAR_G3 = 42, "Bank Guarantee"
    GUAR_G4 = 43, "Corporate Guarantee"
    OTHR_G1 = 44, "Pledge on titles"
    OTHR_G2 = 45, "Pledge on goods or inventory"
    OTHR_G3 = 46, "Pledge on others"
    OTHR_G4 = 47, "Patronage letter"


class ESMAAccountStatusChoices(ChoiceEnum):
    PERF = 1, 'Performing'
    RNAR = 2, 'Restructured - No Arrears'
    RARR = 3, 'Restructured - Arrears'
    DFLT = 4, 'Defaulted according to Article 178 of Regulation (EU) No 575/2013'
    NDFT = 5, "Not defaulted according to Article 178 of Regulation (EU) No 575/2013 but classified as defaulted due ' \
              'to another definition of default being met"
    DTCR = 6, "Defaulted both according to Article 178 of Regulation (EU) No 575/2013 and according to another ' \
              'definition of default being met"
    DADB = 7, 'Defaulted only under another definition of default being met'
    ARRE = 8, 'Arrears'
    REBR = 9, 'Repurchased by Seller – Breach of Representations and Warranties'
    REDF = 10, 'Repurchased by Seller – Defaulted'
    RERE = 11, 'Repurchased by Seller – Restructured'
    RESS = 12, 'Repurchased by Seller – Special Servicing'
    REOT = 13, 'Repurchased by Seller – Other Reason'
    RDMD = 14, 'Redeemed'
    OTHR = 20, 'Other'


class ESMACustomerTypeChoices(ChoiceEnum):
    CNEO = 1, "New customer and not an employee/affiliated with the originator's group"
    CEMO = 2, "New customer and an employee/affiliated with the originator's group"
    CNRO = 3, "New customer and employee/affiliation not recorded"
    ENEO = 4, "Existing customer and not an employee/affiliated with the originator's group"
    EEMO = 5, "Existing customer and an employee/affiliated with the originator's group"
    ENRO = 6, "Existing customer and employee/affiliation not recorded"
    OTHR = 10, "Other"


class ESMAAmortisationTypeChoices(ChoiceEnum):
    FRXX = 1, "French - i.e. Amortisation in which the total amount — principal plus interest — repaid in each " \
              "instalment is the same."
    DEXX = 2, "German - i.e. Amortisation in which the first instalment is interest-only and the remaining " \
              "instalments are constant, including capital amortisation and interest."
    FIXE = 3, "Fixed amortisation schedule - i.e. Amortisation in which the principal amount repaid in each " \
              "instalment is the same."
    BLLT = 4, "Bullet - i.e. Amortisation in which the full principal amount is repaid in the last instalment."
    OTHR = 10, "Other"


class ESMAOriginationChannelChoices(ChoiceEnum):
    BRAN = 1, "Office or Branch Network"
    BROK = 2, "Broker"
    WEBI = 3, "Internet"
    OTHR = 10, "Other"


class ESMASecuritisedReceivablesChoices(ChoiceEnum):
    PRIN = 1, "Principal and Interest"
    PRPL = 2, "Principal Only"
    INTR = 3, "Interest Only"
    OTHR = 10, "Other"


class ESMAReasonForDefaultOrForeclosureChoices(ChoiceEnum):
    UPXX = 1, "In default because the debtor is unlikely to pay, in accordance with Article 178 of Regulation (EU) No " \
              "575/2013."
    PDXX = 2, "In default because any debt is more than 90/180 days past due, in accordance with Article 178 of " \
              "Regulation (EU) No 575/2013."
    UPPD = 3, "In default both because it is considered that the debtor is unlikely to pay and because any debt is " \
              "more than 90/180 days past due, in accordance with Article 178 of Regulation (EU) No 575/2013."


class ChargeTypeChoices(ChoiceEnum):
    FXCH = 1, "Fixed charge"
    FLCH = 2, "Floating charge"
    NOCG = 3, "No charge"
    ATRN = 4, "No charge but an irrevocable power of attorney or similar"
    OTHR = 10, "Other"


class ValuationMethodChoices(ChoiceEnum):
    FAPR = 1, "Full Appraisal"
    DRVB = 2, "Drive-by"
    AUVM = 3, "Automated Value Model"
    IDXD = 4, "Indexed"
    DKTP = 5, "Desktop"
    MAEA = 6, "Managing Agent or Estate Agent"
    PPRI = 7, "Purchase Price"
    HCUT = 8, "Haircut"
    MTTM = 9, "Mark to Market"
    OBLV = 10, "Obligor’s valuation"
    OTHR = 20, "Other"


class InterestRateIndexChoices(ChoiceEnum):
    MAAA = 1, "MuniAAA"
    FUSW = 2, "FutureSWAP"
    LIBI = 3, "LIBID"
    LIBO = 4, "LIBOR"
    SWAP = 5, "SWAP"
    TREA = 6, "Treasury"
    EURI = 7, "Euribor"
    PFAN = 8, "Pfandbriefe"
    EONA = 9, "EONIA"
    EONS = 10, "EONIASwaps"
    EUUS = 11, "EURODOLLAR"
    EUCH = 12, "EuroSwiss"
    TIBO = 13, "TIBOR"
    ISDA = 14, "ISDAFIX"
    GCFR = 15, "GCFRepo"
    STBO = 16, "STIBOR"
    BBSW = 17, "BBSW"
    JIBA = 18, "JIBAR"
    BUBO = 19, "BUBOR"
    CDOR = 20, "CDOR"
    CIBO = 21, "CIBOR"
    MOSP = 22, "MOSPRIM"
    NIBO = 23, "NIBOR"
    PRBO = 24, "PRIBOR"
    TLBO = 25, "TELBOR"
    WIBO = 26, "WIBOR"
    BOER = 27, "Bank of England Base Rate"
    ECBR = 28, "European Central Bank Base Rate"
    LDOR = 29, "Lender's Own Rate"
    OTHR = 30, "Other"
    SOFR = 31, "SOFR"
    SONIA = 32, "SONIA"


class InterestRateIndexTenorChoices(ChoiceEnum):
    OVNG = 1, "Overnight"
    INDA = 2, "IntraDay"
    DAIL = 3, "1 day"
    WEEK = 4, "1 week"
    TOWK = 5, "2 week"
    MNTH = 6, "1 month"
    TOMN = 7, "2 month"
    QUTR = 8, "3 month"
    FOMN = 9, "4 month"
    SEMI = 10, "6 month"
    YEAR = 11, "12 month"
    ONDE = 12, "On Demand"
    OTHR = 13, "Other"


class SPVAssetClassChoices(ChoiceEnum):
    ALOL = 1, "Automobile Loan or Lease"
    CONL = 2, "Consumer Loan"
    CMRT = 3, "Commercial Mortgage"
    CCRR = 4, "Credit-Card Receivable"
    LEAS = 5, "Lease"
    RMRT = 6, "Residential Mortgage"
    MIXD = 7, "Mixed"
    SMEL = 8, "Small and Medium Enterprise"
    NSML = 9, "Non Small and Medium Enterprise Corporate"
    OTHR = 10, "Other"
    TRADE_RECEIVABLES = 11, "Trade Receivables"
    REAL_ESTATE = 12, "Real Estate"
    MERCHANT_CASH_ADVANCES = 13, "Merchant Cash Advances"
    WORKING_CAPITAL_FACILITY = 14, "Working Capital Facility"
    INVENTORY_FINANCING = 15, "Inventory Financing"
    REVENUE_BASED_FINANCING = 16, "Revenue-Based Financing"
    RENTAL_CONTRACT_FINANCING = 17, "Rental Contract Financing"
    NON_PERFORMING_LOAN = 18, "Non-Performing Loan"
    PUBLIC_CLAIMS = 19, "Public Claims"
    CDO = 20, "CDO"
    RECREATIONAL_VEHICLE = 21, "Recreational Vehicle"
    CORPORATE_LOAN = 22, "Corporate Loan"
    BNPL = 23, "BNPL"
    STUDENT_LOAN = 104, "Student Loan"


class SPVWaterfallTypeChoices(ChoiceEnum):
    TRWT = 1, "Turbo Waterfall"
    SQWT = 2, "Sequential Waterfall"
    PRWT = 3, "Pro-rata Waterfall"
    SQPR = 4, "Currently Sequential, with Possibility to Switch to Pro-rata in the Future"
    PRSQ = 5, "Currently Pro-rata, with Possibility to Switch to Sequential in the Future"
    OTHR = 10, "Other"


class SPVRiskRetentionMethodChoices(ChoiceEnum):
    VSLC = 1, "Vertical slice - i.e. Article 6(3)(a)"
    SLLS = 2, "Seller's share - i.e. Article 6(3)(b)"
    RSEX = 3, "Randomly-selected exposures kept on balance sheet - i.e. Article 6(3)(c)"
    FLTR = 4, "First loss tranche - i.e. Article 6(3)(d)"
    FLEX = 5, "First loss exposure in each asset - i.e. Article 6(3)(e)"
    NCOM = 6, "No compliance with risk retention requirements"
    OTHR = 10, "Other"


class SPVRiskRetentionHolderChoices(ChoiceEnum):
    ORIG = 1, "Originator"
    SPON = 2, "Sponsor"
    OLND = 3, "Original Lender"
    SELL = 4, "Seller"
    NCOM = 5, "No Compliance with Risk Retention Requirement"
    OTHR = 10, "Other"


class SPVCashAccountTypeChoices(ChoiceEnum):
    CARE = 1, "Cash Reserve Account"
    CORE = 2, "Commingling Reserve Account"
    SORE = 3, "Set-off Reserve Account"
    LQDF = 4, "Liquidity Facility"
    MGAC = 5, "Margin Account"
    OTHR_1 = 6, "Collection Account"
    OTHR_2 = 10, "Other Account"


class SPVTriggerConsequenceChoices(ChoiceEnum):
    CHPP = 1, "Change in the priority of payments"
    CHCP = 2, "Replacement of a counterparty"
    BOTH = 3, "Both change in the priority of payments and replacement of a counterparty"
    OTHR = 10, "Other consequence"
    TERM = 4, "Termination Event"


class SPVRiskWeightApproachChoices(ChoiceEnum):
    STND = 1, "Standardised Approach"
    FIRB = 2, "Foundation Internal Ratings-Based"
    ADIR = 3, "Advanced Internal Ratings-Based"


class SPVLiabilityAmortizationTypeChoices(ChoiceEnum):
    HBUL = 1, "Hard bullet (i.e. fixed maturity date)"
    SBUL = 2, "Soft bullet (i.e. scheduled maturity date can be extended to the legal maturity date)"
    SAMO = 3, "Scheduled amortisation (i.e. repayment of principal on scheduled amortisation dates)"
    CAMM = 4, "Controlled amortisation (i.e. repayment of principal begins at a specified period)"
    OTHR = 5, "Other"


class SPVCounterpartyTypeChoices(ChoiceEnum):
    ABNK = 1, "Account Bank"
    BABN = 2, "Backup Account Bank"
    ABFC = 3, "Account Bank Facilitator"
    ABGR = 4, "Account Bank Guarantor"
    CAGT = 5, "Collateral Agent"
    PAYA = 6, "Paying Agent"
    CALC = 7, "Calculation Agent"
    ADMI = 8, "Administration Agent"
    ADSA = 9, "Administration Sub-Agent"
    RANA = 10, "Transfer Agent"
    VERI = 11, "Verification agent"
    SECU = 12, "Security agent"
    CAPR = 13, "Cash Advance Provider"
    COLL = 14, "Collateral Provider"
    GICP = 15, "Guaranteed Investment Contract Provider"
    IPCP = 16, "Insurance Policy Credit Provider"
    LQFP = 17, "Liquidity Facility Provider"
    BLQP = 18, "Backup Liquidity Facility Provider"
    SVMP = 19, "Savings Mortgage Participant"
    ISSR = 20, "Issuer"
    ORIG = 21, "Originator"
    SELL = 22, "Seller"
    SSSP = 23, "Sponsor of the Securitisation Special Purpose Entity"
    SERV = 24, "Servicer"
    BSER = 25, "Backup Servicer"
    BSRF = 26, "Backup Servicer Facilitator"
    SSRV = 27, "Special Servicer"
    SUBS = 28, "Subscriber"
    IRSP = 29, "Interest Rate Swap Provider"
    BIPR = 30, "Backup Interest Rate Swap Provider"
    CSPR = 31, "Currency Swap Provider"
    BCSP = 32, "Backup Currency Swap Provider"
    AUDT = 33, "Auditor"
    CNSL = 34, "Counsel"
    TRUS = 35, "Trustee"
    REPN = 36, "Representative of Noteholders"
    UNDR = 37, "Underwriter"
    ARRG = 38, "Arranger"
    DEAL = 39, "Dealer"
    MNGR = 40, "Manager"
    LCPR = 41, "Letter of Credit Provider"
    MSCD = 42, "Multi-Seller Conduit"
    SSPE = 43, "Securitisation Special Purpose Entity"
    LQAG = 44, "Liquidity or Liquidation Agent"
    EQOC = 45, "Equity owner of conduit/SSPE"
    SWNG = 46, "Swingline Facility Provider"
    SULP = 47, "Start-up Loan or Lease Provider"
    RAGC = 48, "Repurchase Agreement Counterparty"
    CASM = 49, "Cash Manager"
    CACB = 50, "Collection Account Bank"
    COLA = 51, "Collateral Account Bank"
    SBLP = 52, "Subordinated Loan Provider"
    CLOM = 53, "Collateralised Loan Obligation Manager"
    PRTA = 54, "Portfolio Advisor"
    SUBA = 55, "Substitution Agent"
    BORR = 56, "Borrower"
    UNDT = 57, "Underlying Trust"
    DPST = 58, "Depositor"
    AGNT = 59, "Agent"
    GENP = 60, "General Partner"
    LIMP = 61, "Limited Partner"
    OTHR = 100, "Other"


class PaymentFrequencyChoices(ChoiceEnum):
    DAIL = 1, "Daily"
    WEEK = 2, "Weekly"
    MNTH = 3, "Monthly"
    QUTR = 4, "Quarterly"
    SEMI = 5, "Semi Annual"
    YEAR = 6, "Annual"
    TWENTY_EIGHT_DAYS = 7, "28 Days"
    BI_WEEKLY = 8, "Bi-Weekly"
    SEMI_MONTHLY = 9, "Semi-Monthly"
    BI_MONTHLY = 11, "Bi-Monthly"
    OTHR = 10, "Other"


class SPVExtensionClauseChoices(ChoiceEnum):
    ISUR = 1, "SSPE only"
    NHLD = 2, "Noteholder"
    ISNH = 3, "Either SSPE or noteholder"
    NOPT = 4, "No option"


class SPVLiabilitySettlementConventionChoice(ChoiceEnum):
    TONE = 1, "T Plus One"
    TTWO = 2, "T Plus Two"
    TTRE = 3, "T Plus Three"
    ASAP = 4, "As soon as possible"
    ENDC = 5, "At the end of Contract"
    MONT = 6, "End of Month"
    FUTU = 7, "Future"
    NXTD = 8, "Next Day"
    REGU = 9, "Regular"
    TFIV = 10, "T Plus Five"
    TFOR = 11, "T Plus Four"
    WHIF = 12, "When and if issued"
    WDIS = 13, "When Distributed"
    WISS = 14, "When Issued"
    WHID = 15, "When Issued or Distributed"
    OTHR = 16, "Other"
