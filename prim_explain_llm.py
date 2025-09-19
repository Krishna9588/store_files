import google.generativeai as genai
import os
from google import genai
from google.genai import types
import json
import re
from itertools import cycle
import threading

# Gemini API KEYs ----------------------------------------------
API_KEYS = ["AIzaSyAeStmlXLi_u2kA_pQiInQBiZVBAM3HRqA"]
# Create a thread-safe lock for accessing the API keys and models
key_lock = threading.Lock()
key_cycler = cycle(API_KEYS)
# --------------------------------------------------------------

target = [
    # Technology usage
    "use", "using", "used", "adopted", "deployed", "implemented",
    "powered by", "enabled by", "built with", "runs on", "based on",
    "utilized", "developed with", "hosted on", "migrated to",
    "relied on", "incorporated", "embedded", "integrated", "engineered with",
    "constructed with", "configured with", "operates on", "compiled with",
    "compiled for", "written in", "coded in", "developed using", "products", "product",

    # Partnerships and integrations
    "partner", "partnership", "strategic partner", "collaborated with", "solution",
    "integrated with", "alliance", "reseller", "technology partner", "solutions",
    "solution partner", "OEM", "channel partner", "vendor", "offering", "applications",
    "works with", "cooperate with", "joint venture", "consortium", "application",
    "affiliate", "associated with", "in collaboration with", "case-studies", "studies",
    "teamed up with", "engaged with", "connected with", "case studies",

    # Hiring indicators
    "hiring", "job posting", "career opportunity", "recruiting",
    "skills required", "experience with", "desired skills", "looking for",
    "join our team", "open roles", "vacancy", "apply", "certified in",
    "seeking", "in search of", "requirement", "mandatory skills",
    "preferred skills", "competency in", "proficiency in", "expertise in",
    "qualified in", "trained in", "hands-on experience",

    # Spending and investment
    "investment", "budget", "procurement", "IT spend", "contract with",
    "financial commitment", "spending", "cost", "deal", "payment to", "funding",
    "allocated", "invested", "purchased", "acquired", "licensed", "subscription",
    "retained", "engaged service", "outsourced to", "sponsored",
    "capital expenditure", "CAPEX", "operational expenditure", "OPEX",

    # Additional technical indicators
    "migration", "upgrade", "refactor", "replatform", "containerized",
    "orchestrated", "automated", "scaled", "optimized", "monitored",
    "maintained", "supported", "configured", "customized", "extended",
    "enhanced", "augmented", "modernized", "transformed", "digitalized"
]

model = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite"
]

model_cycler = cycle(model)


def explain(chunk_text: str, keyword_tech: str, company_name: str, page_url: str,usage_indicators: list = None) -> dict:
    if usage_indicators is None:
        usage_indicators = target
    indicators_str = " ".join([f"'{ind}'" for ind in usage_indicators])

    prompt = f"""
    You are an objective, meticulous technology analyst. Your task: decide using **only** the supplied URL and text whether **{company_name}** is actively and demonstrably using, supporting, developing, working with, or deploying **{keyword_tech}**.
                
    CONTEXT (do not use external sources)
    - URL: "{page_url}" : Use this for reference  and context.
    - Text to analyze: the string provided as `{chunk_text}`
    - Indicator keywords (if any): {indicators_str}
    
    0. Goal
    Weigh positive evidence against the exclusion rules and produce a justified decision.
    
    1. Positive indicators (evidence → return true)
    - **Direct company statements** in first person (e.g., "Our platform is built on...").
    - **Technical content or case studies** from internal teams describing implementation or operations.
    - **Job postings** for internal operational roles that require hands-on skills with the technology.
    - **Integration/compatibility** claims (e.g., "integrates with X", "supports Y").
    - **Strong implementation keywords**: **Refer Indicator keywords**
    
    2. Exclusion rules (if primary evidence matches any → return false)
    - **Context mismatch:** keyword refers to a different concept (acronyms used differently, common words used non-technically).
    - **Educational/certification activity:** pages describing courses, training, or academic work about the technology (not operational use).
    - **No direct company action:** references exclusively to third parties, customers, partners, or individual resumes.
    - **Speculation or future plans:** conditional/future language ("might", "plans to", "could explore").
    
    3. Required output (JSON only)
    Return exactly one JSON object and nothing else. Fields:
    - `"uses_tech"`: boolean — true if the company demonstrably uses the technology per the rules; otherwise false.
    - `"explanation"`: single-line JSON-safe string (no newline characters). It must:
      - Quote the exact supporting excerpt from the supplied text (wrap the excerpt in double quotes).
      - Explicitly name the primary rule applied (one item from section 1 or 2).
      - Be concise and self-contained. And Explain how you got to this conclusion. 
    
    Examples:
    {{"uses_tech": true, "explanation": "The text states \"our platform runs on Kubernetes\" — matches 'Direct company statements' positive indicator."}}
    {{"uses_tech": false, "explanation": "The page mentions \"Kubernetes course\" which fits 'Educational/certification activity' exclusion rule (training, not operational use)." }}
    
    IMPORTANT: Only output the JSON object. Do not add any commentary, analysis, or extra text.
    """

    try:
        with key_lock:
            current_key = next(key_cycler)  # Key Rotation
            current_model = next(model_cycler)
        print(f"|==▶ Using API Key ending in: ..{current_key[-4:]} | current model {current_model}")

        # -------------------------

        # genai.configure(api_key=current_key)
        # model = genai.GenerativeModel(current_model)

        client = genai.Client(
            api_key=current_key,
        )
        model = current_model
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
                request_options={"timeout": 300} # this line might cause an error.
            ),
        ]
        tools = [
            types.Tool(url_context=types.UrlContext()),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=0.2,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
            tools=tools,
        )

        raw_text =  client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,)

        json_str = ""
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)

        # -------------------------

        # -------------------------

        if match:
            json_str = match.group(0)
            try:
                parsed_response = json.loads(json_str, strict=False)
            except json.JSONDecodeError as json_err:
                print(f"|--- JSON PARSING FAILED ---")
                print(f"| Error: {json_err.msg}")
                print(f"| At line {json_err.lineno}, column {json_err.colno} (char {json_err.pos})")
                context_window = 30
                start = max(0, json_err.pos - context_window)
                end = min(len(json_str), json_err.pos + context_window)
                print(f"| Problematic JSON snippet: ...{json_str[start:end]} ...")
                print(f"|--------------------------")

                raise json_err
        else:
            # If no JSON object is found, raise an error to be caught by the main `except` block.
            raise json.JSONDecodeError("No valid JSON object found in the model's response.", raw_text, 0)


        if parsed_response == "true":
            temp = str(chunk_text)
            print(f"|===▶ Out Context (E): {temp[0:100]}")
            return {
                "uses_tech": parsed_response.get("uses_tech", False),
                "explanation": parsed_response.get("explanation", "No explanation from LLM."),
                "push_context": chunk_text
            }
        else:
            return {
                "uses_tech": parsed_response.get("uses_tech", False),
                "explanation": "No explanation from LLM.",
                "push_context": (chunk_text, "No context found.")
            }

    except Exception as e:
        raw_text = response.text.strip()
        if not json_str:
            json_str = str(raw_text)
        usae_raw = str(raw_text[25:30])
        if usae_raw == "true,":
            exe = True
        else:
            exe = False
        return {"uses_tech": exe, "explanation": f"Error. Raw response part: \n {str(json_str)} \n"}