import yaml
import re

# 1. Fix services.yaml
with open('content/data/services.yaml', 'r') as f:
    services = yaml.safe_load(f)

for service in services.get('settling_up_services', []):
    if service['id'] == 'housing-assistance':
        service['features'] = [
            "Consulting assistance navigating listings, leases, and the local process.",
            "Assistance finding a home or apartment (may or may not include working with a Realtor)",
            "Short-term rental guidance while you house-hunt",
            "Title and property search assistance (especially if purchasing)",
            "Finder’s/consultation fee applies upon signing a lease or closing on a home"
        ]

with open('content/data/services.yaml', 'w') as f:
    yaml.dump(services, f, sort_keys=False, allow_unicode=True)

# 2. Fix faq.yaml
with open('content/data/faq.yaml', 'r') as f:
    faq = yaml.safe_load(f)

def update_faq(category, question_match, new_answer):
    for q in faq['faqs'][category]['questions']:
        if question_match.lower() in q['question'].lower():
            # Convert newlines to <br> or wrap in <p>
            # For simple text, just wrap paragraphs in <p>
            paragraphs = [p.strip() for p in new_answer.strip().split('\n\n') if p.strip()]
            html_answer = ""
            for p in paragraphs:
                # if it looks like a list item or header, we could format it, but <p> is safest to preserve exact text
                html_answer += f"<p>{p.replace(chr(10), '<br>')}</p>\n"
            q['answer'] = html_answer
            return
    print(f"Could not find FAQ matching: {question_match}")

# Exact texts from clientfeedback.txt
ans_off_market = """1. Drive for Dollars (Still #1)

Physically drive target neighborhoods.

Look for:

Overgrown yards

Boarded windows

Mail piled up

Faded paint / structural neglect

Write down the address. Then research ownership.

Most abandoned properties are not online.

2. How to Get Owner Info from CRIM (Critical Step)

CRIM = property tax authority in Puerto Rico. This is where you confirm ownership and tax status.

Best Ways to Get Info:

Option 1 – Online (Fastest)

Use the CRIM property search portal.

Search by address or cadastral number (catastro).

You can usually see:

Owner name

Assessed value

Tax balance / delinquency

This works for initial research.

Option 2 – Call the Local CRIM Office

Call the municipal CRIM office where the property is located.

Ask to confirm:

Owner name

Mailing address

Tax status

They may give basic info. They won’t give sensitive data, but ownership and tax balance are often confirmable.

Option 3 – In Person (Most Effective for Complex Situations)
If:

Ownership looks outdated

Owner is deceased

Taxes are severely delinquent

Records are unclear

Go in person.

Staff are more helpful face-to-face, especially in smaller municipalities. Bring:

Property address

Cadastral number if possible

Photo ID

In Puerto Rico, in-person relationships matter. If you plan to source regularly, build rapport.

3. Cross-Check with Registro de la Propiedad

CRIM shows tax owner.
Registro confirms legal owner.

They are not always updated the same.

If the owner is deceased, look for:

Estate not settled

Multiple heirs

No updated deed

That’s opportunity.

4. Heirs / “Herencia” Situations

Huge in Puerto Rico.

Many properties:

Have 3–10 heirs

Sit vacant

Have tax debt

Were never properly transferred

Approach respectfully. You’re solving a paperwork and family burden.

5. Attorneys & Notaries

Build relationships with:

Probate attorneys

Notaries handling estate divisions

Divorce attorneys

They hear about distressed property first.

Bring real buyers, not talk.

6. Municipal Code Violation Lists

Request:

Unsafe structures

Abandoned property lists

Demolition notices

Pressure creates motivation.

7. Facebook Marketplace & Local Groups

Search:

“Se vende urgente”

“Dueño vende”

“Propiedad herencia”

“Necesita arreglos”

Message fast. Speed wins.

8. Talk to Neighbors

Ask:
“Do you know who owns that house?”
“Has anyone tried to buy it?”

Puerto Rico runs on relationships.

9. Contractors & Handymen

They know:

Who ran out of money

Who abandoned a project

Who’s frustrated

Stay top of mind.

10. Follow Up Relentlessly

Most deals close months later.

Puerto Rico sellers move slow.
Consistency beats aggression.

The Real Edge with CRIM

The best investors in PR don’t just pull ownership.

They look for:

3+ years tax delinquent

Owner mailing address in mainland U.S.

Deceased owner

Mismatch between CRIM and Registry

That’s where the real leverage is."""

ans_real_costs = """Here’s a clear look at the real costs of buying residential real estate in Puerto Rico — whether it’s a single-family home, a multifamily building, or a 4–5 unit property. These are based on typical costs on the island and what buyers actually pay at closing and beyond:

📌 1. Down Payment

This isn’t a “closing cost” but is the biggest upfront cash requirement if you’re financing:

Financed purchase:

Conventional loan: typically 20–30% of purchase price (higher for investment properties like 4–5 units).

Some local lenders may allow 15–20% if owner-occupied (subject to lender terms).

All-cash purchase: zero financing requirement, but you pay all closing costs in cash.

Many investors and buyers in PR pay 20–30% down on multifamily or investment property deals.

📌 2. Closing Costs (Buyer’s Side)

Closing costs in Puerto Rico tend to be higher than most U.S. mainland markets — typically about 3% to 6–7% of the purchase price when you include everything.

Typical Closing Cost Items

Cost TypeTypical Amount
Transfer Tax + Stamp Tax (government transfer fees)~0.5%–1.5% of purchase price
Notary + Drafting Fees (required by law)~$3,000–$8,000 or ~0.5–1%
Attorney Fees0.5–1% of purchase price
Title Search & Title Insurance~0.5–1.5%
Recording / Registry Fees$500–$2,000+
Survey (if required)$500–$3,000
Inspections$400–$3,000+
Appraisal (if financing)~$500–$1,000+
Loan Origination & Lender Fees (if financing)~1–2% of loan amount
💡 On a $500,000 property, total closing costs can easily be $15,000–$30,000 or more, depending on financing and inspections.

📌 3. Property Transfer Taxes & Government Fees

These are mandatory fees paid as part of the transfer:

Documentary Stamps / Transfer Tax: ~0.5–1.5% of purchase price (varies by transaction structure).

Registry & Recording Fees: ~$500–$2,000 for deed and mortgage recordings.

Some transactions — especially larger or complex ones — require additional municipal compliance or certification fees.

📌 4. Mortgage & Financing Costs (if applicable)

If you finance the property:

Loan origination / lender fees: ~0.5–1.5% of loan amount.

Appraisal & processing fees: $500–$1,500+.

Mortgage recording fees: ~$300–$800.

Some lenders charge additional processing fees, points, or underwriting fees that add to your total cash-to-close.

📌 **5. Annual Property Taxes (CRIM)

Puerto Rico’s annual property tax system is different from most U.S. states:

Annual property tax (CRIM): Typically low because assessments are based on antiquated valuation schedules — often well below market value.

If rented out, the property is taxed like income property (ordinary income tax + occupancy taxes).

This means tax bills are usually lower than comparable U.S. mainland properties, but they still exist and vary by municipality.

📌 6. Ongoing & HOA Costs

If the property is part of a condominium or association:

HOA / Condo fees: Monthly or quarterly dues that can be significant in multifamily buildings with shared amenities.

Capital contribution at closing: Some associations require an initial capital contribution that can be several months of dues up front.

📌 7. Maintenance, Repairs & Reserves

Especially for multifamily or 4–5 unit buildings:

Budget 1%–3% of property value per year for maintenance, roof, systems, etc.

Older PR homes often have deferred maintenance (hurricane repairs, corrosion issues), so initial rehab costs can be higher.

🔎 Typical Cost Approximation (Illustrative)

Here’s how costs might stack on different price ranges:

Purchase PriceTotal Closing Costs (Est.)Notes
$250,000~$7,500–$15,000+for single-family (cash)
$500,000~$15,000–$30,000+financing adds lender costs
$1,000,000~$30,000–$70,000+luxury and complex title increases fees
💡 These are estimates not guarantees. Actual costs depend on financing, property condition, and transaction complexity.

🧠 Key Takeaways

Closing costs in PR are higher than many U.S. states (often 3–7% of price).

Attorney + Notary involvement is required by law, not optional.

Transfer taxes, registry costs, and title matters add meaningful cash-to-close.

Annual property tax (CRIM) is usually low, but other ongoing costs must be budgeted."""

ans_flood = """Yes — you can buy property in Puerto Rico that lies in a flood zone, but it comes with important financial and safety implications you should understand before you buy. Puerto Rico uses the same Federal Emergency Management Agency (FEMA) flood zone designations as the U.S. mainland, and these codes tell you how likely an area is to flood, how flood insurance requirements apply, and how difficult it may be to build or get a loan.

🧭 FEMA Flood Zone Designations — From Least Risk to Most Risk

FEMA divides land into zones based on the probability of flooding and related hazards. Here’s how they generally rank:

📉 Lower Flood Risk Areas

These zones might flood, but the risk is lower than in high-risk zones.

Zone X (Unshaded) – Minimal flood hazard (outside the 500-year flood area). Not federally required to carry flood insurance, though risks still exist (e.g., heavy rain, poor drainage).

Zone X (Shaded) / Zone B / Zone C – Moderate flood hazard (between 100- and 500-year flood level). Flood insurance is not mandatory for federally backed mortgages but still recommended.

⚠️ Zones with Uncertain or Partial Analysis

Zone D – Possible flood hazard but not thoroughly analyzed. Insurance is optional and rates reflect uncertainty.

🔴 High Flood Risk Areas (Special Flood Hazard Areas — SFHA)

These are the most significant zones in terms of flood risk and insurance requirements:

Zone A / AE – Base floodplain with a 1% chance of flooding in any year (often called the “100-year flood”). Federally backed mortgages typically require flood insurance. AE zones include base flood elevations (BFEs).

Zone AO / AH – Special high-risk areas with shallow flooding or ponding, with average depths shown on maps.

Zone A99 – Areas expected to be protected by a federal flood control system; still show flood risk.

Zone V / VE – Coastal high-risk zones subject to storm surge and wave action. These are often the highest risk designations — construction standards are strict and flood insurance is required.

In simple terms, from lower to higher risk:

Zone X (Unshaded) → Zone X (Shaded) / B / C → Zone D
      → Zone A / AE / AO / AH / A99 → Zone V / VE
🏡 Is It Safe to Buy in a Flood Zone Like in Puerto Rico?

Safety and practicality depend on many factors:

✔️ Insurance & Cost

High-risk flood zones (A and V categories) often require flood insurance for mortgages — especially federally backed ones — and insurance premiums can be thousands of dollars per year.

Even in lower-risk zones (like X or shaded X), buyers are frequently strongly encouraged to carry flood insurance because many flooding events occur outside high-risk areas.

✔️ Resale and Financing

Properties in high-risk zones may be harder to resell or finance because lenders see greater risk and buyers factor in insurance costs.

✔️ Actual Flood Risk Isn’t Zero

No area is completely safe from flooding. Even minimal risk zones can flood due to severe storms, drainage issues, or infrastructure failure.

✔️ Local Conditions Matter

Puerto Rico’s mountainous terrain, tropical rainfall, hurricane exposure, and coastal areas make flood risk especially dynamic — zones can change with updated FEMA maps.

🧠 Practical Steps Before Buying

Check the FEMA Flood Map for the exact property address (FEMA Flood Map Service Center).

Ask for an Elevation Certificate — this shows how high the building sits relative to predicted flood levels.

Get a Flood Insurance Quote Early — costs can dramatically affect your budget.

Consult Local Planner or Floodplain Manager — Puerto Rico may have additional rules, local flood maps, or plans that affect buildability and permitting.

🧩 Quick Summary

ZoneFlood Risk LevelInsurance Required?Key Notes
X (Unshaded)MinimalNoRisk still exists
X (Shaded) / B / CModerateOften not requiredConsider insurance
DUnknownOptionalRisk unclear
A / AE / AO / AH / A99HighGenerally required1% annual flood risk
V / VEVery High (coastal)RequiredStorm surge & waves
📌 Bottom Line

Buying in a flood zone in Puerto Rico is possible, but it needs careful planning:

Understand the specific flood zone designation and how it affects risk.

Prepare for higher insurance costs (when required).

Evaluate long-term resale and risk tolerance.

If risk and cost are deal breakers for you, properties in lower-risk zones (Zone X) are typically easier to own and insure. But even then, factor in climate risks and infrastructure changes over time."""

ans_non_resident = """Yes — you can get a mortgage as a non-resident to buy property in Puerto Rico, but it’s not always as straightforward as getting a conventional loan in the mainland U.S. Let’s break down your options and what works best in most situations:

🏦 1. Mortgages in Puerto Rico as a Non-Resident

Yes — both U.S. citizens living outside Puerto Rico and non-U.S. citizens (foreign nationals) can be approved for a mortgage to buy property in Puerto Rico. There are no ownership restrictions based on citizenship — anyone can buy property there.

Here’s what you should know:

Many Puerto Rico banks offer mortgages to non-residents (U.S. citizens living abroad and foreign nationals alike).

Local lenders are more familiar with Puerto Rico’s legal/real-estate system and typically easier to work with than most U.S. mainland banks when it comes to Puerto Rico properties.

You’ll usually need higher down payments and stronger documentation than a typical U.S. resident loan.

Typical non-resident mortgage terms in PR:

Down payment: ~20% to 35% (sometimes more for non-U.S. buyers).

Documentation: Income verification, bank statements, credit history (U.S. or foreign).

Interest rates: Often slightly higher than in mainland U.S.

Loan-to-Value (LTV): Usually 65%–80% for non-residents.

Main lenders on the island include:

Banco Popular de Puerto Rico

FirstBank (Puerto Rico)

Oriental Bank
…but other local and international banks may also offer financing.

Pros:
✅ Banks know the local market and property laws.
✅ You’re applying directly where the property is located.

Cons:
❌ Potentially slower processing compared with some U.S. mainland mortgages.
❌ Down payments and rates may be higher.

🏦 2. Using a Bank in the U.S. (Mainland)

Technically some U.S. banks might offer “foreign national” or specialty home loans that you could use for any U.S. property — including in Puerto Rico. But in practice:

Many large U.S. lenders don’t finance Puerto Rico properties directly because they aren’t licensed or comfortable with local law and market nuances.

If they do offer financing, it may be as a foreign-national mortgage program, with similar requirements (higher down payment, proof of assets/credit, possibly higher rates) as a Puerto Rico bank but with fewer local specialists.

Some buyers use a loan from a U.S. bank first (e.g., home equity loan / HELOC on existing property) to get cash and close fast, then later refinance locally in Puerto Rico.

Pros:
✅ You might get better pricing or terms if you have a strong relationship with your U.S. bank.
✅ Familiar paperwork and process for you.

Cons:
❌ Not many U.S. banks will do this at all for PR properties.
❌ Those that do may still require a local affiliate or special approval.

💡 3. Cash Purchase First, Mortgage Later

This is a popular strategy, especially for foreigners or investors:

Pay cash at closing to move quickly.

Later, refinance with a local bank once the title is clear and the property is established — sometimes at better terms.

Cash gives you negotiating power (sellers prefer certainty), and refinancing afterward can be smoother once you’re “on the ground.”

🧠 Which Path Is Usually Best?

Here’s a practical recommendation based on typical cases:

✔ If your U.S. bank cannot finance a PR property directly → Line up a mortgage with a Puerto Rico bank before you start seriously shopping. It speeds up closing and shows sellers you’re ready.

✔ If your U.S. bank can lend for PR real estate and offers good terms for you → It might be worth using that financing, especially if you already have a relationship, good credit, and favorable rates.

✔ If you want the simplest closing without financing delays → Cash or a combination strategy (cash + future refinance) can be the most competitive approach in the market."""

ans_q1 = "It depends on the availability of the realtor or seller.  But we can safely say within 24-48 hours or as soon as they are available."
ans_q2 = "We cover the San Juan metropolitan area, the East coast and West Coast.\nWe can cover the South but additional charges may apply."
ans_q3 = """Yes.  Depending on the services requested, you receive:
an edited video of the house exteriors, 
interiors, 
video from the road approaching the house, 
neighbors houses 
and a market analysis reports including commercial places, hospitals, restaurants, malls nearby, local online news stories about crime or floods. 
Or, we can provide a LIVE streaming session so you view the house with us instead of providing an edited video.                                                                       *Zoom live streaming participant recording: Participants cannot record by default. The host must grant recording permissions to a participant, or make them a co-host.  Please request permission to allow you to record the live streaming session. 

Drone video available at additional rates."""
ans_q4 = "Normally we ask for a 24-48 hour window advance notice, but if we are available the same day, as well as the realtor, we will make it happen."
ans_q5 = "We kindly ask for a 24 hour notice for cancellation, otherwise a 20% of the total charge will apply.  The fee can be applied to a future re-schedule."
ans_q8 = "Payment must be received 24 hours prior to the filming.\n\nWe accept Zelle or paypal."
ans_q9 = "The customer will be immediately notified of any situation impeding our labor or any situation they would need to know asap.  The customer will be aware should anything important come up.   There's a kill fee associated with last minute sudden cancellations caused by circumstances outside of our control of 20% of the total fee.   The fee can be applied to a future re-schedule."

update_faq('property_housing', 'How to Actually Find Off-Market Properties', ans_off_market)
update_faq('property_housing', 'Real Costs of buying a property', ans_real_costs)
update_faq('property_housing', 'Is it safe to buy a property in a flood zone', ans_flood)
update_faq('property_housing', 'Can I buy property in PR as a non resident', ans_non_resident)

update_faq('service_booking', 'How quickly can you visit', ans_q1)
update_faq('service_booking', 'What areas of PR do you do', ans_q2)
update_faq('service_booking', 'Do I receive video/photos', ans_q3)
update_faq('service_booking', 'Do you offer same day services', ans_q4)
update_faq('service_booking', 'Can I cancel services anytime', ans_q5)
update_faq('service_booking', 'How do I pay for services', ans_q8)
update_faq('service_booking', 'What if the videographer sees or finds a problem', ans_q9)

with open('content/data/faq.yaml', 'w') as f:
    yaml.dump(faq, f, sort_keys=False, allow_unicode=True)

print("Done updating faq.yaml and services.yaml")
