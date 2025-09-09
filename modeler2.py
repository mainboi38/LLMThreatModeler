from openai import OpenAI
import gradio as gr
from dotenv import load_dotenv
import os
import re
from datetime import datetime

# Load env vars
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_threat_model(system_description):
    # Ask GPT for STRIDE + Mermaid
    prompt = f"""
You are a senior security architect conducting a comprehensive STRIDE threat model analysis. Your goal is to provide actionable security insights for production system deployment.

SYSTEM TO ANALYZE: {system_description}

## Phase 1: System Decomposition & Asset Classification
1. **Component Analysis**: Break down the system into discrete components including:
   - Network boundaries and trust zones  
   - Data stores and processing elements
   - Authentication/authorization mechanisms
   - External interfaces and APIs
   - Third-party integrations and dependencies

2. **Asset Inventory**: For each component, identify:
   - **Data Classification**: Sensitivity level (Public, Internal, Confidential, Restricted)
   - **Business Criticality**: Impact rating (Low, Medium, High, Critical)
   - **Trust Boundaries**: Where data crosses security perimeters
   - **Attack Surface**: External interfaces and entry points

## Phase 2: STRIDE Threat Analysis
For each component, systematically evaluate threats using expanded STRIDE categories:

### **Spoofing (Identity)**
- Authentication bypass mechanisms
- Impersonation attacks (users, services, systems)
- Certificate/token forgery
- Session hijacking vectors

### **Tampering (Integrity)**  
- Data modification in transit and at rest
- Code injection attacks (SQL, XSS, command injection)
- Configuration tampering
- Supply chain compromise

### **Repudiation (Non-repudiation)**
- Insufficient audit logging
- Log tampering or deletion
- Weak digital signatures
- Timeline manipulation

### **Information Disclosure (Confidentiality)**
- Data leakage through side channels
- Unauthorized access to sensitive data
- Metadata exposure
- Error message information leaks

### **Denial of Service (Availability)**
- Resource exhaustion attacks
- Service flooding and amplification
- Single points of failure
- Cascade failure scenarios

### **Elevation of Privilege (Authorization)**
- Privilege escalation vectors
- Authorization bypass
- Confused deputy attacks
- Admin interface exploitation

## Phase 3: Risk Assessment & Prioritization
For each identified threat, evaluate:
- **Likelihood**: Probability of exploitation (1-5 scale)
- **Impact**: Business consequence if exploited (1-5 scale)  
- **Risk Score**: Likelihood × Impact
- **Exploitability**: Required attacker skill/resources
- **Current Controls**: Existing mitigations in place

## Phase 4: Mitigation Strategy
Recommend security controls using defense-in-depth principles:
- **Preventive**: Controls that block attacks
- **Detective**: Controls that identify attacks  
- **Corrective**: Controls that respond to attacks
- **Compensating**: Alternative controls when primary controls aren't feasible

## Phase 5: Visual Threat Model
Create a comprehensive Mermaid diagram with the following structure:

```mermaid
graph TB
    subgraph "Trust Boundary 1"
        Component1[Component Name<br/>Risk: HIGH]
    end
    
    subgraph "STRIDE Threats"
        S[🎭 Spoofing<br/>Identity Attacks]
        T[🔧 Tampering<br/>Integrity Attacks]  
        R[❌ Repudiation<br/>Audit Attacks]
        I[🔍 Information Disclosure<br/>Confidentiality Attacks]
        D[💥 Denial of Service<br/>Availability Attacks]
        E[⬆️ Elevation of Privilege<br/>Authorization Attacks]
    end
    
    Component1 -->|Threat Vector| S
    Component1 -->|Mitigation: TLS 1.3| T
    
    classDef highRisk fill:#ffcdd2,stroke:#d32f2f,stroke-width:3px
    classDef mediumRisk fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef lowRisk fill:#e8f5e8,stroke:#388e3c,stroke-width:1px
    classDef threat fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**Diagram Requirements:**
- Use trust boundaries (subgraphs) to show security perimeters
- Color-code components by risk level (Red=High, Orange=Medium, Green=Low)
- Include threat icons and descriptions for clarity
- Show both threats AND existing mitigations on connections
- Use meaningful component names with risk indicators

## Phase 6: Executive Summary
Provide a concise summary including:
- **Top 5 Critical Risks** with business impact
- **Recommended Priority Actions** with timeline
- **Resource Requirements** for implementation
- **Residual Risk** after mitigation implementation

## Deliverable Format
Structure your response as:
1. **Executive Summary** (2-3 paragraphs)
2. **Component Analysis Table** (Component | Assets | Trust Level | Attack Surface)
3. **Threat Analysis Matrix** (Component | STRIDE Threats | Risk Score | Mitigation)
4. **Visual Threat Model** (Mermaid diagram)
5. **Remediation Roadmap** (Priority | Action | Timeline | Owner)

Focus on **production readiness** - prioritize threats that could impact business operations, customer data, or regulatory compliance. Assume the system will face real-world attacks and needs enterprise-grade security controls.
System:
\"\"\"
{system_description}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    output = response.choices[0].message.content

    # Extract Mermaid block
    mermaid_match = re.search(r"```mermaid\n(.*?)```", output, re.DOTALL)
    mermaid_code = mermaid_match.group(1).strip() if mermaid_match else ""

    # Clean up threat analysis (remove Mermaid block)
    threat_analysis = re.sub(r"```mermaid\n.*?```", "", output, flags=re.DOTALL).strip()

    # Prepare markdown content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/threat_model_{timestamp}.md"
    os.makedirs("outputs", exist_ok=True)

    md_content = f"# STRIDE Threat Model\n\n**Input:**\n```\n{system_description}\n```\n\n## Analysis\n\n{threat_analysis}\n\n## Mermaid Diagram\n```mermaid\n{mermaid_code}\n```"

    with open(filename, "w") as f:
        f.write(md_content)

    return f"Markdown file saved: {filename}"

iface = gr.Interface(
    fn=generate_threat_model,
    inputs=gr.Textbox(lines=5, placeholder="Describe your system architecture..."),
    outputs="text",
    title="STRIDE Threat Model Generator",
    description="Enter a system description. The AI will generate a threat model and save it as a Markdown file with Mermaid diagram."
)

iface.launch()
