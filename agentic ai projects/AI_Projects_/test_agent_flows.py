"""Quick smoke tests for the two independent agent workflows."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def test_p5():
    m=load('p5_verifier',ROOT/'M1-P5-hallucination-assistant'/'verifier.py')
    supported=m.run_agent('Explain photosynthesis')
    unsupported=m.run_agent('What is quantum computing and who invented it?')
    assert supported['label']=='High confidence'
    assert unsupported['label']=='Potentially unsupported'
    assert len(supported['agent_trace'])>=4

def test_p6():
    m=load('p6_news',ROOT/'M1-P6-personalized-news'/'news.py')
    result=m.build_digest(['AI','Science'])
    assert result['total']>=1
    assert len(result['agent_trace'])>=4
    assert all(story['url'].startswith('https://') for stories in result['groups'].values() for story in stories)

if __name__=='__main__':
    test_p5(); test_p6(); print('All agent-flow smoke tests passed.')
