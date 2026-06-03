# Copyright (c) 2022, efeone Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, nowdate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController


class ExpenseEntry(AccountsController):
	def validate(self):
		self.set_missing_values()
		self.validate_company_currency()
		self.validate_expenses()
		self.calculate_total_amount()
		self.set_child_cost_centers()

	def on_submit(self):
		self.make_gl_entries()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
		self.make_gl_entries(cancel=True)

	def set_missing_values(self):
		if not self.posting_date:
			self.posting_date = nowdate()

		if not self.company:
			self.company = frappe.defaults.get_user_default("Company")

		if not self.cost_center and self.company:
			self.cost_center = frappe.get_cached_value("Company", self.company, "cost_center")

		# Resolve the bank/cash account directly from the selected Mode of Payment.
		if self.mode_of_payment and not self.payment_account:
			self.payment_account = get_mode_of_payment_account(self.mode_of_payment, self.company)

		if not self.payment_account:
			frappe.throw(
				_("Could not find a default account for Mode of Payment {0} in company {1}. "
				  "Please set it under Accounting Settings > Mode of Payment.").format(
					frappe.bold(self.mode_of_payment), frappe.bold(self.company)
				)
			)

		if self.payment_account:
			self.account_currency = frappe.get_cached_value(
				"Account", self.payment_account, "account_currency"
			)

	def validate_company_currency(self):
		"""This app keeps everything in the company currency to stay simple and safe."""
		company_currency = frappe.get_cached_value("Company", self.company, "default_currency")
		if self.account_currency and self.account_currency != company_currency:
			frappe.throw(
				_("Payment Account currency ({0}) must match the company currency ({1}).").format(
					frappe.bold(self.account_currency), frappe.bold(company_currency)
				)
			)

	def validate_expenses(self):
		if not self.get("expenses"):
			frappe.throw(_("Please add at least one expense row."))

		for row in self.expenses:
			if flt(row.amount) <= 0:
				frappe.throw(_("Row #{0}: Amount must be greater than zero.").format(row.idx))

			# Fall back to the account name so GL remarks are never blank.
			if not row.description:
				row.description = frappe.get_cached_value("Account", row.expense_account, "account_name")

	def calculate_total_amount(self):
		self.total_amount = sum(flt(row.amount) for row in self.get("expenses"))
		if flt(self.total_amount) <= 0:
			frappe.throw(_("Total Amount must be greater than zero."))

	def set_child_cost_centers(self):
		for row in self.expenses:
			if not row.cost_center:
				row.cost_center = self.cost_center

	def make_gl_entries(self, cancel=False):
		gl_entries = self.get_gl_entries()
		if gl_entries:
			make_gl_entries(gl_entries, cancel=cancel, merge_entries=False)

	def get_gl_entries(self):
		"""Balanced by construction: sum(debits) == total_amount == single credit."""
		gl_entries = []

		# Debit each expense line to its expense account.
		for row in self.expenses:
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": row.expense_account,
						"debit": flt(row.amount),
						"debit_in_account_currency": flt(row.amount),
						"against": self.payment_account,
						"cost_center": row.cost_center or self.cost_center,
						"project": row.project or self.project,
						"remarks": row.description,
					},
					item=row,
				)
			)

		# Credit the bank/cash account with the total.
		gl_entries.append(
			self.get_gl_dict(
				{
					"account": self.payment_account,
					"credit": flt(self.total_amount),
					"credit_in_account_currency": flt(self.total_amount),
					"against": ", ".join(sorted({row.expense_account for row in self.expenses})),
					"cost_center": self.cost_center,
					"remarks": self.remarks or _("Expense Entry {0}").format(self.name),
				},
				item=self,
			)
		)

		return gl_entries


@frappe.whitelist()
def get_mode_of_payment_account(mode_of_payment, company):
	"""Return the default bank/cash account configured on the Mode of Payment for the company."""
	if not (mode_of_payment and company):
		return None

	return frappe.db.get_value(
		"Mode of Payment Account",
		{"parent": mode_of_payment, "company": company},
		"default_account",
	)
