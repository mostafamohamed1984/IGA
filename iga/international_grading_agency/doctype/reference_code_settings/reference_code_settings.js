frappe.ui.form.on('Reference Code Settings', {
    refresh: function(frm) {
        frm.dashboard.add_indicator(__('Reference Code Configuration'), 'blue');
    }
});
