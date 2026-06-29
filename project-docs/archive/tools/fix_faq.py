#!/usr/bin/env python3
"""Fix FAQ entries: off-market 10-step, same-day tone, video qualifier."""
import yaml
import os

FAQ_PATH = os.path.join(os.path.dirname(__file__), '..', 'content', 'data', 'faq.yaml')

with open(FAQ_PATH, 'r') as f:
    data = yaml.safe_load(f)

def find_q(category, substring):
    for i, q in enumerate(data['faqs'][category]['questions']):
        if substring.lower() in q['question'].lower():
            return i
    raise ValueError(f"Question containing '{substring}' not found in {category}")

# ============================================================
# 1. Off-market FAQ — client's clean 10-step version
# ============================================================
idx = find_q('property_housing', 'properties that aren')
data['faqs']['property_housing']['questions'][idx]['answer'] = (
    '<p>In Puerto Rico, a lot of deals never hit Zillow, Realtor, or even MLS. '
    'Off-market here is <strong>relationship-driven, not tech-driven</strong>. '
    "Here's how properties actually get found — and which methods work best:</p>\n\n"

    '<h4>1. Drive for Dollars (Still #1 in PR)</h4>\n'
    '<p>Physically drive target neighborhoods. Look for: overgrown yards, boarded windows, '
    'mail piled up, faded paint, structural neglect.</p>\n'
    '<p>Write down the address. Then research ownership. Most abandoned properties are not online.</p>\n\n'

    '<h4>2. How to Get Owner Info from CRIM (Critical Step)</h4>\n'
    '<p>CRIM = property tax authority in Puerto Rico. This is where you confirm ownership and tax status.</p>\n'
    '<p><strong>Best ways to get info:</strong></p>\n'
    '<ul>\n'
    '  <li><strong>Option 1 \u2014 Online (Fastest):</strong> Use the CRIM property search portal. '
    'Search by address or cadastral number (catastro). You can usually see: owner name, assessed value, '
    'tax balance / delinquency. This works for initial research.</li>\n'
    '  <li><strong>Option 2 \u2014 Call the Local CRIM Office:</strong> Call the municipal CRIM office '
    'where the property is located. Ask to confirm: owner name, mailing address, tax status. '
    'They may give basic info \u2014 they won\u2019t give sensitive data, but ownership and tax balance '
    'are often confirmable.</li>\n'
    '  <li><strong>Option 3 \u2014 In Person (Most Effective for Complex Situations):</strong> '
    'If ownership looks outdated, the owner is deceased, taxes are severely delinquent, or records are unclear '
    '\u2014 go in person. Staff are more helpful face-to-face, especially in smaller municipalities. '
    'Bring: property address, cadastral number if possible, photo ID. '
    'In Puerto Rico, in-person relationships matter. If you plan to source regularly, build rapport.</li>\n'
    '</ul>\n\n'

    '<h4>3. Cross-Check with Registro de la Propiedad</h4>\n'
    '<p>CRIM shows the tax owner. Registro confirms the legal owner. They are not always updated the same.</p>\n'
    '<p>If the owner is deceased, look for: estate not settled, multiple heirs, no updated deed. '
    'That\u2019s opportunity.</p>\n\n'

    '<h4>4. Heirs / \u201cHerencia\u201d Situations</h4>\n'
    '<p>Huge in Puerto Rico. Many properties: have 3\u201310 heirs, sit vacant, have tax debt, '
    'were never properly transferred.</p>\n'
    '<p>Approach respectfully. You\u2019re solving a paperwork and family burden.</p>\n\n'

    '<h4>5. Attorneys & Notaries</h4>\n'
    '<p>Build relationships with: probate attorneys, notaries handling estate divisions, divorce attorneys. '
    'They hear about distressed property first. Bring real buyers, not talk.</p>\n\n'

    '<h4>6. Municipal Code Violation Lists</h4>\n'
    '<p>Request: unsafe structures, abandoned property lists, demolition notices. '
    'Pressure creates motivation.</p>\n\n'

    '<h4>7. Facebook Marketplace & Local Groups</h4>\n'
    '<p>Search: \u201cSe vende urgente,\u201d \u201cDue\u00f1o vende,\u201d '
    '\u201cPropiedad herencia,\u201d \u201cNecesita arreglos.\u201d Message fast. Speed wins.</p>\n\n'

    '<h4>8. Talk to Neighbors</h4>\n'
    '<p>Ask: \u201cDo you know who owns that house?\u201d \u201cHas anyone tried to buy it?\u201d '
    'Puerto Rico runs on relationships.</p>\n\n'

    '<h4>9. Contractors & Handymen</h4>\n'
    '<p>They know: who ran out of money, who abandoned a project, who\u2019s frustrated. '
    'Stay top of mind.</p>\n\n'

    '<h4>10. Follow Up Relentlessly</h4>\n'
    '<p>Most deals close months later. Puerto Rico sellers move slow. Consistency beats aggression.</p>\n\n'

    '<h4>The Real Edge with CRIM</h4>\n'
    '<p>The best investors in PR don\u2019t just pull ownership. They look for: '
    '3+ years tax delinquent, owner mailing address in mainland U.S., deceased owner, '
    'mismatch between CRIM and Registry. That\u2019s where the real leverage is.</p>\n'
)

# ============================================================
# 2. Same-day services — match client's direct tone
# ============================================================
idx = find_q('service_booking', 'same day services')
data['faqs']['service_booking']['questions'][idx]['answer'] = (
    '<p>Normally we ask for a <strong>24\u201348 hour window</strong> of advance notice, '
    'but if we are available the same day, as well as the realtor, we will make it happen.</p>\n'
)

# ============================================================
# 3. Video FAQ — add "depending on services requested" qualifier
# ============================================================
idx = find_q('service_booking', 'video, photos, and reports')
data['faqs']['service_booking']['questions'][idx]['answer'] = (
    "<p>Yes! Depending on the services requested, you receive:</p>\n"
    "<ul>\n"
    "  <li>An <strong>edited video</strong> of the house exteriors and interiors</li>\n"
    "  <li>Video from the road approaching the house</li>\n"
    "  <li>Video of the neighbors' houses and surrounding area</li>\n"
    "  <li>A <strong>market analysis report</strong> including nearby commercial places, hospitals, "
    "restaurants, malls, and local online news stories about crime or floods</li>\n"
    "</ul>\n"
    "<p>Or, we can provide a <strong>LIVE streaming session via Zoom</strong> so you view the house "
    "with us in real time instead of receiving an edited video.</p>\n"
    "<p><strong>Drone video</strong> is available at additional rates.</p>\n"
    "<p><strong>Zoom live streaming \u2014 participant recording notice:</strong> "
    "Participants cannot record by default. The host must grant recording permissions to a participant, "
    "or make them a co-host. Please request permission in advance if you would like to record "
    "the live streaming session.</p>\n"
)

with open(FAQ_PATH, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

print("FAQ fixes applied successfully.")
