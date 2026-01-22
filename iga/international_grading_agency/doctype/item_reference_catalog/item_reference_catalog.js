// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Reference Catalog', {
    onload: function (frm) {
        // Toggle sections on form load
        toggle_type_sections(frm);
        toggle_year_fields(frm);
    },

    refresh: function (frm) {
        // Set read-only for ref_code when Active
        if (frm.doc.status === 'Active') {
            frm.set_df_property('ref_code', 'read_only', 1);
        }

        // Toggle sections on refresh
        toggle_type_sections(frm);
        toggle_year_fields(frm);
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

    // Define which type is selected
    const is_coin_token_medal = ['Coin', 'Token', 'Medal'].includes(type);
    const is_banknote = type === 'Banknote';
    const is_postcard = type === 'Postcard';
    const is_card = type === 'Collectible Card';

    // COINS/TOKENS/MEDALS section fields
    const coin_fields = [
        'coins_tokens_medals_section', 'issue_type', 'era_period', 'quality_type',
        'description_ar', 'description_en', 'section_break_31',
        'denomination_value', 'denomination_unit', 'metal', 'purity',
        'section_break_37', 'weight_g', 'diameter_mm', 'thickness_mm',
        'shape', 'edge_type', 'alignment', 'section_break_45',
        'mint', 'mintmark', 'mintage_qty', 'designer', 'km_catalog', 'mh_catalog',
        'section_break_53', 'obv_notes', 'rev_notes', 'known_variations_note'
    ];

    // BANKNOTE section fields
    const banknote_fields = [
        'banknote_section', 'bn_issue_type', 'bn_denomination_value', 'bn_denomination_unit',
        'pick_number', 'bn_mh_catalog', 'bn_series', 'section_break_65',
        'prefix', 'dimensions_mm', 'bn_shape', 'printer', 'watermark', 'security_features',
        'section_break_73', 'signature', 'bn_designer'
    ];

    // POSTCARDS section fields
    const postcard_fields = [
        'postcards_section', 'publisher', 'publisher_no', 'pc_series',
        'location', 'era', 'used_unused', 'section_break_84',
        'stamp', 'postmark_date', 'postmark_place', 'pc_dimensions_mm',
        'pc_shape', 'designer_photographer', 'section_break_92', 'pc_catalog_ref'
    ];

    // COLLECTIBLE CARDS section fields
    const card_fields = [
        'collectible_cards_section', 'card_brand', 'set_name', 'set_code',
        'card_number', 'character_player', 'cc_year', 'section_break_102',
        'parallel_variant', 'print_run', 'serial_numbered', 'autograph_relic',
        'cc_dimensions_mm', 'cc_shape', 'section_break_110', 'cc_catalog_ref'
    ];

    // Toggle COINS/TOKENS/MEDALS fields
    coin_fields.forEach(field => {
        frm.toggle_display(field, is_coin_token_medal);
    });

    // Toggle BANKNOTE fields
    banknote_fields.forEach(field => {
        frm.toggle_display(field, is_banknote);
    });

    // Toggle POSTCARDS fields
    postcard_fields.forEach(field => {
        frm.toggle_display(field, is_postcard);
    });

    // Toggle COLLECTIBLE CARDS fields
    card_fields.forEach(field => {
        frm.toggle_display(field, is_card);
    });
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
