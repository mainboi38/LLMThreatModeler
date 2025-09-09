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
You're a security engineer helping to perform a threat model using the STRIDE framework.

1. Break down the following system into key components.
2. Identify potential threats using STRIDE.
3. Summarize the threats by component.
4. Then, draw a Mermaid diagram using 'graph LR' for a horizontal layout.

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
