#!/usr/bin/env python3
"""Build Phase 2a: a prepared quote arrives from the review page.

Saving writes the project row and stops. Submitting writes the row and emails
Sandeep a preview carrying the one-tap links Phase 2b answers. Neither path
can reach a customer: the only email module here is addressed to Sandeep.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = "1j7h3PsEwa_vHIIEmJXexvIoSJUoS81gv4V4YZRPvETQ"
TAB = "Projects"
CONN_SHEETS, CONN_MAIL = 10263943, 11641152
HOOK = 3960316
HOOK_URL = "https://hook.eu1.make.com/ic5pbkhzsx981i9q6syysrwj48dmjywk"
APPROVE_HOOK = "https://hook.eu1.make.com/u6k1ltrlcq5qs82upswhorlyujnkd531"
OWNER = "support@buildregs.co.uk"
FROM_LINE = '"BuildRegs" <support@buildregs.co.uk>'
# Salts the approval token. Anyone holding this could mint a valid approval
# link, so it stays in the blueprint and never reaches a page a customer sees.
TOKEN_SALT = "BRQ-7f3a91d2"

INK, BODY, MUTED, LINE, PANEL, PAGE = "#17324B", "#33414D", "#6B7A88", "#E3E8ED", "#F7F9FB", "#F4F6F8"
GREEN, AMBER = "#1E7A4B", "#8A5A00"
FONT = "'Poppins','Segoe UI',Helvetica,Arial,sans-serif"
SLOTS = [1, 2, 3, 4]

W = lambda f: "{{1.%s}}" % f
NUM = lambda f: 'parseNumber(ifempty(1.%s; 0))' % f
HAS = lambda f: 'length(trim(ifempty(1.%s; "")))' % f

def money(expr):
    """Always pass separators. Without them formatNumber uses the organisation
    locale, which here is European and renders 1248.5 as 1.248,50."""
    return 'formatNumber(%s; 2; "."; ",")' % expr

def csv_of(field):
    """Join the filled slots. Every item carries a leading separator and the
    first one is then stripped, so a gap in the slots cannot leave a stray
    comma at the front."""
    raw = " + ".join('if(%s > 0; ", " + 1.%s%d; "")' % (HAS("type%d" % i), field, i) for i in SLOTS)
    return '{{if(length(%s) > 2; substring(%s; 2); "")}}' % (raw, raw)

# ---------------------------------------------------------------- variables
# Sibling variables in one SetVariables module cannot reference each other, so
# the arithmetic is split across modules in dependency order.
m2  = [{"name": "p%d" % i, "value": "{{if(%s > 0; %s; 0)}}" % (HAS("type%d" % i), NUM("price%d" % i))} for i in SLOTS]
m2 += [{"name": "n%d" % i, "value": "{{if(%s > 0; 1; 0)}}" % HAS("type%d" % i)} for i in SLOTS]
# An absent slot is parked above any real price so it can never win the minimum.
m2 += [{"name": "b%d" % i, "value": "{{if(%s > 0; %s; 9000000000)}}" % (HAS("type%d" % i), NUM("price%d" % i))} for i in SLOTS]

LOW12, LOW34 = "if(2.b1 < 2.b2; 2.b1; 2.b2)", "if(2.b3 < 2.b4; 2.b3; 2.b4)"
m3 = [
 {"name": "subtotal",  "value": "{{2.p1 + 2.p2 + 2.p3 + 2.p4}}"},
 {"name": "typeCount", "value": "{{2.n1 + 2.n2 + 2.n3 + 2.n4}}"},
 {"name": "minPrice",  "value": "{{if(%s < %s; %s; %s)}}" % (LOW12, LOW34, LOW12, LOW34)},
 {"name": "typesCsv",  "value": csv_of("type")},
 {"name": "pricesCsv", "value": csv_of("price")},
]

m4 = [
 # 50% off the single lowest-priced type, once, and only with two or more of
 # them. An override from the review page replaces it, zero included.
 {"name": "discount", "value":
    '{{if(%s > 0; parseNumber(1.discount_override); '
    'if(3.typeCount >= 2 and 3.minPrice < 9000000000; 3.minPrice / 2; 0))}}' % HAS("discount_override")},
 {"name": "discountLabel", "value":
    '{{if(%s > 0; "Discount (overridden)"; "Combined project discount")}}' % HAS("discount_override")},
 {"name": "overridden", "value": '{{if(%s > 0; "yes"; "no")}}' % HAS("discount_override")},
 {"name": "quoteRef", "value":
    '{{ifempty(1.quote_reference; "BR-Q-" + formatDate(now; "YYYYMMDD") + "-" + formatDate(now; "HHmmss"))}}'},
 {"name": "token", "value":
    '{{ifempty(1.approval_token; md5(formatDate(now; "x") + ifempty(1.customer_email; "") + "%s"))}}' % TOKEN_SALT},
 {"name": "stamp", "value": '{{formatDate(now; "YYYY-MM-DD HH:mm:ss"; "Europe/London")}}'},
 {"name": "isSubmit", "value": '{{if(lower(trim(ifempty(1.action; "save"))) = "submit"; "yes"; "no")}}'},
]
m5 = [
 {"name": "total",  "value": "{{3.subtotal - 4.discount + %s}}" % NUM("adjustment_amount")},
 {"name": "status", "value": '{{if(4.isSubmit = "yes"; "Awaiting approval"; "Draft")}}'},
]
m6 = [{"name": "totalFmt", "value": "{{%s}}" % money("5.total")}]

# ---------------------------------------------------------------- the row
VALUES = {
 0: "{{4.quoteRef}}", 1: W("project_reference"), 2: "{{5.status}}",
 3: "{{4.stamp}}", 4: "{{4.stamp}}",
 5: W("customer_name"), 6: W("customer_email"), 7: W("customer_phone"),
 8: W("property_address"), 9: W("package"),
 10: "{{3.typesCsv}}", 11: "{{3.pricesCsv}}", 12: "{{3.subtotal}}",
 13: "{{4.discountLabel}}", 14: "{{4.discount}}", 15: "{{4.overridden}}",
 16: '{{ifempty(1.adjustment_amount; 0)}}', 17: W("adjustment_reason"),
 18: "{{5.total}}", 19: W("turnaround_days"),
 20: W("approved_scope"), 21: W("approved_exclusions"), 22: W("next_steps"),
 23: W("india_notes"), 32: "{{4.token}}", 40: "no",
 41: '{{if(4.isSubmit = "yes"; "Prepared and sent for approval"; "Draft saved, not sent")}}',
}
ROW = [VALUES.get(i, "") for i in range(42)]
# On an edit, created_at and the token are left alone so existing approval
# links keep working, and columns 24 to 40 are never touched because they hold
# payment and delivery data that belongs to later stages.
EDIT_COLS = [2] + list(range(4, 24)) + [41]

def a1(idx, row_expr):
    s, n = "", idx + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return "%s!%s%s" % (TAB, s, row_expr)

# ---------------------------------------------------------------- the email
def fee_row(i):
    return ('{{if(2.n%d = 1; "<tr><td style=\'padding:0 0 8px 0; font-size:14px; color:%s;\'>" '
            '+ 1.type%d + "</td><td style=\'padding:0 0 8px 0; font-size:14px; color:%s;\'>'
            '&pound;" + %s + "</td></tr>"; "")}}' % (i, MUTED, i, BODY, money("2.p%d" % i)))

FEES = "".join(fee_row(i) for i in SLOTS)
DISC = ('{{if(4.discount > 0; "<tr><td style=\'padding:0 0 8px 0; font-size:14px; color:%s;\'>" '
        '+ 4.discountLabel + "</td><td style=\'padding:0 0 8px 0; font-size:14px; color:%s;\'>'
        '&minus; &pound;" + %s + "</td></tr>"; "")}}' % (MUTED, GREEN, money("4.discount")))
ADJ = ('{{if(%s != 0; "<tr><td style=\'padding:0 0 8px 0; font-size:14px; color:%s;\'>" '
       '+ ifempty(1.adjustment_reason; "Adjustment") + "</td><td style=\'padding:0 0 8px 0; '
       'font-size:14px; color:%s;\'>&pound;" + %s + "</td></tr>"; "")}}'
       % (NUM("adjustment_amount"), MUTED, BODY, money(NUM("adjustment_amount"))))
NOTES = ('{{if(length(trim(ifempty(1.india_notes; ""))) > 0; "<tr><td style=\'padding:20px 32px 0 32px;\'>'
         '<table width=\'100%\' cellpadding=\'0\' cellspacing=\'0\' border=\'0\' style=\'background-color:#FDF6E8; '
         'border:1px solid #EBD9B4; border-radius:6px;\'><tr><td style=\'padding:16px 20px; '
         'font-family:Poppins,Segoe UI,Helvetica,Arial,sans-serif; font-size:14px; line-height:22px; '
         'color:#5C3D00;\'><strong>Your private notes for the India team</strong><br>" + 1.india_notes '
         '+ "<br><span style=\'font-size:13px;\'>Not sent to the customer, and not seen by the team '
         'until payment is confirmed.</span></td></tr></table></td></tr>"; "")}}')

def btn(label, url, colour):
    return ('<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
            'style="display:inline-block; margin:0 6px 10px 0;"><tr><td align="center" bgcolor="%s" '
            'style="border-radius:6px;"><a href="%s" style="display:inline-block; padding:14px 26px; '
            'font-family:%s; font-size:15px; line-height:20px; font-weight:600; color:#FFFFFF; '
            'text-decoration:none; border-radius:6px;">%s</a></td></tr></table>' % (colour, url, FONT, label))

LINK = APPROVE_HOOK + "?ref={{4.quoteRef}}&token={{4.token}}&action=%s"

def kv(label, value, last=False):
    pb = "0" if last else "8px"
    return ('<tr><td style="padding:0 0 %s 0; font-size:13px; color:%s; width:130px;" valign="top">%s</td>'
            '<td style="padding:0 0 %s 0; font-size:14px; line-height:21px; color:%s;">%s</td></tr>'
            % (pb, MUTED, label, pb, BODY, value))

REVIEW_HTML = """<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{PAGE};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:100%; background-color:#FFFFFF; border:1px solid {LINE}; border-radius:8px;">
<tr><td style="padding:24px 32px 18px 32px; background-color:{INK}; border-radius:8px 8px 0 0; font-family:{FONT};">
<p style="margin:0 0 4px 0; font-size:12px; line-height:18px; color:#AFC3D4; letter-spacing:0.08em; text-transform:uppercase;">Quotation ready for your approval</p>
<h1 style="margin:0; font-size:20px; line-height:28px; font-weight:600; color:#FFFFFF;">{{{{4.quoteRef}}}}</h1></td></tr>
<tr><td style="padding:24px 32px 0 32px; font-family:{FONT};"><p style="margin:0 0 16px 0; font-size:15px; line-height:24px; color:{BODY};">Nothing has been sent to the customer yet. Approve below and the quotation and payment link go out. Request information instead and they are asked for more detail.</p></td></tr>
<tr><td style="padding:0 32px;"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{PANEL}; border:1px solid {LINE}; border-radius:6px;"><tr><td style="padding:18px 20px; font-family:{FONT};"><table width="100%" cellpadding="0" cellspacing="0" border="0">{WHO}</table></td></tr></table></td></tr>
<tr><td style="padding:24px 32px 0 32px; font-family:{FONT};"><h2 style="margin:0 0 12px 0; font-size:15px; font-weight:600; color:{INK};">The quote</h2></td></tr>
<tr><td style="padding:0 32px;"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{PANEL}; border:1px solid {LINE}; border-radius:6px;"><tr><td style="padding:18px 20px; font-family:{FONT};"><table width="100%" cellpadding="0" cellspacing="0" border="0">{FEES}{DISC}{ADJ}<tr><td colspan="2" style="padding:10px 0 0 0; border-top:1px solid {LINE};"></td></tr><tr><td style="padding:0; font-size:15px; color:{INK}; font-weight:600;">Total payable</td><td style="padding:0; font-size:19px; color:{INK}; font-weight:700;">&pound;{{{{6.totalFmt}}}}</td></tr></table></td></tr></table></td></tr>
<tr><td style="padding:20px 32px 0 32px; font-family:{FONT};"><table width="100%" cellpadding="0" cellspacing="0" border="0">{TERMS}</table></td></tr>
{NOTES}
<tr><td align="center" style="padding:26px 32px 6px 32px;">{BTN_OK}{BTN_INFO}</td></tr>
<tr><td style="padding:6px 32px 28px 32px; font-family:{FONT};"><p style="margin:0; font-size:13px; line-height:20px; color:{MUTED}; text-align:center;">Approving sends the quotation and creates the payment link. The India team is not told about this job until the customer has paid.</p></td></tr>
</table></td></tr></table>""".format(
 PAGE=PAGE, LINE=LINE, INK=INK, BODY=BODY, MUTED=MUTED, PANEL=PANEL, FONT=FONT,
 FEES=FEES, DISC=DISC, ADJ=ADJ, NOTES=NOTES,
 WHO=(kv("Customer", "{{1.customer_name}}") + kv("Email", "{{1.customer_email}}")
      + kv("Telephone", '{{ifempty(1.customer_phone; "(not supplied)")}}')
      + kv("Property", "{{1.property_address}}") + kv("Enquiry", "{{1.project_reference}}")
      + kv("Package", "{{1.package}}", last=True)),
 TERMS=(kv("Turnaround", "{{1.turnaround_days}} working days")
        + kv("Scope", "{{1.approved_scope}}")
        + kv("Exclusions", '{{ifempty(1.approved_exclusions; "(none)")}}', last=True)),
 BTN_OK=btn("Approve and send", LINK % "approve", GREEN),
 BTN_INFO=btn("Request information", LINK % "request_info", AMBER))


def page(title, line, tone):
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>BuildRegs</title></head><body style='margin:0; background:%s; "
            "font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;'>"
            "<div style='max-width:420px; margin:48px auto; padding:32px 24px; background:#fff; "
            "border:1px solid %s; border-radius:10px; text-align:center;'>"
            "<h1 style='margin:0 0 12px; font-size:20px; color:%s;'>%s</h1>"
            "<p style='margin:0; font-size:15px; line-height:24px; color:%s;'>%s</p>"
            "</div></body></html>" % (PAGE, LINE, tone, title, BODY, line))

def minify(h):
    return re.sub(r"[ \t]*\n[ \t]*", "", re.sub(r">\s+<", "><", h)).strip()

IS_NEW  = [{"a": '{{length(trim(ifempty(1.quote_reference; "")))}}', "o": "number:equal",   "b": "0"}]
IS_EDIT = [{"a": '{{length(trim(ifempty(1.quote_reference; "")))}}', "o": "number:greater", "b": "0"}]

flow = [
 {"id": 1, "module": "gateway:CustomWebHook", "version": 1,
  "metadata": {"designer": {"x": 0, "y": 0, "name": "1. Quote prepared on the review page"},
               "restore": {"parameters": {"hook": {"label": "BuildRegs Quote Prepared", "data": {"editable": "true"}}}}},
  "parameters": {"hook": HOOK, "maxResults": 1}, "mapper": {}},
 {"id": 2, "module": "util:SetVariables", "version": 1,
  "metadata": {"designer": {"x": 300, "y": 0, "name": "2. Read the four slots"}},
  "mapper": {"scope": "roundtrip", "variables": m2}},
 {"id": 3, "module": "util:SetVariables", "version": 1,
  "metadata": {"designer": {"x": 600, "y": 0, "name": "3. Subtotal and lowest price"}},
  "mapper": {"scope": "roundtrip", "variables": m3}},
 {"id": 4, "module": "util:SetVariables", "version": 1,
  "metadata": {"designer": {"x": 900, "y": 0, "name": "4. Discount, reference and token"}},
  "mapper": {"scope": "roundtrip", "variables": m4}},
 {"id": 5, "module": "util:SetVariables", "version": 1,
  "metadata": {"designer": {"x": 1200, "y": 0, "name": "5. Total and status"}},
  "mapper": {"scope": "roundtrip", "variables": m5}},
 {"id": 6, "module": "util:SetVariables", "version": 1,
  "metadata": {"designer": {"x": 1500, "y": 0, "name": "6. Format the money"}},
  "mapper": {"scope": "roundtrip", "variables": m6}},
 {"id": 50, "module": "builtin:BasicRouter", "version": 1,
  "metadata": {"designer": {"x": 1800, "y": 0, "name": "7. Router"}}, "mapper": {}, "routes": [
   {"flow": [
     {"id": 60, "module": "google-sheets:makeAPICall", "version": 2,
      "metadata": {"designer": {"x": 2100, "y": -200, "name": "8a. New project, append a row"}},
      "parameters": {"__IMTCONN__": CONN_SHEETS},
      "filter": {"name": "No quotation reference supplied", "conditions": [IS_NEW]},
      "mapper": {"url": "spreadsheets/%s/values/%s!A1:append" % (SHEET, TAB), "method": "POST",
                 "qs": [{"key": "valueInputOption", "value": "USER_ENTERED"},
                        {"key": "insertDataOption", "value": "INSERT_ROWS"}],
                 "headers": [], "body": {"values": [ROW]}}}]},
   {"flow": [
     {"id": 70, "module": "google-sheets:filterRows", "version": 2,
      "metadata": {"designer": {"x": 2100, "y": 200, "name": "8b. Find the existing draft"}},
      "parameters": {"__IMTCONN__": CONN_SHEETS},
      "filter": {"name": "A quotation reference was supplied", "conditions": [IS_EDIT]},
      "mapper": {"from": "drive", "limit": "1", "sheetId": TAB, "spreadsheetId": SHEET,
                 "includesHeaders": True, "tableFirstRow": "A1:BZ1", "sortOrder": "asc",
                 "valueRenderOption": "UNFORMATTED_VALUE", "dateTimeRenderOption": "FORMATTED_STRING",
                 "filter": [[{"a": "A", "o": "text:equal", "b": "{{1.quote_reference}}"}]]}},
     {"id": 71, "module": "google-sheets:makeAPICall", "version": 2,
      "metadata": {"designer": {"x": 2400, "y": 200, "name": "9b. Update it in place"}},
      "parameters": {"__IMTCONN__": CONN_SHEETS},
      "mapper": {"url": "spreadsheets/%s/values:batchUpdate" % SHEET, "method": "POST",
                 "headers": [], "qs": [],
                 "body": {"valueInputOption": "USER_ENTERED",
                          "data": [{"range": a1(i, "{{70.__ROW_NUMBER__}}"), "values": [[ROW[i]]]}
                                   for i in EDIT_COLS]}}}]},
   {"flow": [
     {"id": 80, "module": "email:ActionSendEmail", "version": 6,
      "metadata": {"designer": {"x": 2100, "y": 0, "name": "8c. Send Sandeep the preview"}},
      "parameters": {"account": CONN_MAIL, "saveAfterSent": False},
      "filter": {"name": "Submitted for approval, not merely saved",
                 "conditions": [[{"a": "{{4.isSubmit}}", "o": "text:equal", "b": "yes"}]]},
      "mapper": {"to": [OWNER], "cc": [], "bcc": [], "from": FROM_LINE, "sender": "", "replyTo": OWNER,
                 "subject": "Approve quotation {{4.quoteRef}} - {{1.property_address}}",
                 "contentType": "html", "html": minify(REVIEW_HTML), "priority": "high",
                 "headers": [], "attachments": [], "inReplyTo": "", "references": []}}]},
   {"flow": [
     {"id": 90, "module": "gateway:WebhookRespond", "version": 1,
      "metadata": {"designer": {"x": 2100, "y": 400, "name": "8d. Answer the review page"}},
      "mapper": {"status": "200",
                 "headers": [{"key": "Content-Type", "value": "text/html; charset=utf-8"}],
                 "body": '{{if(4.isSubmit = "yes"; "%s"; "%s")}}' % (
                   minify(page("Sent for your approval",
                               "The quote is saved and the approval email is on its way to you. "
                               "Nothing has gone to the customer.", GREEN)).replace('"', "'"),
                   minify(page("Draft saved",
                               "Nothing has been sent. Reopen this quote whenever you want to "
                               "carry on.", AMBER)).replace('"', "'"))}}]}]}]

bp = {"name": "BuildRegs Phase 2a - Quote prepared, await approval",
      "metadata": {"version": 1}, "flow": flow}
out = os.path.join(HERE, "phase2a.blueprint.json")
json.dump(bp, open(out, "w"), indent=1)
print("wrote", out)
print("modules:", 7 + sum(len(r["flow"]) for r in flow[6]["routes"]))
print("flat bytes:", len(json.dumps(bp)))
