# Phase 4: Self-Evaluation with Expert Criteria

> **Status**: ✅ Complete  
> **Date**: August 2026

This document describes the implementation of Phase 4 — Self-Evaluation using the 7-dimension expert framework from the ACL 2025 paper.

---

## Overview

Phase 4 adds automatic self-evaluation of generated answers using the 7 presentational and epistemological dimensions designed by climate experts. The evaluation runs in a separate LLM conversation for objectivity and provides a detailed score breakdown with actionable feedback.

---

## The 7 Evaluation Dimensions

Each dimension has 3 sub-criteria scored as 0 (not met) or 1 (met), giving a maximum of 21 points.

### 1. Context
| Criterion | Description |
|-----------|-------------|
| 1a | Attempts to give some broader context to explain the issue |
| 1b | Provides an introductory paragraph to introduce the topic |
| 1c | Provides a summary paragraph at the end |

### 2. Structure
| Criterion | Description |
|-----------|-------------|
| 2a | Overall response is well structured, easy to read |
| 2b | Headings and subheadings are well structured and logical |
| 2c | Dot points or bullet points are used appropriately |

### 3. Use of Language
| Criterion | Description |
|-----------|-------------|
| 3a | Phrasing is appropriate (easy to read, fluent) |
| 3b | Correct use of grammar |
| 3c | Consistent with language used in climate/agriculture industry |

### 4. Use of Citations
| Criterion | Description |
|-----------|-------------|
| 4a | Citations are used appropriately |
| 4b | The number of citations used is appropriate |
| 4c | Citations are easy to read and follow |

### 5. Specificity
| Criterion | Description |
|-----------|-------------|
| 5a | Gives information specific to a commodity, if appropriate |
| 5b | Gives information specific to the location/region in question |
| 5c | Admits when location-specific information is not available |

### 6. Comprehensiveness
| Criterion | Description |
|-----------|-------------|
| 6a | Response is comprehensive, not partial or incomplete |
| 6b | Shows depth of knowledge or understanding |
| 6c | Answers beyond the question's scope to provide helpful context |

### 7. Scientific Accuracy
| Criterion | Description |
|-----------|-------------|
| 7a | The information appears scientifically robust |
| 7b | Response meets scientific expectations based on sources |
| 7c | Response does not contain obvious errors or contradictions |

---

## New Files Created

### `evaluation.py`

The self-evaluation module implementing the expert criteria framework.

**Key Functions:**

| Function | Description |
|----------|-------------|
| `evaluate_response()` | Main evaluation function - prompts LLM and parses scores |
| `print_evaluation()` | Pretty-print evaluation results with visual progress bar |
| `get_evaluation_summary()` | One-line summary with grade (Excellent/Good/Adequate/etc.) |
| `_build_evaluation_prompt()` | Constructs the structured evaluation prompt |
| `_parse_evaluation_response()` | Parses JSON scores from LLM response |

**Constants:**
- `EVALUATION_CRITERIA` - Dictionary defining all 7 dimensions and 21 sub-criteria
- `EVAL_MODEL` - Default model for evaluation (llama-3.3-70b-versatile)
- `DIMENSION_DESCRIPTIONS` - Human-readable descriptions for each dimension

---

## Modified Files

### `main.py`

**Added `--eval` flag to `ask` command:**
```python
ask_parser.add_argument("--eval", "-e", action="store_true", 
                        help="Run self-evaluation on the generated answer")
```

**Updated command handler:**
```python
if args.eval:
    eval_result = evaluation.evaluate_response(
        question=result["question"],
        answer=result["answer"],
        passages=result["passages"],
        verbose=args.verbose
    )
    evaluation.print_evaluation(eval_result)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 4: SELF-EVALUATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   From Phase 3: Generated Answer + Question + Passages                      │
│        │                                                                    │
│        ▼                                                                    │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  STEP 1: BUILD EVALUATION PROMPT                                 │     │
│   │                                                                   │     │
│   │  • Original question                                              │     │
│   │  • Source passages with metadata                                  │     │
│   │  • Generated response to evaluate                                 │     │
│   │  • 21 evaluation criteria (7 dimensions × 3 sub-criteria)        │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│        │                                                                    │
│        ▼                                                                    │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  STEP 2: LLM EVALUATION (Separate Conversation)                  │     │
│   │                                                                   │     │
│   │  Llama 3.3 70B evaluates with low temperature (0.1)              │     │
│   │  Returns JSON: { scores: {1a: 0/1, 1b: 0/1, ...}, feedback: ""}  │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│        │                                                                    │
│        ▼                                                                    │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  STEP 3: SCORE AGGREGATION                                       │     │
│   │                                                                   │     │
│   │  • Calculate dimension scores (0-3 each)                         │     │
│   │  • Calculate total score (0-21)                                   │     │
│   │  • Calculate percentage and grade                                 │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│        │                                                                    │
│        ▼                                                                    │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  STEP 4: OUTPUT VISUALIZATION                                    │     │
│   │                                                                   │     │
│   │  📊 Overall Score: 19/21 (90.5%)                                 │     │
│   │     [██████████████████░░]                                        │     │
│   │                                                                   │     │
│   │  📋 Dimension Breakdown:                                          │     │
│   │    ✅ Context: 3/3  [✓ ✓ ✓]                                       │     │
│   │    ⚠️ Structure: 2/3  [✓ ✓ ✗]                                     │     │
│   │    ...                                                            │     │
│   │                                                                   │     │
│   │  💬 Feedback: <LLM explanation>                                   │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Usage Examples

### Basic Ask with Evaluation
```bash
python main.py ask -q "How will climate change affect wheat production?" --eval
```

### Verbose Mode
```bash
python main.py ask -q "What are drought adaptation strategies?" --eval -v
```

### With All Options
```bash
python main.py ask -q "Your question" \
    -k 10 \
    --source FAO \
    -m hybrid \
    --eval \
    -v \
    --show-passages
```

---

## Sample Output

```
======================================================================
 SELF-EVALUATION (7 Expert Dimensions)
======================================================================

📊 Overall Score: 19/21 (90.5%)
   [██████████████████░░]

📋 Dimension Breakdown:
--------------------------------------------------
  ✅ Context: 3/3  [✓ ✓ ✓]
  ⚠️ Structure: 2/3  [✓ ✓ ✗]
  ✅ Use of Language: 3/3  [✓ ✓ ✓]
  ✅ Use of Citations: 3/3  [✓ ✓ ✓]
  ⚠️ Specificity: 2/3  [✓ ✓ ✗]
  ✅ Comprehensiveness: 3/3  [✓ ✓ ✓]
  ✅ Scientific Accuracy: 3/3  [✓ ✓ ✓]

--------------------------------------------------
💬 Feedback: The response provides a comprehensive and well-structured 
answer to the question, effectively utilizing the provided sources. 
It meets most criteria, demonstrating good understanding of the topic. 
However, it lacks bullet points and doesn't explicitly address the 
absence of location-specific information when not applicable.

📈 Eval Tokens: 2192
======================================================================
```

---

## Grading Scale

| Score Range | Grade | Description |
|-------------|-------|-------------|
| 90-100% | Excellent | Meets nearly all expert criteria |
| 75-89% | Good | Strong response with minor gaps |
| 60-74% | Adequate | Acceptable but could be improved |
| 40-59% | Needs Improvement | Significant gaps in quality |
| 0-39% | Poor | Does not meet expert expectations |

---

## Technical Details

### Evaluation Prompt Design
- Provides complete context: question, passages, and answer
- Lists all 21 criteria explicitly
- Requests JSON output for reliable parsing
- Uses low temperature (0.1) for consistent scoring

### Score Parsing
- Handles JSON wrapped in markdown code blocks
- Graceful fallback on parsing errors
- Validates all expected score keys

### Visual Output
- Progress bar showing percentage
- Color-coded status icons (✅ ⚠️ ❌)
- Checkmarks for individual sub-criteria
- Token usage tracking

---

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model` | llama-3.3-70b-versatile | LLM for evaluation |
| `temperature` | 0.1 | Low for consistent scoring |
| `max_tokens` | 1024 | Max evaluation response length |

---

## Next Phases

| Phase | Feature | Status |
|-------|---------|--------|
| **5a** | Multi-turn Conversations | 📋 Planned |
| **5b** | User Feedback System | 📋 Planned |
| **5c** | OCR Support | 📋 Planned |
| **5d** | Agentic Iterative Planning | 📋 Planned |
| **5e** | Climate Data API Integration | 📋 Planned |
