import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
from core.gemini_agent import GeminiAgent

class TestGeminiCLIIntegration:
    
    @pytest.mark.asyncio
    async def test_api_key_priority(self):
        """
        Audit: Ensure API Key is used PREFERENCE over CLI if available.
        """
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'fake_key', 'GROQ_API_KEY': 'fake_groq'}):
            agent = GeminiAgent("TestBot", "Tester", model_chain=["gemini-1.5-pro"])
            
            # Mock the REST API call
            agent._call_gemini_api = AsyncMock(return_value=json.dumps({
                "verdict": "PASS", "confidence": 1.0, "evidence": [], "reasoning": "API Used"
            }))
            
            # Mock CLI check to True (to ensure we didn't just fallback because CLI was missing)
            agent.has_gemini_cli = True 
            
            result = await agent.query("test")
            
            # Assertions
            agent._call_gemini_api.assert_called_once()
            assert result["verdict"] == "PASS"
            assert result["reasoning"] == "API Used"

    @pytest.mark.asyncio
    async def test_cli_fallback_logic(self):
        """
        Audit: Ensure system falls back to CLI if API Key is missing.
        """
        # Ensure NO Google Key in env
        with patch.dict('os.environ', {'GOOGLE_API_KEY': '', 'GROQ_API_KEY': 'fake_groq'}):
            with patch('shutil.which', return_value='/usr/bin/gemini'):
                agent = GeminiAgent("TestBot", "Tester", model_chain=["gemini-1.5-pro"])
                
                # Verify state
                assert agent.gemini_key is None or agent.gemini_key == ""
                assert agent.has_gemini_cli is True
                
                # Mock the CLI call
                agent._call_gemini_cli = AsyncMock(return_value=json.dumps({
                    "verdict": "PASS", "confidence": 0.95, "evidence": [], "reasoning": "CLI Used"
                }))
                
                result = await agent.query("test")
                
                # Assertions
                agent._call_gemini_cli.assert_called_once()
                assert result["verdict"] == "PASS"
                assert result["reasoning"] == "CLI Used"

    @pytest.mark.asyncio
    async def test_groq_fallback_chain(self):
        """
        Audit: Ensure system falls back to Groq if Gemini (API & CLI) fails.
        """
        with patch.dict('os.environ', {'GOOGLE_API_KEY': '', 'GROQ_API_KEY': 'fake_groq'}):
            # Mock CLI missing
            with patch('shutil.which', return_value=None):
                agent = GeminiAgent("TestBot", "Tester", model_chain=["gemini-1.5-pro", "llama-3.3-70b-versatile"])
                
                assert agent.has_gemini_cli is False
                
                # Mock Groq Call
                agent._call_groq = AsyncMock(return_value=json.dumps({
                    "verdict": "PASS", "confidence": 0.8, "evidence": [], "reasoning": "Groq Backup"
                }))
                
                # We expect _call_gemini_cli to NOT be called (or fail fast)
                # and _call_gemini_api to NOT be called
                
                result = await agent.query("test")
                
                assert result["verdict"] == "PASS"
                assert result["reasoning"] == "Groq Backup"
                agent._call_groq.assert_called()

    @pytest.mark.asyncio
    async def test_cli_command_construction(self):
        """
        Audit: Verify the subprocess command is constructed safely.
        """
        with patch.dict('os.environ', {'GOOGLE_API_KEY': ''}):
            agent = GeminiAgent("TestBot", "Tester")
            
            # Mock subprocess
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'{"verdict": "PASS", "confidence": 1.0, "evidence": [], "reasoning": "CMD Check"}', b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc) as mock_exec:
                result = await agent._call_gemini_cli("gemini-3-pro", "System", "User Prompt")
                
                # Check args
                args = mock_exec.call_args[0]
                assert args[0] == "gemini"
                assert "--model" in args
                assert "gemini-3-pro" in args
                assert "--output-format" in args
                
                # Check JSON parsing
                data = json.loads(result)
                assert data["verdict"] == "PASS"
