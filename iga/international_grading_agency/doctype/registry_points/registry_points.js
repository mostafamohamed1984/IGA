// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Registry Points', {
    refresh: function (frm) {
        // Set up autocomplete for grade_full field
        setup_grade_autocomplete(frm);
    },

    grade_full: function (frm) {
        // When grade changes, recalculate points
        if (frm.doc.grade_full && frm.doc.reference_item) {
            frm.trigger('calculate_points');
        }
    },

    value: function (frm) {
        // When value changes, recalculate points
        if (frm.doc.grade_full && frm.doc.reference_item) {
            frm.trigger('calculate_points');
        }
    },

    calculate_points: function (frm) {
        // Trigger server-side calculation
        frm.save();
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

                // Set up autocomplete
                frm.fields_dict.grade_full.set_data(grades);

                // Also set as awesomplete
                frm.set_df_property('grade_full', 'options', grades.join('\n'));
            }
        }
    });
}
