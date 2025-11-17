# ✔ 已成功运行代码，复制可直接使用
from bs4 import BeautifulSoup
import json, re

file_path = 'kebiao.html'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

results=[]
allowed=["7号楼A","7号楼B","7号楼C","综合馆-羽毛球场"]
sections=["0102","0304","0506","0708","0910","1112"]
weekdays=["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]

table=soup.find("table",{"id":"timetable"})
rows=table.find_all("tr")[2:]

for row in rows:
    tds=row.find_all("td")
    if not tds: continue
    cname=tds[0].get_text(strip=True)
    for i,td in enumerate(tds[1:],start=1):
        divs=td.find_all("div",class_="kbcontent1")
        if not divs: continue
        wd=(i-1)//6; si=(i-1)%6
        if si>=5: continue
        weekday=weekdays[wd]; section=sections[si]
        for d in divs:
            lines=list(d.stripped_strings)
            if len(lines)<4: continue
            course=lines[0]; cls=lines[1]
            week_raw=re.findall(r"\((.*?)\)", lines[3])
            loc=lines[4] if len(lines)>4 else ""
            bld=None
            for b in allowed:
                if loc.startswith(b): bld=b; break
            if not bld: continue
            weeks=[]
            if week_raw:
                for part in week_raw[0].split(","):
                    nums=re.findall(r"(\d+)-(\d+)",part)
                    if nums:
                        a,b=map(int,nums[0]); weeks+=list(range(a,b+1)); continue
                    nums=re.findall(r"\d+",part)
                    if nums: weeks+=list(map(int,nums))
            rm=re.search(r"(\d{3})$",loc)
            room=rm.group(1) if rm else ""
            floor=int(room[0]) if room else 1
            for w in weeks:
                results.append(dict(building=bld,floor=floor,room_no=room,course_name=course,
                                    class_name=cls,section=section,week=w,weekday=weekday))

out="course_data2.json"
with open(out,"w",encoding="utf-8") as f: json.dump(results,f,ensure_ascii=False,indent=2)

print(len(results), out)
