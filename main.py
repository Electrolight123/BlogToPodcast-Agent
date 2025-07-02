import os # Import os for environment variables
from agno.agent import Agent # Import Agent for creating AI agents
from agno.models.groq import Groq # Import Groq for using Groq models
from agno.tools.eleven_labs import ElevenLabsTools # Import ElevenLabsTools for audio generation
from agno.tools.firecrawl import FirecrawlTools # Import FirecrawlTools for web scraping
from agno.agent import Agent, RunResponse # RunResponse to handle agent responses
from agno.utils.audio import write_audio_to_file  # Utility to write audio files
from agno.utils.log import logger # Import logger for error handling
import streamlit as st # Import Streamlit for web app interface
from uuid import uuid4 # Import uuid for unique file naming

# Streamlit Page Setup
st.set_page_config(page_title="📰 ➡️ 🎙️ Blog to Podcast Agent", page_icon="🎙️") 
st.title("📰 ➡️ 🎙️ Blog to Podcast Agent")

# Sidebar: API Keys
st.sidebar.header("🔑 API Keys")

Groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type="password")
firecrawl_api_key = st.sidebar.text_input("Firecrawl API Key", type="password")

# Check if all keys are provided
keys_provided = all([Groq_api_key, elevenlabs_api_key, firecrawl_api_key])

# Input: Blog URL
url = st.text_input("Enter the Blog URL:", "https://example.com/blog-post") 

# Button: Generate Podcast
generate_button = st.button("🎙️ Generate Podcast", disabled=not keys_provided) 

if not keys_provided:
    st.warning("Please enter all required API keys to enable podcast generation.")

if generate_button:
    if url.strip() == "":
        st.warning("Please enter a blog URL first.")
    else:
        # Set API keys as environment variables for Agno and Tools
        os.environ["GROQ_API_KEY"] = Groq_api_key
        os.environ["ELEVEN_LABS_API_KEY"] = elevenlabs_api_key
        os.environ["FIRECRAWL_API_KEY"] = firecrawl_api_key

        with st.spinner("Processing... Scraping blog, summarizing and generating podcast 🎶"):
            try:
                blog_to_podcast_agent = Agent(
                    name="Blog to Podcast Agent",
                    agent_id="blog_to_podcast_agent",
                    model=Groq(id="llama-3.3-70b-versatile"),
                    tools=[
                        ElevenLabsTools(
                            voice_id="JBFqnCBsd6RMkjVDRZzb",
                            model_id="eleven_multilingual_v2",
                            target_directory="audio_generations"
                        ),
                        FirecrawlTools(),
                    ],
                    description="You are an AI agent that can generate audio using the ElevenLabs API.",
                    instructions=[
                        "When the user provides a blog URL:",
                        "1. Use FirecrawlTools to scrape the blog content",
                        "2. Create a concise summary of the blog content that is NO MORE than 2000 characters long",
                        "3. The summary should capture the main points while being engaging and conversational",
                        "4. Use the ElevenLabsTools to convert the summary to audio",
                        "Ensure the summary is within the 2000 character limit to avoid ElevenLabs API limits",
                    ],
                    markdown=True,
                    debug_mode=True,
                )

                podcast: RunResponse = blog_to_podcast_agent.run(
                    f"Convert the blog content to a podcast: {url}"
                ) # Run the agent with the blog URL

                save_dir = "audio_generations"
                os.makedirs(save_dir, exist_ok=True)

                if podcast.audio and len(podcast.audio) > 0:
                    filename = f"{save_dir}/podcast_{uuid4()}.wav"
                    write_audio_to_file(
                        audio=podcast.audio[0].base64_audio,
                        filename=filename
                    )

                    st.success("Podcast generated successfully! 🎧")
                    audio_bytes = open(filename, "rb").read()
                    
                    st.audio(audio_bytes, format="audio/wav")

                    st.download_button(
                        label="Download Podcast",
                        data=audio_bytes,
                        file_name="generated_podcast.wav",
                        mime="audio/wav"
                    )
                else:
                    st.error("No audio was generated. Please try again.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                logger.error(f"Streamlit app error: {e}")