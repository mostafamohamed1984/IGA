// Custom JavaScript for IGA Membership Application Web Form
frappe.ready(function () {
    console.log("IGA Webform JS Loaded");

    // Populate nationality options
    const populateNationality = () => {
        console.log("Fetching enabled countries...");
        frappe.call({
            method: 'iga.international_grading_agency.doctype.iga_membership_application.iga_membership_application.get_enabled_countries',
            callback: function (r) {
                console.log("Response received:", r);
                if (r.message) {
                    let countries = r.message;
                    // Add an empty option at the beginning
                    countries.unshift("");
                    console.log("Populating countries:", countries);

                    if (typeof frappe.web_form !== 'undefined') {
                        console.log("Using frappe.web_form API");
                        // Web Form API
                        // Try setting options as an array first
                        frappe.web_form.set_df_property('nationality', 'options', countries);

                        // As a more compatible fallback, try setting options as a newline-separated string
                        // This line will always execute and overwrite the previous one.
                        // The original instruction's conditional `if (!frappe.web_form.set_df_property(...))` is problematic
                        // because `set_df_property` returns the web_form object itself, which is truthy.
                        // So, we'll just set it as a string directly as a fallback attempt.
                        frappe.web_form.set_df_property('nationality', 'options', countries.join('\n'));

                        if (frappe.web_form.refresh_field) {
                            frappe.web_form.refresh_field('nationality');
                        }
                    }

                    // Direct DOM manipulation as a strong fallback
                    // We target the field by data-fieldname and find the select within it
                    setTimeout(() => {
                        let $select = $('select[data-fieldname="nationality"]');
                        if ($select.length === 0) {
                            $select = $('[data-fieldname="nationality"] select');
                        }

                        if ($select.length) {
                            console.log("Found select element via jQuery, forcing options");
                            $select.empty();
                            countries.forEach(c => {
                                $select.append($('<option>', {
                                    value: c,
                                    text: c
                                }));
                            });
                            // Trigger change to update UI if needed
                            $select.trigger('change');
                        } else {
                            console.warn("Could not find select element for nationality");
                        }
                    }, 500); // Small delay to ensure DOM is ready
                }
            }
        });
    };

    // Try multiple hooks to ensure it loads
    if (typeof frappe.web_form !== 'undefined') {
        frappe.web_form.on('after_load', populateNationality);
        // Also run immediately if already loaded (e.g., on page refresh or if after_load already fired)
        // This ensures the options are populated even if 'after_load' event was missed.
        populateNationality();
    } else {
        // If frappe.web_form is not defined, run immediately (e.g., in a non-web-form context)
        populateNationality();
    }

    // Validate top 3 priorities - exactly 3 selections required
    const priorityFields = [
        'priority_price', 'priority_speed', 'priority_accuracy',
        'priority_holder_quality', 'priority_professional_photos',
        'priority_easy_delivery', 'priority_customer_service',
        'priority_market_acceptance', 'priority_online_verification', 'priority_warranty'
    ];

    // Add change handlers for priority checkboxes
    priorityFields.forEach(field => {
        $(`[data-fieldname="${field}"]`).on('change', function () {
            validatePriorities();
        });
    });

    function validatePriorities() {
        let count = 0;
        priorityFields.forEach(field => {
            if ($(`[data-fieldname="${field}"] input[type="checkbox"]`).is(':checked')) {
                count++;
            }
        });

        // Show warning if more than 3 selected
        if (count > 3) {
            frappe.msgprint({
                title: 'تحذير',
                message: `يمكنك اختيار 3 أولويات فقط. لقد اخترت ${count}. يرجى إلغاء تحديد ${count - 3} خيار.`,
                indicator: 'red'
            });
        }
    }

    // Validate on form submit
    frappe.web_form.on('before_save', () => {
        let count = 0;
        priorityFields.forEach(field => {
            if ($(`[data-fieldname="${field}"] input[type="checkbox"]`).is(':checked')) {
                count++;
            }
        });

        if (count !== 3) {
            frappe.msgprint({
                title: 'خطأ في التحقق',
                message: `يجب اختيار 3 أولويات بالضبط. لقد اخترت ${count}.`,
                indicator: 'red'
            });
            frappe.web_form.prevent_save = true;
            return false;
        }

        return true;
    });
});
