import pandas as pd
import csv

# Define the updates for Batch 18
updates = {
    'Travel Inn Motel': {'status': 'Verified', 'website': '', 'naics': '721110', 'industry': 'Motel'},
    'Aloft Louisville East': {'status': 'Verified', 'website': 'marriott.com/hotels/travel/sdfae-aloft-louisville-east/', 'naics': '721110', 'industry': 'Hotel (Aloft)'},
    'Courtyard By Marriott Cincinnati Midtownrookwood': {'status': 'Verified', 'website': 'marriott.com/hotels/travel/cvgmw-courtyard-cincinnati-midtown-rookwood/', 'naics': '721110', 'industry': 'Hotel (Courtyard)'},
    'Crowne Plaza Union Station': {'status': 'Verified', 'website': 'ihg.com/crowneplaza/hotels/us/en/indianapolis/inddt/hoteldetail', 'naics': '721110', 'industry': 'Hotel (Crowne Plaza)'},
    'Cutting Crew': {'status': 'Verified', 'website': 'cuttingcrewknoxville.com', 'naics': '812112', 'industry': 'Beauty Salon'},
    'Delta Hotels Ashland Downtown': {'status': 'Verified', 'website': 'marriott.com/hotels/travel/htsda-delta-hotels-ashland-downtown/', 'naics': '721110', 'industry': 'Hotel (Delta Hotels)'},
    'Embassy Suites Charleston': {'status': 'Verified', 'website': 'embassysuitescharlestonwv.com', 'naics': '721110', 'industry': 'Hotel (Embassy Suites)'},
    'Newly Weds Foods': {'status': 'Verified', 'website': 'newlywedsfoods.com', 'naics': '311999', 'industry': 'Food Ingredient Manufacturing'},
    'Ingersoll-Rand': {'status': 'Verified', 'website': 'irco.com', 'naics': '333912', 'industry': 'Air Compressor Manufacturing'},
    'Jm Smucker': {'status': 'Verified', 'website': 'jmsmucker.com', 'naics': '311999', 'industry': 'Branded Food Manufacturing'},
    'Tuff Torq': {'status': 'Verified', 'website': 'tufftorq.com', 'naics': '333612', 'industry': 'Transaxle & Drive Systems Manufacturing'},
    'AL Neyer': {'status': 'Verified', 'website': 'merus.com', 'naics': '236220', 'industry': 'Design-Build Construction (now Merus)'},
    'Accumet Specialty Metals': {'status': 'Verified', 'website': 'accumet.net', 'naics': '423510', 'industry': 'Metal Service Center'},
    'Callisons': {'status': 'Verified', 'website': 'callisons.com', 'naics': '311942', 'industry': 'Flavoring Extracts Manufacturing'},
    'Color Resolutions International': {'status': 'Verified', 'website': 'new.colorresolutions.com', 'naics': '325910', 'industry': 'Printing Ink Manufacturing'},
    'Dcm Products': {'status': 'Verified', 'website': 'magik-stik.com', 'naics': '326199', 'industry': 'Plastic Product Manufacturing'},
    'Det Beverages': {'status': 'Verified', 'website': 'detbeverages.com', 'naics': '424820', 'industry': 'Beverage Wholesaler (Reyes Beverage Group)'},
    'Equivis Nora': {'status': 'Verified', 'website': 'equivis.com', 'naics': '531210', 'industry': 'Commercial Real Estate Brokerage'},
    'Excel Clips': {'status': 'Verified', 'website': 'excelclips.com', 'naics': '332722', 'industry': 'Industrial Fastener Manufacturing'},
    'Fast of Northwest Ohio': {'status': 'Verified', 'website': 'fastnwo.org', 'naics': '713940', 'industry': 'Fitness & Sports Instruction'},
    'Fluid Handling Technology': {'status': 'Verified', 'website': 'fhtindy.com', 'naics': '332912', 'industry': 'Fluid Power Hose & Fitting Mfg'},
    'Galatians Too': {'status': 'Deferred', 'rationale': 'Ambiguous Non-Profit Entity', 'notes': "Likely a small faith-based thrift or holding. No distinct commercial website found."},
    'Galatians Too III IV': {'status': 'Deferred', 'rationale': 'Ambiguous Non-Profit Entity', 'notes': "Likely associated with Galatians Too. No distinct commercial website found."},
    'Good Huber Mob': {'status': 'Deferred', 'rationale': 'Ambiguous Property Entity', 'notes': "Property holding entity in Hilliard. Status lapsed. No distinct website found."},
    'Gw Richmond Excel': {'status': 'Verified', 'website': 'excelcenter.org', 'naics': '611110', 'industry': 'Adult Charter High School'},
    'Ikron': {'status': 'Verified', 'website': 'ikron.org', 'naics': '624310', 'industry': 'Vocational Rehabilitation Services'},
    'Impact Service Group': {'status': 'Verified', 'website': 'impactservicegroup.com', 'naics': '561210', 'industry': 'HVAC Management & Facilities Support'},
    'In Motion Orthopadeics': {'status': 'Verified', 'website': '', 'naics': '621111', 'industry': 'Orthopedic Medical Practice'},
    'India Bazaar': {'status': 'Verified', 'website': 'indiabazaarusa.com', 'naics': '445110', 'industry': 'Indian Grocery Retail'},
    'Indiana Podiatry Group': {'status': 'Verified', 'website': 'inpodiatrygroup.com', 'naics': '621391', 'industry': 'Podiatry Medical Practice'}
}

# Read the CSV
file_path = 'output/work/enrichment/MasterEnrichmentQueue.csv'
df = pd.read_csv(file_path)

# Apply updates
for index, row in df.iterrows():
    name = row['Master Customer Name']
    if name in updates:
        up = updates[name]
        df.at[index, 'Enrichment Status'] = up['status']
        df.at[index, 'Enrichment Source'] = 'Analyst'
        
        if up['status'] == 'Verified':
            df.at[index, 'Company Website (Approved)'] = up.get('website', '')
            df.at[index, 'NAICS (Approved)'] = up.get('naics', '')
            df.at[index, 'Industry Detail (Approved)'] = up.get('industry', '')
            df.at[index, 'Enrichment Confidence'] = 'High'
            df.at[index, 'Enrichment Rationale'] = ''
            df.at[index, 'Notes'] = ''
        else:
            df.at[index, 'Enrichment Rationale'] = up.get('rationale', '')
            df.at[index, 'Notes'] = up.get('notes', '')

# Save back to CSV
df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)
print("Queue updated successfully.")
