# Customer Segmentation Output – Batch “P → T” (v1)

This document applies the **Customer Classification & Segmentation Specification (v1)** to the provided customer list.

## Output Fields
- **Industrial Group**: Locked vertical segment (one per customer entity)
- **Industry Detail**: Short context label
- **NAICS**: Reference classification (text; typically 2–4 digit unless unambiguous)
- **Method**:
  - **Rule-Based**: Deterministic keyword/pattern match
  - **Entity Inference**: Widely recognized organization/brand (no keyword dependency)
  - **AI-Assisted Search**: Ambiguous; requires lookup/semantic search to classify
  - **Heuristic**: Weak-signal best guess; should be reviewable
- **Domain**: Left blank in this batch (domain resolution is a separate enrichment pass)

---

## Manufacturing

| Customer | Industry Detail | NAICS | Method | Domain |
|---|---|---:|---|---|
| PERFETTI VANMELLE | Confectionery manufacturing | 3113 | Entity Inference | |
| PHOENIX METALS | Metal manufacturing/processing | 331 | Heuristic | |
| PIONEER AUTOMOTIVE TECHNOLOGIES | Automotive components | 3363 | Heuristic | |
| PIRAMAL PHARMA SOLUTIONS | Pharmaceutical manufacturing | 3254 | Entity Inference | |
| POLYMER SHAPES | Plastics distribution/manufacturing | 3261 | Heuristic | |
| POST GLOVER RESISTORS | Electronic components | 3344 | Heuristic | |
| PRATT INDUSTRIES | Packaging/paper products | 3222 | Entity Inference | |
| PRECISE TOOLING SOLUTIONS | Tooling / machining | 3327 | Heuristic | |
| PROCTOR AND GAMBLE | Consumer products manufacturing | 3256 | Entity Inference | |
| PROTERIAL CABLE AMERICA | Wire/cable manufacturing | 3359 | Heuristic | |
| PUREMAXX FILTRATION | Filtration products | 3334 | Heuristic | |
| PVS NOLWOOD CHEMICALS | Chemicals manufacturing | 325 | Entity Inference | |
| QUEBECOR WORLD | Printing manufacturing | 3231 | Entity Inference | |
| RAYPAK | HVAC/boilers/water heating equipment | 3334 | Entity Inference | |
| RED BULL DISTRIBUTION CENTER | Beverage distribution (not mfg) | 4244 | Heuristic | |
| REFRESCO BEVERAGES US | Beverage manufacturing | 3121 | Entity Inference | |
| REGAL REXNORD | Industrial motors/drives | 3353 | Entity Inference | |
| REILY FOODS | Food manufacturing | 311 | Entity Inference | |
| RESOURCE LABEL GROUP | Label/packaging printing | 3231 | Entity Inference | |
| REVERE PLASTICS SYSTEMS CLYDE | Plastics manufacturing | 3261 | Entity Inference | |
| RICH PRODUCTS | Food manufacturing | 311 | Entity Inference | |
| ROBERT BOSCH AUTOMOTIVE | Automotive components | 3363 | Entity Inference | |
| ROBERT BOSCH AUTOMOTIVE STEERING | Automotive steering systems | 3363 | Entity Inference | |
| ROHM AND HAAS | Chemicals manufacturing | 325 | Entity Inference | |
| ROUGH BROTHERS | Industrial process equipment | 3339 | Heuristic | |
| RUBBERSEAL PRODUCTS | Rubber products | 3262 | Heuristic | |
| SA RECYCLING | Scrap processing | 4239 | Heuristic | |
| SANDVIK / SANDVIK ABC | Industrial tools/materials | 3335 | Entity Inference | |
| SARGENT AND GREENLEAF | Security hardware manufacturing | 3325 | Entity Inference | |
| SATCO | Lighting products (ambiguous entity) | — | AI-Assisted Search | |
| SAZERAC OF INDIANA | Beverage manufacturing | 3121 | Entity Inference | |
| SCENIC INDUSTRIES | Manufacturing (unclear) | — | AI-Assisted Search | |
| SHAW INDUSTRIES GROUP | Flooring manufacturing | 3141 | Entity Inference | |
| SHERWIN WILLIAMS | Paint/coatings manufacturing | 3255 | Entity Inference | |
| SHOALS TECHNOLOGIES GROUP | Electrical components | 3359 | Entity Inference | |
| SIEMENS MOBILITY | Rail systems/equipment | 3365 | Entity Inference | |
| SIKA AUTOMOTIVE KENTUCKY | Automotive chemicals/adhesives | 3255 | Entity Inference | |
| SIMS METAL | Scrap metal processing | 4239 | Entity Inference | |
| SINOMAX EAST | Foam/furnishings manufacturing | 337 | Heuristic | |
| SLICE OF STAINLESS | Metal fabrication | 3323 | Heuristic | |
| SMC OF AMERICA | Industrial automation components | 3339 | Entity Inference | |
| SMURFITSTONE | Packaging/paper | 3222 | Entity Inference | |
| SNYDERS LANCE | Food manufacturing | 311 | Entity Inference | |
| SONOCO CORRFLEX | Packaging products | 3222 | Entity Inference | |
| SONOCO FLEXIBLE | Packaging products | 3222 | Entity Inference | |
| SPARTECH | Plastics manufacturing | 3261 | Entity Inference | |
| SPRINGS WINDOW FASHIONS | Window coverings manufacturing | 337 | Entity Inference | |
| STANDEX ELECTRONICS | Electronics manufacturing | 3344 | Entity Inference | |
| STERIS | Medical equipment manufacturing | 3391 | Entity Inference | |
| STONEPEAK CERAMICS | Ceramic tile manufacturing | 3271 | Entity Inference | |
| STOROPACK / STOROPACK CSC | Protective packaging | 3222 | Entity Inference | |
| SUBARU OF AMERICA | Automotive (sales/ops) | 4411 | Entity Inference | |
| SUMCO PHOENIX | Semiconductor manufacturing | 3344 | Entity Inference | |
| SUNGWOO HITECH AMERICA | Automotive components | 3363 | Entity Inference | |
| SYENSQO MOUNT PLEASANT | Specialty chemicals/materials | 325 | Entity Inference | |
| SYMMETRY SURGICAL | Medical devices | 3391 | Entity Inference | |
| TAPE PRODUCTS | Packaging tapes | 3261 | Heuristic | |
| TECHMER PM | Plastics compounds | 3259 | Entity Inference | |
| TEKRAN INSTRUMENTS | Scientific instruments | 3345 | Entity Inference | |
| TELEDYNE | Aerospace/electronics manufacturing | 3364 | Entity Inference | |
| THALER MACHINE | Machinery manufacturing | 3339 | Heuristic | |
| THERMAL CARE | Industrial chillers/HVAC equipment | 3334 | Heuristic | |
| THERMATRONX | Industrial equipment (unclear) | — | AI-Assisted Search | |

---

## Construction / Mechanical Contractors

| Customer | Industry Detail | NAICS | Method | Domain |
|---|---|---:|---|---|
| PERFORMANCE CONTRACTING | Specialty contracting (insulation/interiors) | 2383 | Entity Inference | |
| PILOT CONTRACTING | General/specialty contractor | 2362 | Rule-Based | |
| PLUMB TECH SERVICES | Plumbing contractor | 2382 | Rule-Based | |
| PRECISION WALLS | Drywall/framing contractor | 2383 | Rule-Based | |
| PREMIER DESIGN AND BUILD GROUP | Design-build contractor | 2362 | Rule-Based | |
| QUALITY MECHANICALS | Mechanical contractor | 2382 | Rule-Based | |
| RAINBOW RESTORATION | Restoration contractor | 2361 | Entity Inference | |
| REED CONTRACTING GROUP | Contractor | 2362 | Rule-Based | |
| RIEGLER BLACKTOP | Paving/asphalt | 2373 | Rule-Based | |
| RITCHIE MECHANICAL | Mechanical contractor | 2382 | Rule-Based | |
| RITE BOILER | Boiler/HVAC service | 2382 | Heuristic | |
| RPC MECHANICAL | Mechanical contractor | 2382 | Rule-Based | |
| RSC MECHANICAL | Mechanical contractor | 2382 | Rule-Based | |
| RYAN FIRE PROTECTION | Fire protection contractor | 2382 | Rule-Based | |
| RYAN REMODELING | Remodeling contractor | 2361 | Rule-Based | |
| RYANS ALL GLASS | Glazing contractor | 2381 | Rule-Based | |
| SHOFFNER KALTHOFF MES | Mechanical/Electrical services | 2382 | Heuristic | |
| SILCO FIRE AND SECURITY (CENTERVILLE/CINCINNATI) | Fire/security systems contractor | 2382 | Rule-Based | |
| SURE GROUP DBA THE CINCINNATI AIR CONDITIONING | HVAC contractor | 2382 | Rule-Based | |
| SURE MECHANICAL | Mechanical contractor | 2382 | Rule-Based | |

---

## Commercial Real Estate

| Customer | Industry Detail | NAICS | Method | Domain |
|---|---|---:|---|---|
| PERKINS PLACE II | Property entity | 5311 | Rule-Based | |
| PETERS ROAD PARTNERSHIP | Property partnership | 5311 | Rule-Based | |
| PGP HARRISON CROSSING OWNER | Shopping center owner entity | 5311 | Rule-Based | |
| PHILLIPS EDISON | Retail REIT / property owner | 5311 | Entity Inference | |
| PHOENIX VERSAILLES INDUSTRIAL INVESTORS | Industrial property owner | 5311 | Rule-Based | |
| PINNACLE TURKEY CREEK | Property entity | 5311 | Rule-Based | |
| PPA CASTLE CREEK I AND II LP | Property entity | 5311 | Rule-Based | |
| PRECEDENT LAKESIDE ACQUISITIONS | Property acquisition entity | 5311 | Rule-Based | |
| PROLOGIS LP | Industrial REIT / logistics real estate | 5311 | Entity Inference | |
| PRUDENT GROWTH OPERATION | Investment/property (unclear) | — | AI-Assisted Search | |
| PSC CENTRAL PARK | Property entity | 5311 | Rule-Based | |
| QUANTUM INVESTMENTS AND MGMT | Investment/property mgmt (unclear) | 5313 | Heuristic | |
| RAVEN COMMERCIAL GROUP | Commercial property entity | 5311 | Heuristic | |
| REGENCY / REGENCY WEST VIRGINIA VENTURES LL | Property entity | 5311 | Heuristic | |
| RICHWOOD BUILDING ONE / TWO | Property entity | 5311 | Rule-Based | |
| RJ BEISCHEL BUILDING | Property entity | 5311 | Rule-Based | |
| RMR LOUISVILLE | Property/asset mgmt (unclear) | 5313 | Heuristic | |
| ROUSE COMPANIES | Real estate/property (unclear) | 5311 | Heuristic | |
| SCGIV KARCHS CROSSING / SCGIXHARVEST TOWNE / SCGVI WASHINGTON MARKET | Property entities | 5311 | Rule-Based | |
| SENTINEL AMAZON I | Industrial property entity | 5311 | Rule-Based | |
| SPRINGS AT OLDHAM RESERVE | Residential/community property | 5311 | Heuristic | |
| TENNESSEAN HOA BILLING | HOA/property association | 8139 | Heuristic | |
| TAMARACK MARKETPLACE | Retail property entity | 5311 | Rule-Based | |
| TAIN INVESTMENTS III | Investment/property (unclear) | 5311 | Heuristic | |

---

## Retail / Hospitality

| Customer | Industry Detail | NAICS | Method | Domain |
|---|---|---:|---|---|
| PETLAND | Pet retail | 4539 | Entity Inference | |
| PNK OHIO DBA BELTERRA PARK | Casino/entertainment venue | 7132 | Entity Inference | |
| POINT BLANK RANGE AND GUNSHOP | Retail/entertainment (range) | 7139 | Rule-Based | |
| PURE CONCEPT SALON AND SPA | Salon/spa | 8121 | Rule-Based | |
| REEDS JEWELERS | Jewelry retail | 4483 | Entity Inference | |
| RHINEGEIST | Brewery/taproom | 3121 | Entity Inference | |
| RIVERTOWN BREWING | Brewery/taproom | 3121 | Rule-Based | |
| ROADHOUSE DEPOT BREWING | Brewery/taproom | 3121 | Rule-Based | |
| SALON LOFTS | Salon suites / personal care | 8121 | Entity Inference | |
| SALT AND LIGHT SALON AND SPA | Salon/spa | 8121 | Rule-Based | |
| SAM ASH MUSIC | Music retail | 4511 | Entity Inference | |
| SAMUEL ADAMS BREWING | Brewery | 3121 | Entity Inference | |
| SANDWICH SQUAD | Quick service restaurant | 7225 | Rule-Based | |
| SKYLINE CHILI | Restaurant | 7225 | Entity Inference | |
| SLEEP OUTFITTERS OUTLET | Furniture retail | 4421 | Rule-Based | |
| SOHO HOUSE NASHVILLE | Private club/hospitality | 7211 | Entity Inference | |
| SOUTHERN OHIO BREWING | Brewery/taproom | 3121 | Rule-Based | |
| SPEEDWAY SUPERAMERICA | Convenience/fuel retail | 4471 | Entity Inference | |
| STATUS DOUGH | Food service (bakery/pizzeria) | 7225 | Heuristic | |
| STEAK ESCAPE | Restaurant | 7225 | Rule-Based | |
| STITCHFIX | E-commerce retail | 4541 | Entity Inference | |
| SUR LA TABLE BDC | Retail distribution center | 4931 | Heuristic | |
| SWING FIT GOLF CLUB | Recreation/fitness | 7139 | Rule-Based | |
| T REX ARMS | Retail (ambiguous) | — | AI-Assisted Search | |
| TBD FOODS DBA GOLDEN CORRAL | Restaurant franchise | 7225 | Rule-Based | |
| TENNISPOINT | Sporting goods retail (online) | 4541 | Heuristic | |

---

## Commercial Services (Includes logistics, wholesale, software, professional services)

| Customer | Industry Detail | NAICS | Method | Domain |
|---|---|---:|---|---|
| PERFECTSERVE | Healthcare communications software | 5112 | Entity Inference | |
| PERFORMANCE FOOD SERVICE | Food distribution | 4244 | Entity Inference | |
| PFG CUSTOMIZED | Food distribution | 4244 | Entity Inference | |
| PG AND A / PGNA / PGNA | Ambiguous acronym | — | AI-Assisted Search | |
| PETRIA LOWENSTINE | Professional services (unclear) | — | AI-Assisted Search | |
| PITT AND FRANK | Professional services (unclear) | — | AI-Assisted Search | |
| PLANET XCHANGE | Recycling/IT? (unclear) | — | AI-Assisted Search | |
| PLUMBERS SUPPLY | Plumbing wholesale | 4237 | Rule-Based | |
| POWERSCHOOL GROUP | Education software | 5112 | Entity Inference | |
| PREMIER TRANSPORTATION | Transportation/logistics | 4841 | Rule-Based | |
| PRIDE DELIVERY AND INSTALLATION | Delivery/installation services | 4842 | Heuristic | |
| PRO LIFT | Equipment/material handling services | 5324 | Heuristic | |
| PRO ONCALL TECHNOLOGIES | IT/services (unclear) | — | AI-Assisted Search | |
| PROGRESSIVE LOGISTICS | Logistics | 4885 | Rule-Based | |
| PROMOTION | Ambiguous | — | AI-Assisted Search | |
| QUALITY CONTROLS | QA/testing services (unclear) | — | AI-Assisted Search | |
| QUANDELL GROUP | Construction services/engineering (unclear) | — | AI-Assisted Search | |
| QUEST DIAGNOSTICS LOUISVILLE | Clinical lab services | 6215 | Entity Inference | |
| QUESTAR | Ambiguous (utilities/telecom?) | — | AI-Assisted Search | |
| RAWLINGS GROUP | Healthcare services (subrogation/claims) | 5242 | Entity Inference | |
| RAYMOND JAMES | Financial services | 5231 | Entity Inference | |
| REECECAMPBELL | Professional services (unclear) | — | AI-Assisted Search | |
| RELIABLE TRANSMISSION SERVICE | Automotive repair/service | 8111 | Rule-Based | |
| REMAX | Real estate brokerage | 5312 | Entity Inference | |
| RENEWAL BY ANDERSEN | Home improvement services | 4441 | Entity Inference | |
| RESISTATEMPS | Products/services (unclear) | — | AI-Assisted Search | |
| RESULTANT | Consulting | 5416 | Entity Inference | |
| REXARC INTERNATIONAL | Industrial gases equipment/service | 3339 | Heuristic | |
| REYNOLDS FARM EQUIPMENT | Equipment dealer/service | 4238 | Heuristic | |
| RGBS ENTERPRISES | Ambiguous | — | AI-Assisted Search | |
| RITETRACK / RITWAY | Logistics/distribution (unclear) | — | AI-Assisted Search | |
| RIVERSIDE INDUSTRIAL SERVICES | Industrial services | 5617 | Rule-Based | |
| ROCKY TOP NUTRITION BILLING | Retail/health services (unclear) | — | AI-Assisted Search | |
| ROCKY TOP SPORTS WORLD | Sports complex | 7139 | Rule-Based | |
| ROYAL CANIN NORTH AMERICA | Pet food brand (mfg/distribution) | 3111 | Entity Inference | |
| ROYAL SERVICES | Services (unclear) | — | AI-Assisted Search | |
| RUDD EQUIPMENT | Heavy equipment dealer/service | 4238 | Entity Inference | |
| RUE GILT GROUPE | E-commerce retail | 4541 | Entity Inference | |
| RURALMETRO | EMS/ambulance services | 6219 | Entity Inference | |
| RUSH ENTERPRISES / RUSH TRUCK CENTERS | Truck dealer/service | 4412 | Entity Inference | |
| RUSTICI SOFTWARE | Software | 5112 | Entity Inference | |
| RYDER LOGISTICS (sites) | Logistics | 4931 | Entity Inference | |
| SAKSCOM | E-commerce/retail ops (unclear) | — | AI-Assisted Search | |
| SANDPIPER DATA SYSTEMS | IT/services (unclear) | — | AI-Assisted Search | |
| SCHENKER LOGISTICS SUITE A | Logistics | 4931 | Entity Inference | |
| SCHUMACHER DUGAN | Professional services (unclear) | — | AI-Assisted Search | |
| SCI | Ambiguous acronym | — | AI-Assisted Search | |
| SCOS | Ambiguous | — | AI-Assisted Search | |
| SEAPINE SOFTWARE | Software | 5112 | Entity Inference | |
| SEHLHORST EQUIPMENT SERVICES | Equipment services | 8113 | Heuristic | |
| SERVICE WHOLESALE | Wholesale distribution | 423 | Heuristic | |
| SESE INDUSTRIAL SERVICES US | Industrial services | 5617 | Rule-Based | |
| SHARES | Ambiguous | — | AI-Assisted Search | |
| SIBCY CLINE | Real estate services | 5312 | Entity Inference | |
| SIGS SPORTSPLEX | Sports facility | 7139 | Rule-Based | |
| SIMPSON ORGANIZATION | Corporate entity (unclear) | — | AI-Assisted Search | |
| SINGLETON COMPANIES | Ambiguous | — | AI-Assisted Search | |
| SKEENS WAREHOUSE SERVICES | Warehousing | 4931 | Rule-Based | |
| SKICO | Ambiguous | — | AI-Assisted Search | |
| SKILLED TRADES | Staffing/trades services | 5613 | Heuristic | |
| SL TENNESSEE | Ambiguous | — | AI-Assisted Search | |
| SLAMDOT | IT services | 5415 | Entity Inference | |
| SMART TECHNOLOGIES ULC | EdTech/technology | 5112 | Entity Inference | |
| SMOBEE | Ambiguous | — | AI-Assisted Search | |
| SOLID BLEND TECHNOLOGIES | Industrial services (unclear) | — | AI-Assisted Search | |
| SOLTECH | Technology/services (unclear) | — | AI-Assisted Search | |
| SOUTH COAST MANAGMENT | Property management (unclear) | 5313 | Heuristic | |
| SOUTH WESTERN COMMUNICATIONS | Telecom/services (unclear) | — | AI-Assisted Search | |
| SOUTHEASTERN ENVIRONMENTAL SOLUTIONS | Environmental services | 5629 | Rule-Based | |
| SOUTH CHARLESTON SANTIARY BOARD | Municipal utility board | 2213 | Rule-Based | |
| SOUTHERN TENNESEE REGIONAL | Healthcare or government (unclear) | — | AI-Assisted Search | |
| SPARKZ | Recreation/entertainment (unclear) | 7139 | Heuristic | |
| SPCA CINCINNATI | Animal nonprofit | 8133 | Rule-Based | |
| SPIRALEDGE DBA SWIMOUTLETCOM | E-commerce retail | 4541 | Heuristic | |
| SPOHN GLOBAL ENTERPRISES | Ambiguous | — | AI-Assisted Search | |
| SQUARE | Payments/fintech services | 5223 | Entity Inference | |
| SQUARE ROOTS URBAN GROWERS | Urban agriculture | 1114 | Heuristic | |
| SSSB | Ambiguous | — | AI-Assisted Search | |
| STATUS DOUGH | (listed above; may remain Retail/Hospitality) | 7225 | Heuristic | |
| STEP RESOURCES | Energy/resources (unclear) | — | AI-Assisted Search | |
| STEPTOE AND JOHNSON PLLC | Legal services | 5411 | Rule-Based | |
| STEWART TITLE OF CINCINNATI | Title/settlement services | 5411 | Heuristic | |
| STORD FULLFILLMENT | E-commerce fulfillment | 4931 | Entity Inference | |
| STRATA ENVIRONMETAL SERVICES | Environmental services | 5629 | Rule-Based | |
| STRATFORD | Ambiguous | — | AI-Assisted Search | |
| STOKELY HOSPITALITY ENTERPRISES | Hospitality operator | 7211 | Heuristic | |
| SUMMIT ENERGY SERVICES | Energy services | 2213 | Heuristic | |
| SUMMIT EXPRESS POWELL | Retail/service location (unclear) | — | AI-Assisted Search | |
| SUMMIT SUPPLY GROUP | Wholesale distribution | 4238 | Heuristic | |
| SUNBELT RENTALS (incl. climate control) | Equipment rental | 5324 | Entity Inference | |
| SUPERIOR AUTOMOTIVE GROUP | Auto dealer/group | 4411 | Rule-Based | |
| SUPERIOR CAR WASH SOLUTIONS | Car wash services | 8111 | Rule-Based | |
| SUPREMEX / SUPREMEX MIDWEST | Envelope/packaging | 3222 | Entity Inference | |
| SYSTECON / SYSTECON | Consulting/engineering (unclear) | — | AI-Assisted Search | |
| TECHMAH CMF | Ambiguous | — | AI-Assisted Search | |
| TEKWORX | Technology services | 5415 | Entity Inference | |
| TENBARGE | Ambiguous | — | AI-Assisted Search | |
| TENDER MERCIES | Nonprofit social services | 8133 | Entity Inference | |
| TERILLIUM | Consulting/technology | 5416 | Entity Inference | |
| TGT TRANSPORTATION | Transportation/logistics | 4841 | Rule-Based | |
| TERA DATA | Technology (unclear entity string) | — | AI-Assisted Search | |
| TEKWO RX | (covered as TEKWORX) | 5415 | Entity Inference | |

---

## Healthcare / Senior Living

| Customer | Industry Detail | NAICS | Method | Domain |
|---|---|---:|---|---|
| PROVISION CARES PROTON THERAPY CENTER | Specialty healthcare | 6211 | Rule-Based | |
| QUEST DIAGNOSTICS LOUISVILLE | Clinical lab services | 6215 | Entity Inference | |
| SUMMIT BHC | Behavioral health services | 6223 | Entity Inference | |
| SUNRISE MANOR | Senior living / nursing | 6231 | Heuristic | |
| TENNESSEE CANCER SPECIALISTS | Oncology practice | 6211 | Rule-Based | |
| TENNESSEE ENDOSCOPY CENTER | Outpatient endoscopy | 6214 | Rule-Based | |

---

## Public Schools (K–12) and Private Schools

| Customer | Industrial Group | Industry Detail | NAICS | Method |
|---|---|---|---:|---|
| REGENERATION BOND HILL SCHOOL | Public Schools (K–12) | School entity (verify public/charter) | 6111 | Heuristic |
| SAYRE SCHOOL | Private Schools (K–12) | Private school | 6111 | Rule-Based |
| SEVEN HILLS SCHOOL | Private Schools (K–12) | Private school | 6111 | Rule-Based |
| ST JOSEPH SCHOOL | Private Schools (K–12) | Private/parochial school | 6111 | Rule-Based |
| SYCAMORE COMMUNITY SCHOOLS | Public Schools (K–12) | Public school district | 6111 | Rule-Based |
| STS PETER AND PAUL EARLY CHILDHOOD CENTER | Private Schools (K–12) | Early childhood education | 6244 | Heuristic |

---

## Non-Profit / Religious / Civic

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| ROCK OF ISRAEL | Religious organization | 8131 | Rule-Based |
| SHARONVILLE CHAMBER OF COMMERCE | Chamber of commerce | 8139 | Rule-Based |
| SHELBYKY TOURISM COMMISSION AND VISITORS BUREAU | Tourism bureau | 8139 | Heuristic |
| SPRING GROVE CEMETERY | Cemetery (often nonprofit) | 8122 | Heuristic |
| SPRINGFIELD MUSEUM OF ART | Arts nonprofit | 7121 | Rule-Based |
| SPCA CINCINNATI | Animal nonprofit | 8133 | Rule-Based |
| ST WALBURG MONASTERY | Religious organization | 8131 | Rule-Based |
| TENDER MERCIES | Nonprofit social services | 8133 | Entity Inference |

---

## Needs AI-Assisted Search / Review Queue

The following entries are too ambiguous for reliable segmentation using keyword rules alone and should be routed to **Tier 3: AI-Assisted Search** (then optionally locked via manual override for high-value customers).

- PG AND A  
- PGNA  
- PGNA (duplicate)  
- PETRIA LOWENSTINE  
- PITT AND FRANK  
- PLANET XCHANGE  
- PRO ONCALL TECHNOLOGIES  
- PROMOTION  
- QUALITY CONTROLS  
- QUANDELL GROUP  
- QUESTAR  
- REECECAMPBELL  
- RESISTATEMPS  
- RGBS ENTERPRISES  
- RITETRACK  
- RITWAY  
- ROYAL SERVICES  
- SAKSCOM  
- SANDPIPER DATA SYSTEMS  
- SCHUMACHER DUGAN  
- SCI  
- SCOS  
- SHARES  
- SIMPSON ORGANIZATION  
- SINGLETON COMPANIES  
- SKICO  
- SL TENNESSEE  
- SMOBEE  
- SOLID BLEND TECHNOLOGIES  
- SOLTECH  
- SOUTHERN TENNESEE REGIONAL  
- SPOHN GLOBAL ENTERPRISES  
- SSSB  
- STEP RESOURCES  
- STRATFORD  
- SUMMIT EXPRESS POWELL  
- SYSTECON  
- TECHMAH CMF  
- TENBARGE  
- TERA DATA  
- THERMATRONX  

---

## Notes / Implementation Guidance

1. **Commercial Real Estate patterns** (OWNER, LP, PARTNERSHIP, BUILDING, INVESTMENTS) were treated as **Rule-Based** when clear.
2. **Education entities** were separated into Public vs Private only when the name is strongly indicative; otherwise marked **Heuristic**.
3. **NAICS values** are intentionally conservative and should be treated as supporting metadata.
4. **Domain resolution** should be run as a separate enrichment pass with confidence scoring (High/Med/Low) and should not overwrite verified domains.
