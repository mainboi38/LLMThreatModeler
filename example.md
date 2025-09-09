HIPAA-Compliant Hybrid Kubernetes-Based System Description

System Overview:

A healthcare platform, "HealthSecure," manages sensitive patient data in compliance with HIPAA regulations. It operates in a hybrid cloud environment, combining on-premises infrastructure with a public cloud (AWS) to ensure scalability, security, and compliance. The system leverages Kubernetes for container orchestration, handling electronic health records (EHRs), telemedicine services, and analytics for clinical research. It processes Protected Health Information (PHI), requiring stringent security controls, audit logging, and encryption.

Architecture Layers and Components:

Frontend Layer:
Component: React-based single-page application (SPA) hosted on AWS S3 and served via CloudFront CDN.
Functionality: Provides a web portal for patients, clinicians, and administrators to access EHRs, schedule telemedicine appointments, and view analytics dashboards.
Data: Handles PHI (e.g., patient names, medical histories) and non-sensitive data (e.g., appointment schedules).
Authentication: Uses OAuth 2.0 with OpenID Connect (OIDC) via Keycloak, hosted on-premises, for single sign-on (SSO).
Trust Boundary: Public-facing, accessible via the internet, requiring strict input validation and DDoS protection.
API Layer:
Component: Node.js-based RESTful APIs running in Kubernetes pods on Amazon EKS (public cloud).
Functionality: Manages CRUD operations for EHRs, telemedicine session orchestration, and data exchange with analytics services.
Data: Processes PHI (e.g., lab results, prescriptions) and metadata (e.g., API logs).
Security: APIs are secured with JSON Web Tokens (JWTs) issued by Keycloak, rate-limited, and protected by AWS WAF.
Trust Boundary: APIs sit behind an AWS Application Load Balancer (ALB), accessible only via authenticated requests, forming a trust boundary between frontend and backend.
Backend Services Layer:
Components:
Microservices: Go-based microservices running in Kubernetes pods on an on-premises Kubernetes cluster (using Red Hat OpenShift). Services include EHR management, telemedicine session streaming, and billing integration.
Message Queue: Apache Kafka (on-premises) for asynchronous processing of PHI updates (e.g., lab result uploads) and audit events.
Workflow Orchestration: Temporal (on EKS) for managing long-running workflows like claims processing.
Data: PHI and audit logs, with all data encrypted at rest using AES-256.
Security: Service-to-service communication uses mutual TLS (mTLS) with certificates managed by HashiCorp Vault (on-premises).
Trust Boundary: On-premises cluster is isolated from the public cloud, with a DMZ enforced by a firewall.
Data Storage Layer:
Components:
Primary Database: PostgreSQL (on-premises, managed via Kubernetes Operator) for storing EHRs and PHI.
Analytics Database: Amazon Redshift (public cloud) for de-identified data used in clinical research.
File Storage: AWS S3 bucket (public cloud) for encrypted medical images (e.g., X-rays), with client-side encryption using keys from AWS KMS.
Audit Logs: Elasticsearch (on-premises) for tamper-proof logging of all access to PHI.
Data Classification:
PHI in PostgreSQL and S3: Restricted (HIPAA-protected).
De-identified data in Redshift: Internal.
Audit logs: Confidential.
Security: Databases use row-level security, S3 uses server-side encryption, and all data access is logged to Elasticsearch.
Trust Boundary: Data crosses trust boundaries when moving from on-premises to cloud (e.g., de-identified data to Redshift).
External Integrations:
Third-Party Services:
Telemedicine Provider: Zoom API (cloud-based) for video consultations, with PHI encrypted in transit.
Billing Integration: Stripe API for payment processing, handling no PHI but linked to patient IDs.
FHIR Interoperability: Integration with a FHIR server (on-premises) for standardized EHR exchange with other healthcare providers.
Security: External APIs are accessed via API Gateway (AWS) with rate limiting and OAuth 2.0 authentication.
Trust Boundary: External integrations are outside the system’s primary trust boundary, requiring strict egress controls.
Infrastructure and Networking:
Hybrid Setup: On-premises Kubernetes cluster (OpenShift) in a private data center, connected to AWS EKS via AWS Direct Connect for low-latency, secure communication.
Network Security:
AWS VPC with private subnets for EKS.
On-premises firewall with IDS/IPS for intrusion detection.
Istio service mesh for Kubernetes traffic encryption and observability.
Monitoring: Prometheus and Grafana (on-premises) for cluster metrics, integrated with AWS CloudWatch for cloud resources.
Logging: All components log to Elasticsearch, with Splunk (on-premises) for SIEM and HIPAA-compliant audit trails.
Trust Boundary: Hybrid setup creates a trust boundary between on-premises and cloud, with PHI restricted to on-premises unless encrypted.
HIPAA Compliance Controls:
Encryption: All PHI is encrypted in transit (TLS 1.3) and at rest (AES-256).
Access Controls: Role-based access control (RBAC) via Keycloak, with least privilege enforced.
Audit Logging: Immutable logs in Elasticsearch, with 7-year retention for HIPAA compliance.
Backup and Recovery: Daily encrypted backups to AWS S3 (Glacier for long-term storage).
Incident Response: AWS GuardDuty for cloud threat detection, integrated with on-premises SIEM.
Business Associate Agreements (BAAs): Signed with AWS and Zoom to ensure HIPAA compliance.
Business Criticality:

EHR Management: Critical (patient care depends on availability and integrity).
Telemedicine: High (impacts patient access to care).
Analytics: Medium (supports research, not immediate care).
Billing: Medium (financial impact but not patient-facing).

Regulatory Requirements:

HIPAA compliance for all PHI handling.
Regular penetration testing and vulnerability scanning.
Audit trails for all access and modifications to PHI.