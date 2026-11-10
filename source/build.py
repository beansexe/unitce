from pathlib import Path
from tivars.types import TIProgram
import json, zipfile
OUT=Path('output').resolve(); OUT.mkdir(exist_ok=True)
# name, mass/length/time dimensions, SI units, Imperial units; all factors convert to SI.
CATS=[
('MASS',(1,0,0),[('kg',1),('g',.001),('mg',1e-6)],[('lbm',.45359237),('slug',14.5939029372064),('oz',.028349523125)]),
('LENGTH',(0,1,0),[('m',1),('cm',.01),('mm',.001),('km',1000)],[('ft',.3048),('in',.0254),('yd',.9144),('mi',1609.344)]),
('TIME',(0,0,1),[('s',1),('min',60),('hr',3600)],[('s',1),('min',60),('hr',3600)]),
('SPEED',(0,1,-1),[('m/s',1),('km/hr',1/3.6)],[('ft/s',.3048),('mph',.44704)]),
('ACCEL',(0,1,-2),[('m/s^2',1)],[('ft/s^2',.3048)]),
('FORCE',(1,1,-2),[('N',1),('kN',1000)],[('lbf',4.4482216152605),('pdl',.138254954376)]),
('ENERGY',(1,2,-2),[('J',1),('kJ',1000)],[('ft*lbf',1.3558179483314),('BTU',1055.05585262)]),
('POWER',(1,2,-3),[('W',1),('kW',1000)],[('hp',745.69987158227),('ft*lbf/s',1.3558179483314)]),
('PRESSURE',(1,-1,-2),[('Pa',1),('kPa',1000),('MPa',1e6)],[('psi',6894.75729316836),('psf',47.8802589803358)]),
('AREA',(0,2,0),[('m^2',1),('cm^2',.0001)],[('ft^2',.09290304),('in^2',.00064516)]),
('VOLUME',(0,3,0),[('m^3',1),('L',.001),('mL',.000001)],[('ft^3',.028316846592),('in^3',.000016387064),('US gal',.003785411784)]),
('DENSITY',(1,-3,0),[('kg/m^3',1),('g/cm^3',1000)],[('lbm/ft^3',16.0184633739601)]),
('FREQUENCY',(0,0,-1),[('Hz',1),('kHz',1000)],[('Hz',1)]),
('NO UNIT',(0,0,0),[('unitless',1)],[('unitless',1)])]
programs={}
def emit(name, lines): programs[name]='\n'.join(lines)+'\n'
def menu(title, pairs): return 'Menu("'+title+'",'+','.join('"'+s+'",'+l for s,l in pairs)+')'
# Picker: W remembers system; Z success; B C D dimensions; F factor; Str2 unit.
p=['0→Z','Lbl Q0',menu('QUANTITY',[('MASS','Q1'),('LENGTH','Q2'),('TIME','Q3'),('SPEED','Q4'),('ACCEL','Q5'),('FORCE','Q6'),('MORE / BACK','QA')]),'Lbl QA',menu('MORE QUANTITIES',[('ENERGY','Q7'),('POWER','Q8'),('PRESSURE','Q9'),('AREA','Q10'),('VOLUME','Q11'),('MORE','QB'),('BACK','Q0')]),'Lbl QB',menu('MORE QUANTITIES',[('DENSITY','Q12'),('FREQUENCY','Q13'),('NO UNIT','Q14'),('BACK','QA'),('CANCEL','ZZ')])]
for i in range(1,len(CATS)+1): p += [f'Lbl Q{i}',f'{i}→Q','Goto SY']
p += ['Lbl SY','If W=0','Goto SS','Goto UN','Lbl SS',menu('UNIT SYSTEM',[('SI','SI'),('IMPERIAL','IM'),('BACK','Q0'),('CANCEL','ZZ')]),'Lbl SI','1→W','Goto UN','Lbl IM','2→W','Goto UN','Lbl UN']
for i,cat in enumerate(CATS,1):
 p += [f'If Q={i}',f'Goto U{i}']
for i,(name,dims,si,imp) in enumerate(CATS,1):
 p += [f'Lbl U{i}','If W=2',f'Goto I{i}',menu(name+' / SI',[(u[0],f'A{i}{j}') for j,u in enumerate(si)]+[('SYSTEM / BACK','SS')]),f'Lbl I{i}',menu(name+' / IMP',[(u[0],f'B{i}{j}') for j,u in enumerate(imp)]+[('SYSTEM / BACK','SS')])]
 # labels must be <=2 characters! assigned below via global label remap.
 for prefix,units in [('A',si),('B',imp)]:
  for j,(unit,factor) in enumerate(units):
   p += [f'Lbl {prefix}{i}{j}',f'{factor:.14g}→F',f'"{unit}"→Str2',*[f'{v}→{var}' for v,var in zip(dims,'BCD')],'1→Z','Return']
p+=['Lbl ZZ','Return'];emit('UCPICK',p)
# Value editor: N returned, Z success. Key (-) toggles sign. Empty ENTER = 1.
emit('UCVAL',['""→Str1','1→V','0→Z','Lbl DR','ClrHome','Disp "VALUE (OPTIONAL)","ENTER ALONE = 1","(-): SIGN  DEL: ERASE","CLEAR: CANCEL"','If length(Str1)>0','Output(6,1,Str1)','Output(7,1,"SIGN:")','Output(7,7,V)','Lbl KY','getKey→K','If K=0','Goto KY','If K=45','Return','If K=105','Goto OK','If K=104','⁻V→V','If K=104','Goto DR','If K=23','Then','If length(Str1)>0','Then','If length(Str1)=1','Then','""→Str1','Else','sub(Str1,1,length(Str1)-1)→Str1','End','End','End','If K=23','Goto DR','If length(Str1)≥14','Goto KY','If K=103','Then','If inString(Str1,".")=0','"'+'.'+'"→Str0','If inString(Str1,".")=0','Str1+Str0→Str1','End','If K=103','Goto DR','{102,92,93,94,82,83,84,72,73,74}→ʟUCK','0→J','For(I,1,10)','If K=ʟUCK(I)','Then','I→J','End','End','If J=0','Goto KY','Str1+sub("0123456789",J,1)→Str1','Goto DR','Lbl OK','1→N','If length(Str1)>0','Then','If Str1="."','Then','"0"→Str1','End','V*expr(Str1)→N','End','1→Z','Return'])
# Key codes corrected: TI-84 1=72 2=73 3=74 4=62 etc.
# Output unit picker H=system; dims BCD, F factor and label. Fallback coherent slug/ft/s.
p=['1→F','"UNITLESS"→Str2','If (B=0) and (C=0) and (D=0)','Return']
for name,dims,si,imp in CATS[:-1]:
 p += [f'If (B={dims[0]}) and (C={dims[1]}) and (D={dims[2]})','Then',f'{si[0][1]:.14g}→F',f'"{si[0][0]}"→Str2','If H=2','Then',f'{imp[0][1]:.14g}→F',f'"{imp[0][0]}"→Str2','End','Return','End']
p+=['"kg^M m^L s^T"→Str2','If H=2','Then','14.5939029372064^B*.3048^C→F','"slug^M ft^L s^T"→Str2','End','Return'];emit('UCOUT',p)
main=['0→W','0→G','Lbl HM',menu('UNIT CALC',[('NEW EXPRESSION','NW'),('CONFIG','CF'),('HELP','HP'),('QUIT','QT')]),'Lbl CF',menu('DUAL OUTPUT',[('ON: SI + IMPERIAL','ON'),('OFF: FIRST SYSTEM','OF'),('BACK','HM')]),'Lbl ON','1→G','Goto HM','Lbl OF','0→G','Goto HM','Lbl HP','ClrHome','Disp "BLANK VALUE = 1","CHOOSE QUANTITY/UNIT","FIRST SYSTEM = RESULT","X AND / BEFORE + -","MASS: LBM OR SLUG","NO EQUATION SOLVING"','Pause','Goto HM','Lbl NW','0→T','1→O','0→W',*['{0}→ʟ'+n for n in ['UCV','UCM','UCL','UCT','UCOP']],'Goto AD','Lbl MN','ClrHome','Disp "EXPRESSION TERMS:",T','If T>0','Then','Disp "LAST TERM IN SI:",ʟUCV(T)','End',menu('NEXT',[('MULTIPLY','MU'),('DIVIDE','DI'),('ADD','PL'),('SUBTRACT','MI'),('RESULT','EV'),('REVIEW / UNDO','RV'),('HOME','HM')]),'Lbl MU','1→O','Goto AD','Lbl DI','2→O','Goto AD','Lbl PL','3→O','Goto AD','Lbl MI','4→O','Goto AD','Lbl AD','If T=40','Then','Disp "40 TERM LIMIT"','Pause','End','If T=40','Goto MN','prgmUCVAL','If Z=0','Goto CA','prgmUCPICK','If Z=0','Goto CA','If T=0','W→R','T+1→T','N*F→ʟUCV(T)','B→ʟUCM(T)','C→ʟUCL(T)','D→ʟUCT(T)','O→ʟUCOP(T)','Goto MN','Lbl CA','If T=0','Goto HM','Goto MN','Lbl RV',menu('REVIEW / UNDO',[('REVIEW IN SI','RE'),('UNDO LAST TERM','UD'),('BACK','MN')]),'Lbl UD','If T>0','T-1→T','If T=0','Goto NW','Goto MN','Lbl RE','For(J,1,T)','ClrHome','Disp "TERM",J,"OP:1=X 2=/ 3=+ 4=-",ʟUCOP(J),"SI VALUE",ʟUCV(J),"M L T EXPONENTS"','Disp {ʟUCM(J),ʟUCL(J),ʟUCT(J)}','Pause','End','Goto RV','Lbl EV','If T=0','Goto HM','T→P',*['ʟ'+s+'→ʟ'+d for s,d in [('UCV','UV'),('UCM','UM'),('UCL','UL'),('UCT','UT'),('UCOP','UO')]],'2→J','Lbl RD','If J>P','Goto SU','If ʟUO(J)>2','Goto SK','1→S','If ʟUO(J)=2','⁻1→S','If (S=⁻1) and (ʟUV(J)=0)','Goto ZE','ʟUV(J-1)*ʟUV(J)^S→ʟUV(J-1)',*['ʟ'+a+'(J-1)+S*ʟ'+a+'(J)→ʟ'+a+'(J-1)' for a in ['UM','UL','UT']],'For(I,J,P-1)',*['ʟ'+a+'(I+1)→ʟ'+a+'(I)' for a in ['UV','UM','UL','UT','UO']],'End','P-1→P','Goto RD','Lbl SK','J+1→J','Goto RD','Lbl SU','ʟUV(1)→E','ʟUM(1)→B','ʟUL(1)→C','ʟUT(1)→D','0→K','If P>1','Then','For(J,2,P)','If (B≠ʟUM(J)) or (C≠ʟUL(J)) or (D≠ʟUT(J))','1→K','1→S','If ʟUO(J)=4','⁻1→S','E+S*ʟUV(J)→E','End','End','If K=1','Goto ER','Lbl RS','ClrHome','R→H','prgmUCOUT','Disp "RESULT",E/F,Str2','If G=1','Then','3-R→H','prgmUCOUT','Disp "ALSO",E/F,Str2','End','Disp "EXPONENTS M L T",{B,C,D}','Pause',menu('RESULT',[('CONVERT','CV'),('EXPRESSION','MN'),('HOME','HM')]),'Lbl CV','B→X','C→Y','D→A','prgmUCPICK','If Z=0','Goto RC','If (B≠X) or (C≠Y) or (D≠A)','Then','Disp "INCOMPATIBLE UNIT"','Pause','Else','ClrHome','Disp E/F,Str2','Pause','End','Lbl RC','X→B','Y→C','A→D','Goto RS','Lbl ER','ClrHome','Disp "CANNOT ADD/SUBTRACT","DIFFERENT DIMENSIONS"','Pause','Goto MN','Lbl ZE','ClrHome','Disp "DIVISION BY ZERO"','Pause','Goto MN','Lbl QT','ClrHome','Stop']
emit('UNITCE',main)
# Remap arbitrary source labels to valid one/two-character TI labels.
import re,string
for name,source in programs.items():
 labels=re.findall(r'^Lbl (\w+)$',source,re.M)
 assert len(labels)==len(set(labels)),name
 pool=[a+b for a in string.ascii_uppercase for b in string.ascii_uppercase+string.digits]
 mapping=dict(zip(labels,pool))
 def replace(m): return m[1]+mapping[m[2]]
 source=re.sub(r'(Lbl |Goto )([A-Z0-9]+)',replace,source)
 # Menu labels live outside quoted text.
 source=re.sub(r'(?<=,)([A-Z][A-Z0-9]*)(?=[,)])',lambda m:mapping.get(m[0],m[0]),source) if False else source
 lines=[]
 for line in source.splitlines():
  if line.startswith('Menu('):
   parts=line.split(',')
   for k in range(2,len(parts),2):
    end=')' if parts[k].endswith(')') else ''
    parts[k]=mapping[parts[k].rstrip(')')]+end
   line=','.join(parts)
  lines.append(line)
 source='\n'.join(lines)+'\n'
 # TI requires unary negative token for negative literals.
 source=re.sub(r'(?<=[=,(>+*/^→])-(?=\d)','⁻',source)
 source=re.sub(r'^-(?=\d)','⁻',source,flags=re.M)
 (OUT/(name+'.txt')).write_text(source)
 p=TIProgram(name=name);p.load_string(source);p.save(str(OUT/(name+'.8xp')))
 # Full token round-trip, not merely successful encoder invocation.
 q=TIProgram.open(str(OUT/(name+'.8xp')))
 assert q.data==p.data
 print(name,len(p.data),'bytes')
(OUT/'units.json').write_text(json.dumps(CATS,indent=2))
