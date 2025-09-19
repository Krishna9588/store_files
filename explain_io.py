import google.generativeai as genai
import json
from itertools import cycle

# Gemini API KEYs ----------------------------------------------
# API_KEYS = ["AIzaSyCn7YEam6Vw5ToVQTJ6mRZogMwM3GwZAHU",
#             "AIzaSyB8xmrgn87XTBr1_rxim0huAubOBDBvtD4",
#             "AIzaSyB3sYWowbpnFO5fnC0TnJE-hxxlcMmvwIs",
#             "AIzaSyCgXDFPLkH9geHJb13WrbbstKd5G3iYZc0"
#             ]

#API_KEYS = ["AIzaSyAVhxbExANJhkc-6NfYdkmYwc3XzodPxOk", # New Krishna
#            "AIzaSyCYSq8CHApwzZiHzjw23uquyeq4TmBEawk", # Techno
#            "AIzaSyA6iO5xA8ZGfbJmMYKBU78U5vaCf8qYMVk", # Techno
            #"AIzaSyA2-ioWAoq70rnWqwjPTs6M_lWVkCC9Ue4", # Techno
         #   #"AIzaSyA118O5aiXR0fmrOpeRZDXF7PGsLmD8TTk", # Techno
          #  "AIzaSyC0VRuOg3X8Ormud2NZWe9I4-cQZ55U9b8", # Techno
          #  "AIzaSyBj3fr4Ekp4j01jE6xg4fAGwBtoXC721M0"  # Techno
          #  ]

API_KEYS = [
            "AIzaSyD7wXj4vJ9CejTlRSFrR9MfOR7R7Zk5Jn4",
            "AIzaSyD1tz5JH2855URNIYgh4Y8EhIS9JNqQl1g",
            "AIzaSyAlfQ0UeUHFVfpehf-2CcuXdwwscgtXMOU",
            "AIzaSyDfGbkwGom5bpWUIbLwkyId5-pO5_jRBY8",
            "AIzaSyCHMSqnXtUx0MKAZA0Xb4ozuKFSo9MS79M",
            "AIzaSyD-nv2kYjaDf1TAC2guNbEJfiflyE-Jv-o",
            "AIzaSyD186x0vnpxrnt6TcV5c-FCZRhUSt-5ptw",
            "AIzaSyDSQnamGR4d99MlGebQRYUmjz_DyYaFQzU"
            ]

# API_KEYS = [
#             # "AIzaSyARCI7VYHI4GLGAplUPQvFXmFFfGnz9n2Q",
#             # "AIzaSyCfpSlbj6wFXCnSxtJZ-vDOs5bWVIzK1Yo",
#             # "AIzaSyAJXz-IunLmn0RMGDRywLaR7jI-29ofn80",
#             "AIzaSyDGwMZJ56GRd7KV-j2k7wVDVT-w7BjR0cs",
#             # "AIzaSyDzYexW4h90nkhpTb8Bk8zijza62JT_xoo",
#             "AIzaSyBpSdOSNHAhLi_HdsCEbCH8u4jSuQEo4V0",
#             ]
# -----------------------------------------------------------

target = [
    # Technology usage
    "use", "using", "used", "adopted", "deployed", "implemented",
    "powered by", "enabled by", "built with", "runs on", "based on",
    "utilized", "developed with", "hosted on", "migrated to",
    "relied on", "incorporated", "embedded", "integrated", "engineered with",
    "constructed with", "configured with", "operates on", "compiled with",
    "compiled for", "written in", "coded in", "developed using",

    # Partnerships and integrations
    "partner", "partnership", "strategic partner", "collaborated with",
    "integrated with", "alliance", "reseller", "technology partner",
    "solution partner", "OEM", "channel partner", "vendor",
    "works with", "cooperate with", "joint venture", "consortium",
    "affiliate", "associated with", "in collaboration with",
    "teamed up with", "engaged with", "connected with",

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

key_cycler = cycle(API_KEYS)

def explain(chunk_text: str, keyword_tech: str, company_name: str,page_url: str, usage_indicators: list = None) -> dict:
    if usage_indicators is None:
        usage_indicators = target
    # this will kep my code to work with older and new main function together.
    indicators_str = ", ".join([f"'{ind}'" for ind in usage_indicators])


    # Prompt 4
    '''
    prompt = f"""
    You are an objective and meticulous technology analyst. Your primary task is to make a balanced and evidence-based judgment to determine if **{company_name}** is actively and demonstrably using, supporting, developing, or deploying the technology or concept of **'{keyword_tech}'**, based *only* on the provided text.

    Your goal is to weigh the positive evidence against the strict exclusion rules to make a final, justifiable determination.

    ---
    ### **1. Positive Indicators (What constitutes a 'Yes')**

    The answer should be **true** if you find clear, direct evidence of the company's operational use. Strong evidence includes:

    * **Direct Company Statements:** The text explicitly states usage in the first person (e.g., "Our platform is built on...", "We have deployed...", "We partner with...").
    * **Technical Content & Case Studies:** A technical blog post, success story, or case study from a named internal team (e.g., "our engineering team," "the WebClaims division") that details the implementation or operational use of the technology **is considered strong evidence**.
    * **Job Postings:** A job description from the company for an internal, operational role that requires hands-on skills in the technology.
    * **General Indicators:** The text contains strong contextual keywords related to implementation, such as: {indicators_str}.
    * **Integration & Compatibility:** If a product from {company_name} is described as being 'integrated with' or 'compatible with' {keyword_tech}, this is a strong indicator of usage.

    ---
    ### **2. Exclusion Rules (What forces a 'No')**

    The answer must be **false** if the primary evidence falls into any of these categories, even if the keyword is present:

    * **CRITICAL - Context Mismatch:** The keyword is used but refers to the wrong concept.
        * **Acronyms:** An acronym like 'AWS' is used but the text defines it as something else (e.g., "Alliance for Water Stewardship") or the context is non-technical.
        * **Common Words:** A word like 'Glue' refers to a physical substance (e.g., 'chemical glue') and not the specific technology service.
    * **CRITICAL - Educational or Certification Use:** The company's main interaction with the technology is offering training, courses, university programs, or certifications *on* it. This is not operational use.
    * **No Direct Action by Company:**
        * **Third-Parties:** The text describes a customer, partner, or other organization using the technology.
        * **Individual Skills:** The text only refers to an individual employee's personal resume, skills, or certifications.
        * **Speculation:** The text uses conditional or future-looking language (e.g., "might use," "could explore," "plans to adopt").

    ---
    ### **Analysis Task**

    **Company:** `{company_name}`
    **Technology:** `{keyword_tech}`
    **Text to Analyze:** `{chunk_text}`

    ---

    Provide your answer in a JSON format with two keys: "uses_tech" and "explanation".

    1.  `uses_tech`: A boolean (true/false) value based on a balanced application of the rules above.
    2.  `explanation`: A single-line, JSON-safe string that justifies the answer. It must quote the key evidence and explicitly name the primary rule that was applied. Example for a false answer: `"The text mentions 'AWS Education Research Grant' which fails the 'CRITICAL - Educational or Certification Use' rule because it describes academic activity, not operational use."` Example for a true answer: `"The text states 'our entire platform is built on AWS' which meets the 'Direct Company Statements' positive indicator."`
    
    """
    '''

    # Prompt 1
    # '''
    prompt = f"""
    Analyze the following text about {company_name} (company name might not be well structured) to determine if it indicates that {company_name} uses, supports, develops, deploys, partners with, or is actively involved with the technology or concept of '{keyword_tech}'.
    Note: If the technology is mentioned in Job description by that company means they use that technology.
    Note: The company name might not always be explicitly mentioned, could be misspelled, have irregular spacing, or be mixed with unrelated tokens or unknown words. Focus on contextual clues to assess technology usage.
    **Important Guidance:**
    To help you assess company involvement accurately, compare the text against the following key phrases. These are indicators of meaningful involvement with "{keyword_tech}":
    Indications of usage often include words or phrases like: {indicators_str}.
    * Integration & Compatibility: If a product from {company_name} is described as being 'integrated with' or 'compatible with' {keyword_tech}, this is a strong indicator of usage.

    Do not assume involvement unless there is a clear match or a strong semantic equivalent to one of these phrases.
    However, also consider semantic equivalents and contextual implications beyond just these specific words as exceptions are possible and we can't include each indicator separately.

    If the text (chunk) discusses another company (e.g., mentions companies like Wipro, IBM, Infosys, etc.) using or developing the technology, and there is no clear evidence that the company "{company_name}" is directly involved in those activities, then the answer should be **false**.
    Even if "{company_name}" is the host of the content (such as a blog, case study, or article), do **not** assume it is using or endorsing the technology unless explicitly stated.
    Always cross-check if the **actions are attributed directly to {company_name}** and not a third-party company.

    ---
    Text about {company_name}:
    {chunk_text}
    ---

    Provide your answer in a JSON format with two keys:
    1.  "uses_tech": a boolean (true/false) indicating if '{keyword_tech}' is used or involved by the company based on the text and the above guidance.
    2.  "explanation": a brief reason for your answer, quoting relevant parts of the text if possible.
    """
    # '''


    try:
        current_key = next(key_cycler)         # Key Rotation
        print(f"|==▶ Using API Key ending in: ...{current_key[-4:]}")

        # Call Gemini API
        genai.configure(api_key=current_key)

        # models log
        # model = genai.GenerativeModel('gemini-1.5-flash')
        model = genai.GenerativeModel('gemini-2.0-flash-lite-001')

        # response = model.generate_content(prompt)
        response = model.generate_content(
            prompt,
            request_options={"timeout": 300}
        )
        # Clean and parse JSON response
        raw_text = response.text.strip()
        cleaned_text = raw_text.replace("```json\n", "").replace("\n```", "")
        parsed_response = json.loads(cleaned_text)

        ut = parsed_response.get("uses_tech", False)
        exp = parsed_response.get("explanation", "No explanation from LLM.")

        # return {
        #     "uses_tech": parsed_response.get("uses_tech", False),
        #     "explanation": parsed_response.get("explanation", "No explanation from LLM.")
        # }
        temp = str(chunk_text)
        print(f"|===▶ Length:{len(temp)} | Context: {temp[2:101]}")

        return {
            "uses_tech": ut,
            "explanation": exp
        }
    except Exception as e:
        print(f"Error calling Gemini API or parsing response for keyword '{keyword_tech}': {e}")
        usae_raw = str(raw_text[25:30])
        if usae_raw == "true,":
            exe = True
        else:
            exe = False
        return {"uses_tech": exe, "explanation": f"API or parsing error: {e}"}