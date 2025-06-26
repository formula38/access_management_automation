import logging
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from app.models.access_models import AccessRequest, ServiceType, AccessLevel

logger = logging.getLogger(__name__)

# Try to import advanced AI libraries, but handle gracefully if not available
try:
    import requests
    from sentence_transformers import SentenceTransformer
    import chromadb
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    logger.warning("Advanced AI libraries not available. Using simplified AI service.")
    ADVANCED_AI_AVAILABLE = False


class AIService:
    def __init__(self, ollama_url: str = "http://ollama:11434", model_name: str = "llama3"):
        """Initialize AI service with Ollama and embedding models"""
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.advanced_ai_available = ADVANCED_AI_AVAILABLE
        
        if not ADVANCED_AI_AVAILABLE:
            logger.info("Running in simplified AI mode - advanced features will be simulated")
            return
            
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.embedding_model = None
        
        # Initialize vector database
        try:
            self.vector_db = chromadb.Client()
            self.collection = self.vector_db.create_collection("access_policies")
            logger.info("Vector database initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize vector database: {e}")
            self.vector_db = None
            self.collection = None

    def analyze_access_request(self, request: AccessRequest, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze access request using AI for risk assessment and recommendations"""
        try:
            if not self.advanced_ai_available:
                return self._simulate_ai_analysis(request, user_context)
            
            # Prepare analysis prompt
            prompt = self._create_analysis_prompt(request, user_context)
            
            # Get AI analysis
            ai_response = self._call_ollama(prompt)
            
            # Parse and enhance response
            analysis = self._parse_ai_response(ai_response, request)
            
            # Add vector similarity analysis if available
            if self.embedding_model and self.collection:
                similarity_analysis = self._analyze_policy_similarity(request)
                analysis.update(similarity_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._simulate_ai_analysis(request, user_context)

    def _simulate_ai_analysis(self, request: AccessRequest, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulate AI analysis for demo purposes"""
        # Simulate risk scoring based on request characteristics
        risk_score = self._calculate_simulated_risk_score(request, user_context)
        
        # Generate simulated recommendations
        recommendations = self._generate_simulated_recommendations(request, risk_score)
        
        # Determine suggested access level
        suggested_level = self._suggest_access_level(request, risk_score)
        
        # Generate compliance notes
        compliance_notes = self._generate_compliance_notes(request)
        
        analysis = {
            "risk_score": risk_score,
            "risk_factors": [
                "Simulated risk analysis based on request characteristics",
                f"Access level: {request.access_level.value}",
                f"Service type: {request.service_type.value}",
                f"Duration: {request.requested_duration}"
            ],
            "recommendations": recommendations,
            "suggested_access_level": suggested_level,
            "additional_approvers": [],
            "compliance_notes": compliance_notes,
            "ai_model_used": "simulated",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Simulated AI analysis completed for request {request.id}")
        return analysis

    def _calculate_simulated_risk_score(self, request: AccessRequest, user_context: Optional[Dict[str, Any]] = None) -> int:
        """Calculate simulated risk score based on request characteristics"""
        base_score = 50
        
        # Adjust based on access level
        if request.access_level == AccessLevel.ADMIN:
            base_score += 30
        elif request.access_level == AccessLevel.READ_WRITE:
            base_score += 15
        elif request.access_level == AccessLevel.READ_ONLY:
            base_score += 5
        
        # Adjust based on service type
        if request.service_type == ServiceType.CLOUDSQL:
            base_score += 20
        elif request.service_type == ServiceType.LOOKER_STUDIO:
            base_score += 10
        
        # Adjust based on duration
        duration = request.requested_duration
        if "90d" in duration or "180d" in duration:
            base_score += 15
        elif "365d" in duration:
            base_score += 25
        
        # Adjust based on user context
        if user_context:
            department = user_context.get("department", "").lower()
            if "finance" in department or "hr" in department:
                base_score += 10
            elif "it" in department or "admin" in department:
                base_score -= 5
        
        # Add some randomness for demo
        base_score += random.randint(-10, 10)
        
        return max(0, min(100, base_score))

    def _generate_simulated_recommendations(self, request: AccessRequest, risk_score: int) -> List[str]:
        """Generate simulated recommendations based on risk score"""
        recommendations = []
        
        if risk_score > 80:
            recommendations.extend([
                "High risk request - consider additional approval",
                "Review justification carefully",
                "Consider shorter duration if possible"
            ])
        elif risk_score > 60:
            recommendations.extend([
                "Moderate risk - standard approval process",
                "Monitor access usage"
            ])
        else:
            recommendations.append("Low risk - standard approval")
        
        # Add specific recommendations based on request
        if request.access_level == AccessLevel.ADMIN:
            recommendations.append("Consider least privilege access")
        
        if "90d" in request.requested_duration or "180d" in request.requested_duration:
            recommendations.append("Consider shorter access duration")
        
        return recommendations

    def _suggest_access_level(self, request: AccessRequest, risk_score: int) -> str:
        """Suggest appropriate access level based on risk"""
        if risk_score > 80:
            return "read_only"
        elif risk_score > 60:
            return "read_write"
        else:
            return request.access_level.value

    def _generate_compliance_notes(self, request: AccessRequest) -> List[str]:
        """Generate compliance notes for the request"""
        notes = [
            "Simulated compliance check completed",
            "Request reviewed against access policies"
        ]
        
        if request.service_type == ServiceType.CLOUDSQL:
            notes.append("Database access requires additional monitoring")
        
        if request.access_level == AccessLevel.ADMIN:
            notes.append("Admin access requires quarterly review")
        
        return notes

    def _create_analysis_prompt(self, request: AccessRequest, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create prompt for AI analysis"""
        prompt = f"""
        Analyze this access request for security risks and provide recommendations:
        
        Request Details:
        - Requester: {request.requester_email}
        - Resource: {request.resource}
        - Service Type: {request.service_type.value}
        - Access Level: {request.access_level.value}
        - Duration: {request.requested_duration}
        - Justification: {request.justification}
        
        User Context: {json.dumps(user_context) if user_context else 'None'}
        
        Please provide:
        1. Risk score (0-100)
        2. Risk factors
        3. Recommendations
        4. Suggested access level
        5. Additional approvers needed
        6. Compliance notes
        
        Respond in JSON format.
        """
        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API for AI analysis using real LLM"""
        try:
            if not self.ollama_url:
                return "Ollama not available"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            logger.info(f"Calling Ollama at {self.ollama_url}/api/generate with model {self.model_name}")
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Ollama response: {result.get('response', '')[:200]}")
            return result.get("response", "No response from Ollama")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error: {str(e)}"

    def _parse_ai_response(self, ai_response: str, request: AccessRequest) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            # Try to extract JSON from response
            if "{" in ai_response and "}" in ai_response:
                start = ai_response.find("{")
                end = ai_response.rfind("}") + 1
                json_str = ai_response[start:end]
                parsed = json.loads(json_str)
                
                # Ensure required fields
                analysis = {
                    "risk_score": parsed.get("risk_score", 50),
                    "risk_factors": parsed.get("risk_factors", ["AI analysis completed"]),
                    "recommendations": parsed.get("recommendations", ["Standard approval recommended"]),
                    "suggested_access_level": parsed.get("suggested_access_level", request.access_level.value),
                    "additional_approvers": parsed.get("additional_approvers", []),
                    "compliance_notes": parsed.get("compliance_notes", ["AI compliance review completed"]),
                    "ai_model_used": self.model_name,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                
                return analysis
            else:
                # Fallback to simulated analysis
                return self._simulate_ai_analysis(request)
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._simulate_ai_analysis(request)

    def _analyze_policy_similarity(self, request: AccessRequest) -> Dict[str, Any]:
        """Analyze similarity with existing policies using vector embeddings"""
        try:
            if not self.embedding_model or not self.collection:
                return {"similarity_analysis": "Vector analysis not available"}
            
            # Create embedding for the request
            request_text = f"{request.requester_email} {request.resource} {request.service_type.value} {request.access_level.value} {request.justification}"
            embedding = self.embedding_model.encode([request_text])
            
            # Search for similar policies
            results = self.collection.query(
                query_embeddings=embedding.tolist(),
                n_results=5
            )
            
            return {
                "similarity_analysis": {
                    "similar_policies": len(results.get("documents", [])),
                    "top_similarity": results.get("distances", [[1.0]])[0][0] if results.get("distances") else 1.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error in similarity analysis: {e}")
            return {"similarity_analysis": "Error in analysis"}

    def store_policy_embedding(self, policy_id: str, policy_text: str) -> bool:
        """Store policy embedding in vector database"""
        try:
            if not self.embedding_model or not self.collection:
                logger.warning("Vector database not available for policy storage")
                return False
            
            # Create embedding
            embedding = self.embedding_model.encode([policy_text])
            
            # Store in vector database
            self.collection.add(
                embeddings=embedding.tolist(),
                documents=[policy_text],
                metadatas=[{"policy_id": policy_id, "type": "access_policy"}],
                ids=[policy_id]
            )
            
            logger.info(f"Policy embedding stored for policy {policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing policy embedding: {e}")
            return False

    def search_similar_policies(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar policies using vector similarity"""
        try:
            if not self.embedding_model or not self.collection:
                return []
            
            # Create embedding for query
            embedding = self.embedding_model.encode([query])
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=embedding.tolist(),
                n_results=limit
            )
            
            # Format results
            similar_policies = []
            for i in range(len(results.get("ids", [[]])[0])):
                similar_policies.append({
                    "policy_id": results["ids"][0][i],
                    "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {}
                })
            
            return similar_policies
            
        except Exception as e:
            logger.error(f"Error searching similar policies: {e}")
            return []

    def generate_policy_recommendations(self, request: AccessRequest, existing_policies: List[Dict[str, Any]]) -> List[str]:
        """Generate policy recommendations based on existing policies"""
        try:
            recommendations = []
            
            # Analyze existing policies for patterns
            similar_policies = [p for p in existing_policies if p.get("service_type") == request.service_type.value]
            
            if similar_policies:
                # Find common patterns
                access_levels = [p.get("access_level") for p in similar_policies]
                durations = [p.get("duration") for p in similar_policies]
                
                # Recommend based on patterns
                if request.access_level.value not in access_levels:
                    recommendations.append(f"Consider using existing access level patterns: {set(access_levels)}")
                
                if request.requested_duration not in durations:
                    recommendations.append(f"Consider using existing duration patterns: {set(durations)}")
            
            # Add general recommendations
            recommendations.extend([
                "Review existing policies for similar use cases",
                "Ensure compliance with data governance policies",
                "Consider implementing time-based access controls"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating policy recommendations: {e}")
            return ["Error generating recommendations"]

    def validate_request_compliance(self, request: AccessRequest, policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate request compliance against existing policies"""
        try:
            compliance_result = {
                "compliant": True,
                "violations": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check against each policy
            for policy in policies:
                if self._check_policy_violation(request, policy):
                    compliance_result["compliant"] = False
                    compliance_result["violations"].append({
                        "policy_id": policy.get("id"),
                        "policy_name": policy.get("name"),
                        "violation_type": "access_level_mismatch"
                    })
            
            # Add warnings for high-risk requests
            if request.access_level == AccessLevel.ADMIN:
                compliance_result["warnings"].append("Admin access requires additional scrutiny")
            
            if "90d" in request.requested_duration or "180d" in request.requested_duration:
                compliance_result["warnings"].append("Long-term access requires periodic review")
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error validating compliance: {e}")
            return {
                "compliant": False,
                "violations": [],
                "warnings": [f"Error in compliance validation: {str(e)}"],
                "recommendations": []
            }

    def _check_policy_violation(self, request: AccessRequest, policy: Dict[str, Any]) -> bool:
        """Check if request violates a specific policy"""
        try:
            # Check service type
            if policy.get("service_type") != request.service_type.value:
                return False
            
            # Check access level restrictions
            allowed_levels = policy.get("allowed_access_levels", [])
            if allowed_levels and request.access_level.value not in allowed_levels:
                return True
            
            # Check duration restrictions
            max_duration = policy.get("max_duration")
            if max_duration:
                # Simple duration check (in production, use proper duration parsing)
                if "365d" in request.requested_duration and max_duration != "365d":
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking policy violation: {e}")
            return False 