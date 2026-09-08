import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import (
    User, Case, CaseEvent, Subject, Evidence, Analysis,
    Relationship, Report, ActivityLog, Notification, SystemSetting
)
from app.api.auth import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if users already exist
        if db.query(User).first():
            print("Database already seeded.")
            return

        print("Seeding CRIMSON database with demo intelligence data...")
        now = datetime.now(timezone.utc)

        # 1. Users
        admin_user = User(
            email="admin@crimson.intel",
            hashed_password=get_password_hash("crimson2026"),
            full_name="Chief Inspector Sarah Vance",
            role="Administrator",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
        )
        analyst_user = User(
            email="analyst@crimson.intel",
            hashed_password=get_password_hash("crimson2026"),
            full_name="Senior Analyst Marcus Thorne",
            role="Analyst",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
        )
        viewer_user = User(
            email="viewer@crimson.intel",
            hashed_password=get_password_hash("crimson2026"),
            full_name="Auditor David Chen",
            role="Viewer",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"
        )
        db.add_all([admin_user, analyst_user, viewer_user])
        db.commit()

        # 2. Cases
        cases = [
            Case(
                case_number="CAS-2026-001",
                title="Operation Shadow-Grid",
                description="Investigation into critical infrastructure cyber espionage targeting regional energy grid controllers in Northern Europe.",
                category="Counter-Intelligence",
                priority="CRITICAL",
                status="INVESTIGATING",
                assigned_analyst_id=analyst_user.id,
                risk_score=88,
                tags="cyber,espionage,scada,c2-server",
                created_at=now - timedelta(days=14),
                updated_at=now - timedelta(hours=2)
            ),
            Case(
                case_number="CAS-2026-002",
                title="Vanguard Capital Money Laundering",
                description="Cross-border financial crime investigation involving shell companies registered in offshore jurisdictions transferring illicit funds.",
                category="Financial Fraud",
                priority="HIGH",
                status="INVESTIGATING",
                assigned_analyst_id=admin_user.id,
                risk_score=74,
                tags="finance,laundering,crypto,offshore",
                created_at=now - timedelta(days=30),
                updated_at=now - timedelta(days=1)
            ),
            Case(
                case_number="CAS-2026-003",
                title="Aegis Defense Exfiltration",
                description="Internal threat investigation regarding unauthorized intellectual property exfiltration of military radar software blueprints.",
                category="Cybercrime",
                priority="HIGH",
                status="OPEN",
                assigned_analyst_id=analyst_user.id,
                risk_score=68,
                tags="insider-threat,exfiltration,defense",
                created_at=now - timedelta(days=7),
                updated_at=now - timedelta(hours=5)
            ),
            Case(
                case_number="CAS-2026-004",
                title="Titan Syndicate Narcotics Route",
                description="Maritime intelligence tracking transnational smuggling vectors originating from East Asia towards European ports.",
                category="Organized Crime",
                priority="MEDIUM",
                status="PENDING",
                assigned_analyst_id=analyst_user.id,
                risk_score=45,
                tags="maritime,smuggling,narcotics",
                created_at=now - timedelta(days=45),
                updated_at=now - timedelta(days=3)
            ),
            Case(
                case_number="CAS-2026-005",
                title="Apex Syndicate Identity Fraud",
                description="Synthetic identity network exploiting decentralized identity protocols for illicit credit issuance.",
                category="Financial Fraud",
                priority="LOW",
                status="RESOLVED",
                assigned_analyst_id=viewer_user.id,
                risk_score=22,
                tags="identity,fraud,synthetic",
                created_at=now - timedelta(days=90),
                updated_at=now - timedelta(days=12)
            )
        ]
        db.add_all(cases)
        db.commit()

        # 3. Case Events
        events = [
            CaseEvent(case_id=cases[0].id, title="Anomalous Traffic Detected", description="C2 beaconing observed to IP 185.220.101.45", event_date=now - timedelta(days=12), event_type="alert"),
            CaseEvent(case_id=cases[0].id, title="Digital Vault Search Warrant", description="Warrant granted for email communications of Subject Viktor Reznov", event_date=now - timedelta(days=5), event_type="milestone"),
            CaseEvent(case_id=cases[1].id, title="Wire Transfer Trace", description="Intercepted $4.2M wire transfer routed through Zurich Vault account", event_date=now - timedelta(days=20), event_type="financial"),
            CaseEvent(case_id=cases[2].id, title="Flash Drive Artifact Secured", description="Forensic image extracted from suspect workstation in Defense Lab 4", event_date=now - timedelta(days=4), event_type="evidence")
        ]
        db.add_all(events)
        db.commit()

        # 4. Subjects
        subjects = [
            Subject(name="Viktor Reznov", entity_type="Person", description="Suspected cyber espionage operative affiliated with ShadowCorp.", identifiers_json=json.dumps(["Alias: Ghost_09", "Passport: RU-8849201", "Telegram: @v_reznov"]), notes="High threat level. Subject uses encrypted satellite communications.", risk_level="CRITICAL", risk_score=92),
            Subject(name="Elena Rostova", entity_type="Person", description="Financial facilitator and proxy director for offshore shell firms.", identifiers_json=json.dumps(["Alias: E. Rostova", "Passport: CH-449102", "Swiss Bank IBAN: CH9300000000000000000"]), notes="Coordinates wire transfers out of Geneva.", risk_level="HIGH", risk_score=78),
            Subject(name="Apex Cybertech Ltd", entity_type="Organization", description="Front organization providing zero-day exploits under legitimate security audit facade.", identifiers_json=json.dumps(["Reg: CY-88219", "Domain: apexcybertech.io"]), notes="Operates out of Nicosia, Cyprus.", risk_level="HIGH", risk_score=72),
            Subject(name="ShadowCorp Syndicate", entity_type="Organization", description="Advanced Persistent Threat (APT) group focused on critical infrastructure.", identifiers_json=json.dumps(["APT-Group: APT-49", "Signature: ShadowGrid-Malware"]), notes="Primary antagonist in Operation Shadow-Grid.", risk_level="CRITICAL", risk_score=95),
            Subject(name="0x71C7656EC7ab88b098defB751B7401B5f6d8976F", entity_type="Digital Entity", description="Ethereum crypto wallet used for darknet ransom transactions.", identifiers_json=json.dumps(["Network: Ethereum", "Tether Balance: $2,450,000"]), notes="Linked to ransomware payout in Case CAS-2026-001.", risk_level="CRITICAL", risk_score=89),
            Subject(name="Zurich Vault Alpha", entity_type="Location", description="Private bullion and safe deposit institution in Geneva financial district.", identifiers_json=json.dumps(["GPS: 46.2044° N, 6.1432° E", "Address: Bahnhofstrasse 14, Zurich"]), notes="Location of suspected asset stash.", risk_level="MEDIUM", risk_score=48),
            Subject(name="Operation Midnight Exfiltration", entity_type="Event", description="Coordinated cyber attack event executed on November 14.", identifiers_json=json.dumps(["Time: 02:14 UTC", "Target: SCADA Substation 4"]), notes="Event milestone in cyber espionage timeline.", risk_level="HIGH", risk_score=80)
        ]
        db.add_all(subjects)
        db.commit()

        # 5. Evidence
        evidence_list = [
            Evidence(
                evidence_number="EVI-2026-001",
                case_id=cases[0].id,
                title="Encrypted C2 Server Packet Log",
                evidence_type="Document",
                description="PCAP file capturing outbound SSL connections to IP 185.220.101.45 during SCADA shutdown attempt.",
                source="Network IDS Probe #4",
                collection_date=now - timedelta(days=10),
                status="VERIFIED",
                reference_hash="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                created_by_id=analyst_user.id
            ),
            Evidence(
                evidence_number="EVI-2026-002",
                case_id=cases[1].id,
                title="Offshore Banking Ledger - Zurich",
                evidence_type="Record",
                description="Financial spreadsheet documenting 14 wire transfers totaling $4,200,000 to Apex Cybertech Ltd.",
                source="Financial Intelligence Unit Intercept",
                collection_date=now - timedelta(days=18),
                status="VERIFIED",
                reference_hash="7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
                created_by_id=admin_user.id
            ),
            Evidence(
                evidence_number="EVI-2026-003",
                case_id=cases[2].id,
                title="Workstation RAM Dump Forensic Analysis",
                evidence_type="Text",
                description="Memory dump analysis showing decrypted unallocated RAM containing radar blueprint metadata.",
                source="Cyber Forensics Lab",
                collection_date=now - timedelta(days=3),
                status="VERIFIED",
                reference_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                created_by_id=analyst_user.id
            ),
            Evidence(
                evidence_number="EVI-2026-004",
                case_id=cases[0].id,
                title="Darknet Forum Intercept URL",
                evidence_type="URL",
                description="Archived onion forum thread where 'Ghost_09' posted SCADA exploit credentials.",
                source="HUMINT Cyber Division",
                collection_date=now - timedelta(days=8),
                status="VERIFIED",
                reference_hash="c4ca4238a0b923820dcc509a6f75849b2a7c41d13f9f4a7cfa19e34c2b9a764d",
                created_by_id=analyst_user.id
            )
        ]
        db.add_all(evidence_list)
        db.commit()

        # 6. Relationships
        relationships = [
            Relationship(source_type="Subject", source_id=subjects[0].id, target_type="Subject", target_id=subjects[3].id, relation_type="works_for", confidence=0.95, notes="Viktor Reznov is confirmed lead hacker for ShadowCorp."),
            Relationship(source_type="Subject", source_id=subjects[0].id, target_type="Case", target_id=cases[0].id, relation_type="associated_with", confidence=0.98, notes="Primary suspect in Operation Shadow-Grid."),
            Relationship(source_type="Subject", source_id=subjects[1].id, target_type="Subject", target_id=subjects[2].id, relation_type="member_of", confidence=0.91, notes="Elena Rostova acts as director for Apex Cybertech."),
            Relationship(source_type="Subject", source_id=subjects[2].id, target_type="Subject", target_id=subjects[4].id, relation_type="owns", confidence=0.88, notes="Crypto wallet controlled by Apex Cybertech proxy."),
            Relationship(source_type="Subject", source_id=subjects[1].id, target_type="Subject", target_id=subjects[5].id, relation_type="located_at", confidence=0.85, notes="Frequent physical visits to Zurich Vault."),
            Relationship(source_type="Evidence", source_id=evidence_list[0].id, target_type="Subject", target_id=subjects[0].id, relation_type="references", confidence=0.94, notes="Packet logs contain IP assigned to Viktor Reznov."),
            Relationship(source_type="Subject", source_id=subjects[3].id, target_type="Subject", target_id=subjects[6].id, relation_type="associated_with", confidence=0.90, notes="ShadowCorp directed Operation Midnight.")
        ]
        db.add_all(relationships)
        db.commit()

        # 7. Analyses
        analyses = [
            Analysis(
                case_id=cases[0].id,
                query_text="Analyze C2 beaconing activity and Viktor Reznov connection to SCADA shutdown.",
                context_text="Network logs show IP 185.220.101.45 communicating with SCADA substation 4. Darknet thread references Ghost_09 alias.",
                subject_id=subjects[0].id,
                summary="High-confidence link established between subject Viktor Reznov and SCADA malware deployment. Crypto payments traced to 0x71C7656EC7ab88b098defB751B7401B5f6d8976F.",
                key_findings_json=json.dumps([
                    "PCAP log verifies 14 connection attempts to command-and-control server.",
                    "Crypto wallet balance increased by 250 ETH concurrently with cyber intrusion.",
                    "Subject alias Ghost_09 confirmed on darknet forum."
                ]),
                entities_json=json.dumps([
                    {"name": "Viktor Reznov", "type": "Person", "confidence": 0.96},
                    {"name": "ShadowCorp Syndicate", "type": "Organization", "confidence": 0.95},
                    {"name": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F", "type": "Digital Entity", "confidence": 0.98}
                ]),
                relationships_json=json.dumps([
                    {"source": "Viktor Reznov", "target": "ShadowCorp Syndicate", "relation": "works_for", "confidence": 0.95},
                    {"source": "Viktor Reznov", "target": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F", "relation": "owns", "confidence": 0.92}
                ]),
                risk_indicators_json=json.dumps([
                    {"indicator": "Ransomware Deployment", "severity": "CRITICAL", "description": "Active C2 beaconing detected.", "score": 90},
                    {"indicator": "Offshore Crypto Transfer", "severity": "HIGH", "description": "Large value transfer to unhosted wallet.", "score": 82}
                ]),
                confidence_score=0.94,
                recommendations_json=json.dumps([
                    "Issue international Interpol Red Notice for Viktor Reznov.",
                    "Apply sanction freezing order on crypto wallet 0x71C7..."
                ]),
                next_steps_json=json.dumps([
                    "Coordinate with European Cybercrime Centre.",
                    "Extract memory image from auxiliary proxy node."
                ]),
                is_demo=True,
                created_at=now - timedelta(days=2)
            )
        ]
        db.add_all(analyses)
        db.commit()

        # 8. Reports
        reports = [
            Report(
                report_number="REP-2026-001",
                title="Operation Shadow-Grid Preliminary Intelligence Report",
                report_type="Investigation Report",
                case_id=cases[0].id,
                content_json=json.dumps({
                    "title": "Operation Shadow-Grid Preliminary Intelligence Report",
                    "classification": "TOP SECRET // CRIMSON INTELLIGENCE",
                    "overview": "Comprehensive assessment of SCADA cyber intrusion targeting European energy sector.",
                    "key_findings": ["C2 IP identified", "Subject Reznov tied to exploit", "Crypto wallet identified"],
                    "risk_rating": "CRITICAL (88/100)"
                }),
                author_id=analyst_user.id,
                format="JSON",
                created_at=now - timedelta(days=1)
            )
        ]
        db.add_all(reports)
        db.commit()

        # 9. Activity Logs
        activity_logs = [
            ActivityLog(user_id=admin_user.id, user_name=admin_user.full_name, action="Case Created", entity_type="Case", entity_id=cases[0].id, details="Created case CAS-2026-001 (Operation Shadow-Grid)", created_at=now - timedelta(days=14)),
            ActivityLog(user_id=analyst_user.id, user_name=analyst_user.full_name, action="Evidence Added", entity_type="Evidence", entity_id=evidence_list[0].id, details="Uploaded packet log EVI-2026-001", created_at=now - timedelta(days=10)),
            ActivityLog(user_id=analyst_user.id, user_name=analyst_user.full_name, action="Analysis Executed", entity_type="Analysis", entity_id=analyses[0].id, details="Executed DEMO AI Analysis on Viktor Reznov context", created_at=now - timedelta(days=2)),
            ActivityLog(user_id=admin_user.id, user_name=admin_user.full_name, action="Report Generated", entity_type="Report", entity_id=reports[0].id, details="Generated REP-2026-001 Investigation Report", created_at=now - timedelta(days=1))
        ]
        db.add_all(activity_logs)
        db.commit()

        # 10. Notifications
        notifications = [
            Notification(user_id=admin_user.id, title="Critical Case Alert", message="Case CAS-2026-001 priority elevated to CRITICAL due to active C2 traffic.", notification_type="CRITICAL", is_read=False, link="/cases/1", created_at=now - timedelta(hours=3)),
            Notification(user_id=analyst_user.id, title="AI Analysis Complete", message="Local DEMO AI Engine finished intelligence extraction for Case CAS-2026-001.", notification_type="SUCCESS", is_read=True, link="/analysis", created_at=now - timedelta(days=2)),
            Notification(user_id=viewer_user.id, title="Report Ready for Download", message="Investigation Report REP-2026-001 is now ready.", notification_type="INFO", is_read=False, link="/reports", created_at=now - timedelta(days=1))
        ]
        db.add_all(notifications)
        db.commit()

        # 11. System Settings
        settings_list = [
            SystemSetting(key="AI_ENGINE_MODE", value="DEMO_LOCAL", description="Operating mode for NLP intelligence processing."),
            SystemSetting(key="SECURITY_LEVEL", value="HIGH", description="System clearance level requirement for raw evidence download."),
            SystemSetting(key="MAX_GRAPH_NODES", value="100", description="Maximum entity nodes rendered simultaneously in visual network canvas.")
        ]
        db.add_all(settings_list)
        db.commit()

        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
