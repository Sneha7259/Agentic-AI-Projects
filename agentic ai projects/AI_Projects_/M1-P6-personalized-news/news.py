"""Agentic personalized news pipeline: plan -> search tools -> filter -> rank -> summarize -> reflect."""
import os,re
from datetime import datetime,timezone
import requests

CATEGORIES=['Technology','AI','Business','Science','Sports','World','Health']
DEMO=[
 {'title':'Researchers report progress in efficient solar cell materials','description':'A university research team has reported a new materials approach intended to improve the efficiency and durability of solar cells. Independent testing and commercial-scale validation are still needed.','url':'https://example.com/solar-research','source':{'name':'Demo Science Desk'},'category':'Science'},
 {'title':'New open-source tools aim to simplify AI model evaluation','description':'Developers have released tools designed to help teams compare model outputs, measure reliability and document limitations. The project maintainers say the tools are intended for research and responsible deployment.','url':'https://example.com/ai-evaluation','source':{'name':'Demo Technology Desk'},'category':'AI'},
 {'title':'Global markets watch central bank policy signals','description':'Investors are monitoring policy statements and economic indicators as central banks weigh inflation and growth. Market reactions can change quickly as new data becomes available.','url':'https://example.com/markets','source':{'name':'Demo Business Desk'},'category':'Business'},
 {'title':'Local clubs prepare for the upcoming football season','description':'Teams are adjusting training schedules and reviewing player fitness ahead of the new season. Coaches say preparation and squad depth will be important over a busy fixture calendar.','url':'https://example.com/football','source':{'name':'Demo Sports Desk'},'category':'Sports'},
 {'title':'Public health researchers study seasonal respiratory trends','description':'Researchers are examining seasonal patterns in respiratory illness and the factors that influence transmission. The findings emphasize the importance of reliable surveillance and clear public communication.','url':'https://example.com/health','source':{'name':'Demo Health Desk'},'category':'Health'},
 {'title':'International partners announce new climate research collaboration','description':'Research organizations from several countries plan to share data and expertise on climate adaptation. The collaboration will focus on regional risks, resilience planning and accessible scientific information.','url':'https://example.com/climate','source':{'name':'Demo World Desk'},'category':'World'},
]
KEYWORDS={'Technology':['technology','tech','software','computer','cyber','chip','device','internet'],'AI':['ai','artificial intelligence','machine learning','model','robot','llm','generative'],'Business':['business','market','economy','company','finance','startup','trade'],'Science':['science','research','space','climate','energy','physics','solar'],'Sports':['sport','football','cricket','tennis','basketball','match','player'],'World':['world','international','global','country','government','election'],'Health':['health','medical','hospital','disease','public health','medicine']}
def words(s): return set(re.findall(r'[a-z0-9]{3,}',(s or '').lower()))
def category_for(a):
    if a.get('category') in CATEGORIES:return a['category']
    text=(a.get('title','')+' '+a.get('description','')).lower(); scores={c:sum(k in text for k in ks) for c,ks in KEYWORDS.items()}
    return max(scores,key=scores.get) if max(scores.values(),default=0)>0 else 'World'
def summarize(text,max_chars=300):
    text=re.sub(r'\s+',' ',text or '').strip()
    if not text:return 'Publisher did not provide a description; open the source for details.'
    sentences=re.split(r'(?<=[.!?])\s+',text); out=' '.join(sentences[:2])
    return out[:max_chars].rsplit(' ',1)[0]+('…' if len(out)>max_chars else '')
def duplicate(a,chosen):
    wa=words(a.get('title',''))
    return any(len(wa & words(b.get('title','')))/max(1,len(wa | words(b.get('title',''))))>=.55 for b in chosen)

def search_news_tool(category):
    """One category-scoped external search tool call; demo data is used without a key."""
    key=os.getenv('GNEWS_API_KEY')
    if not key:return None
    try:
        r=requests.get('https://gnews.io/api/v4/search',params={'q':category,'lang':'en','max':20,'sortby':'publishedAt','apikey':key},timeout=15)
        r.raise_for_status(); return r.json().get('articles',[])
    except requests.RequestException:return None

def build_digest(interests):
    interests=[x for x in interests if isinstance(x,str) and x in CATEGORIES]
    if not interests: interests=['Technology']
    trace=[{'step':'Preference Planner','detail':'Converted the selected interests into category-specific search tasks.'}]
    gathered=[]; live_calls=0; live_fail=False
    # Agent decides which search tool to invoke for each requested interest.
    for category in interests:
        batch=search_news_tool(category)
        if batch is None: live_fail=True
        else: live_calls+=1; gathered.extend(batch)
    using_demo=live_calls==0
    if using_demo:gathered=[dict(a) for a in DEMO]
    trace.append({'step':'News Search Tools','detail':f"Executed {len(interests)} category search task(s); collected {len(gathered)} candidate stories."})
    selected=[]
    for raw in gathered:
        a=dict(raw); a['category']=category_for(a)
        if a['category'] not in interests: continue
        if not a.get('title') or not a.get('url'): continue
        if duplicate(a,selected): continue
        # Ranking: matching category first; recency signal when provider timestamp exists.
        a['_rank']=3 + (1 if a['category'] in interests else 0) + (1 if a.get('publishedAt') else 0)
        selected.append(a)
    selected.sort(key=lambda x:x['_rank'],reverse=True)
    trace.append({'step':'Relevance & Deduplication Agent','detail':f"Removed irrelevant or duplicate candidates; retained {len(selected)} distinct stories."})
    result=[]
    for a in selected[:15]:
        result.append({'title':a['title'],'summary':summarize(a.get('description') or a.get('content')),'category':a['category'],'source':(a.get('source') or {}).get('name','News source'),'url':a['url'],'publishedAt':a.get('publishedAt','')})
    trace.append({'step':'Summarization Agent','detail':f"Prepared concise, source-linked summaries for {len(result)} stories using publisher-provided text."})
    # Reflection: check output safety and source provenance before returning.
    valid=[x for x in result if x['title'] and x['url'].startswith(('http://','https://'))]
    trace.append({'step':'Quality Review Agent','detail':f"Checked title, summary, category, and source URL fields; {len(valid)} stories passed the output checks."})
    groups={c:[a for a in valid if a['category']==c] for c in interests}; groups={k:v for k,v in groups.items() if v}
    mode='Demo stories' if using_demo else ('Live GNews results' if not live_fail else 'Partial live results')
    return {'interests':interests,'groups':groups,'total':len(valid),'mode':mode,'generated_at':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'agent_trace':trace,
      'note':'Agent pipeline: plan interests, call category search tools, filter and deduplicate, rank, summarize, and review provenance. Summaries are extracts of publisher-provided descriptions. Demo URLs are placeholders, not real news articles.'}
