"""
examples/event_database.py - Database of 35 Real-World Decisions for SERAA Evaluation

Comprehensive collection of historical and contemporary decisions across:
- Government/Policy (10)
- Corporate (10)
- Technology (8)
- Healthcare (7)
"""

from typing import List
from real_world_evaluator import RealWorldEvent


class EventDatabase:
    """Database of real-world events for SERAA evaluation."""
    
    def __init__(self):
        self.events: List[RealWorldEvent] = []
        self._load_all_events()
    
    def _load_all_events(self):
        """Load all events into database."""
        self.events.extend(self._government_events())
        self.events.extend(self._corporate_events())
        self.events.extend(self._technology_events())
        self.events.extend(self._healthcare_events())
    
    def get_by_domain(self, domain: str) -> List[RealWorldEvent]:
        """Get events filtered by domain."""
        domain_map = {
            'government': ['U.S. President', 'Congress', 'Supreme Court', 'U.K. Parliament'],
            'corporate': ['Company', 'Corporation', 'Inc.', 'CEO'],
            'technology': ['Tech', 'Facebook', 'Google', 'Apple', 'Twitter', 'Amazon'],
            'healthcare': ['Hospital', 'CDC', 'FDA', 'Healthcare', 'Pharmaceutical']
        }
        
        keywords = domain_map.get(domain, [])
        return [e for e in self.events if any(k in e.actor for k in keywords)]
    
    def get_by_pac_range(self, min_pac: float, max_pac: float) -> List[RealWorldEvent]:
        """Get events by PAC score range."""
        return [e for e in self.events 
                if min_pac <= e.outcomes.get('pac_score', 0) <= max_pac]
    
    def get_all(self) -> List[RealWorldEvent]:
        """Get all events."""
        return self.events
    
    # ========================================================================
    # GOVERNMENT & POLICY DECISIONS (10)
    # ========================================================================
    
    def _government_events(self) -> List[RealWorldEvent]:
        """Government and policy decisions."""
        return [
            # 1. Travel Ban (2017)
            RealWorldEvent(
                title="Executive Order 13769 (Travel Ban)",
                actor="U.S. President Donald Trump",
                date="January 27, 2017",
                description="Executive order restricting entry from seven Muslim-majority countries.",
                context="National security cited; sudden implementation without agency consultation.",
                stakeholders=["Visa holders", "Refugees", "U.S. citizens with family abroad", "Immigration officials"],
                decision_made="Immediate ban on entry from 7 countries",
                alternatives_available=[
                    "Enhanced vetting without blanket ban",
                    "Gradual implementation with consultation",
                    "Country-specific risk assessment"
                ],
                outcomes={
                    'transparency': 0.2,
                    'consent_obtained': False,
                    'agency_preserved': 0.1,
                    'harm_level': 3,
                    'pac_score': 0.15
                },
                source_urls=["https://en.wikipedia.org/wiki/Executive_Order_13769"]
            ),
            
            # 2. Affordable Care Act (2010)
            RealWorldEvent(
                title="Affordable Care Act (ACA)",
                actor="U.S. President Barack Obama & Congress",
                date="March 23, 2010",
                description="Healthcare reform expanding insurance access with individual mandate.",
                context="Addressing healthcare access crisis through comprehensive legislative reform.",
                stakeholders=["Uninsured Americans", "Insurance companies", "Healthcare providers", "Employers"],
                decision_made="Implement comprehensive healthcare reform",
                alternatives_available=[
                    "Single-payer system",
                    "Public option",
                    "Incremental reforms",
                    "State-level solutions"
                ],
                outcomes={
                    'transparency': 0.7,
                    'consent_obtained': True,
                    'agency_preserved': 0.75,
                    'harm_level': 0,
                    'pac_score': 0.80
                },
                source_urls=["https://en.wikipedia.org/wiki/Affordable_Care_Act"]
            ),
            
            # 3. Citizens United v. FEC (2010)
            RealWorldEvent(
                title="Citizens United v. Federal Election Commission",
                actor="U.S. Supreme Court",
                date="January 21, 2010",
                description="Ruling that political spending is protected free speech, allowing unlimited corporate donations.",
                context="Corporate spending in elections; first amendment considerations.",
                stakeholders=["Voters", "Corporations", "Political candidates", "Democracy advocates"],
                decision_made="Allow unlimited independent political expenditures by corporations",
                alternatives_available=[
                    "Maintain spending limits",
                    "Require disclosure without limits",
                    "Public financing alternative"
                ],
                outcomes={
                    'transparency': 0.4,
                    'consent_obtained': False,
                    'agency_preserved': 0.3,
                    'harm_level': 2,
                    'pac_score': 0.35
                },
                source_urls=["https://en.wikipedia.org/wiki/Citizens_United_v._FEC"]
            ),
            
            # 4. GDPR Implementation (2018)
            RealWorldEvent(
                title="General Data Protection Regulation (GDPR)",
                actor="European Union",
                date="May 25, 2018",
                description="Comprehensive data privacy regulation giving users control over personal data.",
                context="Response to data privacy concerns; harmonizing EU data protection.",
                stakeholders=["EU citizens", "Tech companies", "Data processors", "Advertisers"],
                decision_made="Implement strict data privacy rules with user consent requirements",
                alternatives_available=[
                    "Industry self-regulation",
                    "Voluntary guidelines",
                    "National-level regulations only"
                ],
                outcomes={
                    'transparency': 0.9,
                    'consent_obtained': True,
                    'agency_preserved': 0.90,
                    'harm_level': 0,
                    'pac_score': 0.92
                },
                source_urls=["https://en.wikipedia.org/wiki/General_Data_Protection_Regulation"]
            ),
            
            # 5. Iraq War Authorization (2002)
            RealWorldEvent(
                title="Authorization for Use of Military Force Against Iraq",
                actor="U.S. Congress",
                date="October 16, 2002",
                description="Congressional authorization for military action against Iraq based on WMD claims.",
                context="Post-9/11; claims of weapons of mass destruction later proven false.",
                stakeholders=["U.S. military", "Iraqi civilians", "U.S. citizens", "International community"],
                decision_made="Authorize military invasion of Iraq",
                alternatives_available=[
                    "Continue weapons inspections",
                    "Diplomatic pressure and sanctions",
                    "Coalition-building before action",
                    "Demand concrete WMD evidence"
                ],
                outcomes={
                    'transparency': 0.3,
                    'consent_obtained': True,
                    'agency_preserved': 0.2,
                    'harm_level': 5,
                    'pac_score': 0.18
                },
                source_urls=["https://en.wikipedia.org/wiki/Iraq_Resolution"]
            ),
            
            # 6. Marriage Equality (Obergefell v. Hodges, 2015)
            RealWorldEvent(
                title="Obergefell v. Hodges (Marriage Equality)",
                actor="U.S. Supreme Court",
                date="June 26, 2015",
                description="Legalized same-sex marriage nationwide, recognizing equal protection rights.",
                context="States had varying laws; discrimination against same-sex couples.",
                stakeholders=["LGBTQ+ individuals", "Same-sex couples", "Religious organizations", "State governments"],
                decision_made="Recognize constitutional right to same-sex marriage",
                alternatives_available=[
                    "Leave to states",
                    "Civil unions only",
                    "Religious exemptions",
                    "Status quo (state-by-state)"
                ],
                outcomes={
                    'transparency': 0.8,
                    'consent_obtained': True,
                    'agency_preserved': 0.95,
                    'harm_level': 0,
                    'pac_score': 0.93
                },
                source_urls=["https://en.wikipedia.org/wiki/Obergefell_v._Hodges"]
            ),
            
            # 7. COVID-19 Lockdowns (2020)
            RealWorldEvent(
                title="COVID-19 Nationwide Lockdowns",
                actor="Various Governments Worldwide",
                date="March-April 2020",
                description="Mandatory stay-at-home orders, business closures to slow pandemic spread.",
                context="Novel coronavirus pandemic; uncertainty about transmission and severity.",
                stakeholders=["General public", "Healthcare workers", "Business owners", "Students", "Elderly"],
                decision_made="Implement strict lockdowns with limited exceptions",
                alternatives_available=[
                    "Voluntary social distancing",
                    "Targeted protection of vulnerable",
                    "Regional variations based on case rates",
                    "Gradual restrictions"
                ],
                outcomes={
                    'transparency': 0.6,
                    'consent_obtained': False,
                    'agency_preserved': 0.35,
                    'harm_level': 2,
                    'pac_score': 0.55
                },
                source_urls=["https://en.wikipedia.org/wiki/COVID-19_lockdowns"]
            ),
            
            # 8. Patriot Act (2001)
            RealWorldEvent(
                title="USA PATRIOT Act",
                actor="U.S. Congress",
                date="October 26, 2001",
                description="Expanded surveillance powers for law enforcement post-9/11.",
                context="National security concerns after terrorist attacks; rushed legislative process.",
                stakeholders=["U.S. citizens", "Law enforcement", "Privacy advocates", "Immigrants"],
                decision_made="Grant expanded surveillance and detention powers",
                alternatives_available=[
                    "Targeted reforms with sunset clauses",
                    "Warrant requirements for surveillance",
                    "Gradual implementation with oversight",
                    "International cooperation without domestic surveillance"
                ],
                outcomes={
                    'transparency': 0.2,
                    'consent_obtained': True,
                    'agency_preserved': 0.30,
                    'harm_level': 2,
                    'pac_score': 0.38
                },
                source_urls=["https://en.wikipedia.org/wiki/Patriot_Act"]
            ),
            
            # 9. Brexit Referendum (2016)
            RealWorldEvent(
                title="United Kingdom European Union Membership Referendum (Brexit)",
                actor="U.K. Parliament & David Cameron",
                date="June 23, 2016",
                description="Referendum on UK's membership in European Union; narrow vote to leave.",
                context="EU integration debates; immigration concerns; sovereignty questions.",
                stakeholders=["UK citizens", "EU citizens in UK", "Businesses", "Northern Ireland", "Scotland"],
                decision_made="Hold referendum leading to EU departure",
                alternatives_available=[
                    "Renegotiate EU terms without referendum",
                    "Parliamentary decision",
                    "Supermajority requirement",
                    "Regional consent requirements"
                ],
                outcomes={
                    'transparency': 0.5,
                    'consent_obtained': True,
                    'agency_preserved': 0.60,
                    'harm_level': 2,
                    'pac_score': 0.58
                },
                source_urls=["https://en.wikipedia.org/wiki/2016_United_Kingdom_European_Union_membership_referendum"]
            ),
            
            # 10. Roe v. Wade Overturn (Dobbs, 2022)
            RealWorldEvent(
                title="Dobbs v. Jackson Women's Health Organization",
                actor="U.S. Supreme Court",
                date="June 24, 2022",
                description="Overturned Roe v. Wade, eliminating federal constitutional right to abortion.",
                context="50-year precedent; immediate trigger bans in multiple states.",
                stakeholders=["Women of reproductive age", "Healthcare providers", "State governments", "Religious groups"],
                decision_made="Overturn Roe v. Wade, return decision to states",
                alternatives_available=[
                    "Maintain Roe with modifications",
                    "Gradual transition period",
                    "Federal minimum standards",
                    "Viability-based compromise"
                ],
                outcomes={
                    'transparency': 0.4,
                    'consent_obtained': False,
                    'agency_preserved': 0.25,
                    'harm_level': 3,
                    'pac_score': 0.30
                },
                source_urls=["https://en.wikipedia.org/wiki/Dobbs_v._Jackson_Women%27s_Health_Organization"]
            ),
        ]
    
    # ========================================================================
    # CORPORATE DECISIONS (10)
    # ========================================================================
    
    def _corporate_events(self) -> List[RealWorldEvent]:
        """Corporate decisions."""
        return [
            # 11. Cambridge Analytica (2018)
            RealWorldEvent(
                title="Cambridge Analytica Data Harvesting",
                actor="Facebook / Cambridge Analytica",
                date="March 2018",
                description="Harvested 87 million Facebook users' data without consent for political profiling.",
                context="2016 election targeting; personality quiz app exploited platform.",
                stakeholders=["87 million users", "Voters", "Democracy", "Privacy advocates"],
                decision_made="Allow third-party app to harvest friend data without notification",
                alternatives_available=[
                    "Explicit opt-in consent",
                    "Third-party app audits",
                    "Transparent data access disclosure",
                    "User data dashboards"
                ],
                outcomes={
                    'transparency': 0.1,
                    'consent_obtained': False,
                    'agency_preserved': 0.2,
                    'harm_level': 2,
                    'pac_score': 0.25
                },
                source_urls=["https://en.wikipedia.org/wiki/Facebook%E2%80%93Cambridge_Analytica_data_scandal"]
            ),
            
            # 12. Volkswagen Emissions Scandal (2015)
            RealWorldEvent(
                title="Volkswagen Emissions Scandal (Dieselgate)",
                actor="Volkswagen AG",
                date="September 2015",
                description="Installed defeat devices to cheat emissions tests on 11 million vehicles.",
                context="Environmental regulations; competitive pressure in diesel market.",
                stakeholders=["Car owners", "Public health", "Environment", "Competitors", "Regulators"],
                decision_made="Deliberately program vehicles to cheat emissions tests",
                alternatives_available=[
                    "Invest in legitimate emissions technology",
                    "Disclose actual emissions levels",
                    "Exit diesel market",
                    "Meet standards without cheating"
                ],
                outcomes={
                    'transparency': 0.0,
                    'consent_obtained': False,
                    'agency_preserved': 0.1,
                    'harm_level': 4,
                    'pac_score': 0.08
                },
                source_urls=["https://en.wikipedia.org/wiki/Volkswagen_emissions_scandal"]
            ),
            
            # 13. Johnson & Johnson Talc Powder (2018)
            RealWorldEvent(
                title="Johnson & Johnson Talc Asbestos Cancer Cases",
                actor="Johnson & Johnson",
                date="2018 (lawsuits)",
                description="Sold talc-based powder despite knowing about asbestos contamination risks.",
                context="Decades of internal knowledge; thousands of ovarian cancer cases.",
                stakeholders=["Cancer patients", "Product users", "Families", "Public health"],
                decision_made="Continue selling product without adequate warning or reformulation",
                alternatives_available=[
                    "Reformulate without talc",
                    "Issue clear health warnings",
                    "Voluntary recall",
                    "Transparent disclosure of risks"
                ],
                outcomes={
                    'transparency': 0.1,
                    'consent_obtained': False,
                    'agency_preserved': 0.15,
                    'harm_level': 5,
                    'pac_score': 0.12
                },
                source_urls=["https://en.wikipedia.org/wiki/Talc#Legal_issues"]
            ),
            
            # 14. Wells Fargo Fake Accounts Scandal (2016)
            RealWorldEvent(
                title="Wells Fargo Fake Accounts Scandal",
                actor="Wells Fargo & Company",
                date="September 2016",
                description="Created millions of fraudulent accounts without customer authorization.",
                context="Sales pressure; performance quotas; 5,300 employees fired.",
                stakeholders=["Bank customers", "Employees", "Shareholders", "Banking regulators"],
                decision_made="Maintain aggressive sales quotas leading to fraud",
                alternatives_available=[
                    "Ethical sales practices",
                    "Customer-centric incentives",
                    "Whistleblower protections",
                    "Regular audits and oversight"
                ],
                outcomes={
                    'transparency': 0.2,
                    'consent_obtained': False,
                    'agency_preserved': 0.15,
                    'harm_level': 3,
                    'pac_score': 0.20
                },
                source_urls=["https://en.wikipedia.org/wiki/Wells_Fargo_account_fraud_scandal"]
            ),
            
            # 15. Purdue Pharma OxyContin Marketing (1990s-2010s)
            RealWorldEvent(
                title="Purdue Pharma OxyContin Opioid Crisis",
                actor="Purdue Pharma (Sackler Family)",
                date="1996-2019",
                description="Aggressive marketing of OxyContin while downplaying addiction risks.",
                context="Opioid epidemic; hundreds of thousands of overdose deaths.",
                stakeholders=["Patients", "Addiction victims", "Families", "Healthcare system", "Communities"],
                decision_made="Market opioids as safe and non-addictive despite evidence",
                alternatives_available=[
                    "Honest addiction risk disclosure",
                    "Responsible prescribing guidelines",
                    "Addiction support programs",
                    "Alternative pain management research"
                ],
                outcomes={
                    'transparency': 0.1,
                    'consent_obtained': False,
                    'agency_preserved': 0.1,
                    'harm_level': 5,
                    'pac_score': 0.10
                },
                source_urls=["https://en.wikipedia.org/wiki/Purdue_Pharma"]
            ),
            
            # 16. Patagonia Environmental Commitment (Ongoing)
            RealWorldEvent(
                title="Patagonia 1% for the Planet & Ownership Transfer",
                actor="Patagonia (Yvon Chouinard)",
                date="September 2022",
                description="Transferred company ownership to trust dedicated to fighting climate change.",
                context="Corporate responsibility; climate crisis; stakeholder capitalism.",
                stakeholders=["Employees", "Customers", "Environment", "Business community", "Future generations"],
                decision_made="Transfer $3B company to environmental trust instead of selling or going public",
                alternatives_available=[
                    "Traditional sale to highest bidder",
                    "IPO for shareholder value",
                    "Family inheritance",
                    "Partial donation"
                ],
                outcomes={
                    'transparency': 0.95,
                    'consent_obtained': True,
                    'agency_preserved': 0.90,
                    'harm_level': 0,
                    'pac_score': 0.95
                },
                source_urls=["https://en.wikipedia.org/wiki/Patagonia,_Inc."]
            ),
            
            # 17. Boeing 737 MAX Cover-Up (2018-2019)
            RealWorldEvent(
                title="Boeing 737 MAX MCAS System Failures",
                actor="Boeing Company",
                date="2018-2019",
                description="Concealed critical flight system flaws leading to two fatal crashes (346 deaths).",
                context="Competitive pressure from Airbus; FAA oversight failures.",
                stakeholders=["Passengers (346 dead)", "Pilots", "Airlines", "Aviation safety", "Regulators"],
                decision_made="Rush 737 MAX to market without adequate safety disclosure or pilot training",
                alternatives_available=[
                    "Full MCAS disclosure and training",
                    "Delay launch for proper safety review",
                    "Redesign for redundancy",
                    "Transparent communication with airlines"
                ],
                outcomes={
                    'transparency': 0.1,
                    'consent_obtained': False,
                    'agency_preserved': 0.05,
                    'harm_level': 5,
                    'pac_score': 0.05
                },
                source_urls=["https://en.wikipedia.org/wiki/Boeing_737_MAX_groundings"]
            ),
            
            # 18. Equifax Data Breach (2017)
            RealWorldEvent(
                title="Equifax Data Breach",
                actor="Equifax Inc.",
                date="September 2017",
                description="Failed to patch known vulnerability, exposing 147 million people's sensitive data.",
                context="Credit reporting agency; Social Security numbers, birth dates, addresses exposed.",
                stakeholders=["147 million consumers", "Identity theft victims", "Credit system", "Regulators"],
                decision_made="Delay patching critical vulnerability despite warnings",
                alternatives_available=[
                    "Immediate security patch deployment",
                    "Proactive security audits",
                    "Prompt breach disclosure",
                    "Enhanced data protection measures"
                ],
                outcomes={
                    'transparency': 0.3,
                    'consent_obtained': False,
                    'agency_preserved': 0.2,
                    'harm_level': 4,
                    'pac_score': 0.22
                },
                source_urls=["https://en.wikipedia.org/wiki/2017_Equifax_data_breach"]
            ),
            
            # 19. Costco Employee Treatment Model (Ongoing)
            RealWorldEvent(
                title="Costco Living Wage & Benefits Model",
                actor="Costco Wholesale Corporation",
                date="Ongoing (consistent since 1983)",
                description="Pays significantly above minimum wage with comprehensive benefits.",
                context="Retail industry typically low-wage; shareholder pressure for cost-cutting.",
                stakeholders=["Employees", "Customers", "Shareholders", "Retail industry", "Communities"],
                decision_made="Maintain high wages ($17-24/hr starting) and benefits despite pressure",
                alternatives_available=[
                    "Industry-standard minimum wage",
                    "Part-time workforce without benefits",
                    "Profit maximization model",
                    "Automation to reduce labor costs"
                ],
                outcomes={
                    'transparency': 0.8,
                    'consent_obtained': True,
                    'agency_preserved': 0.85,
                    'harm_level': 0,
                    'pac_score': 0.88
                },
                source_urls=["https://en.wikipedia.org/wiki/Costco#Employee_relations"]
            ),
            
            # 20. Nestle Water Privatization (2000s-2020s)
            RealWorldEvent(
                title="Nestlé Water Extraction in Drought Areas",
                actor="Nestlé Corporation",
                date="2000s-2020s",
                description="Extracted groundwater from drought-stricken areas for bottled water sales.",
                context="California droughts; indigenous land rights; public resource commodification.",
                stakeholders=["Local communities", "Indigenous peoples", "Environment", "Water rights advocates"],
                decision_made="Continue water extraction despite drought and community opposition",
                alternatives_available=[
                    "Halt extraction during droughts",
                    "Fair compensation to communities",
                    "Sustainable extraction limits",
                    "Community water partnerships"
                ],
                outcomes={
                    'transparency': 0.3,
                    'consent_obtained': False,
                    'agency_preserved': 0.25,
                    'harm_level': 3,
                    'pac_score': 0.28
                },
                source_urls=["https://en.wikipedia.org/wiki/Nestl%C3%A9#Water"]
            ),
        ]
    
    # ========================================================================
    # TECHNOLOGY DECISIONS (8)
    # ========================================================================
    
    def _technology_events(self) -> List[RealWorldEvent]:
        """Technology company decisions."""
        return [
            # 21. Apple vs. FBI Encryption (2016)
            RealWorldEvent(
                title="Apple vs. FBI iPhone Encryption Dispute",
                actor="Apple Inc. (Tim Cook)",
                date="February 2016",
                description="Refused FBI order to create encryption backdoor for San Bernardino investigation.",
                context="Terrorist attack investigation; privacy vs. security debate.",
                stakeholders=["iPhone users", "Privacy advocates", "Law enforcement", "Victims' families", "Tech industry"],
                decision_made="Refuse to create encryption backdoor",
                alternatives_available=[
                    "Create one-time backdoor",
                    "Unlock device without creating tool",
                    "Comply with government order",
                    "Assist with alternative forensics"
                ],
                outcomes={
                    'transparency': 0.9,
                    'consent_obtained': True,
                    'agency_preserved': 0.90,
                    'harm_level': 0,
                    'pac_score': 0.92
                },
                source_urls=["https://en.wikipedia.org/wiki/FBI%E2%80%93Apple_encryption_dispute"]
            ),
            
            # 22. Twitter Account Verification Changes (2022)
            RealWorldEvent(
                title="Twitter Blue Verification System",
                actor="Twitter/X (Elon Musk)",
                date="November 2022",
                description="Changed verification from identity confirmation to paid subscription.",
                context="Post-acquisition changes; impersonation risks; misinformation concerns.",
                stakeholders=["Verified users", "Public figures", "General users", "Advertisers", "News organizations"],
                decision_made="Replace legacy verification with $8/month paid system",
                alternatives_available=[
                    "Maintain identity-based verification",
                    "Dual system (legacy + paid tiers)",
                    "Enhanced verification with payment",
                    "Free but stricter verification process"
                ],
                outcomes={
                    'transparency': 0.4,
                    'consent_obtained': False,
                    'agency_preserved': 0.45,
                    'harm_level': 2,
                    'pac_score': 0.48
                },
                source_urls=["https://en.wikipedia.org/wiki/Twitter_Blue"]
            ),
            
            # 23. Google Search Algorithm Changes (Ongoing)
            RealWorldEvent(
                title="Google Search Algorithm Prioritization",
                actor="Google LLC",
                date="Ongoing (2000s-present)",
                description="Controls information access for billions through opaque ranking algorithms.",
                context="Information gatekeeping; antitrust concerns; news ecosystem impact.",
                stakeholders=["Internet users", "Content creators", "News organizations", "Businesses", "Advertisers"],
                decision_made="Maintain proprietary algorithm without transparency",
                alternatives_available=[
                    "Algorithm transparency disclosures",
                    "User-controlled ranking preferences",
                    "Independent algorithm audits",
                    "Neutral ranking option"
                ],
                outcomes={
                    'transparency': 0.3,
                    'consent_obtained': False,
                    'agency_preserved': 0.40,
                    'harm_level': 2,
                    'pac_score': 0.42
                },
                source_urls=["https://en.wikipedia.org/wiki/Google_Search"]
            ),
            
            # 24. TikTok Algorithm & Teen Mental Health
            RealWorldEvent(
                title="TikTok Algorithm and Youth Mental Health",
                actor="ByteDance (TikTok)",
                date="2020-present",
                description="Addictive algorithm optimized for engagement despite mental health concerns.",
                context="Teen anxiety/depression rates; social comparison; screen addiction.",
                stakeholders=["Teen users", "Parents", "Mental health professionals", "Educators", "Regulators"],
                decision_made="Maximize engagement without adequate mental health safeguards",
                alternatives_available=[
                    "Screen time limits for minors",
                    "Mental health content warnings",
                    "Less aggressive recommendation algorithm",
                    "Transparent algorithm disclosure"
                ],
                outcomes={
                    'transparency': 0.2,
                    'consent_obtained': False,
                    'agency_preserved': 0.30,
                    'harm_level': 3,
                    'pac_score': 0.32
                },
                source_urls=["https://en.wikipedia.org/wiki/TikTok#Controversies"]
            ),
            
            # 25. Microsoft Open Source Shift (.NET, VSCode)
            RealWorldEvent(
                title="Microsoft Open Source Transformation",
                actor="Microsoft Corporation (Satya Nadella)",
                date="2014-present",
                description="Shifted from proprietary to open-source strategy; released .NET, VSCode, etc.",
                context="Developer community relations; cloud strategy; competitive landscape.",
                stakeholders=["Developers", "Tech community", "Competitors", "Customers", "Open source community"],
                decision_made="Embrace open source and cross-platform development",
                alternatives_available=[
                    "Maintain proprietary ecosystem",
                    "Limited open source releases",
                    "Acquisition of open source companies",
                    "Dual licensing model"
                ],
                outcomes={
                    'transparency': 0.85,
                    'consent_obtained': True,
                    'agency_preserved': 0.88,
                    'harm_level': 0,
                    'pac_score': 0.90
                },
                source_urls=["https://en.wikipedia.org/wiki/Microsoft_and_open_source"]
            ),
            
            # 26. Amazon Ring Police Partnerships (2018-2021)
            RealWorldEvent(
                title="Amazon Ring Police Partnership Program",
                actor="Amazon (Ring)",
                date="2018-2021",
                description="Partnered with police to access doorbell camera footage without warrants.",
                context="Surveillance concerns; privacy vs. public safety; minimal disclosure.",
                stakeholders=["Ring users", "Neighbors", "Privacy advocates", "Police departments", "Communities"],
                decision_made="Create police portal for footage requests without warrant requirement",
                alternatives_available=[
                    "Warrant requirements for all requests",
                    "User opt-in for police partnerships",
                    "Transparent disclosure of partnerships",
                    "No police partnerships"
                ],
                outcomes={
                    'transparency': 0.3,
                    'consent_obtained': False,
                    'agency_preserved': 0.35,
                    'harm_level': 2,
                    'pac_score': 0.38
                },
                source_urls=["https://en.wikipedia.org/wiki/Ring_(company)#Privacy_concerns"]
            ),
            
            # 27. Signal Encrypted Messaging
            RealWorldEvent(
                title="Signal End-to-End Encryption Standard",
                actor="Signal Foundation",
                date="2013-present",
                description="Maintains strong encryption refusing government backdoor requests.",
                context="Privacy vs. law enforcement access; global surveillance concerns.",
                stakeholders=["Users", "Privacy advocates", "Journalists", "Activists", "Law enforcement"],
                decision_made="Maintain end-to-end encryption without backdoors or data collection",
                alternatives_available=[
                    "Implement government backdoors",
                    "Store metadata",
                    "Selective decryption capability",
                    "Compromise on encryption strength"
                ],
                outcomes={
                    'transparency': 0.95,
                    'consent_obtained': True,
                    'agency_preserved': 0.95,
                    'harm_level': 0,
                    'pac_score': 0.96
                },
                source_urls=["https://en.wikipedia.org/wiki/Signal_(software)"]
            ),
            
            # 28. YouTube Algorithm Radicalization (2010s-2020s)
            RealWorldEvent(
                title="YouTube Recommendation Algorithm Radicalization",
                actor="YouTube (Google)",
                date="2010s-2020s",
                description="Algorithm recommended increasingly extreme content to maximize watch time.",
                context="Conspiracy theories; political radicalization; misinformation spread.",
                stakeholders=["Users", "Content creators", "Society", "Advertisers", "Researchers"],
                decision_made="Optimize recommendations purely for engagement",
                alternatives_available=[
                    "Content diversity requirements",
                    "Limit consecutive similar recommendations",
                    "Transparent algorithm criteria",
                    "User control over recommendations"
                ],
                outcomes={
                    'transparency': 0.2,
                    'consent_obtained': False,
                    'agency_preserved': 0.25,
                    'harm_level': 4,
                    'pac_score': 0.26
                },
                source_urls=["https://en.wikipedia.org/wiki/YouTube#Radicalization_and_extremism"]
            ),
        ]
    
    # ========================================================================
    # HEALTHCARE DECISIONS (7)
    # ========================================================================
    
    def _healthcare_events(self) -> List[RealWorldEvent]:
        """Healthcare and medical decisions."""
        return [
            # 29. Tuskegee Syphilis Study (1932-1972)
            RealWorldEvent(
                title="Tuskegee Syphilis Study",
                actor="U.S. Public Health Service",
                date="1932-1972",
                description="Observed untreated syphilis in Black men without consent or treatment.",
                context="Racist medical experimentation; participants deceived for 40 years.",
                stakeholders=["600 Black men", "Families", "Medical community", "Public health", "Bioethics"],
                decision_made="Continue study without treatment even after penicillin became available",
                alternatives_available=[
                    "Informed consent and treatment",
                    "End study when treatment available",
                    "Full disclosure of risks",
                    "Ethical oversight"
                ],
                outcomes={
                    'transparency': 0.0,
                    'consent_obtained': False,
                    'agency_preserved': 0.0,
                    'harm_level': 5,
                    'pac_score': 0.0
                },
                source_urls=["https://en.wikipedia.org/wiki/Tuskegee_Syphilis_Study"]
            ),
            
            # 30. Henrietta Lacks HeLa Cells (1951)
            RealWorldEvent(
                title="Henrietta Lacks HeLa Cell Line",
                actor="Johns Hopkins Hospital",
                date="1951",
                description="Harvested cancer cells without consent; became invaluable research tool.",
                context="No consent laws at time; family learned decades later; massive scientific value.",
                stakeholders=["Henrietta Lacks", "Lacks family", "Medical researchers", "Biotech industry"],
                decision_made="Harvest and distribute cells without consent or compensation",
                alternatives_available=[
                    "Obtain informed consent",
                    "Family notification and compensation",
                    "Benefit sharing agreement",
                    "Posthumous acknowledgment"
                ],
                outcomes={
                    'transparency': 0.1,
                    'consent_obtained': False,
                    'agency_preserved': 0.1,
                    'harm_level': 3,
                    'pac_score': 0.15
                },
                source_urls=["https://en.wikipedia.org/wiki/Henrietta_Lacks"]
            ),
            
            # 31. COVID-19 Vaccine Development & Distribution
            RealWorldEvent(
                title="COVID-19 mRNA Vaccine Development (Operation Warp Speed)",
                actor="Pharmaceutical Companies & Governments",
                date="2020-2021",
                description="Accelerated vaccine development and emergency authorization during pandemic.",
                context="Global health crisis; unprecedented speed; public-private partnership.",
                stakeholders=["Global population", "Healthcare workers", "Governments", "Pharmaceutical companies"],
                decision_made="Emergency authorization after accelerated trials with transparency",
                alternatives_available=[
                    "Standard multi-year approval process",
                    "Challenge trials with volunteers",
                    "Delayed rollout for more data",
                    "Global patent waiver earlier"
                ],
                outcomes={
                    'transparency': 0.75,
                    'consent_obtained': True,
                    'agency_preserved': 0.80,
                    'harm_level': 0,
                    'pac_score': 0.82
                },
                source_urls=["https://en.wikipedia.org/wiki/COVID-19_vaccine"]
            ),
            
            # 32. Theranos Fraud (2003-2018)
            RealWorldEvent(
                title="Theranos Blood Testing Fraud",
                actor="Theranos Inc. (Elizabeth Holmes)",
                date="2003-2018",
                description="Fraudulent blood testing technology claims endangering patient health.",
                context="Silicon Valley hype; investor fraud; inaccurate medical results.",
                stakeholders=["Patients", "Investors", "Healthcare system", "Walgreens", "Lab industry"],
                decision_made="Falsely claim revolutionary technology while using standard machines",
                alternatives_available=[
                    "Honest disclosure of limitations",
                    "Legitimate research pathway",
                    "Pivot to achievable goals",
                    "Transparent clinical validation"
                ],
                outcomes={
                    'transparency': 0.0,
                    'consent_obtained': False,
                    'agency_preserved': 0.05,
                    'harm_level': 4,
                    'pac_score': 0.05
                },
                source_urls=["https://en.wikipedia.org/wiki/Theranos"]
            ),
            
            # 33. Right to Try Act (2018)
            RealWorldEvent(
                title="Right to Try Act",
                actor="U.S. Congress & President Trump",
                date="May 30, 2018",
                description="Allowed terminally ill patients access to experimental drugs without FDA approval.",
                context="Compassionate use; patient autonomy vs. safety standards.",
                stakeholders=["Terminally ill patients", "Families", "FDA", "Pharmaceutical companies", "Doctors"],
                decision_made="Allow experimental drug access bypassing FDA for terminal patients",
                alternatives_available=[
                    "Expand compassionate use program",
                    "Faster FDA emergency approvals",
                    "Maintain safety requirements",
                    "Case-by-case review process"
                ],
                outcomes={
                    'transparency': 0.7,
                    'consent_obtained': True,
                    'agency_preserved': 0.85,
                    'harm_level': 1,
                    'pac_score': 0.78
                },
                source_urls=["https://en.wikipedia.org/wiki/Right_to_Try"]
            ),
            
            # 34. Mental Health Apps Data Privacy
            RealWorldEvent(
                title="Mental Health Apps Selling User Data",
                actor="Various Mental Health App Companies",
                date="2019-2023",
                description="Mental health apps shared sensitive user data with advertisers without clear consent.",
                context="Digital mental health boom; inadequate HIPAA coverage; data broker market.",
                stakeholders=["App users", "Mental health patients", "Privacy advocates", "Advertisers", "Insurers"],
                decision_made="Monetize sensitive mental health data through third-party sharing",
                alternatives_available=[
                    "HIPAA-compliant data protection",
                    "No data sharing policy",
                    "Explicit opt-in consent",
                    "Transparent data usage disclosure"
                ],
                outcomes={
                    'transparency': 0.2,
                    'consent_obtained': False,
                    'agency_preserved': 0.20,
                    'harm_level': 3,
                    'pac_score': 0.24
                },
                source_urls=["https://www.ftc.gov/news-events/news/press-releases/2023/03/ftc-ban-betterhelp-revealing-consumers-data-including-sensitive-mental-health-information-facebook"]
            ),
            
            # 35. CRISPR Gene Editing (He Jiankui, 2018)
            RealWorldEvent(
                title="CRISPR Gene-Edited Babies Experiment",
                actor="He Jiankui (Chinese researcher)",
                date="November 2018",
                description="Created world's first gene-edited babies without proper ethical review.",
                context="Experimental germline editing; international condemnation; unknown long-term effects.",
                stakeholders=["Gene-edited twins", "Future generations", "Scientific community", "Ethics boards", "Humanity"],
                decision_made="Proceed with human germline editing experiment",
                alternatives_available=[
                    "Animal/cell studies first",
                    "International ethical consensus",
                    "Somatic (non-heritable) editing only",
                    "Transparent peer review"
                ],
                outcomes={
                    'transparency': 0.1,
                    'consent_obtained': False,
                    'agency_preserved': 0.05,
                    'harm_level': 4,
                    'pac_score': 0.08
                },
                source_urls=["https://en.wikipedia.org/wiki/He_Jiankui"]
            ),
        ]


# Export database instance
event_db = EventDatabase()
