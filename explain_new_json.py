import google.generativeai as genai
import json
import re
from itertools import cycle
import threading

# Gemini API KEYs ----------------------------------------------

# API_KEYS = ["AIzaSyCn7YEam6Vw5ToVQTJ6mRZogMwM3GwZAHU",
#             "AIzaSyB8xmrgn87XTBr1_rxim0huAubOBDBvtD4",
#             "AIzaSyB3sYWowbpnFO5fnC0TnJE-hxxlcMmvwIs",
#             "AIzaSyCgXDFPLkH9geHJb13WrbbstKd5G3iYZc0"
#             ]
# API_KEYS = [
#             "AIzaSyD7wXj4vJ9CejTlRSFrR9MfOR7R7Zk5Jn4",
#             "AIzaSyD1tz5JH2855URNIYgh4Y8EhIS9JNqQl1g",
            # "AIzaSyAlfQ0UeUHFVfpehf-2CcuXdwwscgtXMOU",
            # "AIzaSyDfGbkwGom5bpWUIbLwkyId5-pO5_jRBY8",
            # "AIzaSyCHMSqnXtUx0MKAZA0Xb4ozuKFSo9MS79M",
            # "AIzaSyD-nv2kYjaDf1TAC2guNbEJfiflyE-Jv-o",
            # "AIzaSyD186x0vnpxrnt6TcV5c-FCZRhUSt-5ptw",
            # "AIzaSyDSQnamGR4d99MlGebQRYUmjz_DyYaFQzU"
            # ]

API_KEYS = ["AIzaSyAeStmlXLi_u2kA_pQiInQBiZVBAM3HRqA", # Vedisha - NEW_temp
            "AIzaSyDDYP4NIL28a19fupyUtL_oOvG9_d0zaA4", # Krishna_P New
            "AIzaSyB2CMRJNrUBYn_Ow_fy461hKr5xhX6U6po", # Vedisha_P - NEW
            "AIzaSyARqV2CdLY6RxX5BMAhtpvWXokEl3Jj0Vo", # Swapnil
            "AIzaSyARqV2CdLY6RxX5BMAhtpvWXokEl3Jj0Vo", # Techno
            "AIzaSyD1tz5JH2855URNIYgh4Y8EhIS9JNqQl1g",
            "AIzaSyAlfQ0UeUHFVfpehf-2CcuXdwwscgtXMOU",
            "AIzaSyDfGbkwGom5bpWUIbLwkyId5-pO5_jRBY8",
            "AIzaSyCHMSqnXtUx0MKAZA0Xb4ozuKFSo9MS79M",
            "AIzaSyD-nv2kYjaDf1TAC2guNbEJfiflyE-Jv-o",
            "AIzaSyD186x0vnpxrnt6TcV5c-FCZRhUSt-5ptw",
            "AIzaSyDSQnamGR4d99MlGebQRYUmjz_DyYaFQzU"
            ]

# API_KEYS = [
#
# "AIzaSyAwoV3Or8n0eklTN8tXxRU70vF5fJUvToQ",
# "AIzaSyCfpSlbj6wFXCnSxtJZ-vDOs5bWVIzK1Yo",
# "AIzaSyDZRkxEc1kRuzklmIKPO9WFyedADVFMXUA",
# "AIzaSyC4-HTk46kn13rIuN7cSCGdcx0UHkN0py0",
# "AIzaSyDanDops2Iv6KL1mBoEqXIKCNpYh5Tsc0U"
#             ]
#
# API_KEYS = [
#             "AIzaSyAtLE38GARhnoxQHF3DLmOOI1toX90o2lY"
#             ]
# -----------------------------------------------------------

# Create a thread-safe lock for accessing the API keys and models
key_lock = threading.Lock()
key_cycler = cycle(API_KEYS)

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


def explain(chunk_text: str, keyword_tech: str, company_name: str, page_url: str,
            usage_indicators: list = None) -> dict:
    if usage_indicators is None:
        usage_indicators = target
    # this will kep my code to work with older and new main function together.
    indicators_str = " ".join([f"'{ind}'" for ind in usage_indicators])

    if len(str(chunk_text)) > 100:
        print(f"|=▶ Prompt 1 Context Length:{len(str(chunk_text))}, URL to analysis only. ")
        a = 1
        """
        prompt = f'''
        You are an objective and meticulous technology analyst. Your primary task is to make a balanced and evidence-based judgment to determine if **{company_name}** is actively and demonstrably using, supporting, developing, or deploying the technology or concept of **'{keyword_tech}'**, based *only* on the provided text and URL context.

        ### **0: "{page_url}" Your goal is to weigh the positive evidence against the strict exclusion rules to make a final justifiable determination.

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
        **URL:** `{page_url}`
        **Text to Analyze:** `{chunk_text}`

        ---

        Provide your answer in a JSON format with two keys: "uses_tech" and "explanation".
        
        1.  `uses_tech`: A boolean (true/false) value based on a balanced application of the rules above.
        2.  `explanation`: A single-line, JSON-safe string that justifies the answer. It must quote the key evidence and explicitly name the primary rule that was applied. Example for a false answer: `"The text mentions 'AWS Education Research Grant' which fails the 'CRITICAL - Educational or Certification Use' rule because it describes academic activity, not operational use."` Example for a true answer: `"The text states 'our entire platform is built on AWS' which meets the 'Direct Company Statements' positive indicator."`
        
        ---
        Note: Only output the JSON object. Do not include any additional text, commentary, or formatting.

        '''
        """
        prompt = f"""
        You are a specialized text analysis AI. Your task is to analyze a provided text from a company's website and determine the relationship between the company and a specific keyword. You must base your conclusion STRICTLY on the text provided and not use any external knowledge.

        **Inputs:**

        * **Company Name:** "{company_name}"
        * **Keyword:** "{keyword_tech}"
        * **Context:**
        " {chunk_text} "

        **Instructions:**

        1.  Read the **Context** carefully.
        2.  Identify all mentions and discussions related to the **Keyword**.
        3.  Analyze how the **Keyword** is framed in relation to the **Company Name**.
        4.  Formulate a conclusion based exclusively on the information within the **Context**.
        5.  Generate a response in a single, valid JSON object format.

        **Output Constraints:**

        * The output MUST be a single, valid JSON object.
        * Do not include any text, explanation, or markdown formatting before or after the JSON object.
        * The JSON object must contain exactly two keys: `"Explanation"` and `"relationship"`.

        **Key Definitions:**

        * `"uses_tech"`: (String) A short, categorical label for the relationship. Choose from one of the following or a similar concise term: 'Core Service', 'Product Feature', 'Technology Used', 'Company Value', 'Industry Standard', 'Partner', 'Case Study Subject', 'Blog Topic', 'Target Audience'.
        * `"Explanation"`: (String) A concise, 2-3 sentence summary describing how the company uses or refers to the keyword.
        
        **Begin Analysis and Generate JSON Output.**

        """
        '''
        prompt_temp = f""" 
        You are an objective and meticulous technology analyst. Your task is to make a definitive, evidence-based judgment on whether **{company_name}** is actively using or developing the technology **'{keyword_tech}'**.
            ---
            ### **Context and Rules**
            
            You must make your final determination *solely* on the provided text and URL. The output must be a single boolean (`true`/`false`) and a concise, justified explanation.
            
            ---
            ### **1. Positive Indicators (Evidence for 'True')**
            
            A 'true' determination requires finding clear, direct evidence of the company's operational use. Strong evidence includes:
            
            * **Direct Company Statements:** Explicit first-person statements (e.g., "Our platform is built on...", "We have deployed...").
            * **Operational Content:** Technical blog posts, case studies, or documentation from internal teams (e.g., "our engineering team") that detail the implementation or operational use.
            * **Job Postings:** Job descriptions for internal roles that require hands-on skills in the technology.
            * **Integration:** Company products or services described as "integrated with" or "compatible with" the technology.
            
            ---
            ### **2. Exclusion Rules (Conditions for 'False')**
            
            A 'false' determination is required if the primary evidence falls into any of these categories:
            
            * **Context Mismatch:** The keyword is used but refers to a different concept (e.g., a common acronym like 'AWS' is defined differently in the text).
            * **Educational or Certification Use:** The company's main interaction is offering training, courses, or certifications *about* the technology, not using it operationally.
            * **No Direct Company Action:** The text describes a third-party (customer, partner) using the technology, not the company itself.
            * **Speculation:** The text uses conditional or future-looking language (e.g., "might use," "plans to adopt").
            
            ---
            ### **Analysis Task**
            
            **Company:** `{company_name}`
            **Technology:** `{keyword_tech}`
            **URL:** `{page_url}`
            **Text to Analyze:** `{chunk_text}`
            
            Provide your answer in a JSON format with two keys: `uses_tech` and `explanation`. The explanation must quote key evidence and name the primary rule applied.
            
            ---
            **Example True Output:**
            `{ "uses_tech": true, "explanation": "The text states 'our entire platform is built on AWS' which meets the 'Direct Company Statements' positive indicator." }`
            
            **Example False Output:**
            `{ "uses_tech": false, "explanation": "The text mentions 'AWS Education Research Grant' which fails the 'Educational or Certification Use' rule because it describes academic activity, not operational use." }`

        """
'''
    else:
        # {str(url_context)} we use this in line 4 for passing page_url with clear meaning
        prompt = f'''
        You are an expert objective and meticulous Technology Analyst AI. Your mission is to perform an evidence-based analysis to determine if **{company_name}** is actively and demonstrably using, developing, or deploying the technology **'{keyword_tech}'**.

        You must follow a strict conditional process to arrive at your conclusion.
        ---
        ### **Part 0: "{page_url}" Your goal is to weigh the positive evidence against the strict exclusion rules to make a final justifiable determination.

        ### **Part 1: Context Selection & Fallback Mechanism**

        This is your first and most critical step. You must determine which text to analyze.

        1.  **Check Initial Context:** First examine the provided `Text to Analyze`.
            * If the text is present and meaningful you will use this text for your analysis. Proceed directly to **Part 2**.
            * If the text is empty contains only placeholder text or includes the specific phrase **"No Context found"** you MUST activate the fallback mechanism.

        2.  **Fallback Mechanism (If Triggered):**
            * Use your Browse tool to visit the provided `{page_url}`.
            * On the page locate the most relevant mention or section related to **'{keyword_tech}'**.
            * **Extract a new context snippet:** Capture approximately 150 words of text *before* the primary keyword mention and 150 words *after* it. This new ~300-word snippet is now the definitive text you will analyze and must be included in the final output's `context` field.
            * Proceed to **Part 2** using this newly extracted snippet.

        ---
        ### **Part 2: Analysis Framework & Rules**

        Perform your analysis on the selected text (either the original or the one extracted via fallback). Your final answer must be a direct result of applying these rules.

        **A. Positive Indicators (Evidence that forces `uses_tech: true`)**
        The answer should be `true` if you find clear first-person evidence of the company's operational use. Strong evidence includes:

        * **Direct Statements of Use:** First-person statements from the company (e.g. "We use..." "Our platform is built on..." "We have deployed...").
        * **Product Integration:** The company's own product is explicitly described as "integrated with" "compatible with" or "powered by" `{keyword_tech}`.
        * **Technical Implementation Details:** Technical blogs success stories or case studies from the company detailing *how* they use the technology for their operations.
        * **Active Job Roles:** Job postings for internal operational roles (not for consulting or training clients) that require hands-on skills with `{keyword_tech}`.
        * **Strong Contextual Keywords:** The text contains clear implementation-related phrases like: {indicators_str}.1

        **B. CRITICAL Exclusion Rules (Evidence that forces `uses_tech: false`)**
        The answer MUST be `false` if the primary evidence falls into any of these categories, even if the keyword is present.

        * **Context Mismatch:** The keyword is used but refers to the wrong concept (e.g., 'AWS' is mentioned but the text defines it as "American Welding Society," not Amazon Web Services).
        * **Educational/Training Context:** The company's only involvement is offering courses, university programs, or certifications *about* the technology. This is not operational use.
        * **Third-Party Action:** The text describes a *customer*, *partner*, or *another organization* using the technology, not `{company_name}` itself.
        * **Individual Skills/Resumes:** The text only refers to an individual employee's personal skills or certifications, not the company's official use.
        * **Speculative or Future-Looking Language:** The text uses conditional words like "plans to," "could," "might explore," or "potential to use."

        ---
        ### **Part 3: Required Output**

        You must provide your final answer in a single, clean JSON object. Do not add any text or explanation outside of the JSON block.

        **Internal Thought Process (To arrive at the JSON answer):**
        Before generating the JSON, think through these steps:
        1.  **Context Selection:** State whether you are using the original `Text to Analyze` or if you activated the fallback mechanism. If you used the fallback, explicitly state the new context you extracted.
        2.  **Evidence Scan:** Quote all phrases from the selected text that mention or are directly related to '{keyword_tech}'.
        3.  **Rule Application:** Analyze the quotes against the Positive Indicators (A) and Exclusion Rules (B). State which specific rule is the most definitive match.
        4.  **Final Determination:** Based on the winning rule, decide the final `true`/`false` value and formulate the explanation.

        **Final Answer (JSON Block):**

        Provide a JSON object with exactly three keys:

        1.  `uses_tech`: `true` or `false`.
        2.  `explanation`: A single, JSON-safe string that justifies your answer. **It must quote the key evidence and explicitly name the rule that was applied. (*Example (True):* `"The text states 'Our entire data platform is built on {keyword_tech}', which meets the 'Direct Statements of Use' positive indicator."` *Example (False):* `"The text describes a 'partnership with AWS to deliver training', which fails the 'Educational/Training Context' exclusion rule as it's not operational use."`)
        3.  `context`: The complete text used for the analysis. This must be the original `Text to Analyze` or the snippet you extracted from the `page_url` if the fallback was used.
        ---
        Note: Only output the JSON object. Do not include any additional text, commentary, or formatting.

        ---
        ### **Information for Analysis**
        * **Company:** `{company_name}`
        * **Technology:** `{keyword_tech}`
        * **Page URL:** `{page_url}`
        * **Text to Analyze:** `{chunk_text}`
        ---
        '''
        a = 2
        print("|=▶ Prompt 2 Context is Missing, URL for analysis and context. ")

    try:
        # Acquire the lock to safely get the next key and model
        with key_lock:
            current_key = next(key_cycler)  # Key Rotation
            current_model = next(model_cycler)
        print(f"|==▶ Using API Key ending in: ..{current_key[-4:]} | current model {current_model}")

        # Call Gemini API
        genai.configure(api_key=current_key)

        # models log
        # model = genai.GenerativeModel('gemini-1.5-flash')
        model = genai.GenerativeModel(current_model)

        # MODEL_ID = "gemini-2.5-flash"  # @param ["gemini-2.5-flash-lite","gemini-2.5-flash","gemini-2.5-pro"] {"allow-input":true, isTemplate: true}

        # model = genai.GenerativeModel('gemini-2.0-flash-lite-001')

        # response = model.generate_content(prompt)
        response = model.generate_content(prompt,
            request_options = {"timeout": 300}
        )


        raw_text = response.text.strip()
        json_str = ""  # Initialize to avoid NameError in the broad except block

        match = re.search(r'\{.*\}', raw_text, re.DOTALL)

        if match:
            json_str = match.group(0)
            try:
                # The `strict=False` parameter allows control characters (e.g., newlines)
                # inside strings, which is a common issue with LLM-generated JSON.
                parsed_response = json.loads(json_str, strict=False)
            except json.JSONDecodeError as json_err:
                # If parsing fails, print a more detailed error message for debugging.
                print(f"|--- JSON PARSING FAILED ---")
                print(f"| Error: {json_err.msg}")
                print(f"| At line {json_err.lineno}, column {json_err.colno} (char {json_err.pos})")
                # Show the problematic part of the string
                context_window = 30
                start = max(0, json_err.pos - context_window)
                end = min(len(json_str), json_err.pos + context_window)
                print(f"| Problematic JSON snippet: ...{json_str[start:end]} ...")
                print(f"|--------------------------")

                raise json_err
        else:
            # If no JSON object is found, raise an error to be caught by the main `except` block.
            raise json.JSONDecodeError("No valid JSON object found in the model's response.", raw_text, 0)


        if a == 1:
            temp = str(chunk_text)
            print(f"|===▶ Out Context (E): {temp[0:100]}")
            return {
                "uses_tech": parsed_response.get("uses_tech", False),
                "explanation": parsed_response.get("explanation", "No explanation from LLM."),
                "push_context": chunk_text
            }
        elif a == 2:
            temp = parsed_response.get("context")
            if len(str(temp)) < 20:
                temp = "No Context found" # Change 6 aug

            print(f"|===▶ Out Context (G): {temp[0:100]}")
            return {
                "uses_tech": parsed_response.get("uses_tech", False),
                "explanation": parsed_response.get("explanation", "No explanation from LLM."),
                "push_context": str(temp)
            }
        else:
            return {
                "uses_tech": parsed_response.get("uses_tech", False),
                "explanation":"No explanation from LLM.",
                "push_context": (chunk_text, "No context found.")
            }

    except Exception as e:
        # The error message from a JSONDecodeError will now be more specific.
        # print(f"Error processing response for keyword '{keyword_tech}': {e}")
        # When json_str is empty, we'll use raw_text instead.
        raw_text = response.text.strip() # New line added
        if not json_str:
            json_str = str(raw_text)
        # This handles the situation when we get API or parsing error.
        usae_raw = str(raw_text[25:30])
        if usae_raw == "true,":
            exe = True
        else:
            exe = False
        return {"uses_tech": exe, "explanation": f"Error. Raw response part: \n {str(json_str)} \n"}