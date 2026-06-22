import frappe

from expenses.setup.print_formats import setup_expense_print_formats
from expenses.setup.workspaces import setup_expenses_workspace


def after_install():
	setup_expense_print_formats()
	setup_expenses_workspace()
	frappe.db.commit()


def after_migrate():
	setup_expense_print_formats()
	setup_expenses_workspace()
	frappe.db.commit()
