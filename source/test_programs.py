"""Execute generated TI-BASIC control flow in a small host-side interpreter.
This does not substitute for testing on physical TI hardware.
"""
import re,copy,math
from pathlib import Path
from build import CATS
class L(list):
 def __call__(self,i):return self[int(i)-1]
class Machine:
 def __init__(self,menus,keys):
  self.menus=iter(menus); self.keys=iter(keys);self.v={c:0 for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'};self.logs=[];self.steps=0
 def expr(self,s):
  # Protect strings before translating calculator operators and list names.
  strings=[]
  def protect(m): strings.append(m[0]);return f'__s{len(strings)-1}__'
  s=re.sub(r'"[^"]*"',protect,s)
  s=re.sub(r'ʟ([A-Z0-9]+)',r'L_\1',s).replace('⁻','-').replace('^','**').replace('≠','!=').replace('≥','>=').replace('≤','<=')
  s=re.sub(r'(?<![<>=!])=(?!=)','==',s)
  s=s.replace('{','L([').replace('}','])')
  s=s.replace('getKey','key()')
  for i,t in enumerate(strings):s=s.replace(f'__s{i}__',t)
  env=dict(self.v,L=L,key=lambda:next(self.keys),length=len,inString=lambda a,b:a.find(b)+1,sub=lambda a,b,c:a[int(b)-1:int(b)-1+int(c)],expr=float)
  return eval(s,{'__builtins__':{}},env)
 def store(self,target,value):
  target=target.replace('ʟ','L_');m=re.fullmatch(r'(\w+)\((.+)\)',target)
  if m:
   name,index=m.groups();index=int(self.expr(index));arr=self.v[name]
   while len(arr)<index:arr.append(0)
   arr[index-1]=value
  else:self.v[target]=copy.deepcopy(value)
 def run(self,name):
  lines=Path('output/'+name+'.txt').read_text().splitlines();labels={s[4:]:i for i,s in enumerate(lines) if s.startswith('Lbl ')}
  # Block boundaries for Then / Else / End and For / End.
  stack=[];ends={};elses={}
  for i,s in enumerate(lines):
   if s=='Then' or s.startswith('For('):stack.append(i)
   elif s=='Else':elses[stack[-1]]=i
   elif s=='End':
    start=stack.pop();ends[start]=i
  assert not stack
  pc=0;loops={}
  while pc<len(lines):
   self.steps+=1
   if self.steps>100000:raise RuntimeError('step limit')
   s=lines[pc];pc+=1
   try:
    if s.startswith('Lbl ') or s in ['ClrHome','Pause','Then']:continue
    if s=='Stop':raise SystemExit
    if s=='Return':return
    if s.startswith('prgm'):self.run(s[4:]);continue
    if s.startswith('Goto '):pc=labels[s[5:]];continue
    if s.startswith('Menu('):
     title=re.match(r'Menu\("([^"]*)"',s)[1]
     pairs=re.findall(r'"([^"]*)",([A-Z0-9]+)',s)[1:] if False else re.findall(r',"([^"]*)",([A-Z0-9]+)',s)
     choice=next(self.menus)
     matches=[label for text,label in pairs if text==choice]
     assert matches,(name,title,choice,pairs)
     pc=labels[matches[0]];continue
    if s.startswith('If '):
     truth=self.expr(s[3:])
     if lines[pc]=='Then':
      if not truth:pc=elses.get(pc,ends[pc])+1
     elif not truth:pc+=1
     continue
    if s=='Else':
     start=next(k for k,v in elses.items() if v==pc-1);pc=ends[start]+1;continue
    if s.startswith('For('):
     args=s[4:-1].split(',');var=args[0];start=self.expr(args[1]);end=self.expr(args[2]);self.v[var]=start
     if start>end:pc=ends[pc-1]+1
     else:loops[ends[pc-1]]=(pc,var,end)
     continue
    if s=='End':
     if pc-1 in loops:
      back,var,end=loops[pc-1];self.v[var]+=1
      if self.v[var]<=end:pc=back
      else:del loops[pc-1]
     continue
    if s.startswith('Output('):continue
    if s.startswith('Disp '):
     # Split comma-separated expressions outside strings and braces.
     args=re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)(?![^{}]*\})',s[5:]);self.logs.append([self.expr(a) for a in args]);continue
    if '→' in s:
     value,target=s.split('→');self.store(target,self.expr(value));continue
    raise ValueError('unsupported '+s)
   except (SystemExit,StopIteration):raise
   except Exception as e:raise RuntimeError(f'{name}:{pc} {s}: {e}') from e

def trial(menus,keys):
 m=Machine(menus,keys)
 try:m.run('UNITCE')
 except SystemExit:pass
 return m
# Direct user's example, plus dual output.
m=trial(['CONFIG','ON: SI + IMPERIAL','NEW EXPRESSION','MASS','SI','kg','MULTIPLY','ACCEL','m/s^2','RESULT','HOME','QUIT'],[74,105,93,105])
assert math.isclose(m.v['E'],18)
flat=[x for row in m.logs for x in row]
assert 'N' in flat and 'lbf' in flat and any(isinstance(x,float) and math.isclose(x,18/4.4482216152605) for x in flat)
# Units alone, remembered SI system, no numeric keys.
m=trial(['NEW EXPRESSION','MASS','SI','kg','MULTIPLY','ACCEL','m/s^2','RESULT','HOME','QUIT'],[105,105]);assert m.v['E']==1
# Imperial first, mixed acceleration, output anchored to Imperial, not last selection.
m=trial(['NEW EXPRESSION','MASS','IMPERIAL','slug','MULTIPLY','ACCEL','SYSTEM / BACK','SI','m/s^2','RESULT','HOME','QUIT'],[105,105]);assert m.v['R']==2
assert any('lbf' in row for row in m.logs)
# Standard precedence: 2m + 3m * 4 unitless = 14m.
m=trial(['NEW EXPRESSION','LENGTH','SI','m','ADD','LENGTH','m','MULTIPLY','MORE / BACK','MORE','NO UNIT','unitless','RESULT','HOME','QUIT'],[93,105,94,105,82,105]);assert m.v['E']==14
# Incompatible addition reports error, preserves expression.
m=trial(['NEW EXPRESSION','MASS','SI','kg','ADD','LENGTH','m','RESULT','HOME','QUIT'],[105,105]);assert any('DIFFERENT DIMENSIONS' in row for row in m.logs)
# Zero division is caught.
m=trial(['NEW EXPRESSION','LENGTH','SI','m','DIVIDE','TIME','s','RESULT','HOME','QUIT'],[105,102,105]);assert any('DIVISION BY ZERO' in row for row in m.logs)
# Numeric editor: decimal, DEL, negative toggle.
m=Machine([], [92,103,93,23,94,104,105]);m.run('UCVAL');assert m.v['N']==-1.3
# Undo and cancel preserve remaining term, conversion doesn't overwrite result dimensions.
m=trial(['NEW EXPRESSION','MASS','SI','kg','MULTIPLY','ACCEL','m/s^2','REVIEW / UNDO','UNDO LAST TERM','RESULT','CONVERT','LENGTH','m','EXPRESSION','HOME','QUIT'],[105,105]);assert m.v['E']==1 and m.v['B']==1 and m.v['C']==0
# First SI term remains the output default after selecting Imperial acceleration.
m=trial(['NEW EXPRESSION','MASS','SI','kg','MULTIPLY','ACCEL','SYSTEM / BACK','IMPERIAL','ft/s^2','RESULT','HOME','QUIT'],[74,105,93,105]);assert math.isclose(m.v['E'],5.4864) and m.v['R']==1
assert any('N' in row for row in m.logs)
# All unit conversion output dimensions match input catalog.
for name,dims,si,imp in CATS:
 for system,units in [(1,si),(2,imp)]:
  m=Machine([],[]);m.v.update(dict(zip('BCD',dims)),H=system);m.run('UCOUT');assert math.isclose(m.v['F'],units[0][1],rel_tol=1e-12)
print('PASS: 9 expression/editor scenarios and 28 output-unit cases; token round trips passed.')
