# Copyright (c) 2026, Mustafa Nazier and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class IGAPewsArticle(Document):
    def validate(self):
        # Auto-generate slug if not provided or clean it up
        if not self.slug:
            self.slug = self.generate_slug(self.title)
        else:
            self.slug = self.generate_slug(self.slug)

    def generate_slug(self, text):
        if not text:
            return ""
        # Lowercase, replace non-alphanumeric with hyphens
        slug = text.lower().strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        return slug
