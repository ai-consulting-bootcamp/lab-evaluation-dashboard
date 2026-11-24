import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
np.random.seed(42)
base=Path(__file__).parent
categories={'reasoning':(2,3),'knowledge':(4,2),'code':(3,3),'instruction_following':(5,2),'tool_calling':(3,3)}
models=['gpt-4','gpt-4-turbo','gpt-3.5-turbo','claude-3-opus']
rows=[]
for i in range(90):
    day=date(2026,11,24)-timedelta(days=90-i)
    for category,(a,b) in categories.items():
        for _ in range(np.random.randint(5,16)):
            model=np.random.choice(models)
            score=np.clip(np.random.beta(a,b)*100+np.random.normal(0,5),0,100)
            rows.append((len(rows)+1,category,round(score,2),model,day.isoformat()))
df=pd.DataFrame(rows,columns=['evaluation_id','category','score','model_version','date'])
df.to_csv(base/'evaluation_data.csv',index=False)
clean=df.dropna(subset=['score','category']).copy()
assert clean.evaluation_id.is_unique and clean.score.between(0,100).all() and len(clean)>=100
assert set(clean.category)==set(categories)
assert pd.to_datetime(clean.date,format='%Y-%m-%d').notna().all()
clean['score_range']=np.minimum((clean.score//10)*10,90).astype(int)
clean.to_csv(base/'evaluation_data_clean.csv',index=False)
print(f'Rows: {len(clean)}; overall mean: {clean.score.mean():.2f}; dates: {clean.date.min()} to {clean.date.max()}')
print(clean.groupby('category').score.agg(['count','mean']).round(2).to_string())
