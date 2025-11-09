# src/services/gemini_client.py

import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from .model_factory import ModelFactory

load_dotenv()


class GeminiClient:
    def __init__(self) -> None:
        self.client, self.model_name, self.provider = ModelFactory.get_model()

    def analyze_bias(self, article_text: str) -> Dict[str, Any]:
        if not article_text or len(article_text.strip()) < 10:
            return self._get_fallback_response()
            
        prompt = self._create_bias_analysis_prompt(article_text)
        
        try:
            response = self.model.generate_content(prompt)
            result = self._extract_json(response.text)
            
            if self._validate_response(result):
                return result
            else:
                return self._get_fallback_response()
                
        except Exception:
            return self._get_fallback_response()

    def _create_bias_analysis_prompt(self, article_text: str) -> str:
        return f"""
        Analyze this news article for media biases and return ONLY valid JSON:

        ARTICLE: {article_text}

        Check for these bias types:
        1. Emotional language (loaded words, sensationalism, exaggeration)
        2. Framing bias (oversimplification, binary thinking, selective framing)
        3. Omission of important context or facts
        4. Partisan or ideological language

        Return JSON with this exact structure:
        {{
            "emotional_bias_score": 0-100,
            "framing_bias_score": 0-100,
            "omission_bias_score": 0-100,
            "overall_bias_score": 0-100,
            "biased_phrases": [
                {{
                    "text": "exact phrase from article",
                    "bias_type": "emotional/framing/omission/partisan",
                    "explanation": "why this phrasing is biased"
                }}
            ],
            "summary": "brief explanation of main biases found"
        }}

        Return ONLY the JSON object, no additional text.
        """

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            cleaned = text.strip().replace('```json', '').replace('```', '').strip()
            
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start == -1 or end == 0:
                return self._get_fallback_response()
                
            json_str = cleaned[start:end]
            return json.loads(json_str)
            
        except json.JSONDecodeError:
            return self._get_fallback_response()
        except Exception:
            return self._get_fallback_response()

    def _validate_response(self, response: Dict[str, Any]) -> bool:
        required_fields = [
            'emotional_bias_score', 
            'framing_bias_score', 
            'omission_bias_score', 
            'overall_bias_score'
        ]
        return all(field in response for field in required_fields)

    def _get_fallback_response(self) -> Dict[str, Any]:
        return {
            "emotional_bias_score": 50,
            "framing_bias_score": 50,
            "omission_bias_score": 50,
            "overall_bias_score": 50,
            "biased_phrases": [],
            "summary": "Analysis unavailable"
        }