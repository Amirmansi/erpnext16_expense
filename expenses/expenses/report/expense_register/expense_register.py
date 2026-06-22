import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)
	columns = get_columns(filters)
	data = get_data(filters)
	total = sum(flt(row.get("amount")) for row in data)
	report_summary = [
		{
			"value": total,
			"label": _("Total"),
			"datatype": "Currency",
			"indicator": "Blue",
		}
	]
	return columns, data, None, None, report_summary


def validate_filters(filters):
	if not filters.get("company"):
		frappe.throw(_("Please select a Company first."))
	if not filters.get("from_date") or not filters.get("to_date"):
		frappe.throw(_("From Date and To Date are required."))
	if getdate(filters.from_date) > getdate(filters.to_date):
		frappe.throw(_("From Date cannot be after To Date."))


def get_columns(filters):
	return [
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"fieldname": "expense_entry",
			"label": _("Expense Entry"),
			"fieldtype": "Link",
			"options": "Expense Entry",
			"width": 170,
		},
		{
			"fieldname": "mode_of_payment",
			"label": _("Mode of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"width": 180,
		},
		{
			"fieldname": "expense_account",
			"label": _("Expense Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 260,
		},
		{
			"fieldname": "description",
			"label": _("Description"),
			"fieldtype": "Data",
			"width": 320,
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 160,
		},
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200,
		},
		{"fieldname": "currency", "label": _("Currency"), "fieldtype": "Data", "hidden": 1, "width": 80},
	]


def get_data(filters):
	conditions = ["ee.docstatus = 1", "ee.company = %(company)s"]
	values = {
		"company": filters.company,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
	}

	if filters.get("mode_of_payment"):
		conditions.append("ee.mode_of_payment = %(mode_of_payment)s")
		values["mode_of_payment"] = filters.mode_of_payment

	if filters.get("cost_center"):
		conditions.append("IFNULL(ei.cost_center, ee.cost_center) = %(cost_center)s")
		values["cost_center"] = filters.cost_center

	where = " AND ".join(conditions)
	company_currency = frappe.get_cached_value("Company", filters.company, "default_currency")

	rows = frappe.db.sql(
		f"""
		SELECT
			ee.posting_date,
			ee.name AS expense_entry,
			ee.mode_of_payment,
			ei.expense_account,
			ei.description,
			ei.amount,
			IFNULL(ei.cost_center, ee.cost_center) AS cost_center
		FROM `tabExpense Entry` ee
		INNER JOIN `tabExpense Entry Item` ei ON ei.parent = ee.name
		WHERE ee.posting_date BETWEEN %(from_date)s AND %(to_date)s
			AND {where}
		ORDER BY ee.posting_date DESC, ee.name DESC, ei.idx ASC
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row["currency"] = company_currency

	return rows
