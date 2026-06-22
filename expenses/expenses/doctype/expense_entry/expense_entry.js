frappe.ui.form.on("Expense Entry", {
	setup(frm) {
		frm.page.wrapper.addClass("expenses-entry-form");

		frm.set_query("payment_account", () => ({
			filters: {
				account_type: ["in", ["Bank", "Cash"]],
				is_group: 0,
				company: frm.doc.company,
			},
		}));

		frm.set_query("expense_account", "expenses", () => {
			if (!frm.doc.company) {
				frappe.throw(__("Please select a Company first."));
			}
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
					root_type: ["in", ["Expense", "Asset", "Liability"]],
				},
			};
		});

		const cost_center_query = () => ({
			filters: { company: frm.doc.company, is_group: 0 },
		});
		frm.set_query("cost_center", cost_center_query);
		frm.set_query("cost_center", "expenses", cost_center_query);
	},

	onload(frm) {
		if (frm.is_new() && !frm.doc.company) {
			frm.set_value("company", frappe.defaults.get_user_default("Company"));
		}
	},

	refresh(frm) {
		const keep = [
			"naming_series",
			"company",
			"posting_date",
			"mode_of_payment",
			"payment_account",
			"cost_center",
			"expenses",
			"total_amount",
			"reference_no",
			"reference_date",
			"remarks",
		];
		frm.fields.forEach((field) => {
			if (
				keep.includes(field.df.fieldname) ||
				["Section Break", "Column Break", "Tab Break"].includes(field.df.fieldtype)
			) {
				return;
			}
			frm.toggle_display(field.df.fieldname, false);
		});

		if (frm.doc.docstatus > 0) {
			frm.add_custom_button(
				__("Ledger"),
				() => {
					frappe.route_options = {
						voucher_no: frm.doc.name,
						company: frm.doc.company,
						from_date: frm.doc.posting_date,
						to_date: frm.doc.posting_date,
						show_cancelled_entries: frm.doc.docstatus === 2,
					};
					frappe.set_route("query-report", "General Ledger");
				},
				__("View")
			);
		}
	},

	mode_of_payment(frm) {
		if (!frm.doc.mode_of_payment) {
			frm.set_value("payment_account", null);
			return;
		}
		if (!frm.doc.company) {
			frm.set_value("mode_of_payment", null);
			frappe.throw(__("Please select a Company first."));
		}
		frappe.call({
			method: "expenses.expenses.doctype.expense_entry.expense_entry.get_mode_of_payment_account",
			args: { mode_of_payment: frm.doc.mode_of_payment, company: frm.doc.company },
			callback(r) {
				frm.set_value("payment_account", r.message || null);
			},
		});
	},

	cost_center(frm) {
		(frm.doc.expenses || []).forEach((row) => {
			if (!row.cost_center) row.cost_center = frm.doc.cost_center;
		});
		frm.refresh_field("expenses");
	},
});

frappe.ui.form.on("Expense Entry Item", {
	amount: (frm) => calculate_total_amount(frm),
	expenses_add: (frm) => calculate_total_amount(frm),
	expenses_remove: (frm) => calculate_total_amount(frm),

	expense_account(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.expense_account && !row.description) {
			frappe.db.get_value("Account", row.expense_account, "account_name").then((r) => {
				if (r.message && r.message.account_name) {
					frappe.model.set_value(cdt, cdn, "description", r.message.account_name);
				}
			});
		}
	},
});

function calculate_total_amount(frm) {
	let total = 0;
	(frm.doc.expenses || []).forEach((row) => {
		total += flt(row.amount);
	});
	frm.set_value("total_amount", total);
}
