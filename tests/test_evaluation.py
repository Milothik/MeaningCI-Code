import math
import pytest
from meaningci_code.providers import jsd, parse_response, ProviderError, score_pair
from meaningci_code.analysis import metrics, paired

def test_jsd():
    assert jsd({'Y':1,'N':0},{'Y':0,'N':1})==1
    assert jsd({'Y':.4,'N':.6},{'Y':.4,'N':.6})==0

def native(probabilities):
    return {'model':'jev-test','request_id':'test','answers':{'q':{'probabilities':probabilities,'choice':max(probabilities,key=probabilities.get),'confidence':.8}}}

def test_native_validation_and_rounding():
    request = {'questions':{'q':{'criteria':{'Y':'yes','N':'no','U':'unknown'}}}}
    result = parse_response(request,native({'Y':.8,'N':.1,'U':.09}))
    assert sum(result['q']['probabilities'].values())==pytest.approx(1)
    for raw in ({'Y':1.,'N':.2,'U':0},{'Y':float('nan'),'N':.2,'U':0},{'Y':True,'N':0,'U':0}):
        with pytest.raises(ProviderError):parse_response(request,native(raw))
    with pytest.raises(ProviderError):parse_response(request,{'model':'test','request_id':'r','answers':{}})

def test_uncertain_is_not_pass_and_confident_flip_detects():
    vector=lambda y,n,u:{'probabilities':{'YES':y,'NO':n,'UNKNOWN':u},'top':max({'YES':y,'NO':n,'UNKNOWN':u},key={'YES':y,'NO':n,'UNKNOWN':u}.get)}
    direct={'probabilities':{'SAME':.9,'CHANGED':.05,'UNKNOWN':.05},'top':'SAME'}
    out=score_pair({'A_00':vector(.4,.3,.3),'B_00':vector(.4,.3,.3),'direct':direct},1)
    assert out['label_prediction'] is None
    out=score_pair({'A_00':vector(.9,.05,.05),'B_00':vector(.05,.9,.05),'direct':direct},1)
    assert out['label_prediction'] is True

def test_abstention_and_missing_conservative_metrics():
    rows=[{'program':'a','gold_label':True,'predictions':{'a':True,'b':False}}, {'program':'b','gold_label':False,'predictions':{'a':None,'b':False}}, {'program':'c','gold_label':True,'predictions':{}}]
    m=metrics(rows,'a')
    assert m['correct']==1 and m['accuracy']==1/3 and m['abstained']==1 and m['missing']==1
    assert paired(rows,'a','b',100)['mcnemar_exact_p']==1

