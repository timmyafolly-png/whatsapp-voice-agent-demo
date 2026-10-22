#!/usr/bin/env python3
"""Build BuildRegs customer emails.

Writes two things:
  templates/NN-name.html   the deliverable, with {{placeholders}} intact
  preview.html             every email rendered with sample data, for Sandeep

House style taken from the live Phase 1 acknowledgement so the new emails
match what is already going out.
"""
import os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "templates")

LOGO = "https://buildregs.co.uk/wp-content/uploads/2025/11/BuildRegs-Black-1024x227.png"
FONT = "'Poppins','Segoe UI',Helvetica,Arial,sans-serif"

INK      = "#17324B"   # headings
BODY     = "#33414D"   # body copy
MUTED    = "#6B7A88"   # labels
LINE     = "#E3E8ED"   # borders
PANEL    = "#F7F9FB"   # detail panels
PAGE     = "#F4F6F8"   # outer background
GREEN    = "#1E7A4B"   # positive accent
BTN      = "#17324B"   # button fill


def shell(body, preheader=""):
    pre = ""
    if preheader:
        pre = (f'<div style="display:none; max-height:0; overflow:hidden; '
               f'mso-hide:all;">{preheader}</div>')
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{PAGE};">
<tr><td align="center" style="padding:24px 12px;">{pre}
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:100%; background-color:#FFFFFF; border:1px solid {LINE}; border-radius:8px;">
<tr><td align="left" style="padding:28px 32px 20px 32px; border-bottom:1px solid {LINE};">
<img src="{LOGO}" alt="BuildRegs" width="150" style="display:block; width:150px; max-width:150px; height:auto; border:0;">
</td></tr>
{body}
{signature()}
</table>
</td></tr>
</table>"""


def signature():
    return f"""<tr><td style="padding:8px 32px 32px 32px; border-top:1px solid {LINE}; font-family:{FONT};">
<p style="margin:16px 0 0 0; font-size:15px; line-height:24px; color:{BODY};">Kind regards,<br>
<strong style="color:{INK};">The BuildRegs Team</strong><br>
<span style="font-size:13px; line-height:20px; color:{MUTED};">Building Regulations Drawings &amp; Structural Calculations</span><br>
<a href="mailto:support@buildregs.co.uk" style="font-size:13px; line-height:20px; color:{INK};">support@buildregs.co.uk</a><br>
<a href="https://www.buildregs.co.uk/" style="font-size:13px; line-height:20px; color:{INK};">www.buildregs.co.uk</a></p>
</td></tr>"""


def h1(t):
    return (f'<tr><td style="padding:32px 32px 0 32px; font-family:{FONT};">'
            f'<h1 style="margin:0 0 16px 0; font-size:22px; line-height:30px; '
            f'font-weight:600; color:{INK};">{t}</h1></td></tr>')


def para(*ps, top=0, bottom=24):
    out = [f'<tr><td style="padding:{top}px 32px 0 32px; font-family:{FONT};">']
    for i, p in enumerate(ps):
        mb = bottom if i == len(ps) - 1 else 16
        out.append(f'<p style="margin:0 0 {mb}px 0; font-size:15px; '
                   f'line-height:24px; color:{BODY};">{p}</p>')
    out.append('</td></tr>')
    return "".join(out)


def h2(t, top=28):
    return (f'<tr><td style="padding:{top}px 32px 0 32px; font-family:{FONT};">'
            f'<h2 style="margin:0 0 14px 0; font-size:17px; line-height:24px; '
            f'font-weight:600; color:{INK};">{t}</h2></td></tr>')


def row(label, value, bold=False, last=False):
    pb = "0" if last else "10px"
    col = INK if bold else BODY
    weight = "font-weight:600;" if bold else ""
    return (f'<tr><td style="padding:0 0 {pb} 0; font-size:13px; line-height:20px; '
            f'color:{MUTED}; width:150px;">{label}</td>'
            f'<td style="padding:0 0 {pb} 0; font-size:15px; line-height:20px; '
            f'color:{col}; {weight}">{value}</td></tr>')


def panel(inner, top=0, bottom=0):
    return (f'<tr><td style="padding:{top}px 32px {bottom}px 32px;">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="background-color:{PANEL}; border:1px solid {LINE}; border-radius:6px;">'
            f'<tr><td style="padding:20px 24px; font-family:{FONT};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'{inner}</table></td></tr></table></td></tr>')


def block(inner, top=0, bottom=0):
    """Free-form panel, not a label/value table."""
    return (f'<tr><td style="padding:{top}px 32px {bottom}px 32px;">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="background-color:{PANEL}; border:1px solid {LINE}; border-radius:6px;">'
            f'<tr><td style="padding:20px 24px; font-family:{FONT}; font-size:15px; '
            f'line-height:24px; color:{BODY};">{inner}</td></tr></table></td></tr>')


def button(label, url, top=24, bottom=8):
    return (f'<tr><td align="center" style="padding:{top}px 32px {bottom}px 32px;">'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td align="center" bgcolor="{BTN}" style="border-radius:6px;">'
            f'<a href="{url}" style="display:inline-block; padding:15px 32px; '
            f'font-family:{FONT}; font-size:16px; line-height:20px; font-weight:600; '
            f'color:#FFFFFF; text-decoration:none; border-radius:6px;">{label}</a>'
            f'</td></tr></table></td></tr>')


def steps(items, top=28):
    rows = []
    for i, s in enumerate(items, 1):
        pb = "0" if i == len(items) else "12px"
        rows.append(
            f'<tr><td valign="top" style="padding:0 12px {pb} 0; font-size:15px; '
            f'line-height:24px; color:{GREEN}; font-weight:600; width:20px;">{i}</td>'
            f'<td style="padding:0 0 {pb} 0; font-size:15px; line-height:24px; '
            f'color:{BODY};">{s}</td></tr>')
    return (f'<tr><td style="padding:{top}px 32px 0 32px; font-family:{FONT};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0">{"".join(rows)}</table></td></tr>')


# ---------------------------------------------------------------- templates

def t01_acknowledgement():
    subject = "Thank you for your enquiry | BuildRegs"
    body = (
        h1("Thank you for your enquiry")
        + para("{{greeting}}",
               "Thank you for contacting BuildRegs about your project at "
               "<strong>{{property_address}}</strong>.",
               "We&rsquo;ve received your enquiry. {{file_receipt_sentence}}")
        + panel(row("Your reference", "{{project_reference}}", bold=True)
                + row("Project at", "{{property_address}}", last=True))
        + h2("What happens next")
        + para("We&rsquo;ll review the information and respond within "
               "<strong>one working day</strong> with a fixed-fee quotation, or a "
               "request for any further details we need. Your quotation will explain "
               "what&rsquo;s included, the total fee and the expected turnaround, so "
               "you can decide how you&rsquo;d like to proceed.", top=0)
        + para("If there&rsquo;s anything else you&rsquo;d like us to consider, "
               "simply reply to this email.",
               "Our response will come from support@buildregs.co.uk. If you "
               "haven&rsquo;t seen it within one working day, please check your junk "
               "or spam folder.", top=0, bottom=8)
    )
    return subject, shell(body, "We've received your enquiry and will respond within one working day.")


def t02_quotation():
    subject = "Your fixed-fee quotation — {{property_address}} | BuildRegs"
    body = (
        h1("Your fixed-fee quotation")
        + para("{{greeting}}",
               "Thank you for your enquiry. We&rsquo;ve reviewed the information "
               "provided and prepared your fixed-fee quotation for the work outlined "
               "below.",
               "The package sets out the documents we will prepare for your builder "
               "and Building Control, together with the fee and delivery timeframe.")
        + h2("Your project", top=0)
        + panel(row("Property", "{{property_address}}")
                + row("Quotation reference", "{{quote_reference}}", bold=True, last=True))
        + h2("What&rsquo;s included")
        + block("{{approved_scope}}")
        + h2("Your fixed fee")
        + panel("{{itemised_fees}}{{combined_project_discount}}{{price_adjustment}}"
                + f'<tr><td colspan="2" style="padding:12px 0 0 0; border-top:1px solid {LINE};"></td></tr>'
                + f'<tr><td style="padding:0; font-size:15px; line-height:24px; color:{INK}; '
                  f'font-weight:600;">Total payable</td>'
                  f'<td style="padding:0; font-size:20px; line-height:26px; color:{INK}; '
                  f'font-weight:700;">&pound;{{{{total}}}}</td></tr>'
                + f'<tr><td colspan="2" style="padding:6px 0 0 0; font-size:13px; '
                  f'line-height:20px; color:{MUTED};">No VAT to add.</td></tr>')
        + para("This is the total fee for the scope listed above. If you later request "
               "changes to that scope, we&rsquo;ll agree any revised fee with you "
               "before carrying out additional work.", top=20, bottom=0)
        + "{{approved_exclusions_or_conditions}}"
        + h2("Turnaround")
        + para("<strong>{{turnaround}} working days</strong> from receipt of payment "
               "and all required information. We&rsquo;ll confirm your target "
               "delivery date once everything is in place.", top=0, bottom=0)
        + para("To get started, please use the secure Stripe payment button below. "
               "You&rsquo;ll receive confirmation of your payment and the next steps "
               "by email.", top=24, bottom=0)
        + button("Proceed securely &mdash; &pound;{{total}}", "{{stripe_payment_link}}")
        + para("If you&rsquo;d like to clarify anything before proceeding, simply "
               "reply. We&rsquo;ll be happy to explain the scope or answer your "
               "questions.", top=16, bottom=8)
    )
    return subject, shell(body, "Your fixed-fee quotation for {{property_address}}.")


def t04_postcheckout():
    subject = "(page shown after checkout, not an email)"
    body = (
        h1("Thank you for choosing BuildRegs")
        + para("We&rsquo;ll email your payment confirmation and next steps as soon as "
               "your payment is confirmed.",
               "Please look out for an email from support@buildregs.co.uk, and check "
               "your junk or spam folder if needed.",
               "If you need any help, email us with your quotation reference.",
               bottom=8)
    )
    return subject, shell(body)


def t05_payment():
    subject = "Payment received — thank you | {{property_address}}"
    body = (
        h1("Payment received — thank you")
        + para("{{greeting}}",
               "Thank you for choosing BuildRegs. We&rsquo;ve received your payment "
               "of <strong>&pound;{{amount_paid}}</strong> for your project at "
               "<strong>{{property_address}}</strong>.")
        + panel(row("Quotation reference", "{{quote_reference}}", bold=True)
                + row("Agreed services", "{{approved_package_summary}}", last=True))
        + h2("What happens next")
        + steps([
            "We&rsquo;ll check that we have all the drawings and information needed "
            "for the agreed work. If anything is missing, we&rsquo;ll let you know "
            "what we need.",
            "Your turnaround is <strong>{{turnaround}} working days from receipt of "
            "payment and all required information</strong>. Once these are in place, "
            "we&rsquo;ll confirm your target delivery date.",
            "Your completed documents will be reviewed before we send them to you, "
            "and we&rsquo;ll email you when they&rsquo;re ready.",
        ], top=0)
        + para("If you have any questions or further information to share, simply "
               "reply to this email.",
               "We look forward to helping you move your project forward.",
               top=24, bottom=8)
    )
    return subject, shell(body, "We've received your payment. Here's what happens next.")


def t06_delivery():
    subject = "Your project documents are ready — {{property_address}}"
    body = (
        h1("Your project documents are ready")
        + para("{{greeting}}",
               "We&rsquo;ve completed and reviewed your "
               "<strong>{{deliverable_description}}</strong> for "
               "<strong>{{property_address}}</strong>, and they&rsquo;re ready to "
               "download.", bottom=0)
        + button("Download your project documents", "{{approved_documents_link}}")
        + h2("Your next steps", top=20)
        + block("{{project_specific_next_steps}}")
        + para("Please share the relevant documents with your builder and Building "
               "Control.",
               "If they have any questions about our drawings or calculations, please "
               "forward them to us so we can help. You can also reply directly if "
               "you would like anything explained or have difficulty accessing the "
               "files.",
               "Thank you for trusting BuildRegs with your project.",
               top=24, bottom=8)
    )
    return subject, shell(body, "Your completed documents for {{property_address}} are ready to download.")


def t07_checkin():
    subject = "Checking in on your project | BuildRegs"
    body = (
        h1("Checking in on your project")
        + para("{{greeting}}",
               "Just checking that you received the documents for "
               "<strong>{{property_address}}</strong> and that everything is "
               "progressing smoothly.",
               "Have you or your builder had a chance to look through them? If "
               "anything needs explaining, or Building Control has raised a question "
               "about our work, simply reply and let us know.",
               "We&rsquo;re happy to help with any questions about the documents "
               "we&rsquo;ve provided.", bottom=8)
    )
    return subject, shell(body, "Did everything arrive safely?")


def t08_review():
    subject = "Share your experience with BuildRegs"
    body = (
        h1("Share your experience")
        + para("{{greeting}}",
               "Thank you for choosing BuildRegs for your project at "
               "<strong>{{property_address}}</strong>.",
               "We&rsquo;d really appreciate an honest review of your experience. "
               "Your feedback helps us improve our service and gives other "
               "homeowners and professionals a clearer idea of what to expect when "
               "working with us.", bottom=0)
        + button("Share your experience", "{{review_link}}")
        + para("Thank you for taking the time to share your thoughts.",
               top=16, bottom=8)
    )
    return subject, shell(body, "We'd appreciate your honest review.")


TEMPLATES = [
    ("01-enquiry-acknowledgement", t01_acknowledgement),
    ("02-approved-quotation",      t02_quotation),
    ("04-post-checkout-message",   t04_postcheckout),
    ("05-payment-received",        t05_payment),
    ("06-delivery",                t06_delivery),
    ("07-checkin-3-day",           t07_checkin),
    ("08-review-invitation-7-day", t08_review),
]

# ---------------------------------------------------------------- sample data

def fee_row(label, value, strike=False):
    style = f"color:{BODY};"
    if strike:
        style = f"color:{GREEN};"
    return (f'<tr><td style="padding:0 0 10px 0; font-size:14px; line-height:20px; '
            f'color:{MUTED}; width:60%;">{label}</td>'
            f'<td style="padding:0 0 10px 0; font-size:15px; line-height:20px; '
            f'{style}">{value}</td></tr>')


def conditions_block(text):
    return block(f'<strong style="color:{INK};">Please note</strong><br>{text}', top=20)


SAMPLES = {
 "combined": {
   "_label": "Quotation — combined project (two types, 50% off the lower)",
   "first_name": "James",
   "greeting": "Hi James,",
   "property_address": "14 Wells Road, Bristol BS8 2QR",
   "project_reference": "BR-20261019-093711",
   "quote_reference": "BR-Q-20261022-1041",
   "approved_scope": ("Building Regulations drawings, construction specifications and "
                      "structural calculations in one coordinated package for Building "
                      "Control and your contractor, covering the agreed single-storey "
                      "extension and the loft conversion, including foundations, floors, "
                      "walls, roof, staircase, structural supports, insulation, "
                      "ventilation, drainage and fire-safety details."),
   "itemised_fees": (fee_row("Single-Storey Extension", "&pound;799.00")
                     + fee_row("Loft Conversion", "&pound;849.00")),
   "combined_project_discount": fee_row("Combined project discount (50% off Single-Storey Extension)",
                                        "&minus; &pound;399.50", strike=True),
   "price_adjustment": "",
   "total": "1,248.50",
   "approved_exclusions_or_conditions": conditions_block(
       "This quotation covers the two project types listed above at the same property. "
       "Party wall matters and planning applications are not included."),
   "turnaround": "7",
   "stripe_payment_link": "https://checkout.stripe.com/c/pay/cs_test_SAMPLE",
   "amount_paid": "1,248.50",
   "approved_package_summary": "Full package — Single-Storey Extension and Loft Conversion",
   "deliverable_description": "Building Regulations drawings and structural calculations",
   "approved_documents_link": "https://drive.google.com/drive/folders/SAMPLE",
   "project_specific_next_steps": ("Submit the drawings to Building Control with your "
                                   "Building Notice or Full Plans application, and give "
                                   "your builder the construction specification and the "
                                   "structural calculations before work starts on the "
                                   "foundations."),
   "review_link": "https://g.page/r/SAMPLE/review",
   "file_receipt_sentence": "Your plans have been saved and are with our technical team.",
 },
 "calcsonly": {
   "_label": "Quotation — calculations only (single type, no discount)",
   "first_name": "Aleksander",
   "greeting": "Hello,",
   "property_address": "8 Fellbrook Avenue, York YO26 5PR",
   "project_reference": "BR-20261019-151057",
   "quote_reference": "BR-Q-20261022-1042",
   "approved_scope": ("A structural design package for Building Control and your "
                      "contractor, covering the opening identified in this quotation. "
                      "Includes structural calculations, supporting details and a "
                      "structural layout or marked-up drawing for the agreed beam, "
                      "supports and bearings."),
   "itemised_fees": fee_row("Structural Opening / RSJ Calculations", "&pound;249.00"),
   "combined_project_discount": "",
   "price_adjustment": fee_row("Additional beam to rear opening", "&pound;120.00"),
   "total": "369.00",
   "approved_exclusions_or_conditions": conditions_block(
       "This quotation covers structural calculations only. Building Regulations "
       "drawings and construction specifications are not included."),
   "turnaround": "7",
   "stripe_payment_link": "https://checkout.stripe.com/c/pay/cs_test_SAMPLE2",
   "amount_paid": "369.00",
   "approved_package_summary": "Structural-only — Structural Opening / RSJ Calculations",
   "deliverable_description": "structural calculations",
   "approved_documents_link": "https://drive.google.com/drive/folders/SAMPLE2",
   "project_specific_next_steps": ("Give the calculations and the beam schedule to your "
                                   "builder and to Building Control before the opening is "
                                   "formed. The bearing details must be followed exactly."),
   "review_link": "https://g.page/r/SAMPLE/review",
   "file_receipt_sentence": ("If you have any plans or supporting documents, "
                             "you&rsquo;re welcome to reply to this email with them."),
 },
}


def fill(s, data):
    def sub(m):
        return str(data.get(m.group(1), m.group(0)))
    return re.sub(r"\{\{([a-z_]+)\}\}", sub, s)


def main():
    os.makedirs(TPL, exist_ok=True)
    built = []
    for name, fn in TEMPLATES:
        subject, body = fn()
        path = os.path.join(TPL, name + ".html")
        with open(path, "w") as f:
            f.write(f"<!-- SUBJECT: {subject} -->\n{body}\n")
        built.append((name, subject, body))
        print("wrote", path)

    # preview page
    cards = []
    for key, data in SAMPLES.items():
        cards.append(f'<h2 class="set">{html.escape(data["_label"])}</h2>')
        for name, subject, body in built:
            s = fill(subject, data)
            b = fill(body, data)
            cards.append(
                f'<section><div class="meta"><span class="n">{html.escape(name)}</span>'
                f'<span class="s">Subject: {html.escape(s)}</span></div>'
                f'<div class="mail">{b}</div></section>')

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BuildRegs Email Previews</title>
<style>
 :root {{ --ink:{INK}; --line:{LINE}; --muted:{MUTED}; --page:{PAGE}; }}
 body {{ margin:0; background:#fff; color:var(--ink);
        font:16px/1.5 'Poppins','Segoe UI',Helvetica,Arial,sans-serif; }}
 header {{ padding:28px 16px; border-bottom:1px solid var(--line); }}
 header h1 {{ margin:0 0 6px; font-size:22px; }}
 header p {{ margin:0; color:var(--muted); font-size:14px; }}
 h2.set {{ margin:40px 16px 8px; padding:12px 16px; font-size:16px;
           background:var(--ink); color:#fff; border-radius:6px; }}
 section {{ margin:0 0 28px; }}
 .meta {{ padding:14px 16px 8px; }}
 .n {{ display:inline-block; font-size:12px; letter-spacing:.06em;
       text-transform:uppercase; color:var(--muted); }}
 .s {{ display:block; font-size:15px; font-weight:600; margin-top:4px; }}
 .mail {{ border-top:1px solid var(--line); }}
 @media (max-width:640px) {{ .meta {{ padding:12px; }} }}
</style></head><body>
<header>
 <h1>BuildRegs customer emails &mdash; previews</h1>
 <p>Seven messages, each shown twice: once for a combined project, once for a
 calculations-only project. Rendered with sample data. Nothing here has been sent.</p>
</header>
{''.join(cards)}
</body></html>"""
    out = os.path.join(HERE, "preview.html")
    with open(out, "w") as f:
        f.write(page)
    print("wrote", out)


if __name__ == "__main__":
    main()
