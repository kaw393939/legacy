#!/usr/bin/env python3
"""Update FAQ entries based on latest client emails."""
import yaml
import sys
import os

FAQ_PATH = os.path.join(os.path.dirname(__file__), '..', 'content', 'data', 'faq.yaml')

with open(FAQ_PATH, 'r') as f:
    data = yaml.safe_load(f)

# Helper to find a question by substring match
def find_q(category, substring):
    for i, q in enumerate(data['faqs'][category]['questions']):
        if substring.lower() in q['question'].lower():
            return i
    raise ValueError(f"Question containing '{substring}' not found in {category}")

# ============================================================
# 1. Update "off-market properties" FAQ with 10-step version
# ============================================================
idx = find_q('property_housing', 'properties that aren')
data['faqs']['property_housing']['questions'][idx]['answer'] = (
    '<p>In Puerto Rico, a lot of deals never hit Zillow, Realtor, or even MLS. '
    'Off-market here is <strong>relationship-driven, not tech-driven</strong>. '
    "Here's how properties actually get found — and which methods work best:</p>\n\n"

    '<h4>1. Drive for Dollars (Still #1 in PR)</h4>\n'
    '<p>This works extremely well in Puerto Rico because many heirs live on the mainland, '
    'probate takes time, vacant properties sit for years, and storm damage is never fully repaired.</p>\n'
    '<p><strong>What to look for:</strong> overgrown yards, broken windows, water meter removed, '
    'mail piled up, hurricane tarps still on the roof.</p>\n'
    '<p>Take photos, write down the address, build your own list — then skip trace the owner '
    'and call or send a letter. This is sweat equity, but this is where your margin is.</p>\n\n'

    '<h4>2. Go Direct to the Registry (CRIM + Registro)</h4>\n'
    '<p>Ownership data in PR is public but not always digital.</p>\n'
    '<ul>\n'
    '  <li><strong>Centro de Recaudación de Ingresos Municipales (CRIM):</strong> look for delinquent property taxes.</li>\n'
    '</ul>\n'
    '<p><strong>How to check CRIM records:</strong></p>\n'
    '<ul>\n'
    '  <li><strong>Option 1 — Online Portal:</strong> Visit the CRIM website '
    '(<a href="https://www.crimpr.net" target="_blank">crimpr.net</a>), navigate to Property Tax Records or '
    '"Consulta de Propiedad." Enter the property number (número de catastro) or owner name. '
    'You can view outstanding balances, payment history, and assessed value. '
    'Not all records are digitized — older or rural properties may not appear online.</li>\n'
    '  <li><strong>Option 2 — Call the Local CRIM Office:</strong> Each municipality has a local CRIM office. '
    'Call them directly with the property address or owner name. '
    'They can look up tax status, confirm delinquencies, and tell you if the property is headed for tax sale. '
    'Be patient — hold times can be long, and staff may only speak Spanish.</li>\n'
    '  <li><strong>Option 3 — Visit In Person:</strong> Go to the municipal CRIM office with the property address, '
    'catastro number, or owner name. Request a <em>Certificación de Deuda</em> (debt certification) '
    'to confirm exactly what\u2019s owed. This is often the fastest and most reliable way to get complete records, '
    'especially for older properties.</li>\n'
    '</ul>\n'
    '<ul>\n'
    '  <li><strong>Registro de la Propiedad de Puerto Rico:</strong> cross-check ownership, liens, '
    'and inheritance situations at the Registro to confirm legal standing.</li>\n'
    '</ul>\n'
    '<p>Tax delinquency = motivation. You\u2019d be surprised how many owners owe 5\u201310 years '
    'of CRIM taxes and just want out.</p>\n\n'

    '<h4>3. Network with Local Attorneys</h4>\n'
    '<p>Estate attorneys, probate lawyers, and divorce attorneys often know about properties '
    '<strong>before they ever hit the market</strong>. Call 20 attorneys and tell them: '
    '\u201cI buy as-is properties, inherited homes, properties with title issues.\u201d '
    'Be consistent — most investors don\u2019t do this, and that\u2019s why it works.</p>\n\n'

    '<h4>4. Talk to Contractors & Electricians</h4>\n'
    '<p>Contractors know who ran out of money, who is mid-renovation and stuck, and who inherited '
    'and doesn\u2019t want to fix. Buy them lunch, ask for referrals, pay a small finder\u2019s fee. '
    'In PR, <strong>relationships move deals more than MLS</strong>.</p>\n\n'

    '<h4>5. Facebook Marketplace (Manual Search Strategy)</h4>\n'
    '<p>Search for: \u201cse vende por dueño,\u201d \u201ccasa herencia,\u201d \u201cventa urgente,\u201d '
    '\u201cnecesita reparación,\u201d \u201cno realtor.\u201d Also check local Facebook groups in Carolina, '
    'San Juan, Bayamón — many older owners list there first before calling an agent.</p>\n\n'

    '<h4>6. Bandit Signs</h4>\n'
    '<p>A simple sign: <em>\u201cCOMPRO CASA EN EFECTIVO \u2013 CIERRE RÁPIDO\u201d</em> — '
    'Puerto Rico sellers respond to direct Spanish messaging. '
    'Place signs near colmados, busy intersections, and older neighborhoods. '
    'Check municipal sign rules first.</p>\n\n'

    '<h4>7. Property Managers</h4>\n'
    '<p>Call property managers and ask: \u201cDo you have landlords tired of tenants?\u201d or '
    '\u201cAnyone selling before they list?\u201d — especially in short-term rental zones.</p>\n\n'

    '<h4>8. Build a Small Bird Dog Army</h4>\n'
    '<p>Tell Uber drivers, barbers, colmado owners, neighbors, and church members — '
    'offer $1,000\u2013$3,000 referral fee at closing. Make it real money and they\u2019ll start looking for you.</p>\n\n'

    '<h4>9. Check for Heirs (\u201cHerencia\u201d) Situations</h4>\n'
    '<p>Many PR properties are tied up in <strong>inheritance (herencia)</strong> situations — '
    'the original owner passed, and multiple heirs now share ownership but can\u2019t agree on what to do. '
    'These deals take patience but often come at deep discounts. '
    'Look for properties where the CRIM record still shows a deceased owner\u2019s name, '
    'or where neighbors confirm the family moved to the mainland.</p>\n\n'

    '<h4>10. Follow Up Relentlessly</h4>\n'
    '<p>Most off-market deals in Puerto Rico don\u2019t close on the first contact. '
    'The seller might not be ready yet, might be dealing with family disagreements, '
    'or might need time to process. <strong>Follow up every 30\u201360 days</strong> — '
    'a simple call or text: \u201cStill interested whenever you\u2019re ready.\u201d '
    'The investor who follows up is the one who gets the deal.</p>\n\n'

    '<p><strong>Bottom line:</strong> Puerto Rico rewards showing up, speaking Spanish, '
    'being patient, and following up. Off-market here = boots on the ground + local relationships.</p>\n'
)

# ============================================================
# 2. Update "video, photos, and reports" FAQ — add Zoom + recording disclaimer
# ============================================================
idx = find_q('service_booking', 'video, photos, and reports')
data['faqs']['service_booking']['questions'][idx]['answer'] = (
    "<p>Yes! You receive:</p>\n"
    "<ul>\n"
    "  <li>An <strong>edited video</strong> of the house exteriors and interiors</li>\n"
    "  <li>Video from the road approaching the house</li>\n"
    "  <li>Video of the neighbors' houses and surrounding area</li>\n"
    "  <li>A <strong>market analysis report</strong> including nearby commercial places, hospitals, "
    "restaurants, malls, and local online news stories about crime or floods</li>\n"
    "</ul>\n"
    "<p>We can also do a <strong>LIVE session via Zoom</strong> so you view the house with us in real time "
    "instead of receiving an edited video.</p>\n"
    "<p><strong>Drone video</strong> is available at additional rates.</p>\n"
    "<p><strong>Zoom live streaming — participant recording notice:</strong> "
    "Participants cannot record by default. The host must grant recording permissions to a participant, "
    "or make them a co-host. Please request permission in advance if you would like to record the live streaming session.</p>\n"
)

# ============================================================
# 3. Update "same day services" — 24→24-48 hours + realtor mention
# ============================================================
idx = find_q('service_booking', 'same day services')
data['faqs']['service_booking']['questions'][idx]['answer'] = (
    '<p>Not normally — but if we are available, we will make it happen.</p>\n'
    '<p>We typically ask for a <strong>24–48 hour window of advance notice</strong> '
    'to schedule a visit, as well as confirmation from the realtor.</p>\n'
)

# ============================================================
# 4. Update "cancel services" — 50%→20%, add reschedule note
# ============================================================
idx = find_q('service_booking', 'cancel services')
data['faqs']['service_booking']['questions'][idx]['answer'] = (
    '<p>We kindly ask for a <strong>24-hour notice</strong> for cancellation. '
    'Otherwise, a <strong>20% charge</strong> of the total service fee will apply.</p>\n'
    '<p>The fee can be applied to a future re-schedule.</p>\n'
)

# ============================================================
# 5. Update "videographer finds a problem" — add 20% kill fee + reschedule
# ============================================================
idx = find_q('service_booking', 'videographer finds a problem')
data['faqs']['service_booking']['questions'][idx]['answer'] = (
    '<p>You will be <strong>immediately notified</strong> of any situation impeding our work '
    'or anything you would need to know as soon as possible. We keep you fully informed throughout '
    'the entire process — if anything important comes up, you\u2019ll be the first to know.</p>\n'
    '<p>In the event of a sudden cancellation outside our control (e.g., the seller or realtor cancels at the last minute), '
    'a <strong>20% kill fee</strong> of the total service fee will apply to cover time, travel, and preparation.</p>\n'
    '<p>The fee can be applied to a future re-schedule.</p>\n'
)

# Write it back
with open(FAQ_PATH, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

print("FAQ updated successfully.")
print(f"File: {os.path.abspath(FAQ_PATH)}")
