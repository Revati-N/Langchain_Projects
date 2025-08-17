from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
import re

class CodeReviewAgent:
    def __init__(self, name: str, prompt_template: str, llm):
        self.name = name
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["code", "language"],
            template=prompt_template + "\n\nCode to review:\n``````\n\nYour review:"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def review_code(self, code: str, language: str) -> Dict:
        try:
            response = self.chain.run(code=code, language=language)
            return {
                "agent": self.name,
                "review": response,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "review": f"Error occurred: {str(e)}",
                "status": "error"
            }

class MultiAgentCodeReviewer:
    def __init__(self):
        # Initialize Ollama Llama2
        self.llm = Ollama(model="llama2", temperature=0.3)
        
        # Define agent prompts
        self.agent_prompts = {
            "SecureBot": """You are SecureBot, a paranoid but helpful security expert.
            Focus on security vulnerabilities: SQL injection, XSS, authentication flaws, data exposure, input validation.
            Rate severity: CRITICAL, HIGH, MEDIUM, LOW. Explain WHY and HOW to fix.""",
            
            "SpeedDemon": """You are SpeedDemon, obsessed with performance optimization.
            Focus on: algorithm complexity, memory usage, database efficiency, loop optimization, caching.
            Provide measurable improvement suggestions with estimated performance gains.""",
            
            "StyleGuru": """You are StyleGuru, a code aesthetics expert.
            Focus on: naming conventions, code organization, documentation, DRY principle, best practices.
            Suggest specific refactoring with before/after examples.""",
            
            "TeachBot": """You are TeachBot, a patient mentor for beginners.
            Focus on: step-by-step explanations, design patterns, variable clarity, learning resources.
            Use simple language and real-world analogies.""",
            
            "ArchitectMind": """You are ArchitectMind, a senior architect seeing the big picture.
            Focus on: project structure, design patterns, scalability, maintainability, modularity.
            Provide high-level architectural recommendations."""
        }
        
        # Initialize agents
        self.agents = {}
        for name, prompt in self.agent_prompts.items():
            self.agents[name] = CodeReviewAgent(name, prompt, self.llm)
    
    def review_code(self, code: str, language: str) -> Dict:
        reviews = {}
        
        for agent_name, agent in self.agents.items():
            review = agent.review_code(code, language)
            reviews[agent_name] = review
        
        return reviews
    
    def get_summary_review(self, reviews: Dict) -> str:
        summary_prompt = """
        You are a senior code review coordinator. Summarize the following agent reviews into a concise overview:
        
        {reviews}
        
        Provide:
        1. Top 3 priority issues
        2. Overall code quality score (1-10)
        3. Main recommendation
        """
        
        reviews_text = "\n\n".join([f"{name}: {review['review']}" for name, review in reviews.items()])
        
        summary_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["reviews"],
                template=summary_prompt
            )
        )
        
        return summary_chain.run(reviews=reviews_text)
