"""
Prim Natural Language Processing
Provides text processing, tokenization, language models, sentiment analysis,
text classification, and machine translation.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class TokenizerType(Enum):
    """Tokenizer types"""
    WHITESPACE = "whitespace"
    WORD_PIECE = "word_piece"
    BPE = "bpe"
    SENTENCE_PIECE = "sentence_piece"


class ModelType(Enum):
    """Model types"""
    BERT = "bert"
    GPT = "gpt"
    T5 = "t5"
    LSTM = "lstm"
    TRANSFORMER = "transformer"


@dataclass
class Token:
    """Token representation"""
    text: str
    id: int
    position: int
    attention_mask: int = 1


@dataclass
class Sequence:
    """Text sequence"""
    tokens: List[Token]
    text: str
    metadata: Dict[str, Any]


class Tokenizer:
    """Text tokenization"""

    def __init__(self, tokenizer_type: TokenizerType = TokenizerType.WHITESPACE):
        self.tokenizer_type = tokenizer_type
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 0

    def build_vocab(self, texts: List[str]):
        """Build vocabulary from texts"""
        word_counts = {}

        for text in texts:
            tokens = self._tokenize(text)
            for token in tokens:
                word_counts[token] = word_counts.get(token, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

        # Build vocabulary
        self.vocab = {"<PAD>": 0, "<UNK>": 1, "<CLS>": 2, "<SEP>": 3}
        for i, (word, _) in enumerate(sorted_words):
            self.vocab[word] = i + 4

        self.vocab_size = len(self.vocab)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        if self.tokenizer_type == TokenizerType.WHITESPACE:
            return text.split()
        elif self.tokenizer_type == TokenizerType.WORD_PIECE:
            return self._word_piece_tokenize(text)
        else:
            return text.split()

    def _word_piece_tokenize(self, text: str) -> List[str]:
        """WordPiece tokenization (simplified)"""
        tokens = []
        words = text.split()

        for word in words:
            if word in self.vocab:
                tokens.append(word)
            else:
                # Try to split word into subwords
                subwords = []
                remaining = word

                while remaining:
                    # Find longest matching subword
                    found = False
                    for i in range(len(remaining), 0, -1):
                        subword = remaining[:i]
                        if subword in self.vocab:
                            subwords.append(subword)
                            remaining = remaining[i:]
                            found = True
                            break

                    if not found:
                        subwords.append("<UNK>")
                        break

                tokens.extend(subwords)

        return tokens

    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs"""
        tokens = self._tokenize(text)
        return [self.vocab.get(token, self.vocab["<UNK>"]) for token in tokens]

    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs to text"""
        reverse_vocab = {v: k for k, v in self.vocab.items()}
        tokens = [reverse_vocab.get(id, "<UNK>") for id in token_ids]
        return " ".join(tokens)

    def tokenize(self, text: str) -> Sequence:
        """Tokenize text with metadata"""
        tokens = self._tokenize(text)

        sequence_tokens = []
        for i, token_text in enumerate(tokens):
            token_id = self.vocab.get(token_text, self.vocab["<UNK>"])
            sequence_tokens.append(Token(
                text=token_text,
                id=token_id,
                position=i
            ))

        return Sequence(
            tokens=sequence_tokens,
            text=text,
            metadata={"token_count": len(tokens)}
        )


class LanguageModel:
    """Language model for text generation"""

    def __init__(self, model_type: ModelType = ModelType.TRANSFORMER):
        self.model_type = model_type
        self.embeddings: Optional[np.ndarray] = None
        self.vocab_size = 0

    def load_embeddings(self, embeddings: np.ndarray):
        """Load word embeddings"""
        self.embeddings = embeddings
        self.vocab_size = embeddings.shape[0]

    def generate(self, prompt: str, max_length: int = 100,
                temperature: float = 1.0) -> str:
        """Generate text from prompt"""
        # Simplified generation
        words = prompt.split()
        generated = words.copy()

        for _ in range(max_length - len(words)):
            # In practice, this would use the actual model
            next_word = self._sample_next_word(generated, temperature)
            generated.append(next_word)

            if next_word == "<EOS>":
                break

        return " ".join(generated)

    def _sample_next_word(self, context: List[str], temperature: float) -> str:
        """Sample next word from context"""
        # Simplified - would use actual model in practice
        import random

        if self.embeddings is not None:
            # Sample from vocabulary
            vocab_words = list(range(self.vocab_size))
            next_id = random.choice(vocab_words)
            return f"word_{next_id}"
        else:
            return "the"


class SentimentAnalyzer:
    """Sentiment analysis"""

    def __init__(self):
        self.model = None
        self.classes = ["negative", "neutral", "positive"]

    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        # Simplified sentiment analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "horrible", "poor"]

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total = positive_count + negative_count + 1  # Avoid division by zero

        positive_score = positive_count / total
        negative_score = negative_count / total
        neutral_score = 1.0 - positive_score - negative_score

        return {
            "positive": positive_score,
            "neutral": neutral_score,
            "negative": negative_score
        }

    def classify(self, text: str) -> str:
        """Classify sentiment"""
        scores = self.analyze(text)
        return self.classes[np.argmax([scores["positive"], scores["neutral"], scores["negative"]])]


class TextClassifier:
    """Text classification"""

    def __init__(self):
        self.model = None
        self.classes: List[str] = []

    def train(self, texts: List[str], labels: List[str]):
        """Train classifier"""
        # Build class list
        self.classes = list(set(labels))

        # Simplified training - would use actual model in practice
        self.model = {"classes": self.classes}

    def predict(self, text: str) -> Tuple[str, float]:
        """Predict class for text"""
        if not self.model:
            raise RuntimeError("Model not trained")

        # Simplified prediction
        import random
        predicted_class = random.choice(self.classes)
        confidence = random.random()

        return predicted_class, confidence

    def predict_proba(self, text: str) -> Dict[str, float]:
        """Predict class probabilities"""
        if not self.model:
            raise RuntimeError("Model not trained")

        # Simplified prediction
        import random
        probs = {cls: random.random() for cls in self.classes}

        # Normalize
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}

        return probs


class NamedEntityRecognizer:
    """Named entity recognition"""

    def __init__(self):
        self.model = None
        self.entity_types = ["PERSON", "ORG", "LOC", "MISC"]

    def recognize(self, text: str) -> List[Dict[str, Any]]:
        """Recognize named entities"""
        # Simplified NER - would use actual model in practice
        entities = []

        words = text.split()
        for i, word in enumerate(words):
            # Simple pattern matching
            if word[0].isupper() and len(word) > 1:
                entities.append({
                    "text": word,
                    "label": "ORG",
                    "start": i,
                    "end": i + 1
                })

        return entities


class MachineTranslator:
    """Machine translation"""

    def __init__(self, source_lang: str = "en", target_lang: str = "fr"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.model = None

    def translate(self, text: str) -> str:
        """Translate text"""
        # Simplified translation - would use actual model in practice
        if self.model is None:
            # Return mock translation
            return f"[{self.target_lang}] {text}"

        # Use actual model
        return self._translate_with_model(text)

    def _translate_with_model(self, text: str) -> str:
        """Translate using model"""
        # Placeholder for actual translation
        return text


class TextSummarizer:
    """Text summarization"""

    def __init__(self):
        self.model = None

    def summarize(self, text: str, max_length: int = 100) -> str:
        """Summarize text"""
        # Simplified summarization - extract first few sentences
        sentences = re.split(r'[.!?]+', text)
        summary = ' '.join(sentences[:3])

        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    def abstractive_summarize(self, text: str, max_length: int = 100) -> str:
        """Abstractive summarization"""
        # Simplified - would use actual model in practice
        sentences = re.split(r'[.!?]+', text)

        # Select important sentences
        important_sentences = []
        for sentence in sentences:
            if len(sentence) > 10:  # Filter short sentences
                important_sentences.append(sentence)

        summary = ' '.join(important_sentences[:2])

        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary


class QuestionAnswering:
    """Question answering"""

    def __init__(self):
        self.model = None

    def answer(self, question: str, context: str) -> Tuple[str, float]:
        """Answer question from context"""
        # Simplified QA - extract relevant sentence
        sentences = re.split(r'[.!?]+', context)

        # Find sentence with most words in common with question
        question_words = set(question.lower().split())
        best_sentence = ""
        best_score = 0

        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            common_words = question_words & sentence_words
            score = len(common_words)

            if score > best_score:
                best_score = score
                best_sentence = sentence

        confidence = min(best_score / len(question_words), 1.0) if question_words else 0.0

        return best_sentence, confidence


def create_tokenizer(tokenizer_type: TokenizerType = TokenizerType.WHITESPACE) -> Tokenizer:
    """Create tokenizer"""
    return Tokenizer(tokenizer_type)


def create_language_model(model_type: ModelType = ModelType.TRANSFORMER) -> LanguageModel:
    """Create language model"""
    return LanguageModel(model_type)


def main():
    """Main entry point for testing"""
    print("Testing Natural Language Processing...")

    # Test Tokenizer
    tokenizer = create_tokenizer()
    texts = ["hello world", "this is a test", "another example"]
    tokenizer.build_vocab(texts)

    encoded = tokenizer.encode("hello world test")
    decoded = tokenizer.decode(encoded)
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")

    # Test Language Model
    lm = create_language_model()
    embeddings = np.random.randn(100, 128)
    lm.load_embeddings(embeddings)

    generated = lm.generate("hello", max_length=10)
    print(f"Generated: {generated}")

    # Test Sentiment Analyzer
    sentiment_analyzer = SentimentAnalyzer()
    scores = sentiment_analyzer.analyze("This is a great product!")
    print(f"Sentiment scores: {scores}")
    print(f"Classification: {sentiment_analyzer.classify('This is a great product!')}")

    # Test Text Classifier
    classifier = TextClassifier()
    classifier.train(texts, ["positive", "negative", "neutral"])
    pred_class, confidence = classifier.predict("This is good")
    print(f"Prediction: {pred_class} ({confidence:.2f})")

    # Test Named Entity Recognizer
    ner = NamedEntityRecognizer()
    entities = ner.recognize("John works at Google in California")
    print(f"Entities: {len(entities)}")

    # Test Machine Translator
    translator = MachineTranslator("en", "fr")
    translated = translator.translate("Hello world")
    print(f"Translated: {translated}")

    # Test Text Summarizer
    summarizer = TextSummarizer()
    text = "This is a long text. It has multiple sentences. Each sentence contains information. The summary should be shorter."
    summary = summarizer.summarize(text)
    print(f"Summary: {summary}")

    # Test Question Answering
    qa = QuestionAnswering()
    answer, confidence = qa.answer("What is the capital?", "The capital of France is Paris. Paris is beautiful.")
    print(f"Answer: {answer} ({confidence:.2f})")

    print("\nNatural Language Processing initialized successfully")


if __name__ == "__main__":
    main()
