// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Graded Items Archive', {
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
                // Extract grade names
                let grades = r.message.grade_scoring_configuration.map(g => g.grade_full);

                // Set up autocomplete using awesomplete
                frm.fields_dict.grade_full.$input.autocomplete({
                    source: grades,
                    minLength: 0
                }).focus(function () {
                    $(this).autocomplete('search', '');
                });
            }
        }
    });
}
