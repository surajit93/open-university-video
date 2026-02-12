# scripts/comment_analyzer.py

import re
from collections import Counter
from typing import List, Dict


class CommentAnalyzer:

    def extract_questions(self, comments: List[str]) -> Dict:
        questions = []

        for c in comments:
            if "?" in c:
                questions.append(c.lower())

        keywords = []
        for q in questions:
            words = re.findall(r'\b[a-z]{4,}\b', q)
            keywords.extend(words)

        freq = Counter(keywords)

        return {
            "question_count": len(questions),
            "top_keywords": freq.most_common(10)
        }
