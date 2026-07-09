# app/engine.py
import re
import base64
import math
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM

class SecurityEngine:
    def __init__(self):
        print("Initializing Jailbreak Guard Models... (This takes a moment on first startup)")
        # 1. Base Classifier: Meta's Prompt Guard (Optimized for injections & jailbreaks)
       
        
        # Inside app/engine.py change lines 13 & 14 to this:

# 1. Base Classifier: Public Prompt Guard Mirror (No gating restrictions)
        self.guard_tokenizer = AutoTokenizer.from_pretrained("Niansuh/Prompt-Guard-86M")
        self.guard_model = AutoModelForSequenceClassification.from_pretrained("Niansuh/Prompt-Guard-86M")

        # 2. Reference Model for Perplexity checks (Catches random token noise/automated GCG attacks)
        self.ref_tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.ref_model = AutoModelForCausalLM.from_pretrained("gpt2")
        print("All security models successfully loaded.")

    def normalize_input(self, text: str) -> str:
        """Layer 1: Normalization. Decodes hidden payloads and flags obfuscation."""
        cleaned = text.strip()
        
        # Detect and decode Base64 strings smuggles
        b64_matches = re.findall(r'(?:[A-Za-z0-9+/]{4}){2,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?', cleaned)
        for match in b64_matches:
            if len(match) > 16:  # Prevent matching short accidental normal words
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    if len(decoded) > 4:
                        cleaned += f" [DECODED_PAYLOAD: {decoded}]"
                except Exception:
                    pass
        return cleaned

    def calculate_perplexity(self, text: str) -> float:
        """Layer 2: Perplexity Check. High perplexity indicates malicious gibberish/GCG."""
        if not text.strip():
            return 0.0
        inputs = self.ref_tokenizer(text, return_tensors="pt")
        input_ids = inputs["input_ids"]
        with torch.no_grad():
            outputs = self.ref_model(input_ids, labels=input_ids)
        neg_log_likelihood = outputs.loss
        return math.exp(neg_log_likelihood.item())

    def evaluate_semantic_threat(self, text: str) -> dict:
        """Layer 3: Small-LM Transformer evaluation via Prompt-Guard."""
        inputs = self.guard_tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            logits = self.guard_model(**inputs).logits
            
        probabilities = torch.softmax(logits, dim=-1).numpy()[0]
        # Prompt-Guard maps classifications to [0: Benign, 1: Injection, 2: Jailbreak]
        labels = ["benign", "injection", "jailbreak"]
        
        return {
            "verdict": labels[np.argmax(probabilities)],
            "scores": {labels[i]: float(probabilities[i]) for i in range(len(labels))}
        }

    def inspect_prompt(self, raw_prompt: str) -> dict:
        """Coordinates pipeline and outputs standardized audit logs."""
        normalized = self.normalize_input(raw_prompt)
        perplexity = self.calculate_perplexity(normalized)
        semantic_analysis = self.evaluate_semantic_threat(normalized)
        
        is_adversarial = False
        reason = "Clear baseline text"
        
        # Policy definitions
        if perplexity > 150.0:  # Baseline marker for unnatural token noise anomalies
            is_adversarial = True
            reason = "High perplexity anomalies detected (Suspected GCG attack)"
        elif semantic_analysis["verdict"] == "jailbreak" and semantic_analysis["scores"]["jailbreak"] > 0.6:
            is_adversarial = True
            reason = f"Semantic alignment match: Jailbreak Vector ({round(semantic_analysis['scores']['jailbreak']*100)}% certainty)"

        return {
            "blocked": is_adversarial,
            "reason": reason,
            "metrics": {
                "perplexity": round(perplexity, 2),
                "semantic_verdict": semantic_analysis["verdict"],
                "confidence_score": round(max(semantic_analysis["scores"].values()), 4)
            },
            "processed_text": normalized
        }