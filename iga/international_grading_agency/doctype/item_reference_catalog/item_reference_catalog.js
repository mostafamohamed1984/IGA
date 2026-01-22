// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Reference Catalog', {
    refresh: function (frm) {
        // Set read-only for ref_code when Active
        if (frm.doc.status === 'Active') {
            frm.set_df_property('ref_code', 'read_only', 1);
        }
    },

    collectible_type: function (frm) {
        // Toggle section visibility based on collectible type
        toggle_type_sections(frm);
    },

    status: function (frm) {
        // Lock ref_code when Active
        if (frm.doc.status === 'Active') {
            frm.set_df_property('ref_code', 'read_only', 1);
        } else {
            frm.set_df_property('ref_code', 'read_only', 0);
        }
    },

    calendar_type: function (frm) {
        // Toggle year field requirements
        toggle_year_fields(frm);
    }
});

function toggle_type_sections(frm) {
    const type = frm.doc.collectible_type;

    // Show/hide sections based on collectible type
    const is_coin_token_medal = ['Coin', 'Token', 'Medal'].includes(type);
    const is_banknote = type === 'Banknote';
    const is_postcard = type === 'Postcard';
    const is_card = type === 'Collectible Card';

    // Toggle section visibility
    frm.toggle_display('coins_tokens_medals_section', is_coin_token_medal);
    frm.toggle_display('banknote_section', is_banknote);
    frm.toggle_display('postcards_section', is_postcard);
    frm.toggle_display('collectible_cards_section', is_card);
}

function toggle_year_fields(frm) {
    const calendar_type = frm.doc.calendar_type;

    // Show/hide year fields based on calendar type
    const show_ad = ['AD', 'Both'].includes(calendar_type);
    const show_ah = ['AH', 'Both'].includes(calendar_type);

    frm.toggle_display('year_ad', show_ad);
    frm.toggle_display('year_ah', show_ah);

    // Set mandatory
    frm.toggle_reqd('year_ad', show_ad);
    frm.toggle_reqd('year_ah', show_ah);
}
