// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Graded Items Archive', {
    onload: function (frm) {
        // Set up autocomplete for grade_full field on form load
        setup_grade_autocomplete(frm);
    },

    refresh: function (frm) {
        // Set up autocomplete for grade_full field
        setup_grade_autocomplete(frm);
    },

    grade_full: function (frm) {
        // Trigger validation when grade is entered
        if (frm.doc.grade_full) {
            frm.trigger('validate_grade');
        }
    }
});

function setup_grade_autocomplete(frm) {
    // Fetch available grades from Module Settings
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Module Settings',
            name: 'Module Settings'
        },
        callback: function (r) {
            if (r.message && r.message.grade_scoring_configuration) {
                // Extract grade names into array
                let grades = r.message.grade_scoring_configuration.map(g => g.grade_full);

                // Use ERPNext's set_data method for autocomplete on Data fields
                if (frm.fields_dict.grade_full) {
                    frm.fields_dict.grade_full.set_data(grades);
                }
            }
        }
    });
}
