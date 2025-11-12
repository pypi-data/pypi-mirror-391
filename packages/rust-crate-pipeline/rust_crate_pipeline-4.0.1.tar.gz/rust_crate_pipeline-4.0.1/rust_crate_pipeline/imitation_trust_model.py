"""
Imitation-based trust model for Rust crate evaluation.

This module demonstrates how to use the Imitation library to create
a trust evaluation system that learns from expert demonstrations.
"""

import logging
import importlib
from typing import Any, Dict, Tuple
import numpy as np

try:
    networks = importlib.import_module("imitation.util.networks")
    IMITATION_AVAILABLE = True
except Exception:
    IMITATION_AVAILABLE = False
    logging.warning("Imitation library not available - using fallback trust model")

logger = logging.getLogger(__name__)


class ImitationTrustModel:
    """
    Imitation-based trust model for evaluating Rust crates.
    
    This model learns from expert demonstrations of what constitutes
    a trustworthy crate and applies that learning to new crates.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the imitation trust model.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.expert_demonstrations = []
        self.feature_extractor = None
        
        if IMITATION_AVAILABLE:
            self._initialize_model()
        else:
            self.logger.warning("Using fallback trust model - imitation library not available")
    
    def _initialize_model(self):
        """Initialize the imitation learning model."""
        try:
            # Create a simple policy network for trust evaluation
            # In a real implementation, this would be more sophisticated
            self.feature_extractor = networks.build_mlp_actor_critic(
                observation_space=None,  # Will be set during training
                action_space=None,      # Will be set during training
                lr_schedule=lambda _: 0.001,
                net_arch=[64, 64]
            )
            
            self.logger.info("✅ Imitation trust model initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize imitation model: {e}")
            self.model = None
    
    def add_expert_demonstration(self, crate_data: Dict[str, Any], trust_score: float):
        """
        Add an expert demonstration to the training data.
        
        Args:
            crate_data: Crate metadata and features
            trust_score: Expert-assigned trust score (0.0 to 1.0)
        """
        if not IMITATION_AVAILABLE:
            return
            
        try:
            # Convert crate data to feature vector
            features = self._extract_features(crate_data)
            
            # Store demonstration
            demonstration = {
                "features": features,
                "trust_score": trust_score,
                "crate_name": crate_data.get("name", "unknown"),
                "metadata": crate_data
            }
            
            self.expert_demonstrations.append(demonstration)
            self.logger.info(f"Added expert demonstration for {crate_data.get('name', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Failed to add expert demonstration: {e}")
    
    def _extract_features(self, crate_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from crate data for the trust model.
        
        Args:
            crate_data: Crate metadata and features
            
        Returns:
            Feature vector as numpy array
        """
        # Simple feature extraction - in a real implementation this would be more sophisticated
        features = []
        
        # Basic metrics
        features.append(crate_data.get("downloads", 0) / 10000.0)  # Normalize downloads
        features.append(crate_data.get("github_stars", 0) / 1000.0)  # Normalize stars
        features.append(len(crate_data.get("dependencies", [])) / 50.0)  # Normalize deps
        features.append(len(crate_data.get("keywords", [])) / 10.0)  # Normalize keywords
        
        # Text-based features (simplified)
        description = crate_data.get("description", "")
        features.append(len(description) / 1000.0)  # Description length
        
        readme = crate_data.get("readme", "")
        features.append(len(readme) / 10000.0)  # README length
        
        # Security features
        features.append(1.0 if crate_data.get("has_security_audit", False) else 0.0)
        features.append(1.0 if crate_data.get("has_ci_cd", False) else 0.0)
        features.append(1.0 if crate_data.get("has_tests", False) else 0.0)
        
        # Convert to numpy array and ensure fixed size
        feature_vector = np.array(features, dtype=np.float32)
        
        # Pad or truncate to fixed size (10 features)
        if len(feature_vector) < 10:
            feature_vector = np.pad(feature_vector, (0, 10 - len(feature_vector)), 'constant')
        elif len(feature_vector) > 10:
            feature_vector = feature_vector[:10]
            
        return feature_vector
    
    def train(self) -> bool:
        """
        Train the imitation model on expert demonstrations.
        
        Returns:
            True if training was successful, False otherwise
        """
        if not IMITATION_AVAILABLE or not self.expert_demonstrations:
            self.logger.warning("Cannot train: imitation library not available or no demonstrations")
            return False
            
        try:
            if len(self.expert_demonstrations) < 5:
                self.logger.warning(f"Need at least 5 demonstrations, got {len(self.expert_demonstrations)}")
                return False
            
            # Prepare training data
            features = np.array([d["features"] for d in self.expert_demonstrations])
            trust_scores = np.array([d["trust_score"] for d in self.expert_demonstrations])
            
            # Simple behavioral cloning (in a real implementation, this would use the imitation library properly)
            # For now, we'll use a simple linear regression as a placeholder
            from sklearn.linear_model import LinearRegression
            
            self.model = LinearRegression()
            self.model.fit(features, trust_scores)
            
            self.logger.info(f"✅ Trained imitation model on {len(self.expert_demonstrations)} demonstrations")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to train imitation model: {e}")
            return False
    
    def evaluate_trust(self, crate_data: Dict[str, Any]) -> Tuple[float, float]:
        """
        Evaluate trust for a crate using the imitation model.
        
        Args:
            crate_data: Crate metadata and features
            
        Returns:
            Tuple of (trust_score, confidence)
        """
        if not IMITATION_AVAILABLE or self.model is None:
            # Fallback to simple heuristic
            return self._fallback_trust_evaluation(crate_data)
        
        try:
            # Extract features
            features = self._extract_features(crate_data)
            features = features.reshape(1, -1)  # Reshape for prediction
            
            # Predict trust score
            trust_score = self.model.predict(features)[0]
            trust_score = np.clip(trust_score, 0.0, 1.0)  # Clamp to [0, 1]
            
            # Calculate confidence based on feature quality
            confidence = self._calculate_confidence(crate_data)
            
            return float(trust_score), float(confidence)
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate trust: {e}")
            return self._fallback_trust_evaluation(crate_data)
    
    def _fallback_trust_evaluation(self, crate_data: Dict[str, Any]) -> Tuple[float, float]:
        """
        Fallback trust evaluation when imitation model is not available.
        
        Args:
            crate_data: Crate metadata and features
            
        Returns:
            Tuple of (trust_score, confidence)
        """
        # Simple heuristic-based trust evaluation
        score = 0.0
        confidence = 0.5
        
        # Downloads
        downloads = crate_data.get("downloads", 0)
        if downloads > 10000:
            score += 0.3
        elif downloads > 1000:
            score += 0.2
        elif downloads > 100:
            score += 0.1
        
        # GitHub stars
        stars = crate_data.get("github_stars", 0)
        if stars > 100:
            score += 0.3
        elif stars > 10:
            score += 0.2
        elif stars > 1:
            score += 0.1
        
        # Documentation
        if crate_data.get("description"):
            score += 0.1
        if crate_data.get("readme"):
            score += 0.1
        
        # Dependencies (fewer is better for security)
        deps = len(crate_data.get("dependencies", []))
        if deps < 10:
            score += 0.1
        elif deps > 50:
            score -= 0.1
        
        # Security features
        if crate_data.get("has_security_audit", False):
            score += 0.2
        if crate_data.get("has_tests", False):
            score += 0.1
        
        # Clamp score to [0, 1]
        score = max(0.0, min(1.0, score))
        
        return score, confidence
    
    def _calculate_confidence(self, crate_data: Dict[str, Any]) -> float:
        """
        Calculate confidence in the trust evaluation.
        
        Args:
            crate_data: Crate metadata and features
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Simple confidence calculation based on data completeness
        confidence = 0.5  # Base confidence
        
        # Increase confidence for more complete data
        if crate_data.get("description"):
            confidence += 0.1
        if crate_data.get("readme"):
            confidence += 0.1
        if crate_data.get("downloads") is not None:
            confidence += 0.1
        if crate_data.get("github_stars") is not None:
            confidence += 0.1
        if crate_data.get("dependencies") is not None:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model state.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_type": "imitation_learning" if IMITATION_AVAILABLE else "fallback_heuristic",
            "trained": self.model is not None,
            "demonstrations_count": len(self.expert_demonstrations),
            "imitation_available": IMITATION_AVAILABLE,
            "feature_dimensions": 10
        }
