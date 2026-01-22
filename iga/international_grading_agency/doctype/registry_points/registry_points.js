// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Registry Points', {
    onload: function (frm) {
        // Populate grade options from Module Settings
        populate_grade_options(frm);
    },

    refresh: function (frm) {
        // Populate grade options from Module Settings
        populate_grade_options(frm);
    },

    grade_full: function (frm) {
        // When grade changes, recalculate points
        if (frm.doc.grade_full && frm.doc.reference_item) {
            frm.save();
        }
    },

    value: function (frm) {
        // When value changes, recalculate points
        if (frm.doc.grade_full && frm.doc.reference_item) {
            frm.save();
        }
    }
});

function populate_grade_options(frm) {
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

                // Set the options for the Select field
                frm.set_df_property('grade_full', 'options', grades.join('\n'));
            }
        }
    });
}
