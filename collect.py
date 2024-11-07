from bs4 import BeautifulSoup
import pandas as pd
import os

d= {'element':[],'text':[]}
for file in os.listdir("data"):
    try:
        with open("data/elements.html")as f:
             html_doc=f.read()
        soup= BeautifulSoup(html_doc, 'html.parser')
        
        
        for tag in soup.find_all(True):
            d['element'].append(tag.name)
            d['id'].append(tag.get('id'))
            class_name = tag.get('class')[0] if tag.get('class') else ''
            d['class'].append(class_name)
            d['text'].append(tag.get_text(strip=True))

    
    except Exception as e:
        print(e)

# print(d['id'])
        
df=pd.DataFrame(data=d)
df.to_csv(f"example1.csv")
    