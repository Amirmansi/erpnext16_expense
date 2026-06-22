import json

import frappe


def setup_expenses_workspace(name="Expenses"):
	shortcuts = [
		{
			"label": "مصروف جديد",
			"type": "DocType",
			"link_to": "Expense Entry",
			"doc_view": "New",
			"color": "Green",
		},
		{
			"label": "قائمة المصروفات",
			"type": "DocType",
			"link_to": "Expense Entry",
			"doc_view": "List",
			"color": "Blue",
		},
		{
			"label": "مصروفات اليوم",
			"type": "DocType",
			"link_to": "Expense Entry",
			"doc_view": "List",
			"color": "Orange",
			"stats_filter": '{"posting_date":["Timespan","today"],"docstatus":1}',
		},
		{
			"label": "مصروفات الشهر",
			"type": "DocType",
			"link_to": "Expense Entry",
			"doc_view": "List",
			"color": "Purple",
			"stats_filter": '{"posting_date":["Timespan","this month"],"docstatus":1}',
		},
		{
			"label": "سجل المصروفات",
			"type": "Report",
			"link_to": "Expense Register",
			"color": "Red",
		},
	]

	links = [
		{"type": "Card Break", "label": "المصروفات", "link_count": 0, "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"type": "Link", "label": "مصروف جديد", "link_type": "DocType", "link_to": "Expense Entry", "onboard": 0, "hidden": 0, "is_query_report": 0},
		{"type": "Link", "label": "قائمة المصروفات", "link_type": "DocType", "link_to": "Expense Entry", "onboard": 0, "hidden": 0, "is_query_report": 0},
		{"type": "Link", "label": "سجل المصروفات", "link_type": "Report", "link_to": "Expense Register", "onboard": 0, "hidden": 0, "is_query_report": 1},
		{"type": "Link", "label": "دفتر الأستاذ", "link_type": "Report", "link_to": "General Ledger", "onboard": 0, "hidden": 0, "is_query_report": 1},
	]

	content = [
		{"type": "header", "text": '<span class="h4"><b>المصروفات</b></span>'},
		{"type": "shortcut", "label": "مصروف جديد", "col": 3},
		{"type": "shortcut", "label": "قائمة المصروفات", "col": 3},
		{"type": "shortcut", "label": "سجل المصروفات", "col": 3},
		{"type": "shortcut", "label": "مصروفات الشهر", "col": 3},
	]

	ws_name = _find_workspace(name)
	if ws_name:
		ws = frappe.get_doc("Workspace", ws_name)
		ws.charts = []
		ws.number_cards = []
		ws.shortcuts = []
		ws.links = []
		ws.quick_lists = []
		ws.custom_blocks = []
	else:
		ws = frappe.new_doc("Workspace")
		ws.name = name
		ws.module = "Expenses"
		ws.parent_page = ""

	ws.title = "المصروفات"
	ws.label = "المصروفات"
	ws.icon = "expense"
	ws.sequence_id = 7.0
	ws.public = 1
	ws.content = _build_content(content)

	for sc in shortcuts:
		ws.append("shortcuts", sc)
	for link in links:
		ws.append("links", link)

	ws.save(ignore_permissions=True)
	frappe.db.set_value("Workspace", ws.name, {"label": "المصروفات", "title": "المصروفات"}, update_modified=False)


def _find_workspace(default_name):
	for candidate in (default_name, "المصروفات"):
		if frappe.db.exists("Workspace", candidate):
			return candidate
	row = frappe.db.get_value("Workspace", {"module": "Expenses"}, "name")
	return row


def _build_content(blocks):
	items = []
	for block in blocks:
		item = {"id": frappe.generate_hash(length=10), "type": block["type"], "data": {}}
		if block["type"] == "header":
			item["data"] = {"text": block["text"], "col": 12}
		elif block["type"] == "shortcut":
			item["data"] = {"shortcut_name": block["label"], "col": block.get("col", 3)}
		items.append(item)
	return json.dumps(items)
