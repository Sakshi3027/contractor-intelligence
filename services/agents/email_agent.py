import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") or ""


def create_email_agent():
    return Agent(
        role="B2B Partnership Outreach Specialist",
        goal="""Write highly personalized, compelling outreach emails
        that get responses from IT services company decision makers.""",
        backstory="""You are an expert B2B copywriter with 10 years of
        experience writing cold outreach for technology partnerships.
        You write emails that feel personal, not templated. You focus
        on the recipient's specific situation and lead with value.
        Your emails are concise, warm, and always include a clear
        low-friction call to action. You never use generic phrases
        like 'I hope this email finds you well'.""",
        llm="groq/llama-3.3-70b-versatile",
        verbose=False,
        allow_delegation=False
    )


def create_email_task(business: dict, research: str) -> Task:
    return Task(
        description=f"""
        Write a personalized partnership outreach email for this company.

        COMPANY DETAILS:
        Name: {business['name']}
        City: {business['city']}
        Email: {business.get('email', 'N/A')}
        Rating: {business.get('google_rating', 'N/A')}
        Reviews: {business.get('google_review_count', 0)}
        Lead Score: {business.get('score', 'N/A')}

        RESEARCH INSIGHTS:
        {research}

        EMAIL REQUIREMENTS:
        - Subject line: compelling, specific, under 50 chars
        - Opening: reference something specific about their business
        - Body: explain the contractor partnership opportunity clearly
        - Value prop: focus on how we solve their staffing/capacity problems
        - Length: 150-200 words maximum
        - Tone: professional but conversational
        - CTA: simple — ask for a 15-minute call
        - NO generic openers like 'I hope this finds you well'
        - NO excessive flattery
        - Sound like a human, not a template

        FORMAT YOUR RESPONSE EXACTLY AS:
        SUBJECT: [subject line here]

        BODY:
        [email body here]
        """,
        expected_output="""A personalized outreach email with subject
        line and body.""",
        agent=create_email_agent()
    )


def generate_email(business: dict, research: str) -> dict:
    agent = create_email_agent()
    task = create_email_task(business, research)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False
    )
    result = crew.kickoff()
    raw = str(result)

    subject = ""
    body = ""

    if "SUBJECT:" in raw and "BODY:" in raw:
        parts = raw.split("BODY:")
        subject = parts[0].replace("SUBJECT:", "").strip()
        body = parts[1].strip()
    else:
        lines = raw.strip().split("\n")
        subject = lines[0].replace("Subject:", "").strip()
        body = "\n".join(lines[1:]).strip()

    return {
        "subject": subject,
        "body": body,
        "raw": raw
    }
