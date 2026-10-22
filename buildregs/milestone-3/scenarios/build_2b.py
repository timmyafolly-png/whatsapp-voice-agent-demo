#!/usr/bin/env python3
"""Build the Phase 2b blueprint: quote approval links.

Sandeep taps Approve or Request information in his internal email. This
scenario is what those links hit. Nothing here can reach a customer unless
the token on the link matches the token stored on the project row.
"""
import json, os, re
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = "1j7h3PsEwa_vHIIEmJXexvIoSJUoS81gv4V4YZRPvETQ"
TAB = "Projects"
CONN_SHEETS = 10263943
CONN_MAIL = 11641152
CONN_STRIPE = 10506139
HOOK = 3957194          # BuildRegs Quote Approval
HOOK_URL = "https://hook.eu1.make.com/u6k1ltrlcq5qs82upswhorlyujnkd531"
SCENARIO_ID = 8118767

# Projects columns as filterRows 0-based indices
C = {n: i for i, n in enumerate([
 "quote_reference","project_reference","status","created_at","updated_at",
 "customer_name","customer_email","customer_phone","property_address","package",
 "project_types","standard_prices","subtotal","discount_type","discount_amount",
 "discount_overridden","adjustment_amount","adjustment_reason","total",
 "turnaround_days","approved_scope","approved_exclusions","next_steps",
 "india_notes","project_folder_url","plans_folder_url","approved_output_url",
 "stripe_session_id","stripe_payment_id","amount_paid","payment_currency",
 "paid_at","approval_token","approved_at","quote_sent_at","handover_sent_at",
 "ready_for_review_at","delivered_at","checkin_sent_at","review_request_sent_at",
 "awaiting_information","notes"])}

def col(name):
    """filterRows reference for a Projects column."""
    return "{{2.`%d`}}" % C[name]

def enc(name):
    """A Projects column, percent-encoded for a form-urlencoded body. The
    property address carries spaces and commas, which would otherwise break
    the body Stripe parses."""
    return "{{encodeURL(%s)}}" % col(name).strip("{}")


def a1(name, row_expr):
    """A1 column letter for a Projects column, with a mapped row number."""
    i, s = C[name], ""
    n = i + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return "%s!%s%s" % (TAB, s, row_expr)

ROW = "{{2.__ROW_NUMBER__}}"
STAMP = '{{formatDate(now; "YYYY-MM-DD HH:mm:ss"; "Europe/London")}}'

# ---------------------------------------------------------------- fee lines
def fee_line(n):
    """One itemised fee row, rendered only when an nth project type exists."""
    types = 'split(%s; ", ")' % col("project_types").strip("{}")
    prices = 'split(%s; ", ")' % col("standard_prices").strip("{}")
    return (
      '{{if(length(%s) >= %d; '
      '"<tr><td style=\'padding:0 0 10px 0; font-size:14px; line-height:20px; color:#6B7A88; width:60%%;\'>" '
      '+ get(%s; %d) + '
      '"</td><td style=\'padding:0 0 10px 0; font-size:15px; line-height:20px; color:#33414D;\'>&pound;" '
      '+ formatNumber(parseNumber(get(%s; %d)); 2) + "</td></tr>"; "")}}'
      % (types, n, types, n, prices, n))

ITEMISED = "".join(fee_line(i) for i in range(1, 5))

DISCOUNT_ROW = (
  '{{if(parseNumber(ifempty(%s; 0)) > 0; '
  '"<tr><td style=\'padding:0 0 10px 0; font-size:14px; line-height:20px; color:#6B7A88;\'>" '
  '+ %s + '
  '" discount</td><td style=\'padding:0 0 10px 0; font-size:15px; line-height:20px; color:#1E7A4B;\'>&minus; &pound;" '
  '+ formatNumber(parseNumber(%s); 2) + "</td></tr>"; "")}}'
  % (col("discount_amount").strip("{}"), col("discount_type").strip("{}"),
     col("discount_amount").strip("{}")))

ADJUSTMENT_ROW = (
  '{{if(parseNumber(ifempty(%s; 0)) != 0; '
  '"<tr><td style=\'padding:0 0 10px 0; font-size:14px; line-height:20px; color:#6B7A88;\'>" '
  '+ ifempty(%s; "Adjustment") + '
  '"</td><td style=\'padding:0 0 10px 0; font-size:15px; line-height:20px; color:#33414D;\'>&pound;" '
  '+ formatNumber(parseNumber(%s); 2) + "</td></tr>"; "")}}'
  % (col("adjustment_amount").strip("{}"), col("adjustment_reason").strip("{}"),
     col("adjustment_amount").strip("{}")))

CONDITIONS = (
  '{{if(length(trim(ifempty(%s; ""))) > 0; '
  '"<tr><td style=\'padding:20px 32px 0 32px;\'><table role=\'presentation\' width=\'100%%\' '
  'cellpadding=\'0\' cellspacing=\'0\' border=\'0\' style=\'background-color:#F7F9FB; '
  'border:1px solid #E3E8ED; border-radius:6px;\'><tr><td style=\'padding:20px 24px; '
  'font-family:Poppins,Segoe UI,Helvetica,Arial,sans-serif; font-size:15px; line-height:24px; '
  'color:#33414D;\'><strong style=\'color:#17324B;\'>Please note</strong><br>" + %s '
  '+ "</td></tr></table></td></tr>"; "")}}'
  % (col("approved_exclusions").strip("{}"), col("approved_exclusions").strip("{}")))

# ---------------------------------------------------------------- email body
TPL = open(os.path.join(HERE, "..", "emails", "templates",
                        "02-approved-quotation.html")).read()
TPL = re.sub(r"^<!-- SUBJECT:.*?-->\n", "", TPL, flags=re.S)

SUBS = {
 "greeting": "{{10.greeting}}",
 "property_address": col("property_address"),
 "quote_reference": col("quote_reference"),
 "approved_scope": col("approved_scope"),
 "itemised_fees": ITEMISED,
 "combined_project_discount": DISCOUNT_ROW,
 "price_adjustment": ADJUSTMENT_ROW,
 "total": "{{10.totalFmt}}",
 "approved_exclusions_or_conditions": CONDITIONS,
 "turnaround": col("turnaround_days"),
 "stripe_payment_link": "{{21.body.url}}",
}
def minify(h):
    """Collapse whitespace between tags. Inline styles are untouched, so this
    changes the bytes on the wire and not the rendering."""
    h = re.sub(r">\s+<", "><", h)
    return re.sub(r"[ \t]*\n[ \t]*", "", h).strip()

QUOTE_HTML = minify(re.sub(r"\{\{([a-z_]+)\}\}",
                           lambda m: SUBS.get(m.group(1), m.group(0)), TPL))

INFO_HTML = """<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#F4F6F8;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:100%; background-color:#FFFFFF; border:1px solid #E3E8ED; border-radius:8px;">
<tr><td align="left" style="padding:28px 32px 20px 32px; border-bottom:1px solid #E3E8ED;">
<img src="https://buildregs.co.uk/wp-content/uploads/2025/11/BuildRegs-Black-1024x227.png" alt="BuildRegs" width="150" style="display:block; width:150px; max-width:150px; height:auto; border:0;"></td></tr>
<tr><td style="padding:32px 32px 0 32px; font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">
<h1 style="margin:0 0 16px 0; font-size:22px; line-height:30px; font-weight:600; color:#17324B;">We need a little more information</h1>
<p style="margin:0 0 16px 0; font-size:15px; line-height:24px; color:#33414D;">{{10.greeting}}</p>
<p style="margin:0 0 16px 0; font-size:15px; line-height:24px; color:#33414D;">Thank you for your enquiry about your project at <strong>""" + col("property_address") + """</strong>. Before we can prepare your fixed-fee quotation, we need a little more detail about the work.</p>
<p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#33414D;">""" + ("{{ifempty(1.message; \"Please reply to this email describing the work you are planning, and attach any drawings or supporting documents you already have.\")}}") + """</p></td></tr>
<tr><td style="padding:0 32px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#F7F9FB; border:1px solid #E3E8ED; border-radius:6px;">
<tr><td style="padding:20px 24px; font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:0 0 10px 0; font-size:13px; line-height:20px; color:#6B7A88; width:150px;">Your reference</td><td style="padding:0 0 10px 0; font-size:15px; line-height:20px; color:#17324B; font-weight:600;">""" + col("quote_reference") + """</td></tr>
<tr><td style="padding:0; font-size:13px; line-height:20px; color:#6B7A88;">Property</td><td style="padding:0; font-size:15px; line-height:20px; color:#33414D;">""" + col("property_address") + """</td></tr>
</table></td></tr></table></td></tr>
<tr><td style="padding:24px 32px 0 32px; font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">
<p style="margin:0 0 8px 0; font-size:15px; line-height:24px; color:#33414D;">Just reply to this email and we will pick it up from there. As soon as we have what we need, we will send your quotation.</p></td></tr>
<tr><td style="padding:8px 32px 32px 32px; border-top:1px solid #E3E8ED; font-family:'Poppins','Segoe UI',Helvetica,Arial,sans-serif;">
<p style="margin:16px 0 0 0; font-size:15px; line-height:24px; color:#33414D;">Kind regards,<br>
<strong style="color:#17324B;">The BuildRegs Team</strong><br>
<span style="font-size:13px; line-height:20px; color:#6B7A88;">Building Regulations Drawings &amp; Structural Calculations</span><br>
<a href="mailto:support@buildregs.co.uk" style="font-size:13px; line-height:20px; color:#17324B;">support@buildregs.co.uk</a><br>
<a href="https://www.buildregs.co.uk/" style="font-size:13px; line-height:20px; color:#17324B;">www.buildregs.co.uk</a></p></td></tr>
</table></td></tr></table>"""


def page(title, line, tone="#1E7A4B"):
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>BuildRegs</title></head>"
            "<body style='margin:0; background:#F4F6F8; font-family:-apple-system,"
            "BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;'>"
            "<div style='max-width:420px; margin:48px auto; padding:32px 24px; "
            "background:#fff; border:1px solid #E3E8ED; border-radius:10px; text-align:center;'>"
            "<h1 style='margin:0 0 12px; font-size:20px; color:%s;'>%s</h1>"
            "<p style='margin:0; font-size:15px; line-height:24px; color:#33414D;'>%s</p>"
            "</div></body></html>" % (tone, title, line))


# The first word of the customer name, or "Hello," when there is none. Built as a
# whole greeting rather than "Hi " plus a field, so an empty name can never
# produce "Hi ,".
_FIRST = 'trim(get(split(%s; " "); 1))' % col("customer_name").strip("{}")
GREETING = ('{{if(length(ifempty(' + _FIRST + '; "")) > 0; "Hi " + '
            + _FIRST + ' + ","; "Hello,")}}')

TOKEN_OK = [{"a": "{{1.token}}", "o": "text:equal", "b": col("approval_token")}]

flow = [
 {"id": 1, "module": "gateway:CustomWebHook", "version": 1,
  "metadata": {"designer": {"x": 0, "y": 0, "name": "1. Approval link tapped"},
               "restore": {"parameters": {"hook": {"label": "BuildRegs Quote Approval",
                                                   "data": {"editable": "true"}}}}},
  "parameters": {"hook": HOOK, "maxResults": 1}, "mapper": {}},

 {"id": 2, "module": "google-sheets:filterRows", "version": 2,
  "metadata": {"designer": {"x": 300, "y": 0, "name": "2. Find the project row"}},
  "parameters": {"__IMTCONN__": CONN_SHEETS},
  "mapper": {"from": "drive", "limit": "1", "sheetId": TAB,
             "spreadsheetId": SHEET, "includesHeaders": True,
             "tableFirstRow": "A1:BZ1", "sortOrder": "asc",
             "valueRenderOption": "UNFORMATTED_VALUE",
             "dateTimeRenderOption": "FORMATTED_STRING",
             "filter": [[{"a": "A", "o": "text:equal", "b": "{{1.ref}}"}]]}},

 {"id": 10, "module": "util:SetVariables", "version": 1,
  "metadata": {"designer": {"x": 600, "y": 0, "name": "3. Build the fields"}},
  "mapper": {"scope": "roundtrip", "variables": [
    {"name": "greeting", "value": GREETING},
    {"name": "totalFmt", "value": "{{formatNumber(parseNumber(%s); 2)}}" % col("total").strip("{}")},
    {"name": "totalPence", "value": "{{round(parseNumber(%s) * 100)}}" % col("total").strip("{}")},
    {"name": "packageName",
     "value": '{{ifempty(%s; "BuildRegs package")}}' % col("package").strip("{}")},
    {"name": "stamp", "value": STAMP}]}},

 {"id": 50, "module": "builtin:BasicRouter", "version": 1,
  "metadata": {"designer": {"x": 900, "y": 0, "name": "4. Router"}},
  "mapper": {}, "routes": [

   # ---- route 1: kill any previous unpaid payment link
   {"flow": [
     {"id": 20, "module": "stripe:makeAnApiCall", "version": 1,
      "metadata": {"designer": {"x": 1200, "y": -300,
                                "name": "5a. Expire the old payment link"}},
      "parameters": {"__IMTCONN__": CONN_STRIPE},
      "filter": {"name": "Approving, and an old session exists",
                 "conditions": [TOKEN_OK
                                + [{"a": "{{1.action}}", "o": "text:equal", "b": "approve"},
                                   # NOT "exist": in Make an empty string exists, so a
                                   # blank session id would send the expire call to
                                   # /v1/checkout/sessions//expire with no id in the path.
                                   {"a": "{{length(trim(ifempty(%s; \"\")))}}" % col("stripe_session_id").strip("{}"),
                                    "o": "number:greater", "b": "0"}]]},
      "mapper": {"url": "/v1/checkout/sessions/%s/expire" % col("stripe_session_id"),
                 "method": "POST", "headers": [], "qs": [], "body": ""},
      "onerror": [{"id": 29, "module": "builtin:Resume", "version": 1,
                   "metadata": {"designer": {"x": 1500, "y": -300,
                                             "name": "Already expired or paid, carry on"}},
                   "mapper": {}}]}]},

   # ---- route 2: approve, then and only then create the link and send
   {"flow": [
     {"id": 21, "module": "stripe:makeAnApiCall", "version": 1,
      "metadata": {"designer": {"x": 1200, "y": 0, "name": "5b. Create the payment link"}},
      "parameters": {"__IMTCONN__": CONN_STRIPE},
      "filter": {"name": "Token matches and action is approve",
                 "conditions": [TOKEN_OK
                                + [{"a": "{{1.action}}", "o": "text:equal", "b": "approve"}]]},
      "mapper": {"url": "/v1/checkout/sessions", "method": "POST",
                 "headers": [{"key": "Content-Type",
                              "value": "application/x-www-form-urlencoded"}],
                 "qs": [],
                 "body": "".join([
                     "mode=payment",
                     "&success_url=https://buildregs.co.uk/thank-you",
                     "&customer_email=", enc("customer_email"),
                     "&line_items[0][quantity]=1",
                     "&line_items[0][price_data][currency]=gbp",
                     "&line_items[0][price_data][unit_amount]={{10.totalPence}}",
                     "&line_items[0][price_data][product_data][name]=",
                     quote("BuildRegs - "), "{{encodeURL(10.packageName)}}",
                     "&line_items[0][price_data][product_data][description]=",
                     quote("Project: "), enc("property_address"),
                     quote(" / Quotation reference: "), enc("quote_reference"),
                     "&custom_text[submit][message]=", quote(
                         "Secure payment for the services set out in your BuildRegs "
                         "quotation. Once your payment is confirmed, we will email your "
                         "confirmation and next steps. For any questions before paying, "
                         "contact support@buildregs.co.uk."),
                     "&metadata[quote_reference]=", enc("quote_reference"),
                     "&metadata[project_reference]=", enc("project_reference"),
                     "&metadata[client_email]=", enc("customer_email"),
                     "&metadata[final_price]=", col("total"),
                 ])}},

     {"id": 22, "module": "email:ActionSendEmail", "version": 6,
      "metadata": {"designer": {"x": 1500, "y": 0, "name": "6b. Send the quotation"}},
      "parameters": {"account": CONN_MAIL, "saveAfterSent": False},
      "mapper": {"to": [col("customer_email")], "cc": [], "bcc": [],
                 "from": "", "sender": "BuildRegs", "replyTo": "support@buildregs.co.uk",
                 "subject": "Your fixed-fee quotation - " + col("property_address") + " | BuildRegs",
                 "contentType": "html", "html": QUOTE_HTML,
                 "priority": "normal", "headers": [], "attachments": [],
                 "inReplyTo": "", "references": []}},

     {"id": 23, "module": "google-sheets:makeAPICall", "version": 2,
      "metadata": {"designer": {"x": 1800, "y": 0, "name": "7b. Record it on the project row"}},
      "parameters": {"__IMTCONN__": CONN_SHEETS},
      "mapper": {"url": "spreadsheets/%s/values:batchUpdate" % SHEET,
                 "method": "POST", "headers": [], "qs": [],
                 "body": {"valueInputOption": "USER_ENTERED", "data": [
                   {"range": a1("status", ROW), "values": [["Quote sent"]]},
                   {"range": a1("updated_at", ROW), "values": [["{{10.stamp}}"]]},
                   {"range": a1("approved_at", ROW), "values": [["{{10.stamp}}"]]},
                   {"range": a1("quote_sent_at", ROW), "values": [["{{10.stamp}}"]]},
                   {"range": a1("stripe_session_id", ROW), "values": [["{{21.body.id}}"]]}]}}},

     {"id": 24, "module": "gateway:WebhookRespond", "version": 1,
      "metadata": {"designer": {"x": 2100, "y": 0, "name": "8b. Confirm to Sandeep"}},
      "mapper": {"status": "200",
                 "headers": [{"key": "Content-Type", "value": "text/html; charset=utf-8"}],
                 "body": page("Quotation approved and sent",
                              "The quotation for " + col("quote_reference")
                              + " has gone to the customer with a payment link. "
                                "The India team has not been notified; that happens "
                                "only once payment is confirmed.")}}]},

   # ---- route 3: ask the customer for more information, no quote, no link
   {"flow": [
     {"id": 30, "module": "email:ActionSendEmail", "version": 6,
      "metadata": {"designer": {"x": 1200, "y": 300, "name": "5c. Ask for more information"}},
      "parameters": {"account": CONN_MAIL, "saveAfterSent": False},
      "filter": {"name": "Token matches and action is request information",
                 "conditions": [TOKEN_OK
                                + [{"a": "{{1.action}}", "o": "text:equal",
                                    "b": "request_info"}]]},
      "mapper": {"to": [col("customer_email")], "cc": [], "bcc": [],
                 "from": "", "sender": "BuildRegs", "replyTo": "support@buildregs.co.uk",
                 "subject": "We need a little more information | BuildRegs",
                 "contentType": "html", "html": minify(INFO_HTML),
                 "priority": "normal", "headers": [], "attachments": [],
                 "inReplyTo": "", "references": []}},

     {"id": 31, "module": "google-sheets:makeAPICall", "version": 2,
      "metadata": {"designer": {"x": 1500, "y": 300, "name": "6c. Record it on the project row"}},
      "parameters": {"__IMTCONN__": CONN_SHEETS},
      "mapper": {"url": "spreadsheets/%s/values:batchUpdate" % SHEET,
                 "method": "POST", "headers": [], "qs": [],
                 "body": {"valueInputOption": "USER_ENTERED", "data": [
                   {"range": a1("status", ROW), "values": [["Draft"]]},
                   {"range": a1("updated_at", ROW), "values": [["{{10.stamp}}"]]},
                   {"range": a1("notes", ROW),
                    "values": [["Information requested from the customer on {{10.stamp}}"]]}]}}},

     {"id": 32, "module": "gateway:WebhookRespond", "version": 1,
      "metadata": {"designer": {"x": 1800, "y": 300, "name": "7c. Confirm to Sandeep"}},
      "mapper": {"status": "200",
                 "headers": [{"key": "Content-Type", "value": "text/html; charset=utf-8"}],
                 "body": page("Information requested",
                              "We have asked the customer for more detail about "
                              + col("quote_reference")
                              + ". No quotation and no payment link were sent. The "
                                "draft is saved and waiting for you.",
                              "#8A5A00")}}]}]}]

bp = {"name": "BuildRegs Phase 2b - Quote approval (approve or request info)",
      "metadata": {"version": 1}, "flow": flow}

out = os.path.join(HERE, "phase2b.blueprint.json")
with open(out, "w") as f:
    json.dump(bp, f, indent=1)
print("wrote", out)
print("modules:", 1 + 1 + 1 + 1 + sum(len(r["flow"]) for r in flow[3]["routes"]))
print("quote html bytes:", len(QUOTE_HTML))
