# SentinelAI — Viva Voce Preparation Guide (45 Questions & Answers)

This guide contains 45 technically rigorous, concise questions and answers designed for final-year engineering project defense, comprehensive viva voce examinations, and technical presentations.

---

## Category 1: Network Intrusion Detection Fundamentals

### Q1: What is a Network Intrusion Detection System (NIDS), and how does SentinelAI implement it?
**Answer:**
A Network Intrusion Detection System (NIDS) monitors network traffic traversing a segment or host to identify unauthorized, anomalous, or malicious activity. SentinelAI implements an integrated, host-level and sensor-ingested hybrid NIDS. It ingests network flow records from both live Windows socket telemetry (`netstat` inspection) and Suricata EVE logs, extracts statistical flow features, and submits them concurrently to deterministic rules and trained machine-learning classifiers to detect port scans, denial of service (DoS), brute force, and beaconing.

### Q2: What is the difference between a flow-based NIDS and a packet-inspection NIDS?
**Answer:**
- **Packet-inspection NIDS (Deep Packet Inspection / DPI)** examines raw Ethernet frames, IP packet headers, and payload contents (e.g., regex pattern matching on HTTP URIs or exploit signatures). It requires significant memory and CPU overhead.
- **Flow-based NIDS** abstracts individual packets into bidirectional network conversations defined by 5-tuples (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol`) and computes summary statistics (e.g., flow duration, packet counts, bytes per second, flag distributions). SentinelAI primarily operates as a flow-based NIDS, reducing processing latency while remaining effective against encrypted traffic where payload inspection is blinded.

### Q3: What is the difference between an Intrusion Detection System (IDS) and an Intrusion Prevention System (IPS)?
**Answer:**
An IDS operates out-of-band or passively; it monitors traffic, generates security alerts, and logs incidents without directly disrupting network packet transmission. An IPS sits in-line with the network path and actively drops packets or alters firewall tables automatically. SentinelAI bridges both paradigms by operating as an IDS with **Controlled Active Response**—it flags threats automatically but requires explicit administrative approval before applying firewall block rules.

### Q4: Why is automated, unverified blocking considered dangerous in enterprise security operations?
**Answer:**
Fully autonomous firewall response can cause self-inflicted Denial of Service (DoS). If an attacker spoofs the source IP address of critical infrastructure (such as default gateways, Active Directory domain controllers, or upstream DNS resolvers like `8.8.8.8`), an unverified IPS would block legitimate network dependencies, crashing enterprise connectivity. SentinelAI solves this via the "Two-Person Rule" (analyst submission + admin approval) combined with hardcoded protected target guardrails.

---

## Category 2: Rule-Based vs Machine-Learning Detection

### Q5: What are the primary trade-offs between rule-based and machine learning-based detection?
**Answer:**
- **Rule-Based Detection**: Fast ($O(1)$ to $O(k)$ evaluation), deterministic, zero false positives for exact known patterns, highly explainable, but unable to detect zero-day variants, altered thresholds, or obfuscated attacks.
- **Machine Learning Detection**: Generalizes across non-linear feature relationships, identifies novel variations of attacks and structural statistical anomalies, but can suffer from false positives, training distribution shift, and requires labeled data.
SentinelAI combines both in a **Hybrid Architecture** where rules provide deterministic instant triage and ML models provide contextual classification and anomaly scoring.

### Q6: How does SentinelAI resolve conflicts between the rule engine and ML models?
**Answer:**
SentinelAI uses a weighted risk aggregation engine:
$$\text{Risk Score} = w_r \cdot \text{Score}_{\text{rule}} + w_{rf} \cdot (P_{\text{threat}} \times 100) + w_{if} \cdot (\text{Anomaly} \times 100)$$
If a high-confidence rule matches (e.g., SYN Flood signature), an alert is triggered immediately regardless of ML score. If rules do not match but the Random Forest model reports malicious probability $> 0.85$ or Isolation Forest flags a severe structural anomaly, an alert is also raised. This ensures zero regression on known attacks while maintaining zero-day detection.

### Q7: What are the five baseline rules configured in SentinelAI?
**Answer:**
1. **R-001 (Port Scan Detection)**: $> 15$ SYN packets within a short duration directed across multiple destination ports.
2. **R-002 (DoS SYN Flood)**: Ratio of SYN to ACK flags exceeding $20:1$ with forward packet volume $> 500$ packets/sec.
3. **R-003 (Repeated Authentication Failures)**: Consecutive connection resets (`RST`) or retransmissions to service ports (22, 3389) $> 10$ attempts.
4. **R-004 (DNS Tunneling / High-Entropy Queries)**: Outbound UDP 53 packets with unusual payload sizes or continuous low-latency queries.
5. **R-005 (Anomalous Outbound Data Exfiltration)**: Backward byte-to-forward byte asymmetry $> 50:1$ to unknown external endpoints.

### Q8: What is alert fatigue, and how does your project address it?
**Answer:**
Alert fatigue occurs when security operations center (SOC) analysts are overwhelmed by high volumes of redundant, low-severity, or false-positive alerts, causing them to miss critical intrusions. SentinelAI addresses alert fatigue through:
1. **Temporal Deduplication**: Collapses identical flow events within a sliding 60-second window into an incremented `occurrence_count` on an existing alert.
2. **Confidence-Weighted Severity**: Suppresses alerts whose combined risk score falls below the configurable threshold ($< 40$).

---

## Category 3: Machine Learning Algorithms: Random Forest, Decision Tree & Isolation Forest

### Q9: Why did you select Random Forest as the primary supervised classifier?
**Answer:**
Random Forest is an ensemble learning method constructed from numerous de-correlated decision trees trained on bootstrap samples (bagging) with random feature selection. It was selected because:
1. It is resilient to overfitting on noisy network traffic.
2. It handles non-linear relationships and interactions among heterogeneous network features.
3. It has extremely fast inference latency ($< 0.1\text{ ms}$ per sample), making it suitable for near-real-time packet flow inspection.
4. It outputs calibrated probability estimates for confidence scoring.

### Q10: What is the role of the Decision Tree model in SentinelAI?
**Answer:**
The Decision Tree (`DecisionTreeClassifier` with `max_depth=12`) serves as an explainable, lightweight baseline classifier. Because individual decision trees execute an explicit sequence of orthogonal split conditions (e.g., `if syn_flag_count > 12 and flow_duration < 500ms`), it provides transparent rule extraction and interpretable decision paths that SOC analysts can inspect to understand why an event was categorized as malicious.

### Q11: How does Isolation Forest work, and why is it used for unsupervised anomaly detection?
**Answer:**
Isolation Forest detects anomalies rather than profiling normal points. It recursively partitions feature space using random split values. Because anomalies are "few and different," they require significantly fewer splits to isolate (shorter path lengths from the tree root). SentinelAI uses Isolation Forest ($100$ estimators, contamination $0.05$) to catch zero-day attacks, stealthy C2 beaconing, and anomalous protocol behaviors that have no supervised labels or pre-existing rules.

### Q12: How are the model artifacts stored and reloaded in production?
**Answer:**
Trained models, preprocessing scalers, and label encoders are serialized as binary joblib files in `backend/app/ml/models/`:
- `random_forest.joblib`
- `decision_tree.joblib`
- `isolation_forest.joblib`
- `scaler.joblib`
- `label_encoder.joblib`
The `ModelRegistry` class implements a thread-safe singleton pattern that loads these artifacts into memory on application startup, enabling concurrent read-only inference across worker threads without disk I/O bottlenecks.

### Q13: How does the system handle class imbalance during model training?
**Answer:**
In network intrusion datasets, benign traffic typically outnumbers attack traffic by orders of magnitude (e.g., $95\%$ benign vs $5\%$ attack). To counter this, SentinelAI:
1. Uses `class_weight="balanced"` in scikit-learn classifiers, which automatically penalizes misclassifications inversely proportional to class frequencies.
2. Evaluates performance using Precision, Recall, and F1-score rather than raw classification accuracy, which is biased by majority classes.

---

## Category 4: Feature Extraction and Preprocessing

### Q14: Which network features are extracted from raw packet flows?
**Answer:**
SentinelAI extracts 14 core statistical features modeled after the Canadian Institute for Cybersecurity (CIC) intrusion benchmarks:
1. `dst_port` (Destination Port)
2. `flow_duration` (Microseconds)
3. `total_fwd_packets` (Client-to-server packet count)
4. `total_bwd_packets` (Server-to-client packet count)
5. `flow_bytes_s` (Byte throughput rate)
6. `flow_packets_s` (Packet throughput rate)
7. `flow_iat_mean` (Mean inter-arrival time between packets)
8. `flow_iat_std` (Standard deviation of inter-arrival time)
9. `fwd_packet_length_max` (Maximum packet length in forward direction)
10. `bwd_packet_length_mean` (Average packet length in backward direction)
11. `syn_flag_count` (SYN flags observed)
12. `rst_flag_count` (RST flags observed)
13. `ack_flag_count` (ACK flags observed)
14. `down_up_ratio` (Download-to-upload packet ratio)

### Q15: Why is standard scaling (z-score normalization) critical before inference?
**Answer:**
Network features have vastly different numeric magnitudes. For example, `flow_duration` can exceed $10,000,000\ \mu\text{s}$, while `syn_flag_count` ranges from $0$ to $50$, and `down_up_ratio` ranges between $0.0$ and $5.0$. Without normalization, distance-based metrics and gradient updates would be dominated by microsecond durations. StandardScaler transforms each feature to zero mean and unit variance:
$$z = \frac{x - \mu}{\sigma}$$

### Q16: How does SentinelAI handle infinite values, NaNs, and extreme outliers during feature preprocessing?
**Answer:**
In live network calculations, division by zero occurs if `flow_duration == 0`, producing `inf` for `flow_bytes_s`. The preprocessor `FlowPreprocessor`:
1. Replaces `+inf` and `-inf` with predefined numeric maximum limits ($10^9$).
2. Imputes missing or `NaN` values with the median learned during training.
3. Applies clipping to fitted feature ranges to prevent extreme packet spikes from generating numeric overflow in floating-point calculations.

### Q17: What was the bug identified in Phase 4 regarding feature clipping, and how was it fixed?
**Answer:**
In Phase 4, the preprocessor erroneously applied a hard numeric clip of `[-10, 10]` to **raw** unscaled network features before passing them to the scaler. This corrupted raw features (e.g., clipping port $443$ down to $10$, and clipping a $50,000\ \mu\text{s}$ duration to $10$). The fix properly restricted clipping to the **post-standardized** z-score values, preserving the physical meaning of raw network features.

---

## Category 5: CIC-IDS2017 Benchmark Compatibility

### Q18: What is the CIC-IDS2017 dataset?
**Answer:**
CIC-IDS2017 is an industry-standard network security benchmark developed by the Canadian Institute for Cybersecurity and the University of New Brunswick. It includes realistic background traffic (HTTP, HTTPS, SSH, FTP) combined with modern attack scenarios (Port Scan, DoS Slowloris, DDoS, Brute Force, Infiltration, Heartbleed).

### Q19: How does SentinelAI achieve compatibility with CIC-IDS2017?
**Answer:**
The schema and feature vector of SentinelAI's `FlowPreprocessor` map directly to the normalized header names of the CIC-IDS2017 CSV files (e.g., `Destination Port`, `Flow Duration`, `Total Fwd Packets`, `FIN Flag Count`). The training loader script `backend/app/ml/training/load_dataset.py` parses these headers, cleans invalid tokens, and standardizes multi-class labels into canonical categories (`benign`, `port_scan`, `dos`, `brute_force`, `bot`).

### Q20: What is the difference between synthetic benchmark splits and real-world network traffic?
**Answer:**
Synthetic benchmark splits (or partitioned historical datasets like CIC-IDS2017) are pre-filtered, static, and often exhibit higher feature separation than real enterprise environments. Real network traffic contains jitter, NAT address translation, asymmetric routing, packet loss, and zero-day applications. Therefore, SentinelAI explicitly differentiates between benchmark metrics (e.g., $100\%$ on clean synthetic splits) and real-world operational baselines (e.g., $92.5\%$ F1-score with $2.1\%$ false positive rate in noisy environments).

---

## Category 6: Backend Architecture & FastAPI REST APIs

### Q21: Why was FastAPI chosen over Flask or Django for this cybersecurity backend?
**Answer:**
1. **Asynchronous Concurrency**: Built on `Starlette` and `uvloop`, FastAPI handles high-throughput asynchronous I/O natively (`async/await`), crucial for high-volume network telemetry ingestion.
2. **Pydantic Validation**: Automatic schema enforcement and data serialization with clear validation error responses.
3. **Automatic OpenAPI/Swagger Documentation**: Interactive documentation available at `/docs` speeds up testing and frontend integration.
4. **Dependency Injection**: Streamlines database session management and JWT authentication enforcement across endpoints.

### Q22: What are FastAPI Lifespan Handlers, and how are they used in SentinelAI?
**Answer:**
Lifespan handlers (`@asynccontextmanager`) define startup and shutdown sequences for the application. In SentinelAI, the lifespan handler:
- **On Startup**: Establishes the MongoDB Atlas connection pool, initializes database indexes, loads ML model artifacts into memory via `ModelRegistry`, and spawns background telemetry polling and rule expiration worker threads.
- **On Shutdown**: Gracefully signals background workers to terminate and closes the PyMongo client connection pool to prevent socket leaks.

### Q23: What background workers operate within the backend service?
**Answer:**
Three background worker threads operate independently of the request-response cycle:
1. `IngestionWorker`: Continuously polls registered network collectors (Windows socket collector, Suricata log tailer) at configured polling intervals.
2. `DetectionWorker`: Consumes ingested event queues, feeds them through the ML inference pipeline, and generates correlated alerts.
3. `ExpiryWorker`: Periodically checks active firewall block actions and automatically reverts/expires temporary rules whose lease duration (`duration_minutes`) has elapsed.

### Q24: How does SentinelAI handle Cross-Origin Resource Sharing (CORS)?
**Answer:**
CORS is handled via FastAPI's `CORSMiddleware`. Allowed origins are loaded from `CORS_ORIGINS` in `settings.py` (allowing `http://localhost:8080`, `http://127.0.0.1:8080`, and `http://localhost:5173`). This allows the React SPA running on port 8080 to safely interact with the backend API on port 8000 while disallowing unauthorized external origins.

---

## Category 7: Database Design, MongoDB Atlas & Document Storage

### Q25: Why is MongoDB Atlas suited for storing network telemetry and security alerts?
**Answer:**
1. **Schema Flexibility**: Network events vary significantly based on protocol and collector source (e.g., DNS events contain query names; TCP flows contain flag counts; ICMP events contain type/code). MongoDB's document model stores heterogeneous flow records without requiring complex multi-table relational joins.
2. **High Write Throughput**: Document insertion with write concern `w=1` provides fast ingestion of streaming network events.
3. **Cloud Resilience**: Atlas provides automated replication, encryption at rest, TLS in transit, and cloud-managed backups.

### Q26: What are the main MongoDB collections used in SentinelAI?
**Answer:**
1. `events`: Raw network flow documents and connection records.
2. `alerts`: Correlated threat incidents with severity, risk score, and matched rule/ML metadata.
3. `rules`: Seeded and custom deterministic detection rules.
4. `block_requests`: Analyst-submitted firewall block proposals awaiting approval.
5. `firewall_actions`: Executed firewall blocking rules (active, expired, or rolled back).
6. `audit_logs`: Immutable security audit trails for all sensitive administrator actions.
7. `users`: Seeded user accounts with hashed credentials and role assignments.

### Q27: Which indexes are created in MongoDB, and why?
**Answer:**
- `events`: Compound index on `(timestamp: -1, source_ip: 1)` and single index on `status` to ensure fast filtering on the Network Traffic page.
- `alerts`: Indexes on `timestamp: -1`, `severity: 1`, and `status: 1` for fast SOC dashboard rendering.
- `alerts`: Compound deduplication index on `(source_ip: 1, category: 1, status: 1)` to accelerate deduplication queries.
- `users`: Unique index on `username` and `email` to prevent duplicate account registration.
- `firewall_actions`: Index on `(status: 1, expires_at: 1)` to allow `ExpiryWorker` to quickly find rules ready for expiration.

### Q28: How does the system protect MongoDB Atlas connection credentials?
**Answer:**
MongoDB Atlas connection strings (`mongodb+srv://...`) are stored exclusively in the root and `backend/.env` configuration files, which are listed in `.gitignore`. Credentials are dynamically loaded via `pydantic-settings` into memory. When logging database health or errors, the URI is sanitized to mask passwords (`***`), preventing accidental exposure in console outputs or debug logs.

---

## Category 8: Authentication, Authorization & JWT RBAC

### Q29: How does JWT authentication work in SentinelAI?
**Answer:**
When a user posts valid credentials to `/api/v1/auth/login`, the backend:
1. Verifies the password using `bcrypt` against the salted hash in `users`.
2. Generates a signed JSON Web Token (JWT) using HMAC-SHA256 (`HS256`).
3. Encodes the user's `sub` (username), `role` (analyst or administrator), and expiration time (`exp`) in the payload.
4. The client includes this token in the `Authorization: Bearer <token>` HTTP header for subsequent protected requests.

### Q30: What is the difference between the Security Analyst and Administrator roles?
**Answer:**
- **Security Analyst (`role: analyst`)**: Can view dashboard metrics, inspect network traffic, search alerts, download CSV reports, and submit proposed firewall block requests (`POST /api/v1/firewall/requests`).
- **Administrator (`role: administrator`)**: Has full system privileges, including modifying detection rules, approving/rejecting block requests, triggering firewall rollbacks, modifying user settings, and purging historical logs.

### Q31: How are passwords hashed and secured?
**Answer:**
Passwords are never stored in plaintext. SentinelAI uses the `passlib` library with the `bcrypt` hashing algorithm. Bcrypt incorporates a unique 128-bit salt per user and a tunable work factor (cost parameter) that slows down dictionary and rainbow-table attacks.

---

## Category 9: Event Deduplication & Alert Correlation Logic

### Q32: What is event deduplication, and what algorithm is implemented in SentinelAI?
**Answer:**
Event deduplication prevents repeated occurrences of the same attack pattern from generating hundreds of separate alerts. When a new event triggers an alert:
1. The system searches MongoDB for an existing alert matching the same `source_ip` and `category` where `status == "active"` and `(current_time - last_seen) < 60,000 ms`.
2. If an active alert is found, the system increments its `occurrence_count`, updates `last_seen = current_time`, appends the new event ID to `related_event_ids`, and updates the risk score without creating a new alert document.
3. If no matching alert exists within the 60-second window, a new alert is generated.

### Q33: How does alert correlation link raw network events to security incidents?
**Answer:**
Alert correlation links multiple disparate flow events to a single security incident. In SentinelAI, each alert document maintains:
- `related_event_id`: The primary event triggering the detection.
- `related_event_ids`: An array of associated event IDs collected across the attack sequence.
This enables SOC analysts clicking an alert to immediately view all associated raw packet records in a single modal without running manual database queries.

### Q34: What is the significance of the 60-second deduplication window?
**Answer:**
A 60-second window balances real-time visibility with alert suppression. High-speed attacks (such as a 10,000-packet SYN flood) execute in seconds; collapsing these into a single incident with an updated occurrence counter prevents database bloat. Conversely, if the same IP attacks again 10 minutes later, it is treated as a distinct incident, allowing the SOC to track recurring campaigns over time.

---

## Category 10: Telemetry Ingestion: Suricata vs Windows Socket Collector

### Q35: How does the native Windows Socket Collector function?
**Answer:**
The Windows Socket Collector (`WindowsSocketCollector`) polls active TCP and UDP sockets using the host OS utility `netstat -n -o`. It parses the active network table to extract foreign IP addresses, foreign ports, protocol types, and process identifiers (PIDs). It filters out loopback connections (`127.0.0.1`) and enriches each socket record with flow statistical defaults so it can be evaluated by the hybrid detection engine in real time.

### Q36: How does the Suricata EVE collector integrate with SentinelAI?
**Answer:**
Suricata outputs structured JSON event records to an Extensible Event Format file (`eve.json`). SentinelAI implements `SuricataEveCollector`, which maintains a non-blocking file pointer (tailing the file like `tail -F`). When Suricata writes an `alert` or `flow` event, the collector parses the JSON object, maps Suricata's 5-tuple and flow metadata into SentinelAI's unified `NetworkEvent` schema, and injects it into the processing pipeline.

### Q37: Why does Suricata display "Disconnected" during the local demonstration, and is this an error?
**Answer:**
It is **not an error**; it represents honest sensor status reporting. Suricata is an external open-source IDS engine that requires installation of WinPcap/Npcap drivers and dedicated configuration files not bundled with the lightweight web repository. SentinelAI's architecture is sensor-agnostic: when Suricata is not running, the collector reports `state: disconnected` while the system continues monitoring traffic via the active Windows Socket Collector and safe simulation engines.

---

## Category 11: Controlled Firewall Response, Guardrails & Rollback Mechanism

### Q38: What is the "Two-Person Rule" in SentinelAI's firewall response?
**Answer:**
The Two-Person Rule requires two distinct roles to execute a disruptive network action:
1. **Initiator (Analyst)**: Analyzes a security incident and submits a proposed block request detailing target IP, reason, direction, and lease duration.
2. **Approver (Administrator)**: Reviews the request, inspects the associated telemetry, and formally approves or rejects it.
This separation of duties prevents single-point compromise or rogue analyst actions from disrupting production networks.

### Q39: What is Simulation Mode (`FIREWALL_MODE=simulation`)?
**Answer:**
In simulation mode, the firewall driver logs the exact command that would be executed (e.g., `netsh advfirewall firewall add rule...` on Windows or `iptables -A INPUT -s ... -j DROP` on Linux) and records the action in MongoDB Atlas, but does not execute the destructive system command on the host OS. This allows safe, realistic evaluation and student demonstration without risking workstation network disconnection.

### Q40: What are Protected Target Guardrails?
**Answer:**
The `FirewallService` maintains a non-configurable blacklist of protected IPs:
- Loopback addresses: `127.0.0.1`, `::1`
- RFC 5737 documentation networks
- Upstream DNS resolvers: `8.8.8.8`, `1.1.1.1`
- Local default gateway (e.g., `192.168.1.1`)
Any attempt by a user or automated recommendation to block a protected target immediately throws a `ProtectedTargetError` (HTTP `400 Bad Request`) and aborts the operation.

### Q41: How does the Rollback Mechanism work?
**Answer:**
Every approved firewall block action is assigned a unique UUID and recorded with status `active`. When an administrator clicks "Rollback" or calls `POST /api/v1/firewall/actions/{id}/rollback`:
1. The firewall driver executes the inverse command (e.g., `netsh advfirewall firewall delete rule name="SentinelAI_Block_<IP>"`).
2. The action document status is updated to `rolled_back` with a `rolled_back_at` timestamp and the reviewer's username.
3. An audit log is written, ensuring complete accountability.

---

## Category 12: Testing Methodology, Metrics, False Positives & Future Work

### Q42: What testing methodologies were used to validate SentinelAI?
**Answer:**
1. **Unit Testing**: 39 automated PyTest tests verifying feature extraction, z-score scaling, rule triggers, model inference, password hashing, and exception handling.
2. **Integration Testing**: Testing API endpoint responses, MongoDB Atlas reads/writes, and JWT authorization flows.
3. **End-to-End Demonstration Testing**: Verifying the complete pipeline from simulated packet injection to alert generation and firewall rollback.
4. **Static Code Analysis & Production Build**: Running TypeScript compilation and Vite bundling (`npm run build`) with zero linting or type errors across 2,642 modules.

### Q43: How do you explain the difference between your software tests and machine learning metrics?
**Answer:**
A software test (e.g., "39 passed tests") evaluates code logic correctness, exception handling, and database queries—it is a binary pass/fail verification of software engineering quality. In contrast, machine learning metrics (Precision, Recall, F1-score, ROC-AUC) quantify the statistical ability of a trained model to discriminate between benign and malicious traffic on an evaluation dataset. Presenting passing unit tests as "model accuracy" is scientifically incorrect.

### Q44: What are the current limitations of the SentinelAI implementation?
**Answer:**
1. **Telemetry Rate Limit**: In high-throughput 10 Gbps enterprise backbones, Python-based socket polling cannot capture line-rate traffic; it requires DPDK (Data Plane Development Kit) or eBPF kernel probes.
2. **Encrypted Payload Blindness**: Flow-based statistics cannot inspect encrypted TLS payloads for application-layer injection (e.g., SQLi or Log4j).
3. **Local Sensor Deployment**: Suricata is not locally configured on the Windows workstation, meaning external packet inspection relies on simulation or socket polling.

### Q45: What future enhancements are planned for SentinelAI?
**Answer:**
1. **eBPF (Extended Berkeley Packet Filter) Integration**: Deploying kernel-level eBPF probes on Linux nodes for line-rate packet capture with near-zero CPU overhead.
2. **Graph Neural Networks (GNNs)**: Modeling enterprise network topologies as graphs to detect lateral movement across subnets.
3. **Automated Continuous Retraining (MLOps)**: Setting up a feedback loop where analyst false-positive confirmations automatically trigger retraining of Random Forest and Isolation Forest models.
4. **MITRE ATT&CK Mapping**: Tagging alerts directly with MITRE ATT&CK tactics and techniques (e.g., T1046 Network Service Scanning, T1110 Brute Force).
