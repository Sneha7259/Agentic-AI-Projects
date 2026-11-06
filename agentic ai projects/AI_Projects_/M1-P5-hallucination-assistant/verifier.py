"""Agentic evidence assistant: plan -> retrieve -> verify -> critique -> answer/abstain.

The demo tools are deterministic and inspectable. Confidence is a heuristic evidence score,
not a calibrated probability or a guarantee of truth.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone

EVIDENCE = [
 {"id":"E1","title":"Water cycle","text":"The water cycle describes the continuous movement of water between Earth's surface and the atmosphere. Major processes include evaporation, condensation, precipitation, and collection.","source":"Demo knowledge base — Earth science"},
 {"id":"E2","title":"Photosynthesis","text":"Photosynthesis is the process by which green plants, algae, and some bacteria convert light energy into chemical energy. In plants, it uses carbon dioxide and water and releases oxygen.","source":"Demo knowledge base — Biology"},
 {"id":"E3","title":"Python programming language","text":"Python is a high-level, general-purpose programming language known for readable syntax. It is commonly used in web development, automation, data analysis, and machine learning.","source":"Demo knowledge base — Computing"},
 {"id":"E4","title":"Computer networks","text":"A computer network is a group of interconnected computing devices that communicate and share resources. Common network types include LANs and WANs.","source":"Demo knowledge base — Computing"},
 {"id":"E5","title":"Renewable energy","text":"Renewable energy comes from sources that are naturally replenished, such as sunlight, wind, and flowing water. Solar and wind power are examples of renewable energy technologies.","source":"Demo knowledge base — Energy"},
]
STOP=set("the a an is are was were be been being of to in on for with and or by from how what why when where which who explain define tell me about can does do did give me".split())
def tokens(s): return [w for w in re.findall(r"[a-zA-Z]{3,}",s.lower()) if w not in STOP]

def retrieve_evidence(query, limit=4):
    q=set(tokens(query)); found=[]
    for item in EVIDENCE:
        words=set(tokens(item['title']+' '+item['text'])); overlap=len(q & words)
        if overlap: found.append((overlap/max(1,len(q)),item))
    return [dict(x) for _,x in sorted(found,key=lambda z:z[0],reverse=True)[:limit]]

def verify_evidence(query, evidence):
    q=set(tokens(query)); checks=[]
    for item in evidence:
        words=set(tokens(item['title']+' '+item['text']))
        checks.append({"evidence_id":item['id'],"coverage":round(len(q & words)/max(1,len(q)),3),"matched_terms":sorted(q & words)})
    return checks

def critique_answer(query, evidence, checks):
    if not evidence: return {"pass":False,"reason":"No evidence was retrieved; answering would require unsupported generation."}
    best=max((c['coverage'] for c in checks),default=0)
    if best < .40: return {"pass":False,"reason":"Retrieved evidence is only weakly related to the question."}
    if len(tokens(query)) >= 5 and best < .50:
        return {"pass":False,"reason":"Evidence coverage is too low for a multi-part question."}
    return {"pass":True,"reason":"At least one retrieved passage has meaningful lexical support. This is a relevance check, not fact verification."}

def run_agent(question):
    trace=[]
    trace.append({"step":"Planner","detail":"Break the request into a topic query and identify the evidence needed before drafting."})
    # Tool 1: evidence retrieval
    evidence=retrieve_evidence(question)
    trace.append({"step":"Evidence Retrieval Tool","detail":f"Searched the local trusted-source demo library and returned {len(evidence)} candidate passage(s)."})
    # Tool 2: claim/evidence alignment
    checks=verify_evidence(question,evidence)
    trace.append({"step":"Evidence Verification Tool","detail":"Compared question terms with each passage and measured support coverage."})
    # Agent reflection: decide whether to answer or abstain
    critique=critique_answer(question,evidence,checks)
    trace.append({"step":"Critic / Reflection Agent","detail":critique['reason']})
    if not critique['pass']:
        answer="I cannot answer this reliably from the evidence currently available. I am abstaining rather than inventing information."
        label="Potentially unsupported"; score=max([c['coverage'] for c in checks],default=0)
    else:
        best_i=max(range(len(evidence)),key=lambda i:checks[i]['coverage'])
        best=evidence[best_i]; score=checks[best_i]['coverage']
        answer=best['text']
        if score >= .55: label="High confidence"
        elif score >= .30: label="Inferred information"
        else: label="Potentially unsupported"
        if label == "Potentially unsupported":
            answer="The available evidence is related but insufficient to support a reliable answer. " + answer
    confidence=round(min(96,max(8,score*100)))
    trace.append({"step":"Response Policy","detail":"Returned a grounded response with provenance and uncertainty label; unsupported cases are explicitly withheld."})
    return {"answer":answer,"label":label,"confidence":confidence,
      "explanation":critique['reason']+" The score is based on lexical evidence coverage and is not a calibrated probability.",
      "evidence":evidence,"verification":checks,"agent_trace":trace,
      "disclaimer":"Prototype agent using a small local demo corpus. Add vetted sources, claim-level semantic/NLI checks, calibrated evaluation, and human review before high-stakes use.",
      "generated_at":datetime.now(timezone.utc).isoformat()}

# Backward-compatible entry point
def answer_question(question): return run_agent(question)
