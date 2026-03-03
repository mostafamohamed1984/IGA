// Custom JavaScript for IGA Membership Application Web Form
frappe.ready(function() {
    // Validate top 3 priorities - exactly 3 selections required
    const priorityFields = [
        'priority_price', 'priority_speed', 'priority_accuracy',
        'priority_holder_quality', 'priority_professional_photos',
        'priority_easy_delivery', 'priority_customer_service',
        'priority_market_acceptance', 'priority_online_verification', 'priority_warranty'
    ];
    
    // Add change handlers for priority checkboxes
    priorityFields.forEach(field => {
        $(`[data-fieldname="${field}"]`).on('change', function() {
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
