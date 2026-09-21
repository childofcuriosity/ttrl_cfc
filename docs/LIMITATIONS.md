# Scope and next measurements

The format-only intervention is directly supported by the preserved
Qwen2.5-Math-1.5B / MATH-TTT log. Its result establishes the contribution of
format compliance in that training and evaluation setup.

The next experiments should measure how the relationship changes across:

1. answer extractors that accept equivalent formats rather than requiring
   `\\boxed{...}`;
2. exact-match, symbolic-equivalence and human-judged evaluation;
3. multiple random seeds;
4. AMC, AIME and CommonsenseQA under the same explicit reward-mode switch;
5. instruction-tuned and base models with matched decoding settings.

The Llama-3.1-8B-Instruct run displayed unstable training dynamics in the
preserved logs, so it is recorded as diagnostic evidence rather than included
in the headline estimate. The CommonsenseQA run log is available in the local
archive, while its original launcher remains a recovery target.

The 0.6625 full-TTRL value and approximately 0.3200 starting value were recovered
from the contemporaneous experiment record. The format-only value 0.6285 and
its complete stepwise trajectory are backed by the preserved training log.
