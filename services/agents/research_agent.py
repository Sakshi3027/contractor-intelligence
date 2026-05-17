import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") or ""


def create_research_agent():
    return Agent(
        role="Business Intelligence Researcher",
        goal="""Research IT service companies to find key information
        that will make outreach highly personalized and relevant.""",
        backstory="""You are an expert business researcher who specializes
        in IT services companies. You analyze businesses to understand their
        size, specialization, target market, pain points, and growth stage.
        Your research helps craft perfectly targeted partnership proposals.""",
        llm="groq/llama-3.3-70b-versatile",
        verbose=False,
        allow_delegation=False
    )


def create_research_task(business: dict) -> Task:
    return Task(
        description=f"""
        Research this IT services company and provide a structured analysis:

        Company: {business['name']}
        City: {business['city']}
        Website: {business.get('website', 'N/A')}
        Google Rating: {business.get('google_rating', 'N/A')}
        Reviews: {business.get('google_review_count', 0)}
        Lead Score: {business.get('score', 'N/A')}
        Tier: {business.get('tier', 'N/A')}

        Based on the company name, location, and available data provide:

        1. COMPANY PROFILE
           - Estimated company size
           - Primary IT services they likely offer
           - Target market

        2. PARTNERSHIP OPPORTUNITY
           - Why they would benefit from contractor partnerships
           - Specific pain points they likely face

        3. PERSONALIZATION HOOKS
           - 2-3 specific talking points for outreach
           - Local market angle

        4. RECOMMENDED APPROACH
           - Tone and key value proposition

        Keep the analysis concise and actionable.
        """,
        expected_output="""A structured business analysis with company
        profile, partnership opportunity, personalization hooks, and
        recommended outreach approach.""",
        agent=create_research_agent()
    )


def research_business(business: dict) -> str:
    agent = create_research_agent()
    task = create_research_task(business)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False
    )
    result = crew.kickoff()
    return str(result)
