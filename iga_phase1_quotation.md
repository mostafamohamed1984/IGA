# International Grading Agency (IGA) System Development
## Phase 1 - Complete Quotation & Implementation Timeline

**Project Value:** 40,000 EGP  
**Duration:** 4 Weeks (28 Days)  
**Delivery Model:** Fixed-Scope with Weekly Milestones  
**Developer:** Mustafa Nazier  
**Date:** December 25, 2025

---

## Executive Summary

This document outlines the complete development plan for Phase 1 of the International Grading Agency (IGA) grading and certification system. The project will deliver a production-ready, audit-compliant platform built on ERPNext as the operational backbone, with a secure API integration layer connecting to a public-facing website.

**Phase 1 delivers:**
- Complete ERPNext implementation with custom IGA application
- Role-Based Access Control (RBAC) with separation of duties
- End-to-end submission and grading workflows
- Structured grading system with audit trails
- Imaging and digital archiving
- Invoicing and inventory management
- Public website with verification and tracking
- Secure REST API with authentication and rate limiting

---

## Project Scope - Phase 1

### Core Deliverables

#### 1. ERPNext Core Operational Backbone
- Fresh ERPNext installation and configuration
- Custom IGA application development
- Database schema design and implementation
- System configuration and optimization

#### 2. Roles, Permissions & Governance
- Implementation of RBAC system
- User role definitions (Admin, Grader, QC Officer, Imaging Operator, Finance, Operations)
- Separation of duties enforcement
- Permission matrix implementation

#### 3. Submissions Intake & End-to-End Tracking
- Customer onboarding workflow
- Submission creation and intake process
- Status tracking system
- Communication notifications

#### 4. Structured Grading Inputs & Grade Calculation
- Master coin reference data management
- Coin instance creation
- Grading input forms (structured)
- Automated grade calculation engine
- Prohibition of manual grade entry

#### 5. Grade Approval, Locking & Overrides
- Multi-level approval workflow
- Grade locking mechanism
- Override authorization system with justification
- Complete audit trail for all actions
- Historical data preservation

#### 6. Imaging & Digital Archiving
- Image upload and management system
- Metadata tagging and linking to coin instances
- Image storage optimization
- Quality control for images

#### 7. Invoicing & Basic Finance Records
- Automated invoice generation
- Payment tracking
- Basic financial reporting
- Integration with ERPNext Accounting module

#### 8. Inventory of Consumables & Basic Stock Control
- Slab and label inventory management
- Stock level tracking
- Reorder point notifications
- Usage logging per certification

#### 9. Shipping / Fulfillment Status Management
- Shipping status workflow
- Carrier integration preparation
- Tracking number management
- Customer notification system

#### 10. Public Website
- Informational pages (About, Services, Contact)
- Submission guidance pages
- Certification verification tool (by cert number)
- Customer submission status tracking
- Responsive design for mobile and desktop

#### 11. Secure API Integration Layer
- RESTful API development
- JWT-based authentication
- Request logging and audit trails
- Rate limiting implementation (100 requests/hour per user)
- API documentation with Swagger/OpenAPI
- Error handling and validation

---

## Technology Stack

### Backend
- **ERPNext:** Version 15.x (Latest Stable)
- **Frappe Framework:** Version 15.x
- **Database:** MariaDB 10.6+
- **Server:** Ubuntu 22.04 LTS
- **Python:** 3.10+
- **API Framework:** Frappe REST API + Custom endpoints

### Frontend (Website)
- **Framework:** To be provided by client's frontend developer
- **API Integration:** RESTful consumption
- **Authentication:** JWT tokens

### Infrastructure
- **Hosting:** VPS or Cloud (AWS/DigitalOcean/Client's choice)
- **Web Server:** Nginx
- **SSL:** Let's Encrypt
- **Backup:** Automated daily backups

### Development Tools
- **Version Control:** Git/GitHub
- **Documentation:** Markdown + Swagger
- **Testing:** Frappe Test Framework

---

## Financial Breakdown

### Total Project Cost: 40,000 EGP

#### Cost Allocation by Task Category

| Category | Tasks | Budget (EGP) | % of Total |
|----------|-------|--------------|------------|
| **Week 1: Infrastructure & Foundation** | Environment setup, ERPNext installation, initial configuration | 8,000 | 20% |
| **Week 2: Core Application Development** | Custom doctypes, workflows, grading system, RBAC | 12,000 | 30% |
| **Week 3: Advanced Features & Integration** | API development, imaging system, inventory, invoicing | 12,000 | 30% |
| **Week 4: Website Integration & Testing** | API finalization, documentation, testing, deployment | 8,000 | 20% |

#### Detailed Task Breakdown with Budget

**Week 1: Infrastructure & Foundation (8,000 EGP)**
- Server provisioning and configuration: 1,200 EGP
- ERPNext installation and initial setup: 1,500 EGP
- Database configuration and optimization: 1,000 EGP
- Custom IGA app scaffolding: 1,500 EGP
- Version control setup: 500 EGP
- Development environment configuration: 800 EGP
- Documentation framework setup: 500 EGP
- Security hardening (firewall, SSL): 1,000 EGP

**Week 2: Core Application Development (12,000 EGP)**
- Master data doctypes (Coin Types, Designations): 1,500 EGP
- Customer and Submission doctypes: 2,000 EGP
- Coin Instance and Certification Number system: 2,500 EGP
- Grading input forms and calculation engine: 3,000 EGP
- RBAC implementation (roles, permissions): 1,500 EGP
- Workflow automation (submission intake): 1,000 EGP
- Email notification system: 500 EGP

**Week 3: Advanced Features & Integration (12,000 EGP)**
- Grade approval and locking mechanism: 2,000 EGP
- Override system with audit trail: 1,500 EGP
- Imaging system development: 2,500 EGP
- API endpoint development (auth, submissions, verification): 3,000 EGP
- Inventory management (slabs/labels): 1,500 EGP
- Invoicing automation: 1,000 EGP
- Shipping management: 500 EGP

**Week 4: Website Integration & Testing (8,000 EGP)**
- API documentation (Swagger/OpenAPI): 1,000 EGP
- Rate limiting and security hardening: 1,500 EGP
- Frontend developer support and integration: 2,000 EGP
- Comprehensive testing (functional, security, RBAC): 2,000 EGP
- User acceptance testing support: 500 EGP
- Deployment and go-live: 500 EGP
- Handover documentation: 500 EGP

---

## Implementation Timeline - 4 Weeks

### Week 1: Foundation & Infrastructure Setup
**Days 1-7 | Budget: 8,000 EGP**

#### Day 1-2: Environment Provisioning
- [ ] Server provisioning (VPS/Cloud setup)
- [ ] Ubuntu 22.04 LTS installation and configuration
- [ ] Firewall configuration (UFW)
- [ ] SSH key-based authentication setup
- [ ] Basic security hardening
- **Deliverable:** Secure server environment ready for ERPNext

#### Day 3-4: ERPNext Installation
- [ ] Install required dependencies (Python, Node.js, MariaDB, Redis)
- [ ] Frappe bench installation
- [ ] ERPNext installation via bench
- [ ] Site creation and initial configuration
- [ ] Administrator account setup
- [ ] SSL certificate installation (Let's Encrypt)
- [ ] Nginx configuration for production
- **Deliverable:** Fully functional ERPNext instance accessible via HTTPS

#### Day 5: Database & Performance Configuration
- [ ] MariaDB optimization for production
- [ ] Database backup strategy implementation
- [ ] Redis cache configuration
- [ ] Performance monitoring setup
- [ ] Log rotation configuration
- **Deliverable:** Optimized database and caching layer

#### Day 6-7: Custom IGA Application Scaffolding
- [ ] Create custom Frappe app: `iga_grading`
- [ ] Define module structure
- [ ] Configure hooks.py for custom behavior
- [ ] Setup version control (Git repository)
- [ ] Create development branch strategy
- [ ] Initial documentation structure (README, CONTRIBUTING)
- **Deliverable:** IGA custom app framework with version control

**Week 1 Milestone Payment: 8,000 EGP**  
**Acceptance Criteria:** ERPNext running on secure server with custom IGA app initialized

---

### Week 2: Core Application Development
**Days 8-14 | Budget: 12,000 EGP**

#### Day 8-9: Master Data Doctypes
- [ ] Create Coin Type doctype (denomination, country, year, series)
- [ ] Create Designation doctype (MS, PR, PF, etc.)
- [ ] Create Grade Scale doctype (1-70 scale)
- [ ] Create Label Template doctype
- [ ] Setup reference data relationships
- [ ] Implement data validation rules
- [ ] Create import templates for bulk data entry
- **Deliverable:** Complete master data structure

#### Day 10-11: Customer & Submission Management
- [ ] Customer doctype enhancement (collector/dealer designation)
- [ ] Submission doctype with intake workflow
- [ ] Submission Item child table
- [ ] Status tracking (Received, In Grading, QC, Complete)
- [ ] Auto-numbering for submission IDs
- [ ] Email notification triggers
- **Deliverable:** Functional submission intake system

#### Day 12: Coin Instance & Certification System
- [ ] Coin Instance doctype (individual coin record)
- [ ] Permanent Certification Number generation (unique, immutable)
- [ ] Lineage tracking fields (for regrades)
- [ ] Metadata fields (slab ID, label variant)
- [ ] Population counter integration
- [ ] Certification PDF template
- **Deliverable:** Core certification infrastructure

#### Day 13: Grading Input System
- [ ] Grading Input doctype (strike, surface, luster, eye appeal)
- [ ] Grading criteria configuration
- [ ] Grade calculation formula implementation
- [ ] Prohibition of manual grade entry (validation)
- [ ] Grading notes and comments system
- [ ] Grader assignment logic
- **Deliverable:** Structured grading system with automatic calculation

#### Day 14: RBAC Implementation
- [ ] Define custom roles:
  - System Administrator
  - Grader
  - Quality Control Officer
  - Imaging Operator
  - Finance Officer
  - Operations/Shipping Officer
- [ ] Configure role permissions for each doctype
- [ ] Implement separation of duties rules
- [ ] User role assignment workflow
- [ ] Permission validation testing
- **Deliverable:** Complete RBAC system with separation of duties

**Week 2 Milestone Payment: 12,000 EGP**  
**Acceptance Criteria:** All core doctypes operational with RBAC enforced

---

### Week 3: Advanced Features & API Development
**Days 15-21 | Budget: 12,000 EGP**

#### Day 15-16: Grade Approval & Locking System
- [ ] Grade approval workflow (multi-level)
- [ ] Quality Control review process
- [ ] Grade locking mechanism (make record read-only)
- [ ] Override authorization system
- [ ] Override justification requirement (mandatory text field)
- [ ] Audit log for all grading actions
- [ ] Historical data preservation (version control)
- [ ] Email notifications for approvals
- **Deliverable:** Complete approval workflow with audit trail

#### Day 17: Imaging & Digital Archiving
- [ ] Image Upload doctype
- [ ] Image-to-Coin Instance linking
- [ ] Metadata tagging (obverse/reverse, angles)
- [ ] Image quality validation
- [ ] Thumbnail generation
- [ ] Storage optimization (compression)
- [ ] Image viewer integration
- [ ] Imaging operator workflow
- **Deliverable:** Complete imaging system with quality control

#### Day 18-19: API Development - Core Endpoints
- [ ] Setup Frappe REST API framework
- [ ] Implement JWT authentication
- [ ] Create API endpoints:
  - `/api/auth/login` - User authentication
  - `/api/auth/validate` - Token validation
  - `/api/submissions/create` - New submission
  - `/api/submissions/{id}` - Submission details
  - `/api/submissions/list` - User's submissions
  - `/api/coin/{cert_number}` - Coin verification
  - `/api/coin/{cert_number}/images` - Coin images
- [ ] Request/response validation
- [ ] Error handling implementation
- [ ] API logging system
- **Deliverable:** Functional REST API with authentication

#### Day 20: Inventory & Invoicing
- [ ] Consumables doctype (slabs, labels, holders)
- [ ] Stock level tracking
- [ ] Reorder point notifications
- [ ] Usage logging per certification
- [ ] Invoice generation automation
- [ ] Link submissions to invoices
- [ ] Payment status tracking
- [ ] Basic financial reporting
- **Deliverable:** Inventory and invoicing systems operational

#### Day 21: Shipping Management
- [ ] Shipping Status doctype
- [ ] Fulfillment workflow
- [ ] Tracking number assignment
- [ ] Carrier selection
- [ ] Customer notification on shipment
- [ ] Delivery confirmation
- **Deliverable:** Complete shipping workflow

**Week 3 Milestone Payment: 12,000 EGP**  
**Acceptance Criteria:** All features operational with API endpoints functional

---

### Week 4: Integration, Testing & Deployment
**Days 22-28 | Budget: 8,000 EGP**

#### Day 22: API Security & Rate Limiting
- [ ] Implement rate limiting (100 requests/hour per user)
- [ ] Setup Redis for rate limit storage
- [ ] IP-based blocking for abuse
- [ ] CORS configuration
- [ ] API key management for frontend
- [ ] Security headers configuration
- [ ] SQL injection prevention validation
- **Deliverable:** Production-grade API security

#### Day 23: API Documentation
- [ ] Generate Swagger/OpenAPI specification
- [ ] Write API endpoint descriptions
- [ ] Provide request/response examples
- [ ] Authentication flow documentation
- [ ] Error code reference
- [ ] Rate limit documentation
- [ ] Integration guide for frontend developer
- **Deliverable:** Complete API documentation

#### Day 24: Frontend Developer Support
- [ ] Provide API credentials and base URL
- [ ] Support integration testing
- [ ] Debug authentication issues
- [ ] Verify data flow between website and ERPNext
- [ ] Test certification verification on website
- [ ] Test submission status tracking
- **Deliverable:** Successful frontend-API integration

#### Day 25-26: Comprehensive Testing
- [ ] Functional testing of all workflows
- [ ] RBAC permission validation (test each role)
- [ ] Grading calculation accuracy testing
- [ ] Audit trail verification
- [ ] Override system testing
- [ ] API endpoint testing (Postman collection)
- [ ] Security testing (authentication, authorization)
- [ ] Performance testing (load testing)
- [ ] Data integrity validation
- [ ] Backup and restore testing
- **Deliverable:** Test report with all issues resolved

#### Day 27: User Acceptance Testing (UAT)
- [ ] Prepare UAT environment
- [ ] Create test scenarios and scripts
- [ ] Conduct UAT sessions with client
- [ ] Document feedback and issues
- [ ] Implement critical fixes
- [ ] Re-test after fixes
- **Deliverable:** UAT sign-off document

#### Day 28: Deployment & Handover
- [ ] Production deployment
- [ ] Database migration verification
- [ ] Performance monitoring setup
- [ ] Backup verification
- [ ] Create system administrator guide
- [ ] Create user role manuals (per role)
- [ ] Provide operational procedures document
- [ ] Handover credentials (server, database, ERPNext)
- [ ] Remove developer access
- [ ] Final project documentation delivery
- **Deliverable:** Production system with complete documentation

**Week 4 Milestone Payment: 8,000 EGP**  
**Acceptance Criteria:** System live in production with full documentation delivered

---

## Deliverables Checklist

### Software Deliverables
- [ ] ERPNext production instance with IGA custom app
- [ ] All custom doctypes and workflows
- [ ] REST API with full functionality
- [ ] Database with initial configuration
- [ ] SSL-secured web access

### Documentation Deliverables
- [ ] System Architecture Document
- [ ] Database Schema Documentation
- [ ] API Documentation (Swagger/OpenAPI)
- [ ] User Manuals (per role):
  - System Administrator Guide
  - Grader User Guide
  - QC Officer Guide
  - Imaging Operator Guide
  - Finance Officer Guide
  - Operations/Shipping Guide
- [ ] ERPNext Customization Guide
- [ ] Deployment and Environment Guide
- [ ] Security and Backup Procedures
- [ ] Troubleshooting Guide

### Access & Credentials
- [ ] Server SSH credentials
- [ ] Database root credentials
- [ ] ERPNext Administrator credentials
- [ ] API authentication keys
- [ ] Git repository access
- [ ] All credentials documented in secure handover document

---

## Payment Schedule

| Milestone | Deliverables | Amount (EGP) | Due Date |
|-----------|--------------|--------------|----------|
| **Milestone 1** | Week 1 completion - Infrastructure ready with ERPNext installed | 8,000 | End of Week 1 |
| **Milestone 2** | Week 2 completion - Core application with RBAC | 12,000 | End of Week 2 |
| **Milestone 3** | Week 3 completion - All features and API operational | 12,000 | End of Week 3 |
| **Milestone 4** | Week 4 completion - Testing, deployment, handover | 8,000 | End of Week 4 |
| **Total** | | **40,000 EGP** | |

**Payment Terms:**
- Payments due upon written acceptance of milestone deliverables
- Each milestone requires client sign-off before proceeding to next
- Final payment upon complete system handover and documentation delivery

---

## Acceptance Criteria

### Week 1 Acceptance
- ERPNext accessible via HTTPS
- Custom IGA app installed and visible
- Database optimized and backed up
- Development environment functional

### Week 2 Acceptance
- All master data tables operational
- Submission intake workflow functional
- Grading system calculating grades correctly
- RBAC enforcing separation of duties
- All roles testable with demo users

### Week 3 Acceptance
- Grade approval and locking working
- Imaging system uploading and displaying images
- All API endpoints responding correctly
- JWT authentication functional
- Inventory and invoicing generating records

### Week 4 Acceptance
- API documentation complete and accurate
- All security measures active (rate limiting, logging)
- Website successfully consuming API
- All tests passed with zero critical issues
- Complete documentation delivered
- System deployed in production

---

## Assumptions & Dependencies

### Client Responsibilities
1. **Server/Hosting:** Client to provide or approve server specifications (minimum 2 vCPU, 4GB RAM, 50GB SSD)
2. **Domain Name:** Client to provide domain for ERPNext and API
3. **Frontend Developer:** Client's frontend developer available for API integration starting Week 3
4. **Content:** Client to provide:
   - Initial master data (coin types, designations)
   - Company logo and branding assets
   - Website content (text, images)
   - Terms of service and privacy policy
5. **Testing Participation:** Client availability for UAT in Week 4
6. **Timely Feedback:** Client to provide feedback within 24 hours of milestone delivery

### Developer Responsibilities
1. Complete all deliverables as specified
2. Maintain code quality and documentation standards
3. Provide support during frontend integration
4. Ensure security best practices
5. Deliver on schedule

### Exclusions (Not Included in Phase 1)
- Population/Census advanced features (Phase 2)
- Regrade lineage advanced views (Phase 2)
- Dealer/Collector advanced portals (Phase 2)
- Collector Registry (Phase 2)
- Advanced reporting and dashboards (Phase 2)
- Mobile application development
- Content creation for website
- Ongoing maintenance after handover (separate contract)

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ERPNext version compatibility issues | Low | Medium | Use latest stable version, test upgrades in dev environment |
| API integration delays | Medium | High | Start API development early, provide comprehensive documentation |
| Scope creep | Medium | High | Formal change request process, clear exclusions documented |
| Frontend developer availability | Medium | Medium | Clear API documentation, test endpoints independently |
| Data migration complexity | Low | Medium | Start with clean database, import templates for bulk data |
| Performance issues | Low | Medium | Load testing, database optimization, caching strategy |
| Security vulnerabilities | Low | High | Security testing, follow OWASP guidelines, regular updates |

---

## Change Management

Any changes to the agreed scope must follow this process:

1. **Change Request:** Client submits written change request with detailed description
2. **Impact Analysis:** Developer evaluates impact on timeline and budget
3. **Quotation:** Developer provides separate quotation for change
4. **Approval:** Client approves change with adjusted timeline/budget
5. **Implementation:** Change implemented after approval and payment terms agreed

Changes requested during development may delay original delivery timeline.

---

## Post-Delivery Support

### Warranty Period: 30 Days
- Bug fixes for issues present at delivery (not new feature requests)
- Critical security patches
- Configuration assistance
- Documentation clarifications

### Ongoing Support (Separate Contract)
After 30-day warranty, ongoing support available at:
- **Monthly Retainer:** 3,000 EGP/month (includes 10 hours support)
- **Hourly Rate:** 400 EGP/hour (for ad-hoc requests)
- **Phase 2 Development:** Separate quotation upon request

---

## Technical Specifications

### Server Requirements (Minimum)
- **CPU:** 2 vCPU cores
- **RAM:** 4 GB (8 GB recommended)
- **Storage:** 50 GB SSD (100 GB recommended)
- **OS:** Ubuntu 22.04 LTS
- **Network:** 100 Mbps bandwidth

### Software Versions
- **ERPNext:** 15.x (latest stable)
- **Frappe:** 15.x
- **Python:** 3.10+
- **MariaDB:** 10.6+
- **Node.js:** 18.x LTS
- **Redis:** 7.x
- **Nginx:** Latest stable

### API Specifications
- **Protocol:** HTTPS only
- **Format:** JSON
- **Authentication:** JWT (JSON Web Tokens)
- **Rate Limit:** 100 requests/hour per authenticated user
- **Versioning:** /api/v1/ prefix for future compatibility

### Security Standards
- TLS 1.2+ encryption
- Strong password requirements (min 12 chars, complexity rules)
- Session timeout: 24 hours
- Failed login lockout: 5 attempts
- All sensitive data encrypted at rest
- Audit logs immutable and retained for 7 years
- Regular automated backups (daily, retained 30 days)

---

## Appendix A: API Endpoint Reference

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/validate` - Validate token

### Submission Endpoints
- `POST /api/submissions` - Create new submission
- `GET /api/submissions/{id}` - Get submission details
- `GET /api/submissions` - List user's submissions
- `PATCH /api/submissions/{id}` - Update submission

### Coin/Certification Endpoints
- `GET /api/coin/{cert_number}` - Verify certification
- `GET /api/coin/{cert_number}/details` - Full coin details
- `GET /api/coin/{cert_number}/images` - Coin images
- `GET /api/coin/{cert_number}/history` - Grading history (if regrade)

### Invoice Endpoints
- `GET /api/invoices/{id}` - Get invoice (read-only)
- `GET /api/invoices` - List user's invoices

### Public Endpoints (No Auth Required)
- `GET /api/verify/{cert_number}` - Public certification verification
- `GET /api/population/{coin_type}` - Population report

---

## Appendix B: Master Data Structure

### Coin Types Table
- Denomination (e.g., Quarter Dollar)
- Country (e.g., United States)
- Year (e.g., 1932)
- Mint Mark (e.g., S, D, P)
- Series/Type (e.g., Washington Quarter)
- Composition (e.g., Silver)

### Designations Table
- Code (e.g., MS, PF, PR)
- Full Name (e.g., Mint State, Proof)
- Description

### Grade Scale Table
- Grade Number (1-70)
- Grade Label (e.g., MS-65, PF-70)
- Description

---

**Document Version:** 1.0  
**Last Updated:** December 25, 2025  
**Status:** Final Proposal
