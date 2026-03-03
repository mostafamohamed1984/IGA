import frappe

def get_context(context):
    """Context for terms and conditions page"""
    context.no_cache = 1
    context.show_sidebar = 0
    return context
