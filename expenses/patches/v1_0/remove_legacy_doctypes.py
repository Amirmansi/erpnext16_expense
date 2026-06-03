# Copyright (c) 2022, efeone Pvt Ltd and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Drop the legacy tax/settings doctypes removed in the v15 rewrite.

	The new Expense Entry has no taxes and no approval settings, so these
	tables/doctypes are obsolete. Safe to run repeatedly.
	"""
	legacy_doctypes = [
		"Expense Entry Taxes and Charges",
		"Expenses Settings",
	]

	for doctype in legacy_doctypes:
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_missing=True)
