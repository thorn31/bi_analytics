# Customer Segmentation Output – Pilot Batch (v1)

This document applies the **Customer Classification & Segmentation Specification (v1)** to the provided customer list.

Fields:
- **Industrial Group**: Locked vertical segment
- **Industry Detail**: Human-readable refinement
- **NAICS**: Reference classification (2–4 digit, text)
- **Method**: How classification was determined
- **Domain**: Returned only when high confidence

---

## Manufacturing

| Customer | Industry Detail | NAICS | Method | Domain |
|--------|-----------------|-------|--------|--------|
| THYSSENKRUPP BILSTEIN | Automotive shock absorbers | 336390 | Entity Inference | |
| TOPURA AMERICA FASTENER | Industrial fasteners | 332722 | Heuristic | |
| TPG PLASTICS | Plastics manufacturing | 326199 | Heuristic | |
| TRANE | HVAC equipment manufacturing | 333415 | Entity Inference | trane.com |
| TRIM PARTS | Automotive components | 336390 | Heuristic | |
| TSUDA USA | Automotive components | 336390 | Heuristic | |
| TUFF TORQ | Power transmission components | 333612 | Heuristic | |
| UBE AUTOMOTIVE NORTH AMERICA | Automotive components | 336390 | Heuristic | |
| UGN | Automotive components | 336390 | Heuristic | |
| UPM PHARMACEUTICALS | Pharmaceutical manufacturing | 325412 | Heuristic | |
| UST DBA LANDMARK CERAMICS | Ceramic tile manufacturing | 327122 | Heuristic | |
| USUI INTERNATIONAL | Automotive components | 336390 | Heuristic | |
| UTC AEROSPACE SYSTEMS | Aerospace components | 336413 | Entity Inference | |
| VALASSIS DIRECT MAIL | Printing & marketing services | 323111 | Heuristic | |
| VALEO | Automotive systems | 336390 | Entity Inference | valeo.com |
| VALEO CLIMATE CONTROL | Automotive thermal systems | 336390 | Entity Inference | valeo.com |
| VALTRONICS | Electronics manufacturing | 334419 | Heuristic | |
| VANDERBILT CHEMICALS | Specialty chemicals | 325998 | Entity Inference | vanderbiltchemicals.com |
| VENTRA PLASTICS (FLEX-N-GATE) | Automotive plastics | 326199 | Entity Inference | |
| VIKING PLASTICS | Plastics manufacturing | 326199 | Heuristic | |
| VINYLMAX | Windows & doors | 321911 | Heuristic | |
| VYTRON | Electronics manufacturing | — | AI-Assisted Search | |
| WABTEC | Rail & industrial equipment | 336510 | Entity Inference | wabteccorp.com |
| WAUPACA FOUNDRY | Metal casting | 331511 | Heuristic | |
| WESTROCK | Packaging & paper | 322211 | Entity Inference | westrock.com |
| WESTROCK CINCINNATI | Packaging & paper | 322211 | Entity Inference | westrock.com |
| WOODGRAIN DOOR SHOP | Millwork & doors | 321911 | Heuristic | |
| WOODLAWN RUBBER | Rubber products | 326299 | Heuristic | |
| YANFENG GLOBAL AUTOMOTIVE INTERIORS | Automotive interiors | 336360 | Entity Inference | |
| YAPP USA AUTOMOTIVE SYSTEMS | Automotive fuel systems | 336390 | Heuristic | |
| YKK AP | Architectural fenestration | 321911 | Entity Inference | ykkap.com |
| ZF BOGE ELASTMETALL | Automotive components | 336390 | Entity Inference | |
| ZF NORTH AMERICA | Automotive components | 336390 | Entity Inference | |
| ZF STEERING SYSTEMS | Automotive steering systems | 336390 | Entity Inference | |

---

## Construction / Mechanical Contractors

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| THREE RIVERS SHEET METAL | Sheet metal & HVAC | 238160 | Rule-Based |
| TP MECHANICAL | Mechanical contractor | 238220 | Rule-Based |
| TOTAL RESTORATION SOLUTIONS | Building restoration | 236118 | Rule-Based |
| TRI STATE MECHANICAL | Mechanical contractor | 238220 | Rule-Based |
| VFP FIRE SYSTEMS | Fire protection systems | 238290 | Rule-Based |
| VOLUNTEER MECHANICAL | Mechanical contractor | 238220 | Rule-Based |

---

## Energy Services

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| UK CENTER FOR APPLIED ENERGY RESEARCH | Energy research institute | 541715 | Rule-Based |
| VEREGY INDIANA | Energy services / ESCO | 221330 | Entity Inference |

---

## Commercial Real Estate

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| TOWER CONDOMINIUMS | Condominium ownership | 531110 | Rule-Based |
| TLP 117 COLLINS | Property holding entity | 531120 | Rule-Based |
| TUFF 2200 SUTHERLAND AVE | Property holding entity | 531120 | Rule-Based |
| UNION ODC BREP I | Property ownership | 531120 | Heuristic |
| UNION STATION | Property ownership | 531120 | Heuristic |
| UNIVERISTY TOWER | Property ownership | 531120 | Rule-Based |
| URBAN SITES | Real estate development | 236220 | Heuristic |
| VICTORIAN SQUARE | Property ownership | 531120 | Heuristic |
| WATKINS ROAD OWNER | Property ownership | 531120 | Rule-Based |
| WEST HIGH ST INVESTMENTS | Property investment | 531120 | Heuristic |
| WESTERN PLAZA / WP GENERAL PARTNERSHIP | Shopping center ownership | 531120 | Rule-Based |

---

## Retail / Hospitality

| Customer | Industry Detail | NAICS | Method | Domain |
|--------|-----------------|-------|--------|--------|
| THIRD EYE BREWING | Brewery / taproom | 312120 | Rule-Based | |
| YEE HAW BREWING | Brewery / taproom | 312120 | Rule-Based | |
| TOPGOLF | Entertainment venue | 713990 | Entity Inference | |
| TOPGOLF NASHVILLE | Entertainment venue | 713990 | Entity Inference | |
| TOWN AND COUNTRY FORD | Auto dealership | 441110 | Rule-Based | |
| TRACTOR SUPPLY | Farm & ranch retail | 444130 | Entity Inference | tractorsupply.com |
| TRIPLE HEARTS DBA TACK HOUSE PUB | Restaurant / pub | 722511 | Rule-Based | |
| WINE SHOP | Specialty retail | 445310 | Rule-Based | |
| WOODCRAFT SUPPLY | Specialty retail | 444130 | Rule-Based | |
| WAYFAIR (all locations) | E-commerce retail | 454110 | Entity Inference | wayfair.com |

---

## Commercial Services

| Customer | Industry Detail | NAICS | Method | Domain |
|--------|-----------------|-------|--------|--------|
| THIRD ROCK CONSULTANTS | Management consulting | 541690 | Rule-Based | |
| THOMPSON HINE LLP | Legal services | 541110 | Rule-Based | |
| TITLE BOXING CLUB | Fitness services | 713940 | Rule-Based | |
| TKO GRAPHIX | Printing & graphics | 323111 | Rule-Based | |
| TLG PETERBILT | Truck sales & service | 441228 | Rule-Based | |
| TRANSPORT INTERNATIONAL POOL | Transportation asset pooling | 488510 | Heuristic | |
| U-HAUL | Moving & storage | 484210 | Entity Inference | uhaul.com |
| ULINE | Industrial supplies distribution | 424690 | Entity Inference | uline.com |
| UNIFIRST | Uniform rental services | 812332 | Entity Inference | unifirst.com |
| UNITED STATES COLD STORAGE | Cold storage logistics | 493120 | Rule-Based | |
| US FOOD SERVICE (KNOXVILLE) | Food distribution | 424490 | Rule-Based | |
| US HAZMAT RENTALS | Equipment rental | 532490 | Rule-Based | |
| WAREHOUSE OPTIMIZERS | Warehouse consulting | 541614 | Rule-Based | |
| XTRALEASE | Equipment leasing | 532120 | Rule-Based | |
| WVLT TV CHANNEL 8 | Television broadcasting | 515120 | Rule-Based | |

---

## Telecommunications

| Customer | Industry Detail | NAICS | Method | Domain |
|--------|-----------------|-------|--------|--------|
| US CELLULAR | Wireless telecommunications | 517312 | Entity Inference | uscellular.com |

---

## Healthcare / Senior Living

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| TRIPLE CREEK RETIREMENT | Senior living | 623312 | Rule-Based |
| VANDERBILT MAURY RADIATION ONCOLOGY | Radiation oncology | 621111 | Rule-Based |
| VISION BEST EYE CARE | Optometry | 621320 | Rule-Based |
| WESLEY VILLAGE | Senior living | 623312 | Heuristic |
| WILLIAMSON MEMORIAL | Hospital system | 622110 | Heuristic |

---

## Public Schools (K–12)

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| TIPPECANOE SCHOOL | Public school | 611110 | Rule-Based |
| WILLIAMSBURG SCHOOLS | Public school district | 611110 | Rule-Based |
| WILLIAMSTOWN INDEPENDENT SCHOOL | Public school district | 611110 | Rule-Based |
| WINTON WOODS SCHOOLS | Public school district | 611110 | Rule-Based |
| XENIA COMMUNITY SCHOOLS BUSINESS OFFICE | Public school district | 611110 | Rule-Based |

---

## Private Schools (K–12)

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| WEBB SCHOOL OF KNOXVILLE | Private school | 611110 | Rule-Based |

---

## Non-Profit / Religious

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| YMCA | Non-profit recreation | 813410 | Rule-Based |
| YMCA OF GREATER CINCINNATI | Non-profit recreation | 813410 | Rule-Based |
| YMCA OF HARRISON COUNTY | Non-profit recreation | 813410 | Rule-Based |
| VICTORIA THEATRE ASSOCIATION | Performing arts nonprofit | 813990 | Rule-Based |
| WESTMINSTER NEIGHBORHOOD SERVICES | Community services nonprofit | 813319 | Rule-Based |

---

## Individual / Misc

| Customer | Industry Detail | NAICS | Method |
|--------|-----------------|-------|--------|
| THOMAS OVERTON | Individual | — | Rule-Based |

---

## Requires AI-Assisted Search (High Ambiguity)

These entities require Tier-3 AI-assisted lookup before confident segmentation:

- THOTH  
- THOMA AND SUTTON OFC  
- THOMAS CLARK SOLUTIONS  
- TIPTON INTEREST  
- TIPTON MILLS FOODS  
- TOLSMA LEGACY TRUST  
- TOMZ  
- TOPY AMERICA  
- TRADE MARK INDUSTRIAL  
- TRANZONIC COMPANIES  
- TREALITY SVS  
- TRENWA  
- TRILOGY  
- TTGROUP AMERICA  
- UNLIMITED SYSTEMS  
- VALCOM ENTERPRISES  
- VALIDATED CUSTOM SOLUTIONS  
- VALS BOTIQUE  
- VIOX SERVICES  
- VRC  
- WALKER / WALKER SCM AELSPAN  
- WIEDEMANN  
- WISCHMEIER TRANSPORTATION SOLUTIONS  
- YH AMERICA  
- YSK / YUSA  

---

## Notes

- Domains are intentionally omitted unless confidence is high.
- NAICS is supporting metadata and does not drive segmentation.
- Method indicates governance posture and review priority.
- This output is suitable for direct ingestion into a CustomerEntity dimension.
