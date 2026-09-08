import re
import json
from typing import Dict, Any, List

class LocalAIEngine:
    """
    CRIMSON Local Intelligence & NLP Analysis Engine (Demo Mode).
    Performs deterministic pattern matching, entity extraction, sentiment/risk flag identification,
    relationship mapping, and recommendations generation without external paid APIs.
    """

    PATTERNS = {
        "EMAIL": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "IP_ADDRESS": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "CRYPTO_WALLET": r'\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b',
        "PHONE": r'\+?[0-9]{1,4}?[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}',
        "PASSPORT_ID": r'\b[A-Z]{1,2}[0-9]{6,8}\b',
        "AMOUNT": r'\$(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?|\b\d+\s?(?:USD|EUR|BTC|ETH|USDT)\b'
    }

    RISK_KEYWORDS = {
        "CRITICAL": ["ransomware", "money laundering", "espionage", "exfiltration", "exploit", "c2 server", "terrorist", "assassination", "trafficking", "breach"],
        "HIGH": ["suspicious transfer", "unauthorized access", "malware", "shell company", "darknet", "sanction", "smuggling", "kickback", "bribe"],
        "MEDIUM": ["offshore account", "encrypted chat", "vpn proxy", "wire transfer", "alias", "falsified", "alias"],
        "LOW": ["meeting", "correspondence", "travel log", "routine check", "inquiry"]
    }

    def __init__(self):
        self.mode = "DEMO AI MODE (Local Intelligence Engine)"

    def analyze(self, query_text: str, context_text: str = "", case_title: str = None, subject_name: str = None) -> Dict[str, Any]:
        combined_text = f"{query_text}\n{context_text}".strip()
        
        # 1. Entity Extraction
        entities = self._extract_entities(combined_text)
        if subject_name and not any(e["name"].lower() == subject_name.lower() for e in entities):
            entities.insert(0, {
                "name": subject_name,
                "type": "Person",
                "confidence": 0.95,
                "context": "Primary subject of analysis"
            })

        # 2. Risk Indicators Detection
        risk_indicators = self._detect_risk_indicators(combined_text)

        # 3. Relationship Extraction
        relationships = self._extract_relationships(entities, combined_text)

        # 4. Summary & Findings Generation
        key_findings = self._generate_key_findings(combined_text, entities, risk_indicators)
        summary = self._generate_summary(query_text, case_title, entities, risk_indicators)

        # 5. Calculate Confidence & Risk
        confidence_score = round(min(0.98, 0.75 + (len(entities) * 0.03) + (len(risk_indicators) * 0.02)), 2)

        # 6. Recommendations & Next Steps
        recommendations = self._generate_recommendations(risk_indicators, entities)
        next_steps = self._generate_next_steps(entities, risk_indicators)

        return {
            "summary": summary,
            "key_findings": key_findings,
            "entities": entities,
            "relationships": relationships,
            "risk_indicators": risk_indicators,
            "confidence_score": confidence_score,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "is_demo": True
        }

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        extracted = []
        seen = set()

        # Regex entities
        for etype, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            for m in set(matches):
                val = m if isinstance(m, str) else m[0]
                if val not in seen:
                    seen.add(val)
                    extracted.append({
                        "name": val,
                        "type": "Digital Entity" if etype in ["IP_ADDRESS", "CRYPTO_WALLET", "EMAIL"] else "Object",
                        "confidence": 0.96,
                        "subtype": etype
                    })

        # Common intelligence entities (demo NER dictionary + pattern matching)
        known_orgs = ["Aegis Global", "Vanguard Financial", "Apex Cybertech", "Titan Syndicate", "Interpol", "FSB", "ShadowCorp", "Nexus Logistics"]
        known_people = ["Viktor Reznov", "Elena Rostova", "Marcus Vance", "Dr. Aris Thorne", "Sarah Jenkins", "Dmitri Volkov", "Chen Wei"]
        known_locs = ["Zurich", "Singapore", "Cyprus", "Geneva", "Panama City", "Dubai", "Hong Kong", "London", "Moscow"]

        for org in known_orgs:
            if org.lower() in text.lower() and org not in seen:
                seen.add(org)
                extracted.append({"name": org, "type": "Organization", "confidence": 0.92})

        for person in known_people:
            if person.lower() in text.lower() and person not in seen:
                seen.add(person)
                extracted.append({"name": person, "type": "Person", "confidence": 0.94})

        for loc in known_locs:
            if loc.lower() in text.lower() and loc not in seen:
                seen.add(loc)
                extracted.append({"name": loc, "type": "Location", "confidence": 0.90})

        # Capitalized multi-word fallback for names/orgs
        cap_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        for phrase in cap_phrases:
            if phrase not in seen and len(phrase.split()) <= 3 and phrase not in known_orgs and phrase not in known_people:
                seen.add(phrase)
                extracted.append({"name": phrase, "type": "Person" if len(phrase.split()) == 2 else "Organization", "confidence": 0.82})

        return extracted[:10]

    def _detect_risk_indicators(self, text: str) -> List[Dict[str, Any]]:
        indicators = []
        text_lower = text.lower()

        for level, keywords in self.RISK_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    indicators.append({
                        "indicator": kw.title(),
                        "severity": level,
                        "description": f"Identified suspicious pattern matching '{kw}' in intelligence text.",
                        "score": 85 if level == "CRITICAL" else (70 if level == "HIGH" else 45)
                    })

        if not indicators:
            indicators.append({
                "indicator": "Standard Activity Pattern",
                "severity": "LOW",
                "description": "No immediate critical risk indicators detected in target text.",
                "score": 15
            })

        return indicators

    def _extract_relationships(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        rels = []
        if len(entities) < 2:
            return rels

        # Link pairs of entities found in text
        for i in range(len(entities) - 1):
            e1 = entities[i]
            e2 = entities[i+1]
            rel_type = "associated_with"
            if e1["type"] == "Person" and e2["type"] == "Organization":
                rel_type = "works_for"
            elif e1["type"] == "Person" and e2["type"] == "Digital Entity":
                rel_type = "owns"
            elif e1["type"] == "Organization" and e2["type"] == "Location":
                rel_type = "located_at"
            elif e1["type"] == "Person" and e2["type"] == "Person":
                rel_type = "collaborates_with"

            rels.append({
                "source": e1["name"],
                "target": e2["name"],
                "relation": rel_type,
                "confidence": round((e1.get("confidence", 0.9) + e2.get("confidence", 0.9)) / 2, 2)
            })

        return rels

    def _generate_key_findings(self, text: str, entities: List[Dict[str, Any]], risk_indicators: List[Dict[str, Any]]) -> List[str]:
        findings = [
            f"Extracted {len(entities)} high-confidence entities across {len(set(e['type'] for e in entities))} classifications.",
            f"Identified {len(risk_indicators)} threat/risk indicators in intelligence context."
        ]

        crit_high = [r for r in risk_indicators if r["severity"] in ["CRITICAL", "HIGH"]]
        if crit_high:
            findings.append(f"Critical flag detected: {crit_high[0]['indicator']} ({crit_high[0]['description']}).")
        else:
            findings.append("No critical severity red flags detected in analyzed text sample.")

        crypto_ips = [e for e in entities if e["type"] == "Digital Entity"]
        if crypto_ips:
            findings.append(f"Digital intelligence markers isolated: {', '.join([c['name'] for c in crypto_ips[:3]])}.")

        return findings

    def _generate_summary(self, query: str, case_title: str, entities: List[Dict[str, Any]], risk_indicators: List[Dict[str, Any]]) -> str:
        case_str = f" related to case '{case_title}'" if case_title else ""
        entity_names = ", ".join([e["name"] for e in entities[:3]]) if entities else "specified terms"
        top_risk = risk_indicators[0]["indicator"] if risk_indicators else "Low Risk"
        
        return (
            f"Intelligence assessment conducted on query '{query[:60]}...'{case_str}. "
            f"Key entities identified include {entity_names}. Primary risk vector evaluated as '{top_risk}'. "
            f"Local NLP engine processed input with high pattern matching reliability."
        )

    def _generate_recommendations(self, risk_indicators: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> List[str]:
        recs = [
            "Cross-reference extracted entities against active threat databases and OSINT registries.",
            "Verify digital wallet address and IP routing paths with specialized cyber intelligence tools."
        ]
        if any(r["severity"] in ["CRITICAL", "HIGH"] for r in risk_indicators):
            recs.append("Escalate case priority to HIGH/CRITICAL and initiate formal surveillance review.")
        else:
            recs.append("Maintain routine monitoring of associated subject profiles and periodic updates.")
        return recs

    def _generate_next_steps(self, entities: List[Dict[str, Any]], risk_indicators: List[Dict[str, Any]]) -> List[str]:
        return [
            "Issue subpoenas for financial transactions associated with primary organizations.",
            "Schedule interview with key person of interest.",
            "Log evidence item into CRIMSON vault with cryptographic proof hash."
        ]

local_ai_engine = LocalAIEngine()
