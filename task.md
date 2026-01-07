# IGA Coin Project - Phase 1 Roadmap

## Week 1: Foundation & Infrastructure Setup
- [ ] Verify ERPNext installation and access <!-- id: 0 -->
- [ ] Create custom Frappe app `iga_grading` <!-- id: 1 -->
- [ ] Initialize git repository and version control <!-- id: 2 -->
- [ ] Configure `hooks.py` for custom app <!-- id: 3 -->

## Week 2: Core Application Development
### Master Data
- [ ] Create `Coin Type` DocType <!-- id: 4 -->
- [ ] Create `Designation` DocType <!-- id: 5 -->
- [ ] Create `Grade Scale` DocType <!-- id: 6 -->
- [ ] Create `Label Template` DocType <!-- id: 7 -->

### Customer & Submission Management
- [ ] Enhance `Customer` DocType (add collector/dealer fields) <!-- id: 8 -->
- [ ] Create `Submission` DocType with intake workflow <!-- id: 9 -->
- [ ] Create `Submission Item` Child Table <!-- id: 10 -->
- [ ] Implement Status Tracking (Received, In Grading, QC, Complete) <!-- id: 11 -->

### Coin Instance & Certification
- [ ] Create `Coin Instance` DocType <!-- id: 12 -->
- [ ] Implement Certification Number generation logic <!-- id: 13 -->
- [ ] Create Certification PDF Template <!-- id: 14 -->

### Grading System
- [ ] Create `Grading Input` DocType <!-- id: 15 -->
- [ ] Implement Grade Calculation Logic <!-- id: 16 -->
- [ ] Implement Grader Assignment Logic <!-- id: 17 -->

### RBAC Implementation
- [ ] Define Roles: Grader, QC Officer, Imaging Operator, Finance, Operations <!-- id: 18 -->
- [ ] Configure Permissions for all new DocTypes <!-- id: 19 -->

## Week 3: Advanced Features & API
### Grading Workflows
- [ ] Implement Approval Workflow <!-- id: 20 -->
- [ ] Implement Grade Locking Mechanism <!-- id: 21 -->
- [ ] Create `Override Request` DocType and Logic <!-- id: 22 -->

### Imaging
- [ ] Create `Image Upload` DocType <!-- id: 23 -->
- [ ] Implement Image Linking to Coin Instance <!-- id: 24 -->

### API Development
- [ ] Setup API Authentication (JWT) <!-- id: 25 -->
- [ ] Create Endpoint: `/api/submissions/create` <!-- id: 26 -->
- [ ] Create Endpoint: `/api/coin/{cert_number}` <!-- id: 27 -->
- [ ] Create Endpoint: `/api/submissions/list` <!-- id: 28 -->

### Inventory & Finance
- [ ] Create `Consumables` DocType <!-- id: 29 -->
- [ ] Integrate with Sales Invoice <!-- id: 30 -->

### Shipping
- [ ] Create `Shipping Status` DocType <!-- id: 31 -->
- [ ] Implement Shipping Notification Workflow <!-- id: 32 -->

## Week 4: Integration & Testing
- [ ] Implement API Rate Limiting <!-- id: 33 -->
- [ ] Generate API Documentation (Swagger) <!-- id: 34 -->
- [ ] Perform End-to-End Testing <!-- id: 35 -->
- [ ] User Acceptance Testing (UAT) <!-- id: 36 -->
- [ ] Production Deployment & Handover <!-- id: 37 -->
