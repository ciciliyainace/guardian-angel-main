# SentinelAI — System Architecture & Workflow Diagrams

This document contains the official architectural, data flow, and workflow diagrams for **SentinelAI — AI-Powered Firewall Attack Detection System**. All diagrams are written in standard Mermaid specification and accurately reflect the system's codebase.

---

## 1. Overall System Architecture

This diagram illustrates the 3-tier structure of SentinelAI, depicting the Presentation Tier (React + Vite), the Application Tier (FastAPI, Detection Engine, and Background Workers), and the Persistence Tier (MongoDB Atlas).

```mermaid
graph TB
    subgraph Client_Tier [Presentation Tier - React + TypeScript]
        UI[SOC Dashboard UI :8080]
        Router[TanStack Router]
        State[React Query / API Client]
        Components[SOC Metric Cards / Recharts / Tables]
    end

    subgraph Backend_Tier [Application & Detection Tier - FastAPI :8000]
        API[FastAPI REST API Routes]
        Auth[JWT & RBAC Security Layer]
        
        subgraph Ingestion_Engine [Ingestion & Telemetry]
            WinCol[Windows Socket Collector]
            SuriCol[Suricata EVE-JSON Tailer]
            SimCol[Safe RFC 5737 Simulator]
            Dedup[60s Sliding Deduplicator]
        end
        
        subgraph Detection_Engine [Hybrid Detection Pipeline]
            RuleEng[Stateful Rule Engine R-001 to R-005]
            Prep[Preprocessor & 24-Feature Vector]
            RF[Random Forest Multi-Class Classifier]
            DT[Decision Tree Baseline Model]
            IForest[Isolation Forest Anomaly Engine]
            Hybrid[Hybrid Arbitration & Risk Scoring 0-100]
        end
        
        subgraph Response_Engine [Controlled Firewall Response]
            FWService[Firewall Service]
            SafetyVal[Target Safety Validator]
            ActionVal[Action & Lease Validator]
            SimAdapter[Simulation Adapter - Safe Mode]
            WinAdapter[Windows Firewall Adapter - Disabled]
            AuditSvc[Audit Trail Service]
        end
    end

    subgraph Data_Tier [Persistence Tier - MongoDB Atlas Cluster]
        DB[(MongoDB Atlas - sentinelai)]
        C1[users]
        C2[network_events]
        C3[alerts]
        C4[detection_rules]
        C5[firewall_requests]
        C6[firewall_actions]
        C7[model_registry]
        C8[audit_logs]
        C9[system_settings]
        C10[feedback]
    end

    %% Client to Backend
    UI --> Router
    Router --> State
    State <--> |HTTP / JSON REST API| API

    %% Backend Internals
    API --> Auth
    API --> WinCol & SuriCol & SimCol
    WinCol & SuriCol & SimCol --> Dedup
    Dedup --> Hybrid
    Hybrid --> RuleEng
    Hybrid --> Prep
    Prep --> RF & DT & IForest
    RF & DT & IForest --> Hybrid

    API --> FWService
    FWService --> SafetyVal
    SafetyVal --> ActionVal
    ActionVal --> SimAdapter
    SimAdapter -.-> AuditSvc

    %% Backend to Database
    API <--> |PyMongo Driver Pool| DB
    DB --- C1 & C2 & C3 & C4 & C5 & C6 & C7 & C8 & C9 & C10
```

---

## 2. Event Ingestion and Hybrid Detection Flow

This sequence diagram details the end-to-end lifecycle of a network event, from telemetry ingestion and sliding-window deduplication to hybrid arbitration and correlated alert creation.

```mermaid
sequenceDiagram
    autonumber
    actor Source as Network Telemetry Source
    participant Collector as Collector Layer
    participant API as FastAPI Ingestion Endpoint
    participant Dedup as 60s Sliding Deduplicator
    participant Engine as Hybrid Detection Engine
    participant Rules as Rule Engine (R-001 to R-005)
    participant ML as ML Inference (RF + IF + DT)
    participant DB as MongoDB Atlas

    Source->>Collector: Raw Flow / Socket / EVE Record
    Collector->>API: POST /api/v1/events/ingest (Standardized Dict)
    API->>Dedup: find_duplicate(source_ip, dest_ip, ports, proto, 60s)
    
    alt Duplicate Detected Within 60s Window
        Dedup-->>API: Existing NetworkEvent record
        API->>DB: update_one(increment duplicates count, update timestamp)
        API-->>Source: Return existing NetworkEvent (Alert creation suppressed)
    else Unique Event Record
        API->>Engine: analyze(flow_features, metadata, timestamp)
        par Deterministic Rule Evaluation
            Engine->>Rules: evaluate(source_ip, dest_ip, ports, timestamp)
            Rules-->>Engine: rule_ids, rule_evidence, rule_severity, rule_category
        and Statistical & Anomaly ML Evaluation
            Engine->>ML: run_inference(24 canonical flow features)
            ML->>ML: Preprocessor.transform(vector)
            ML->>ML: Random Forest predict & predict_proba
            ML->>ML: Isolation Forest anomaly score & intensity
            ML-->>Engine: predicted_class, ml_risk_score, anomaly_intensity
        end
        Engine->>Engine: Hybrid Arbitration (Base Score + Multi-Detector Consensus)
        Engine-->>API: Composite Risk Score (0-100), Severity, Category, Action
        
        API->>DB: insert_one(network_events document)
        
        opt Threat Identified (Risk Score >= 60 OR Severity in High/Critical) AND Category != 'Benign'
            API->>DB: insert_one(alerts document with related_event_id)
        end
        
        API-->>Source: Return new EventResponse JSON (with isSimulated & eventSource)
    end
```

---

## 3. MongoDB Persistence and API Data Flow

This diagram illustrates how client requests traverse route controllers, repositories, and MongoDB Atlas collections, highlighting the secure credential boundary.

```mermaid
graph LR
    subgraph Client [Client Dashboard]
        FE[React Components]
    end

    subgraph API_Layer [FastAPI REST Routes]
        R_Events[/api/v1/events]
        R_Alerts[/api/v1/alerts]
        R_Rules[/api/v1/rules]
        R_FW[/api/v1/firewall]
        R_Analytics[/api/v1/analytics]
        R_Health[/api/v1/health]
    end

    subgraph Service_Repository_Layer [Service & Repository Layer]
        S_Evt[EventService / EventRepository]
        S_Alt[AlertService / AlertRepository]
        S_Rul[RuleService / RuleRepository]
        S_FW[FirewallService / FirewallRepository]
        S_Ana[AnalyticsService]
        DBMgr[MongoDBManager Singleton]
    end

    subgraph Mongo_Atlas [MongoDB Atlas Cloud Cluster]
        coll_events[(network_events)]
        coll_alerts[(alerts)]
        coll_rules[(detection_rules)]
        coll_fw_req[(firewall_requests)]
        coll_fw_act[(firewall_actions)]
        coll_audit[(audit_logs)]
        coll_models[(model_registry)]
    end

    FE <--> |JSON API Requests| API_Layer
    R_Events <--> S_Evt
    R_Alerts <--> S_Alt
    R_Rules <--> S_Rul
    R_FW <--> S_FW
    R_Analytics <--> S_Ana
    R_Health <--> DBMgr

    S_Evt <--> DBMgr
    S_Alt <--> DBMgr
    S_Rul <--> DBMgr
    S_FW <--> DBMgr
    S_Ana <--> DBMgr

    DBMgr <--> |PyMongo TLS Encrypted Pool| Mongo_Atlas
    Mongo_Atlas --- coll_events & coll_alerts & coll_rules & coll_fw_req & coll_fw_act & coll_audit & coll_models
```

---

## 4. Controlled Firewall Request, Approval, and Rollback Workflow

This stateful workflow diagram models the Human-in-the-Loop (HITL) firewall containment process, demonstrating strict boundary checks, role separation, and automatic lease expiry.

```mermaid
stateDiagram-v2
    [*] --> ThreatIdentified: Alert Risk Score >= 60

    state "Block Request Creation" as Step1 {
        ThreatIdentified --> SafetyValidation: Analyst requests IP block
        SafetyValidation --> RejectedInvalid: Target is 127.0.0.1 / DNS / Gateway
        SafetyValidation --> PendingApproval: Target is valid external IP
    }

    state "Two-Person Authorization" as Step2 {
        PendingApproval --> RejectedAdmin: Admin rejects (Reason logged)
        PendingApproval --> SelfApprovalCheck: Admin reviews request
        SelfApprovalCheck --> PolicyViolation: Analyst attempted self-approval
        SelfApprovalCheck --> Approved: Authorized Administrator approves
    }

    state "Firewall Actuation & Lifecycle" as Step3 {
        Approved --> RuleApplied: Simulation Adapter adds rule to memory
        RuleApplied --> ActiveLease: Target IP contained (Duration lease active)
        ActiveLease --> Expired: Expiration Worker detects elapsed duration
        ActiveLease --> ManualRollback: Admin initiates rollback action
    }

    state "Audit Logging" as Step4 {
        RejectedInvalid --> LogAudit
        RejectedAdmin --> LogAudit
        PolicyViolation --> LogAudit
        Expired --> LogAudit
        ManualRollback --> LogAudit
        LogAudit --> [*]
    }
```

---

## 5. Project Use-Case Diagram

This diagram outlines the functional use cases available to the three primary actors in the SentinelAI ecosystem: SOC Analyst, Security Administrator, and System Collectors/Workers.

```mermaid
graph LR
    subgraph Actors
        Analyst[SOC Security Analyst]
        Admin[Security Administrator]
        System[Telemetry Collectors / Workers]
    end

    subgraph SentinelAI_Use_Cases [SentinelAI Platform Use Cases]
        UC1(Authenticate & Manage Sessions)
        UC2(View Live SOC Overview Dashboard)
        UC3(Inspect Security Events & Raw Telemetry)
        UC4(Filter & Search Correlated Alerts)
        UC5(Propose Firewall Block Requests)
        UC6(Approve or Reject Block Requests)
        UC7(Execute Safe IP Rollback)
        UC8(Configure Detection Rule Thresholds)
        UC9(Trigger Safe Attack Simulation Scenarios)
        UC10(Review AI Model Evaluation & Confusion Matrix)
        UC11(Inspect System & Collector Health)
        UC12(Inspect Immutable Audit Trail)
        UC13(Ingest Socket & Sensor Telemetry)
        UC14(Revoke Expired Firewall Leases Automatically)
    end

    %% Analyst associations
    Analyst --> UC1
    Analyst --> UC2
    Analyst --> UC3
    Analyst --> UC4
    Analyst --> UC5
    Analyst --> UC10
    Analyst --> UC11

    %% Admin associations
    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12

    %% System / Worker associations
    System --> UC9
    System --> UC13
    System --> UC14
```
