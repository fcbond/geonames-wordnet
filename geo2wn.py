##
## Create GeoNames Wordnet
##
## first download geonames data to gndata
##
## then run geo2wn.py
## maybe change the list of languages you want

from collections import defaultdict as dd
from xml.sax.saxutils import escape
from iso639 import languages

#import pinyin
prefix='gnwn-'

def qe(data):
    return escape(data, entities={
        "'": "&apos;",
        "\"": "&quot;"
    })
### todo
##- check for multiple preferred
##- decide what to do when language is unknown
##- decide whether to merge variants
##- add meronyms




lgs= ['eu', 'bg', 'my', 'ca', 'hr', 'nl', 'et', 'fi', 'gl', 'ga', 'it', 'pt', 'sl', 'es', 'th', 'ro',  'ja', 'pl', 'id', 'de', 'zh', 'ar', 'en', 'fa', 'hi', 'ms', 'mr', 'sa', 'tr', 'is', 'he', 'sq', 'nn', 'no', 'da', 'lt', 'xh', 'zu', 've', 'tn'   ]
#lgs= ['ja', 'pl', 'zh', 'id', 'de','zh', 'ar', 'en']
#lgs= ['ja', 'en']

limit = 1000000000
#limit=1000  Only do the first limit for debugging

### todo
##- check for multiple preferred
##- combine with links in WN
##- decide what to do when language is unknown
##- decide whether to merge variants
log = open('gnwn.log', 'w')


f=open('data/geo_domain_wordnet_eng.tsv')
tops = dd(list)
pwn2geo=dict()
for l in f:
    row = l.strip().split('\t')
    tops[row[0]] =  [row[1], row[2], row[-1], row[3:-1]] #lemma def geo, lnks
    for x in row[3:-1]:
        if x.endswith(';DGM_equivalent'):
            #print(x[:-15])
            pwn2geo[x[:-15]]  = row[-1]
topsyns = dd(list) #  (ili, definition, note, [(target, relation), ...]] 
for i in tops:
    (lm, df, geo, lnks) = tops[i]
    synset=prefix+geo
    ili=''
    links = []
    #print(i, lnks)
    for l in lnks:
        if not l:
            continue
        #print("L", l)
        (t,r) = l.split(';')
        if   r == 'DGM_equivalent':
            ili=t  ### fixme ilify!
        elif t== 'has_hypernym':
            links.append((prefix+tops[r][2],  'hypernym'))
        elif t== 'meronym':
            links.append((prefix+tops[r][2], 'mero_part'))
        elif   r == 'DGM_hyponym':
            if t in pwn2geo:
                links.append((prefix+pwn2geo[t], 'hypernym'))
            else:
                print(i, "can't link", r, t)
        elif   r == 'DGM_meronym':
            if t in pwn2geo:
                links.append((prefix+pwn2geo[t], 'mero_part'))
            else:
                print(i, "can't link", r, t)
        else:
            print(i, 'unknown relation', r, t)
    if not (ili or links):
        print('orphan',i)
    topsyns[synset] = [ili, df, lm, links]


f =  open('gndata/allCountries.txt')
# geonameid         : integer id of record in geonames database
# name              : name of geographical point (utf8) varchar(200)
# asciiname         : name of geographical point in plain ascii characters, varchar(200)
# alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
# latitude          : latitude in decimal degrees (wgs84)
# longitude         : longitude in decimal degrees (wgs84)
# feature class     : see http://www.geonames.org/export/codes.html, char(1)
# feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
# country code      : ISO-3166 2-letter country code, 2 characters
# cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
# admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
# admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
# admin3 code       : code for third level administrative division, varchar(20)
# admin4 code       : code for fourth level administrative division, varchar(20)
# population        : bigint (8 byte int) 
# elevation         : in meters, integer
# dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
# timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
# modification date : date of last modification in yyyy-MM-dd format
geo = dict()
adm = dict()
for l in f:   
    row = l.strip().split('\t')
    gid= row[0]
    name = row[1]
    names = row[2]
    domain = "{}.{}".format(row[6],row[7])
    country = row[8]
    admin1 = row[10]
    admin2 = row[11]
    admin3 = row[12]
    admin4 = row[13]
    geo[gid] =  (name, names, domain, country, admin1, admin2, admin3, admin4)
    if row[7] == 'ADM1':
        adm[country, 'ADM1', row[10]] = gid
    elif  row[7] == 'ADM2':
        adm[country, 'ADM2', row[11]] = gid
    elif  row[7] == 'ADM3':
        adm[country, 'ADM3', row[12]] = gid
    elif  row[7] == 'ADM4':
        adm[country, 'ADM4', row[13]] = gid
        
lemmas= dd(list)
# I can append directly, opens a new empty list.
# lemmas is a list of tuples.
# each tuple has (altid, lang, lemma, meta)
# meta = P S C H
f = open('gndata/alternateNamesV2.txt')

##The table 'alternate names' :
##-----------------------------
##alternateNameId   : the id of this alternate name, int
##geonameid         : geonameId referring to id in table 'geoname', int
##isolanguage       : iso 639 language code 2- or 3-characters; 4-characters 'post' for postal codes and 'iata','icao' and faac for airport codes, fr_1793 for French Revolution names,  abbr for abbreviation, link to a website (mostly to wikipedia), wkdt for the wikidataid, varchar(7)
##alternate name    : alternate name or name variant, varchar(400)
##isPreferredName   : '1', if this alternate name is an official/preferred name
##isShortName       : '1', if this is a short name like 'California' for 'State of California'
##isColloquial      : '1', if this alternate name is a colloquial or slang term. Example: 'Big Apple' for 'New York'.
##isHistoric        : '1', if this alternate name is historic and was used in the past. Example 'Bombay' for 'Mumbai'.
##from		  : from period when the name was used
##to		  : to period when the name was used
count =0
for l in f:
    if count > limit:
        break
    count += 1 
    row = l.strip().split('\t')
    altid = row[0]
    gid = row[1]
    lang = row[2]
    lemma = row[3]
    if lang is None or lang == '':
        lang = 'unknown'
    meta = ''
    if len(row)>4 and row[4] == '1':
        #check if 1 is string
        #print(gid, 'has preferred name', lemma)
        meta += 'P'
    if len(row)>5 and row[5] == '1':
        #check if 1 is string
        #print(gid, 'has short name', lemma)
        meta += 'S'
    if len(row)>6 and row[6] == '1':
        #check if 1 is string
        #print(gid, 'has colloquial name', lemma)
        meta += 'C'
    if len(row)>7 and row[7] == '1':
        #check if 1 is string
        #print(gid, 'has historical name', lemma)
        meta += 'H'
    if len(row)>8:
        frm = str(row[8])
    else:
        frm = ''
    if len(row)>9:
        to = str(row[9])
    else:
        to = ''
    frmto = ''
    if frm or to:
        #print(gid, 'has from or to', lemma)
        frmto = "{}~{}".format(frm, to)
    lemmas[gid].append((altid, lemma, lang, meta, frmto))

# test
##for gid in '2174003 1884384 1642911 1141103 1143865'.split():
##    for (altid, lemma, lang, meta, frmto) in lemmas[gid]:
##        print(altid, lemma, lang, meta, frmto, sep='\t')

#lng='ja'
lexes = dd(lambda: dd(list))
syns = dd(lambda: dd(tuple)) #
for gid in lemmas:
    # lems = [x[1] for x in lemmas[gid] if x[2] in lgs]
    # #print(gid, lems)
    # if not lems:
    #     continue
    #print (gid,  geo[gid][0], geo[gid][3], geo[gid][2])
    for (altid, lemma, lang, meta, frmto) in lemmas[gid]:
        #print('', lemma, lang, meta, sep='\t')
        if lang in lgs:
            synset=prefix+gid
            typ=prefix+geo[gid][2]
            if typ in topsyns: ## do we have the supertype?
                lexes[lang][lemma].append((synset, 'P' in meta))
                if synset not in syns[lang]: ### do we have this already?
                    syns[lang][synset] = ['', '', geo[gid][0], [(typ, 'instance_hypernym')]]
            else:
                print('TYPE UNKNOWN', typ, gid, sep='\t',file=log)
#            print(gid,lemma,synset,typ)
###
### Add meronyms iff they are in the lexicon (or add the country)
###
for lng in syns:
    #print(lng)
    for synset in syns[lng]:
        gid = synset[5:]
        #print(geo[gid])
        if geo[gid][2].startswith('A.ADM'):
            continue
        admin = ''
        if geo[gid][7]:
            admin =  (geo[gid][3], 'ADM4', geo[gid][7])
            if admin in adm and (adm[admin] in syns[lng]):
                syns[lng][synset][3].append((prefix+adm[admin],'mero_location'))
            else:
                admin = ''
        if (not admin) and geo[gid][6]:
            admin =  (geo[gid][3], 'ADM3', geo[gid][6])
            if admin in adm and (adm[admin] in syns[lng]):
                syns[lng][synset][3].append((prefix+adm[admin],'mero_location'))
            else:
                admin = ''
        if (not admin) and geo[gid][5]:
            admin =  (geo[gid][3], 'ADM2', geo[gid][5])
            if admin in adm and (adm[admin] in syns[lng]):
                syns[lng][synset][3].append((prefix+adm[admin],'mero_location'))
            else:
                admin = ''
        if (not admin) and  geo[gid][4]:
            admin =  (geo[gid][3], 'ADM1', geo[gid][4])
            if admin in adm and (adm[admin] in syns[lng]):
                syns[lng][synset][3].append((prefix+adm[admin],'mero_location'))
            else:
                admin = ''
        # elif geo[gid][3]:
        #     # add the country
        #     print('ADDED country', geo[gid][4], mero, geo[mero],file=log)

###
###
###


def printStats(lngs, lexes, syns):
    totlem = 0
    totsense =0
    synsets = set()
    print("""\\begin{tabular}{llrrrll}
Language & Code & Synsets & Lemmas & Senses & Asia & Most Common\\\\ \\hline""")
    for lng in sorted(lngs):
        # Names for asia gid=6255147
        asia = ', '.join([x[1] for x in lemmas['6255147'] if x[2] == lng]) or '---'
        # Names for most common
        mx = max(len(lexes[lng][g]) for  g in lexes[lng])
        maxes = [g for g in lexes[lng] if len(lexes[lng][g]) == mx]
        if len(maxes) > 3 or len(maxes) < 1:
            common == '---'
        else:
            common = ', '.join(maxes)
        numsenses =  sum(len(lexes[lng][l]) for  l in lexes[lng])
        print ("{} &  {} & {:,d} & {:,d}  & {:,d} & {} & {} \\\\ ".format(
            languages.get(alpha2=lng).name,
            lng,
            len(syns[lng]),
            len(lexes[lng]),
            numsenses,
            asia,
            common))
        totlem += len(lexes[lng])
        totsense += numsenses
        synsets = synsets.union(set(syns[lng])) 
    print ("{} &  {} & {:,d} & {:,d}  & {:,d} & {} & {} \\\\ ".format(
        'Total',
        len(lngs),
        len(synsets),
        totlem,
        totsense,
        '---',
        '---'))
    print("""\\end{tabular}""")
    
printStats(lgs, lexes, syns)
                

def printHeader(lng,fh):
    print("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.0.dtd">
<LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">
<Lexicon id="gnwn-{0}"
             label="GeoNames Wordnet for {5} "
             language="{0}" 
             email="{1}"
             license="{2}"
             version="{3}"
             citation="{4}"
             url="{5}"
             dc:publisher="Global Wordnet Association"
             dc:description=""""""
             confidenceScore="1.0" >
    """.format(lng,
               'bond@ieee.org',
               'https://creativecommons.org/licenses/by/4.0/',
               0.9,
               "Francis Bond and Arthur Bond (2019) GeoNames Wordnet (gnwn) — extracting wordnets from GeoNames, Proceedings of the 10th Global WordNet Conference (GWC-2019)",
               "https://github.com/fcbond/geonames-wordnet",
               languages.get(alpha2=lng).name),file=fh)

def printFooter(fh):
    print('</Lexicon>\n</LexicalResource>',file=fh)

def printLexs(lexes,fh):
    """dictionary with lemma as key
    lexes['lemma'] = [(target, note, preferred)]
    lexes['東京'] = [('geown-1245', 'Tokyo', True), 
                     ('geown-7397798', 'Dongjing', False)]"""
    wid = 1
    for l in lexes:
        print ("""  <LexicalEntry id="w{0}">
    <Lemma writtenForm="{1}" partOfSpeech="n"/>""".format(wid,qe(l)),
               file=fh)
        #print(l, lexes[l])
        for (t,p) in lexes[l]:
            if p:
                print ("""    <Sense id="{1}-w{0}" synset="{1}">
        <Count>1</Count>
      </Sense>""".format(wid,t),
                       file=fh)
            else:
                print ("""    <Sense  id="{1}-w{0}" synset="{1}"/>""".format(wid,t)
                       ,file=fh)
        print("""  </LexicalEntry>""",file=fh)
        wid +=1

def printSyns(syns,fh):
    """dictionary with synset as key
    syns[synset] = [ili, def, note, links)
    syns['geown-1245'] = ['', '', 'Tokyo', [('geo-L.PPL', 'instance_hypernym')]]""" 
    for s in syns:
        [i,d,n,l] = syns[s]
        print("""  <Synset id="{}" ili="{}" partOfSpeech="n" note="{}">""".format(s,i,qe(n)),file=fh)
        if d:
            print("""    <Definition>{}</Definition>""".format(d),file=fh)   
        for (t,r) in l:
            print("""    <SynsetRelation target="{}" relType="{}"/>""".format(t,r),file=fh)
        print("""  </Synset>""",file=fh)
    
        

for lng in lgs:
    #print(lexes[lng])
    #print(syns[lng])
    fh = open('gnwn-{}-lmf.xml'.format(lng), 'w')
    printHeader(lng, fh)
    printLexs(lexes[lng], fh)
    printSyns(topsyns, fh)
    printSyns(syns[lng], fh)
    printFooter(fh)
    fh.close()
