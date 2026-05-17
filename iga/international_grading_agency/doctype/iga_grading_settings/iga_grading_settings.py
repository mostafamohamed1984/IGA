import frappe
from frappe import _
from frappe.model.document import Document
import json


class IGAGradingSettings(Document):
    
    def validate(self):
        self._validate_json_fields()
        self._validate_scoring_components()
    
    def _validate_json_fields(self):
        """Validate JSON fields."""
        if self.grade_map:
            try:
                json.loads(self.grade_map)
            except json.JSONDecodeError as e:
                frappe.throw(_("Invalid JSON in Grade Map: {0}").format(str(e)))
        
        if self.penalty_rules:
            try:
                json.loads(self.penalty_rules)
            except json.JSONDecodeError as e:
                frappe.throw(_("Invalid JSON in Penalty Rules: {0}").format(str(e)))
    
    def _validate_scoring_components(self):
        """Validate that scoring components sum to 100% for both types."""
        if not self.scoring_components:
            return
        
        unc_total = sum(c.weight_uncirculated or 0 for c in self.scoring_components)
        circ_total = sum(c.weight_circulated or 0 for c in self.scoring_components)
        
        if abs(unc_total - 100) > 0.01:
            frappe.throw(_("Uncirculated weights must sum to 100% (currently {0}%)").format(unc_total))
        
        if abs(circ_total - 100) > 0.01:
            frappe.throw(_("Circulated weights must sum to 100% (currently {0}%)").format(circ_total))
    
    @frappe.whitelist()
    def test_grading_calculation(self, coin_type="Uncirculated"):
        """Test grading calculation with sample data."""
        if not self.scoring_components:
            return {"error": "No scoring components defined"}
        
        # Sample component scores (1-10 scale)
        sample_scores = {
            "Strike": 9,
            "Luster": 8,
            "Surface Preservation": 7,
            "Eye Appeal": 9,
            "Color/Toning": 8,
            "Centering": 9
        }
        
        total_score = 0
        breakdown = []
        
        for component in self.scoring_components:
            weight = component.weight_uncirculated if coin_type == "Uncirculated" else component.weight_circulated
            score = sample_scores.get(component.component_name, 5)
            weighted_score = (score / 10) * weight
            total_score += weighted_score
            
            breakdown.append({
                "component": component.component_name,
                "raw_score": score,
                "weight": weight,
                "weighted_score": round(weighted_score, 2)
            })
        
        # Map to numeric grade (1-70)
        numeric_grade = self._map_score_to_grade(total_score)
        
        return {
            "coin_type": coin_type,
            "total_score": round(total_score, 2),
            "numeric_grade": numeric_grade,
            "breakdown": breakdown
        }
    
    def _map_score_to_grade(self, score):
        """Map total score (0-100) to numeric grade (1-70)."""
        if self.grade_map:
            try:
                grade_map = json.loads(self.grade_map)
                # Find appropriate grade from map
                for grade_range in sorted(grade_map, key=lambda x: x.get("min_score", 0), reverse=True):
                    if score >= grade_range.get("min_score", 0):
                        return grade_range.get("numeric_grade", 1)
            except:
                pass
        
        # Default linear mapping: 0-100 score → 1-70 grade
        return max(1, min(70, int(score * 0.7)))
