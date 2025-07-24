#!/usr/bin/env python3
"""
Podcast Agent Wrapper for API Integration
Provides a simple interface to the existing podcast agent functionality.
"""

import asyncio
from typing import Optional
from google.adk.runners import Runner
from google.adk.agents.invocation_context import InvocationContext

from .agent import PodcastPipeline, NewsResearcher, PodcastScripter, PodcastProducer
from .tools import fetch_local_news, synthesize_speech


class PodcastAgent:
    """Simple wrapper for podcast generation functionality."""
    
    def __init__(self):
        self.runner = Runner()
    
    async def generate_podcast_script(self, city: str, duration_minutes: int) -> str:
        """Generate a podcast script for the given city and duration."""
        
        try:
            # Step 1: Fetch local news
            news_articles = fetch_local_news(city, limit=10)
            
            if not news_articles:
                return f"No recent news found for {city}. Please try a different city or check back later."
            
            # Step 2: Create news summary
            news_summary = self._create_news_summary(news_articles)
            
            # Step 3: Generate podcast script
            script_prompt = f"""
            Create a {duration_minutes}-minute podcast script based on the following local news from {city}:
            
            {news_summary}
            
            Requirements:
            - Make it engaging and conversational
            - Structure it for audio presentation
            - Keep it within {duration_minutes} minutes when spoken
            - Focus on the most important and interesting stories
            - Use natural transitions between stories
            - Do NOT include music, sound effects, or non-news content
            - Write in a clear, professional news style
            """
            
            # For now, create a simple script based on the news
            # In a full implementation, you would use the LLM agent here
            script = self._generate_simple_script(city, news_articles, duration_minutes)
            
            return script
            
        except Exception as e:
            raise Exception(f"Failed to generate podcast script: {str(e)}")
    
    def _create_news_summary(self, articles: list) -> str:
        """Create a summary of news articles."""
        summary_parts = []
        
        for i, article in enumerate(articles[:5], 1):  # Limit to top 5 articles
            title = article.get('title', 'No title')
            description = article.get('description', 'No description available')
            
            summary_parts.append(f"{i}. {title}\n   {description}")
        
        return "\n\n".join(summary_parts)
    
    def _generate_simple_script(self, city: str, articles: list, duration_minutes: int) -> str:
        """Generate a simple podcast script from news articles."""
        
        # Calculate approximate words per minute (average speaking rate is ~150 WPM)
        target_words = duration_minutes * 150
        
        script_parts = [
            f"Hello and welcome to your daily news podcast! I'm your host bringing you the latest updates from {city}.",
            "Let's dive into today's most important stories that matter to you."
        ]
        
        words_used = len(" ".join(script_parts).split())
        
        for article in articles:
            if words_used >= target_words:
                break
                
            title = article.get('title', '')
            description = article.get('description', '')
            
            if title and description:
                story = f"In other news, {title}. {description}"
                story_words = len(story.split())
                
                if words_used + story_words <= target_words:
                    script_parts.append(story)
                    words_used += story_words
        
        script_parts.append(f"That wraps up today's news from {city}. Thank you for tuning in to your daily news podcast! Stay informed, stay connected, and we'll see you next time. Have a wonderful day!")
        
        return " ".join(script_parts)
    
    async def generate_full_podcast(self, city: str, duration_minutes: int, voice: str = "en-US-Studio-O", speaking_rate: float = 0.95) -> tuple[str, str]:
        """Generate both script and audio for a podcast."""
        
        # Generate script
        script = await self.generate_podcast_script(city, duration_minutes)
        
        # Generate audio
        audio_filename = f"podcast_{city}_{duration_minutes}min.mp3"
        audio_path = synthesize_speech(
            text=script,
            output_path=audio_filename,
            voice=voice,
            speaking_rate=speaking_rate
        )
        
        return script, audio_path
