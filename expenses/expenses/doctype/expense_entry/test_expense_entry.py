# Copyright (c) 2022, efeone Pvt Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestExpenseEntry(FrappeTestCase):
	def test_gl_entries_balance_on_submit(self):
		company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company found in the test site")

		cost_center = frappe.get_cached_value("Company", company, "cost_center")
		expense_account = frappe.db.get_value(
			"Account", {"company": company, "root_type": "Expense", "is_group": 0}, "name"
		)
		payment_account = frappe.db.get_value(
			"Account",
			{"company": company, "account_type": ["in", ["Bank", "Cash"]], "is_group": 0},
			"name",
		)
		if not (cost_center and expense_account and payment_account):
			self.skipTest("Test site is missing required accounts")

		doc = frappe.get_doc(
			{
				"doctype": "Expense Entry",
				"company": company,
				"posting_date": frappe.utils.nowdate(),
				"cost_center": cost_center,
				"payment_account": payment_account,
				"account_currency": frappe.get_cached_value("Account", payment_account, "account_currency"),
				"expenses": [
					{"expense_account": expense_account, "amount": 100, "cost_center": cost_center},
					{"expense_account": expense_account, "amount": 50, "cost_center": cost_center},
				],
			}
		)
		# Pre-set the payment account so the Mode of Payment lookup is not required here.
		doc.flags.ignore_mandatory = True
		doc.insert()
		self.assertEqual(doc.total_amount, 150)

		doc.submit()
		gl = frappe.get_all(
			"GL Entry",
			filters={"voucher_type": "Expense Entry", "voucher_no": doc.name, "is_cancelled": 0},
			fields=["debit", "credit"],
		)
		total_debit = sum(row.debit for row in gl)
		total_credit = sum(row.credit for row in gl)
		self.assertEqual(total_debit, 150)
		self.assertEqual(total_credit, 150)
		self.assertEqual(total_debit, total_credit)

		doc.cancel()
