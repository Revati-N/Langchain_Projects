import os
import streamlit as st
from datetime import datetime, date
from bs4 import BeautifulSoup
import requests
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Optional, List

# Optional: Enable session memory for multi-turn chat
USE_MEMORY = True

def get_seasonal_produce(month: str, year: int) -> str:
    """Scrape a reliable 'what's in season' site for seasonal produce."""
    url = "https://www.simplyrecipes.com/seasonal-produce-guide"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        # Robust parsing for month and year
        for h2 in soup.find_all("h2"):
            if month.lower() in h2.get_text().lower() and str(year) in h2.get_text():
                ul = h2.find_next_sibling("ul")
                if ul:
                    items = [
                        li.get_text().strip()
                        for li in ul.find_all("li")
                        if li.get_text().strip()
                    ]
                    if items:
                        return f"In season: {', '.join(items)}"
        return "No specific seasonal produce found for this month."
    except Exception as e:
        return f"Could not fetch seasonal produce: {e}"

def generate_recipe(ingredients: str, date_str: str, extras: str, memory: Optional[dict] = None) -> str:
    """Generate a recipe with context, optionally using memory for chat history."""
    llm = Ollama(base_url="http://localhost:11434", model="llama2")
    prompt = ChatPromptTemplate.from_template(
        "Today's date is {date}. The user has these ingredients: {ingredients}. "
        "Extras in season: {extras}. Please suggest a detailed, step-by-step recipe. "
        "Include preparation time, servings, and cooking tips. If possible, use the seasonal extras."
    )
    chain = prompt | llm | StrOutputParser()
    context = {"date": date_str, "ingredients": ingredients, "extras": extras}
    # Example: Add previous recipes/questions from memory (optional)
    if memory and "history" in memory and USE_MEMORY:
        context["history"] = "\n".join(memory["history"])
    return chain.invoke(context)

def main():
    st.title("AI Recipe Generator 🌱")
    st.caption("Powered by Llama2 (Ollama), LangChain, and Streamlit")

    # Date input with validation
    selected_date = st.date_input(
        "Select date for seasonal produce",
        datetime.now(),
    )
    ingredients = st.text_area(
        "Enter available ingredients (one per line or comma-separated):",
        placeholder="E.g., chicken, carrots, rice",
        height=120,
    )
    refine = st.checkbox("Use previous recipe history (memory)", value=False)

    # Session state for memory
    if "recipe_history" not in st.session_state:
        st.session_state.recipe_history = []

    if st.button("Generate Recipe", type="primary"):
        if not ingredients.strip():
            st.warning("Please enter at least one ingredient!")
        else:
            month = selected_date.strftime("%B")
            year = selected_date.year
            # Preprocess ingredients (handle commas/newlines)
            ingredients_list = [
                x.strip()
                for x in ingredients.replace("\n", ",").split(",")
                if x.strip()
            ]
            formatted_ingredients = ", ".join(ingredients_list)
            date_str = selected_date.strftime("%B %d, %Y")
            extras = get_seasonal_produce(month, year)
            memory = {"history": st.session_state.recipe_history} if refine else None
            with st.spinner("Generating your recipe..."):
                try:
                    recipe = generate_recipe(
                        formatted_ingredients,
                        date_str,
                        extras,
                        memory
                    )
                    st.subheader("Your AI-Generated Recipe")
                    st.markdown("##### 🥕 Ingredients:")
                    st.markdown(f"- **Available:** {formatted_ingredients}")
                    if extras:
                        st.markdown(f"- **Seasonal Extras:** {extras}")
                    st.markdown("##### 👨‍🍳 Instructions:")
                    st.write(recipe)
                    # Add to memory if enabled
                    if refine:
                        st.session_state.recipe_history.append(recipe)
                        st.info("Previous recipes will influence future suggestions.")
                except Exception as e:
                    st.error("Failed to generate recipe. Please try again.")
                    st.caption(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
