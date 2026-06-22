import frappe

from expenses.setup.print_templates import EXPENSE_ENTRY_HTML


def setup_expense_print_formats():
	if not frappe.db.exists("Print Format", "Expense Entry Standard"):
		frappe.get_doc(
			{
				"doctype": "Print Format",
				"name": "Expense Entry Standard",
				"doc_type": "Expense Entry",
				"module": "Expenses",
				"print_format_type": "Jinja",
				"custom_format": 1,
				"standard": "No",
				"disabled": 0,
				"default_print_language": "ar",
				"html": EXPENSE_ENTRY_HTML,
			}
		).insert(ignore_permissions=True)
	else:
		doc = frappe.get_doc("Print Format", "Expense Entry Standard")
		doc.html = EXPENSE_ENTRY_HTML
		doc.disabled = 0
		doc.save(ignore_permissions=True)

	_set_default_print_format("Expense Entry", "Expense Entry Standard")


def _set_default_print_format(doctype, print_format):
	if frappe.db.exists(
		"Property Setter",
		{"doc_type": doctype, "property": "default_print_format"},
	):
		frappe.db.set_value(
			"Property Setter",
			{"doc_type": doctype, "property": "default_print_format"},
			"value",
			print_format,
		)
	else:
		frappe.make_property_setter(
			{
				"doctype": doctype,
				"fieldname": None,
				"property": "default_print_format",
				"property_type": "Data",
				"value": print_format,
			}
		)
