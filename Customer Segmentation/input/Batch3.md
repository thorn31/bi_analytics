# Customer Segmentation Output – Batch 3 (K → P) (v1)

This document applies the **Customer Classification & Segmentation Specification (v1)** to the provided customer list.

## Output Fields
- **Industrial Group**: Locked vertical segment (one per customer entity)
- **Industry Detail**: Short context label
- **NAICS**: Reference classification (text; typically 2–4 digit unless unambiguous)
- **Method**:
  - **Rule-Based**: Deterministic keyword/pattern match
  - **Entity Inference**: Widely recognized organization/brand
  - **AI-Assisted Search**: Ambiguous; requires lookup/semantic search
  - **Heuristic**: Weak-signal best guess; reviewable
- **Domain**: Not included in this batch (domain resolution is a separate enrichment pass)

---

## Public Schools (K–12)

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| KINGS LOCAL SCHOOLS | Public school district | 6111 | Rule-Based |
| MSD OF GREATER CINCINNATI | Public school district | 6111 | Rule-Based |
| PARIS INDEPENDENT SCHOOLS | Public school district | 6111 | Rule-Based |

---

## Private Schools (K–12)

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| OAK HILL SCHOOL | Private/parochial school (verify) | 6111 | Heuristic |

---

## Municipal / Government / Public Sector

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| OAK RIDGE NATIONAL LABORATORY | Federal research laboratory | 5417 | Entity Inference |
| ORSANCO | Regional commission/public authority | 9211 | Heuristic |
| OHIO VALLEY EDUCATIONAL COOPERATIVE | Education cooperative | 6117 | Rule-Based |

---

## Healthcare / Senior Living

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| LIBERTY DIALYSIS OF NORWOOD | Dialysis clinic | 6214 | Rule-Based |
| LOUISVILLE ENDOSCOPY CENTER | Outpatient endoscopy | 6214 | Rule-Based |
| MIDWEST EYE INSTITUTE | Eye care / clinic | 6213 | Rule-Based |
| NEPTUNE EYE | Eye care (verify) | 6213 | Heuristic |
| NORTHERN KY ORTHOPAEDICS | Orthopedics practice | 6211 | Rule-Based |
| NORTHERN KENTUCKY EYECARE | Eye care | 6213 | Rule-Based |
| ORTHOPEDIC SPORTS MEDICINE | Ortho / sports medicine | 6211 | Rule-Based |
| PAIN TREATMENT CENTER | Pain management clinic | 6211 | Rule-Based |
| OTTERBEIN HOMES | Senior living | 6233 | Entity Inference |
| MORNING POINTE | Senior living | 6233 | Entity Inference |
| MYRIAD GENETICS | Clinical/genetic testing | 6215 | Entity Inference |
| MEDPACE | Clinical research organization | 5417 | Entity Inference |

---

## Non-Profit / Religious / Community

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| LOUISVILLE CENTRAL COMMUNITY CENTER | Community nonprofit | 8133 | Rule-Based |
| NEW HOPE OF INDIANA | Social services nonprofit | 8133 | Heuristic |
| OVER THE RHINE COMMUNITY HOUSING | Community housing nonprofit | 8133 | Rule-Based |
| PEOPLE WORKING COOPERATIVELY | Social services nonprofit | 8133 | Rule-Based |
| PEASLEE NEIGHBORHOOD CENTER | Community nonprofit | 8133 | Rule-Based |
| PARIS BOURBON COUNTY YMCA | YMCA nonprofit | 8134 | Rule-Based |
| ME LYONS YMCA | YMCA nonprofit | 8134 | Rule-Based |
| MAYERSON JCC | Community center nonprofit | 8134 | Heuristic |

---

## Commercial Real Estate

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| KPA NIGHTINGALE LANE | Property entity (address/LP-style) | 5311 | Rule-Based |
| LAME INVESTMENTS | Investment/property entity | 5311 | Heuristic |
| LAND OAK 2 | Property entity | 5311 | Rule-Based |
| LANDEN SQUARE 3 | Property entity | 5311 | Rule-Based |
| LANDMARK CENTER | Property entity | 5311 | Rule-Based |
| LAZARUS PARTNERSHIP NMP | Partnership/property entity | 5311 | Rule-Based |
| LINDYDAYTON TOWERS | Property entity | 5311 | Rule-Based |
| LINK LOGISTICS | Logistics real estate (industrial) | 5311 | Entity Inference |
| LOUISVILLE PUBLC WAREHOUSE DBA AMERICA PLACE | Warehouse property/operations (verify owner/operator) | 4931 | Heuristic |
| MAGNOLIA CAPITAL INVESTMENTS | Investment/property entity | 5311 | Heuristic |
| MAGNOLIA CHEROKEE MILLS LP | Property LP | 5311 | Rule-Based |
| MAGNOLIA HILLSBORO LP | Property LP | 5311 | Rule-Based |
| MATT WARREN RENTAL | Property rental entity | 5311 | Rule-Based |
| MATT WILLIAMS RESIDENCE | Residential entity | 5311 | Rule-Based |
| MELROSE PLACE … GP DBA MELROSE PLACE | Property entity | 5311 | Rule-Based |
| MIDAMERICA MGMTWEST CRESCENTVILLE | Property mgmt/entity | 5313 | Heuristic |
| MIDSOUTH BUILDING III REIT | REIT/property entity | 5311 | Rule-Based |
| MQ BUILDING | Property entity | 5311 | Rule-Based |
| MOUNT VERNON DEVELOPMENTAL CENTER | Govt/health (ambiguous) | — | AI-Assisted Search |
| MURPHY RESIDENCE | Residential entity | 5311 | Rule-Based |
| NASHVILLE OFFICE 1 | Office property entity | 5311 | Rule-Based |
| NDH REIT OP LP | REIT property entity | 5311 | Rule-Based |
| NP DAYON BUILDING VIII / NP DWBA / NP FTC LLL | Property entities | 5311 | Rule-Based |
| ONEC1TY | Mixed-use development (verify) | 5311 | Heuristic |
| OLYMBEC USA | Industrial real estate (verify) | 5311 | Heuristic |
| PARK PLACE AT LYTLE | Property entity | 5311 | Rule-Based |
| PARKSTONE INDIANAPOLIS | Property entity | 5311 | Rule-Based |
| PEACOCK NORTHGATE | Property entity | 5311 | Rule-Based |

---

## Construction / Mechanical / Building Trades

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| KODIAK CONSTRUCTORS | Contractor | 2362 | Rule-Based |
| LABOR WORKS | Trades/labor services | 5613 | Rule-Based |
| LANDMARK SPRINKLER | Fire sprinkler contractor | 2382 | Rule-Based |
| LATHAM MECHANICAL | Mechanical contractor | 2382 | Rule-Based |
| LICHTENBERG CONSTRUCTION | Contractor | 2362 | Rule-Based |
| LITHKO CONTRACTING | Concrete contractor | 2381 | Entity Inference |
| LEN RIEGLER BLACKTOP | Paving/asphalt | 2373 | Rule-Based |
| MATTAR ELECTIC | Electrical contractor | 2382 | Rule-Based |
| MECHANICAL SYSTEMS OF DAYTON | Mechanical contractor | 2382 | Rule-Based |
| METAL TECH BUILDING SPECIALISTS | Metal building contractor | 2362 | Rule-Based |
| MILESTONE CONTRACTORS | Civil contractor | 2373 | Entity Inference |
| NASHVILLE SHEET METAL | Sheet metal/HVAC | 2381 | Rule-Based |
| OHIO VALLEY ELECTRICAL SERVICES | Electrical contractor | 2382 | Rule-Based |
| OROURKE WRECKING | Demolition contractor | 2389 | Rule-Based |
| OVERHEAD DOOR OF GREATER CINCINNATI | Overhead doors contractor | 2382 | Entity Inference |
| PATTI ENGINEERING | Engineering services | 5413 | Rule-Based |

---

## Manufacturing (includes defense/aerospace and industrial)

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| KIMBALL ELECTRONICS | Electronics manufacturing | 3344 | Entity Inference |
| KNAUF INSULATION | Insulation manufacturing | 3279 | Entity Inference |
| KOBE ALUMINUM AUTOMOTIVE PRODUCTS | Automotive aluminum components | 3363 | Entity Inference |
| KOBELCO ALUMINUM | Aluminum manufacturing | 3313 | Entity Inference |
| KOCH FOODS | Poultry/food manufacturing | 3116 | Entity Inference |
| L3 FUZING AND ORDNANCE SYSTEMS | Defense manufacturing | 3329 | Entity Inference |
| L3 HARRIS TECHNOLOGIES | Defense/aerospace | 3364 | Entity Inference |
| LENNOX INDUSTRIES | HVAC equipment manufacturing | 3334 | Entity Inference |
| LINK BELT CRANES | Crane manufacturing | 3331 | Entity Inference |
| LIPPERT COMPONENTS | RV/transport components | 3363 | Entity Inference |
| LOREAL USA | Consumer products manufacturing | 3256 | Entity Inference |
| LOUISVILLE BEDDING | Bedding manufacturing | 3379 | Heuristic |
| M AND H CABINETS | Millwork/cabinets manufacturing | 3371 | Heuristic |
| MALIBU BOATS | Boat manufacturing | 3366 | Entity Inference |
| MARBLE PRODUCTS INTERNATIONAL | Stone products | 3279 | Heuristic |
| MARS CHOCOLATE | Confectionery manufacturing | 3113 | Entity Inference |
| MARTINREA HEAVY STAMPING | Automotive stamping | 3363 | Entity Inference |
| MASONITE | Doors manufacturing | 3219 | Entity Inference |
| MAZAK | Machine tools manufacturing | 3335 | Entity Inference |
| MBX BIOSCIENCES | Biotech (verify mfg vs R&D) | 3254 | Heuristic |
| MILACRON / MILACRON PLASTICS TECHNOLOGY GROUP | Plastics machinery | 3332 | Entity Inference |
| MILLAT INDUSTRIES | Manufacturing (unclear) | — | AI-Assisted Search |
| MITSUI KINZOKU CATALYSTS AMERICA | Chemical catalysts | 325 | Entity Inference |
| MOELLER PRECISION TOOL | Precision machining | 3327 | Entity Inference |
| MONDELEZ GLOBAL | Food manufacturing | 311 | Entity Inference |
| MORGAN FOODS | Food manufacturing | 311 | Entity Inference |
| MTM MOLDED PRODUCTS | Plastics manufacturing | 3261 | Heuristic |
| MUBEA | Automotive components | 3363 | Entity Inference |
| MULTICOLOR | Labels/packaging printing | 3231 | Entity Inference |
| MUNDET TENNESSEE | Plastics/packaging (verify) | 3261 | Heuristic |
| MURAKAMI USA | Automotive components | 3363 | Heuristic |
| NESTLE USA | Food manufacturing | 311 | Entity Inference |
| NEWLY WEDS FOODS | Food manufacturing | 311 | Entity Inference |
| NEWPAGE | Paper manufacturing | 3221 | Entity Inference |
| NIAGARA BOTTLING | Beverage manufacturing | 3121 | Entity Inference |
| NITTO | Industrial materials (verify entity) | 325 | Heuristic |
| NORITAKE USA | Ceramics/industrial materials | 327 | Entity Inference |
| NORTH AMERICAN STAINLESS | Steel manufacturing | 3311 | Entity Inference |
| NORTHROP GRUMMAN | Defense/aerospace | 3364 | Entity Inference |
| NORTHROPGRUMMANXETRON | Defense/aerospace (sub-entity) | 3364 | Entity Inference |
| OBARA | Welding automation (verify) | 3339 | Heuristic |
| OGARA HESS AND EISENHARDT ARMORING | Vehicle armoring | 3369 | Entity Inference |
| OTICS USA | Manufacturing (unclear) | — | AI-Assisted Search |
| PCS PURIFIED PHOSPHATES | Chemical processing | 325 | Heuristic |
| PD PHARMATECH | Pharmaceutical equipment/services | 3339 | Heuristic |
| PEPSIAMERICAS | Beverage (distribution/manufacturing) | 3121 | Entity Inference |
| PEPSICO | Food/beverage manufacturing | 311/312 | Entity Inference |

---

## Retail / Hospitality

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| LAND ROVER OF KNOXVILLE | Auto dealership | 4411 | Rule-Based |
| LANCE CUNNINGHAM FORD | Auto dealership | 4411 | Rule-Based |
| LAST STOP BREWING | Brewery/taproom | 3121 | Rule-Based |
| LEMON D BIKES (LEMOND BIKES) | Retail/brand (verify) | — | AI-Assisted Search |
| LEMS SHOES | Footwear retail/brand | 4482 | Heuristic |
| LES NAILS AND SPA | Nail salon | 8121 | Rule-Based |
| LESLIES SALON | Salon | 8121 | Rule-Based |
| LETS PLAY SPORTS | Recreation/retail (unclear) | 7139 | Heuristic |
| LEVEL UP GAMES AND HOBBIES | Hobby retail | 4511 | Rule-Based |
| LOWES | Home improvement retail | 4441 | Entity Inference |
| LUCAS OIL LATE MODEL DIRT SERIES | Sports/entertainment | 7113 | Heuristic |
| LULULEMON / LULULEMON USA | Apparel retail | 4481 | Entity Inference |
| LUXOTTICA RETAIL | Optical retail | 4461 | Entity Inference |
| MACYS BACKSTAGE DISTRIBUTION CENTER | Retail distribution | 4931 | Entity Inference |
| MAGNUM PIERCING | Body art services | 8121 | Rule-Based |
| MAYDAY BREWERY | Brewery/taproom | 3121 | Rule-Based |
| MCSCROOGES WINES AND SPIRITS | Alcohol retail | 4453 | Rule-Based |
| MIAMI VALLEY GAMING AND RACING | Gaming/casino | 7132 | Entity Inference |
| MONOPRICE | E-commerce retail | 4541 | Entity Inference |
| MONSTER GOLF | Recreation/entertainment | 7139 | Rule-Based |
| MOONSHINE MOUNTAIN COOKIE | Food service/retail | 7225 | Heuristic |
| MORE THAN A BAKERY | Bakery/food service | 7225 | Rule-Based |
| N SALON | Salon | 8121 | Rule-Based |
| NAILS DESIRE | Nail salon | 8121 | Rule-Based |
| OLD TIME POTTERY / OLD TIME POTTERY BILLING | Retail | 4422 | Entity Inference |
| OLIVE GARDEN | Restaurant | 7225 | Entity Inference |
| OLLIES BARGAIN OUTLET | Discount retail | 4523 | Entity Inference |
| OUTPOST ARMORY | Retail (firearms-related; classify only) | 4539 | Rule-Based |
| PANDORA JEWELLERY (incl. PANDORA S9) | Jewelry retail | 4483 | Entity Inference |
| PASTELITOS CUBAN BAKERY | Bakery/food service | 7225 | Rule-Based |
| PAW PET ADVENTURES WORLDWIDE | Pet services (unclear) | — | AI-Assisted Search |
| PEBBLE BROOK GOLF CLUB | Golf club | 7139 | Rule-Based |
| PEPOS BURRITO BAR 2 | Restaurant | 7225 | Rule-Based |

---

## Commercial Services (Logistics, Distribution, Professional)

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| KINNECTION CHIROPRACTIC | Chiropractic clinic | 6213 | Rule-Based |
| KKT CHILLERS | HVAC equipment/services (unclear) | — | AI-Assisted Search |
| KLH ENGINEERS | Engineering services | 5413 | Rule-Based |
| KOHRS LONNEMANN HEIL ENGINEERS | Engineering services | 5413 | Rule-Based |
| KT DESIGN GROUP | Design/architecture (unclear) | 5414 | Heuristic |
| LA COMEDIA ENTERPRISES | Performing arts/venue | 7111 | Heuristic |
| LAW OFFICE OF C M WATSON | Legal services | 5411 | Rule-Based |
| LBMC KNOXVILLE CPA ADVISORS AND CONSULTANTS | Accounting/consulting | 5412 | Rule-Based |
| LCNB | Banking/financial services | 5221 | Entity Inference |
| LEE / LELLYETT AND ROGERS / LEWIS THOMASON | Legal services (verify names) | 5411 | Heuristic |
| LEOPARDO COMPANIES | Property/contracting (unclear) | — | AI-Assisted Search |
| LEVEL UP GAMES AND HOBBIES | (also retail; kept retail above) | 4511 | Rule-Based |
| LIBERTY MARKING SYSTEMS | Industrial marking equipment/services | 3339 | Heuristic |
| LINKS UNLIMITED | Promotional products/services | 5418 | Heuristic |
| LIQUIDITY SERVICES | Asset recovery/auctions | 5619 | Entity Inference |
| LW OFFICE FURNITURE WAREHOUSE | Office furniture distribution | 4232 | Rule-Based |
| MAC PAPERS NASHVILLE | Paper distribution | 4241 | Rule-Based |
| MACOMB GROUP | Industrial supply distribution | 4238 | Heuristic |
| MCLANE / MCLANE DISTRIBUTION / MCLANE FOODSERVICE DISTRIBUTION | Wholesale distribution | 4244 | Entity Inference |
| MECO | Services/manufacturing (unclear) | — | AI-Assisted Search |
| MEDIC DBA MEDIC REGIONAL BLOOD CENTER | Blood center | 6219 | Rule-Based |
| MEGACITY OF CINCINNATI | Ambiguous | — | AI-Assisted Search |
| MELALEUCA | Consumer products (direct sales) | 4543 | Heuristic |
| MELINK / MELINK SOLAR | Energy efficiency services | 5413 | Heuristic |
| METAL IMPROVEMENT | Metal fabrication/services | 3323 | Heuristic |
| METALKRAFT COACHWERKES | Vehicle upfitting | 3363 | Heuristic |
| METZCOR | Ambiguous | — | AI-Assisted Search |
| MIDPARK KNOXVILLE | Business entity (unclear) | — | AI-Assisted Search |
| MIDWEST FINISHING SYSTEMS | Industrial finishing services | 3328 | Heuristic |
| MIDWEST MOLD AND TEXTURE | Mold/texturing services | 3335 | Heuristic |
| MIDWEST SEA SALT | Food/wholesale (unclear) | — | AI-Assisted Search |
| MIKE ALBERT | Fleet/leasing services | 5321 | Entity Inference |
| MILLAN ENTERPRISES (incl. BILLING) | Ambiguous | — | AI-Assisted Search |
| MILLER VALENTINE GROUP | Real estate development/services | 5313 | Entity Inference |
| MILLERS TEXTILE SERVICES | Textile rental services | 8123 | Entity Inference |
| MOMENTUM | Ambiguous | — | AI-Assisted Search |
| MONAIRE | HVAC services (unclear) | — | AI-Assisted Search |
| MOTION INDUSTRIES | Industrial parts distribution | 4238 | Entity Inference |
| MOUNTAIN LINEN SERVICE | Linen services | 8123 | Rule-Based |
| MOUNTAIN VALLEY PIPELINE | Pipeline operator | 4862 | Entity Inference |
| MUELLER | Manufacturing/distribution (too broad) | — | AI-Assisted Search |
| MURPHY TRACTOR AND EQUIPMENT | Heavy equipment dealer | 4238 | Rule-Based |
| NUCO2 | Beverage gas services | 4246 | Entity Inference |
| NASCO | Distribution/education supplies (unclear) | — | AI-Assisted Search |
| NATIONAL CITY EQUIPMENT FINANCE | Equipment finance | 5222 | Rule-Based |
| NATIONAL INDOOR RV CENTER | RV sales/service | 4412 | Rule-Based |
| NEHEMIAH | Nonprofit/education (unclear) | — | AI-Assisted Search |
| NEOGEN | Life sciences/testing | 5417 | Entity Inference |
| NETFOR | Staffing/services (unclear) | — | AI-Assisted Search |
| NEXT GENERATION CHILDCARE | Childcare | 6244 | Rule-Based |
| NLIGN ANALYTICS ETEGENT | Ambiguous | — | AI-Assisted Search |
| NNODUM PHARMACEUTICALS | Pharma (unclear) | — | AI-Assisted Search |
| NORTHERN KENTUCKY ASSOCIATION OF REALTORS | Trade association | 8139 | Rule-Based |
| ODW LOGISTICS | Logistics/3PL | 4931 | Entity Inference |
| OFFICE FURNITURE SOURCE | Office furniture distribution | 4232 | Rule-Based |
| OIA GLOBAL | Logistics/freight forwarding | 4885 | Entity Inference |
| OMNIA360 FACILITY SOLUTIONS | Facilities services (unclear) | — | AI-Assisted Search |
| OAK RIDGE LOCKSMITH | Locksmith services | 5616 | Rule-Based |
| ON DISPLAY | Ambiguous | — | AI-Assisted Search |
| OPTIMIRA ENERGY | Energy services (unclear) | — | AI-Assisted Search |
| OSWALD | Insurance services (likely) | 5242 | Heuristic |
| OTC INDUSTRIAL TECHNOLOGIES | Industrial distribution | 4238 | Entity Inference |
| PALM RIDGE CAPITAL GROUP | Investment entity | 5239 | Heuristic |
| PALMER CONSERVATION CONSULTING | Consulting | 5416 | Rule-Based |
| PAM SPRAGUEDAVE COLLINS | Person/entity ambiguous | — | AI-Assisted Search |
| PANORAMA | Ambiguous | — | AI-Assisted Search |
| PASSAGEWAYS DBA ONBOARD | Services (unclear) | — | AI-Assisted Search |
| PATHOLOGY AND CYTOLOGY LAB | Medical lab | 6215 | Rule-Based |
| PATRICK SHAAD | Individual | — | Rule-Based |
| PEACE COMMUNICATIONS | Telecom/IT (unclear) | — | AI-Assisted Search |
| PEARSON VUE (INDY/LEX) | Testing services | 6117 | Entity Inference |
| PENTAGON GROUP | Ambiguous | — | AI-Assisted Search |
| PEPSICO NASS ACCOUNTS PAYABLES | Corporate AP entity | 311/312 | Entity Inference |

---

## Internal / Related Entities (Perfection Group)

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| PERFECTION GROUP | Your organization (internal) | — | Manual Override |
| PERFECTION MECHANICAL | Mechanical contractor (internal brand) | 2382 | Manual Override |
| PERFECTION SERVICES | Services (internal brand) | — | Manual Override |
| PERFECTION PRINTING | Printing services (internal/affiliate?) | 3231 | Heuristic |

---

## Individuals (Rule-Based)

| Customer | Industry Detail | NAICS | Method |
|---|---|---:|---|
| KIM M ORTMAN | Individual | — | Rule-Based |
| MARK LAUGHNER | Individual | — | Rule-Based |
| MARY K BRIGGS | Individual | — | Rule-Based |
| MARYANN STRALEY | Individual | — | Rule-Based |
| MEGAN CARTY | Individual | — | Rule-Based |
| MERLIN KING | Individual (verify) | — | Heuristic |
| ROBERT SEAGO | Individual | — | Rule-Based |

---

## Needs AI-Assisted Search / Review Queue

Use Tier 3 (AI-assisted search) for these before you rely on them for vertical revenue reporting:

- KINDEVA  
- KKT CHILLERS  
- KPPE  
- LAME INVESTMENTS (if material)  
- LANDFORM  
- LAWRENCE BROTHERS  
- LCNB (if you want sub-vertical within Financial Services)  
- LEE / LELLYETT AND ROGERS (confirm legal vs other)  
- LEMON D BIKES / LEMON D COMPOSITES (confirm entities)  
- LEOPARDO COMPANIES  
- LHP TELEMATIC  
- LATONIA BULK  
- LIMA USA  
- MANTIS INNOVATION  
- MARKSBURY FARM (farm vs brand)  
- MASS MARKETING  
- MASSEY SERVICES  
- MASTERS PHARMACEUTICALS  
- MASTRONARDI BEREA  
- MATRIX TECHNOLOGIES  
- MBM REFRIGERATION  
- MBX BIOSCIENCES (verify)  
- MCH  
- MECO  
- MEGACITY OF CINCINNATI  
- METZCOR  
- MIDPARK KNOXVILLE  
- MIDWEST SEA SALT  
- MILLAT INDUSTRIES  
- MOMENTUM  
- MONAIRE  
- MUELLER  
- NASCO  
- NEHEMIAH  
- NETFOR  
- NLIGN ANALYTICS ETEGENT  
- NNODUM PHARMACEUTICALS  
- OBARA  
- OMNIA360 FACILITY SOLUTIONS  
- ONEC1TY  
- OLYMBEC USA  
- ON DISPLAY  
- OPTIMIRA ENERGY  
- OSBORN ENTERPRISES  
- PAM SPRAGUEDAVE COLLINS  
- PANORAMA  
- PASSAGEWAYS DBA ONBOARD  
- PAW PET ADVENTURES WORLDWIDE  
- PEACE COMMUNICATIONS  
- PENTAGON GROUP  

---

## Notes / Implementation Guidance

1. “OWNER / LP / REIT / BUILDING / RESIDENCE” patterns are treated as **Commercial Real Estate** via Rule-Based logic.
2. Recognizable national brands are **Entity Inference**.
3. NAICS is intentionally conservative and should be treated as supporting metadata.
4. Domain resolution should be run separately with confidence scoring and caching/override rules.
