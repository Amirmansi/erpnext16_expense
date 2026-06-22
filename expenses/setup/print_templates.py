_BASE_STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; color: #1a1a1a; }
.exp-print { width: 100%; max-width: 210mm; margin: 0 auto; padding: 16px; }
.exp-header { text-align: center; border-bottom: 2px solid #059669; padding-bottom: 12px; margin-bottom: 14px; }
.exp-company { font-size: 20px; font-weight: 800; color: #059669; }
.exp-title { font-size: 15px; font-weight: 700; margin-top: 4px; }
.exp-meta { font-size: 11px; color: #64748b; margin-top: 4px; }
.exp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.exp-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; }
.exp-box-title { font-size: 10px; font-weight: 700; color: #64748b; margin-bottom: 6px; }
.exp-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px; gap: 8px; }
.exp-row span:first-child { color: #64748b; flex-shrink: 0; }
.exp-row span:last-child { font-weight: 600; text-align: left; }
table { width: 100%; border-collapse: collapse; margin-bottom: 12px; table-layout: fixed; }
th { background: #059669; color: #fff; padding: 8px 10px; font-size: 11px; text-align: right; }
td { padding: 7px 10px; font-size: 11px; border-bottom: 1px solid #f1f5f9; word-wrap: break-word; }
tr:nth-child(even) td { background: #f8fafc; }
.amt { text-align: left; font-weight: 600; white-space: nowrap; }
.exp-total { background: linear-gradient(135deg, #059669, #10b981); color: #fff; border-radius: 8px; padding: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.exp-total-label { font-size: 14px; font-weight: 700; }
.exp-total-value { font-size: 20px; font-weight: 900; }
.exp-footer { text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px; margin-top: 14px; }
.exp-sig { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 18px; }
.exp-sig div { border-top: 2px solid #059669; padding-top: 6px; text-align: center; font-size: 10px; color: #64748b; }
@media print { body { margin: 0; } .exp-print { padding: 8px; } }
"""

EXPENSE_ENTRY_HTML = (
	"""{% set items = doc.expenses %}
<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><style>"""
	+ _BASE_STYLE
	+ """</style></head><body>
<div class="exp-print">
  <div class="exp-header">
    <div class="exp-company">{{ doc.company }}</div>
    <div class="exp-title">سند مصروف</div>
    <div class="exp-meta">{{ doc.name }} | {{ frappe.format(doc.posting_date, 'Date') }}</div>
  </div>
  <div class="exp-grid">
    <div class="exp-box">
      <div class="exp-box-title">بيانات الدفع</div>
      <div class="exp-row"><span>طريقة الدفع</span><span>{{ doc.mode_of_payment }}</span></div>
      <div class="exp-row"><span>حساب الدفع</span><span>{{ doc.payment_account }}</span></div>
      {% if doc.reference_no %}<div class="exp-row"><span>رقم المرجع</span><span>{{ doc.reference_no }}</span></div>{% endif %}
    </div>
    <div class="exp-box">
      <div class="exp-box-title">تفاصيل إضافية</div>
      <div class="exp-row"><span>مركز التكلفة</span><span>{{ doc.cost_center or '-' }}</span></div>
      {% if doc.project %}<div class="exp-row"><span>المشروع</span><span>{{ doc.project }}</span></div>{% endif %}
      {% if doc.remarks %}<div class="exp-row"><span>ملاحظات</span><span>{{ doc.remarks }}</span></div>{% endif %}
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th style="width:8%">#</th>
        <th style="width:28%">حساب المصروف</th>
        <th style="width:34%">الوصف</th>
        <th style="width:15%">مركز التكلفة</th>
        <th style="width:15%">المبلغ</th>
      </tr>
    </thead>
    <tbody>
    {% for item in items %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ item.expense_account }}</td>
        <td>{{ item.description or item.expense_account }}</td>
        <td>{{ item.cost_center or doc.cost_center or '-' }}</td>
        <td class="amt">{{ frappe.format(item.amount, {'fieldtype':'Currency','currency':doc.account_currency}) }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <div class="exp-total">
    <span class="exp-total-label">إجمالي المصروف</span>
    <span class="exp-total-value">{{ frappe.format(doc.total_amount, {'fieldtype':'Currency','currency':doc.account_currency}) }}</span>
  </div>
  <div class="exp-sig">
    <div>المُعد</div>
    <div>المُراجع</div>
    <div>المُعتمد</div>
  </div>
  <div class="exp-footer">تم الطباعة {{ frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M') }}</div>
</div></body></html>"""
)
