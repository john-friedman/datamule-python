headers = {
    "User-Agent": "Peter Smith petersmith@gmail.com"  # Replace with your information
}

dataset_10k_url_list = [
    {'year': 2024, 'urls': [
        'https://www.dropbox.com/scl/fi/3gd9whn8qtychbxuxnbsa/2024_archive.zip.001?rlkey=2n8qwhcccevniqkvy39ksa467&st=hn3kacs6&dl=1',
        'https://www.dropbox.com/scl/fi/8citjlh4h58speyag3hd9/2024_archive.zip.002?rlkey=ymadt6wc81e9m3a15znwum7s1&st=opzcpxye&dl=1'
    ]},
    {'year': 2023, 'urls': [
        'https://www.dropbox.com/scl/fi/hdnb6bbr7l3xgrfmc73ht/2023_archive.zip.001?rlkey=kd0npzwvscacfdz0syq2irnu7&st=nzmh3lwr&dl=1',
        'https://www.dropbox.com/scl/fi/ubiyq3tssa95enbb8xi9u/2023_archive.zip.002?rlkey=xkef3tx3q5a4f3oh38tx4cjy4&st=z3nrs8g3&dl=1'
    ]},
    {'year': 2022, 'urls': [
        'https://www.dropbox.com/scl/fi/rlhvogepk9cpnohhq4gs7/2022_archive.zip.001?rlkey=81hmjgdt1rtjub64wrlp9oy5t&st=i6ecnbux&dl=1',
        'https://www.dropbox.com/scl/fi/r5m6y1j8uf02uy61u3fcn/2022_archive.zip.002?rlkey=z80qlgjifbtf5mjuqlu98478p&st=7wqvhekh&dl=1'
    ]},
    {'year': 2021, 'urls': [
        'https://www.dropbox.com/scl/fi/wemvdqxsqddlhlcgon36g/2021_archive.zip.001?rlkey=tjl3525vn60zwosnqdgznecj5&st=66bycsgf&dl=1',
        'https://www.dropbox.com/scl/fi/si0nynzxxf31kxpxobzrf/2021_archive.zip.002?rlkey=93oczu6hs5iusex2f65k2mxc7&st=x8cymp6w&dl=1'
    ]},
    {'year': 2020, 'urls': [
        'https://www.dropbox.com/scl/fi/vxvgwrw2q04qlj5m2aoog/2020_archive.zip.001?rlkey=88h3x78axn5ghvk9t5otqpdjd&st=72xwi1y1&dl=1',
        'https://www.dropbox.com/scl/fi/9blysoqztxg5vedrf2l2i/2020_archive.zip.002?rlkey=msvos1omcb8fowb4q1nm38m6e&st=bscfunry&dl=1'
    ]},
    {'year': 2019, 'urls': [
        'https://www.dropbox.com/scl/fi/hq5o9zo8xrqmd7l4o06hy/2019_archive.zip.001?rlkey=sazeziru87k7qptqhxenv0d6m&st=241jmwwd&dl=1',
        'https://www.dropbox.com/scl/fi/2jyxw65unxhhsk5fuhuon/2019_archive.zip.002?rlkey=nzyf1em08qgxdhpz2vuoj417u&st=ii9zpdxi&dl=1'
    ]},
    {'year': 2018, 'urls': [
        'https://www.dropbox.com/scl/fi/c1vexzflxr6qcsg25nxp7/2018_archive.zip.001?rlkey=hnb5zeashbtqfhxsnf9vt94vv&st=wy9i633f&dl=1',
        'https://www.dropbox.com/scl/fi/yzt3464lscpmy5n39olk5/2018_archive.zip.002?rlkey=tu3lbnjnd1xwni8f6nfpbmtgm&st=c0zur5sz&dl=1'
    ]},
    {'year': 2017, 'urls': [
        'https://www.dropbox.com/scl/fi/3trjwjx6v64ilnt8nyp02/2017_archive.zip.001?rlkey=vl4x1rrp0fisjy3djrraayjoe&st=ept0d24k&dl=1',
        'https://www.dropbox.com/scl/fi/p011jrntmkrmlb9u84k62/2017_archive.zip.002?rlkey=55uka4y2d90eb5d8lgu86yl6c&st=ildtcc94&dl=1'
    ]},
    {'year': 2016, 'urls': [
        'https://www.dropbox.com/scl/fi/5oydfbume2mxqfobn2e9r/2016_archive.zip.001?rlkey=4h76gl9ny8e7vgcdnphf7bzn9&st=jkr0ioby&dl=1',
        'https://www.dropbox.com/scl/fi/faofea4f2mkzjslt12s0b/2016_archive.zip.002?rlkey=bolnuqm3fq7yrfqhf5ek92dgp&st=33w8ivrx&dl=1'
    ]},
    {'year': 2015, 'urls': [
        'https://www.dropbox.com/scl/fi/75rdrrsrgbg95qcedcr65/2015_archive.zip.001?rlkey=pb4ec6sda3ii0lnzua4enxnr3&st=t7wkjb60&dl=1',
        'https://www.dropbox.com/scl/fi/ixfttx508tp8cuf3xismr/2015_archive.zip.002?rlkey=xcoqtcx3vjnh3ctxhpqe4jv2j&st=56fgbb8w&dl=1'
    ]},
    {'year': 2014, 'urls': [
        'https://www.dropbox.com/scl/fi/1y1j6ct6mox76euu38t2c/2014_archive.zip.001?rlkey=hwh83ttl3nahb1oegib05p3k7&st=d01umhdp&dl=1',
        'https://www.dropbox.com/scl/fi/bh2yu3coqcshj5mybk3wd/2014_archive.zip.002?rlkey=0g4ftzhytyn3vk8kgwu72b6lf&st=jz9pzdoy&dl=1'
    ]},
    {'year': 2013, 'urls': [
        'https://www.dropbox.com/scl/fi/jraed38u18c9y16mwcnmo/2013_archive.zip.001?rlkey=fvy6flk8uxk2mn5wjvynu96ag&st=3sivwbx7&dl=1',
        'https://www.dropbox.com/scl/fi/cgi8opfbnu727seazzmvd/2013_archive.zip.002?rlkey=sm7h7wfzud22u3ed1pw8fr7u9&st=19tunve8&dl=1'
    ]},
    {'year': 2012, 'urls': [
        'https://www.dropbox.com/scl/fi/hji2bb1ce2wdwf5yc6dyf/2012_archive.zip.001?rlkey=0r53m8roo6e8grqez3lnhpayk&st=1jx5jq4r&dl=1',
        'https://www.dropbox.com/scl/fi/hqoh4l305b168619eytkj/2012_archive.zip.002?rlkey=2laeldqzlwskwoha9idmioolf&st=1w8zowyp&dl=1'
    ]},
    {'year': 2011, 'urls': [
        'https://www.dropbox.com/scl/fi/z7z8qnmf73hqr33b386zu/2011_archive.zip.001?rlkey=kdkd3urxmo830n30gwiapqvkz&st=2hsuxpcm&dl=1',
        'https://www.dropbox.com/scl/fi/illd2qfsj2vuy4yjd13el/2011_archive.zip.002?rlkey=oewcg57c92wlbufwhon21mjeq&st=ir05xure&dl=1'
    ]},
    {'year': 2010, 'urls': [
        'https://www.dropbox.com/scl/fi/j41ta06g0fso473x4oa1f/2010_archive.zip.001?rlkey=1r83ibenn06fxs6zhm6oi46pr&st=iia9qtid&dl=1',
        'https://www.dropbox.com/scl/fi/31b6huoywrrc44b76wm1w/2010_archive.zip.002?rlkey=40jfl7zqnw5sikgd4wuo1095m&st=igy563mu&dl=1'
    ]},
    {'year': 2009, 'urls': [
        'https://www.dropbox.com/scl/fi/4y6c1icwvkjwwqbgx4w1a/2009_archive.zip.001?rlkey=3qqp4ikinplktw6g39x68rdmj&st=dcg0eik1&dl=1',
        'https://www.dropbox.com/scl/fi/jq808ah0j0vg1sqdmvnnm/2009_archive.zip.002?rlkey=wbgtvj8fkpgmcj5oxpj88jfog&st=4txza2fu&dl=1'
    ]},
    {'year': 2008, 'urls': [
        'https://www.dropbox.com/scl/fi/uf1ym44ns1936uj8vqfwk/2008_archive.zip.001?rlkey=9rivaprk7yjrutdfu7sqo3jxv&st=gj75o1ne&dl=1'
    ]},
    {'year': 2007, 'urls': [
        'https://www.dropbox.com/scl/fi/58qmwj7m3rrl7kr00lwat/2007_archive.zip.001?rlkey=815zw0gnb7gowcdf0iuvtctqh&st=7cajp3ii&dl=1'
    ]},
    {'year': 2006, 'urls': [
        'https://www.dropbox.com/scl/fi/gxi8qzpz53f9qcvn2hpl5/2006_archive.zip.001?rlkey=hmehz1azpbxzpw6j1wy5eppq0&st=czxrdcnh&dl=1'
    ]},
    {'year': 2005, 'urls': [
        'https://www.dropbox.com/scl/fi/tjstefvwfzs3p0a1vzlbg/2005_archive.zip.001?rlkey=825m16ziekd9mwc3ybvjvisj0&st=4dyy121i&dl=1'
    ]},
    {'year': 2004, 'urls': [
        'https://www.dropbox.com/scl/fi/2g25emvme8gqoxnv5fhla/2004_archive.zip.001?rlkey=lz8oyniqgc7xvn343d39600ic&st=yvmi9h1t&dl=1'
    ]},
    {'year': 2003, 'urls': [
        'https://www.dropbox.com/scl/fi/d2ub0o4sqo0b2evd9s9z3/2003_archive.zip.001?rlkey=qxsltqjfxnk0xrp0qx5c49v57&st=cc4dzjo2&dl=1'
    ]},
    {'year': 2002, 'urls': [
        'https://www.dropbox.com/scl/fi/9xy6y09y2b5zp4w4c7cty/2002_archive.zip.001?rlkey=c4qqact06zz7ykmfc1n5odf2a&st=d93mptu8&dl=1'
    ]},
    {'year': 2001, 'urls': [
        'https://www.dropbox.com/scl/fi/b3miae1kvths87e0cq8fs/2001_archive.zip.001?rlkey=g21mnbzicju3czney275bpjyp&st=0nji6q8l&dl=1'
    ]}
]

dataset_10q_url_list = [
    {'year': 2001, 'urls': ['https://www.dropbox.com/scl/fi/1bzig8wabbtezfg6dipou/2001_archive.zip.001?rlkey=4sddwex8k9kd4jahypsxgvbs2&st=s5x7wnh5&dl=1']},
    {'year': 2002, 'urls': ['https://www.dropbox.com/scl/fi/qe0om30w0dhtg3byse8n1/2002_archive.zip.001?rlkey=7ji21x7ppavstwoe1dz7028r5&st=hb5dkzo2&dl=1']},
    {'year': 2003, 'urls': ['https://www.dropbox.com/scl/fi/9dfpof4es1kfdttpejkb1/2003_archive.zip.001?rlkey=36xwaacvtb3rw8mqkd1dwgav2&st=vfmo1tph&dl=1']},
    {'year': 2004, 'urls': ['https://www.dropbox.com/scl/fi/l2tv1ywmltlx2ygbmy1k4/2004_archive.zip.001?rlkey=sdrczfb9irv9q2xi10a2y169j&st=6a1v0pos&dl=1']},
    {'year': 2005, 'urls': ['https://www.dropbox.com/scl/fi/16euq6ies55c0q4z2ws0q/2005_archive.zip.001?rlkey=l80ig2irksajd7djmlv6bith0&st=yc5ing9t&dl=1']},
    {'year': 2006, 'urls': ['https://www.dropbox.com/scl/fi/wi66433i8xdh3g6ozozod/2006_archive.zip.001?rlkey=zg09b09mdg77ni8zsq7p8dex9&st=347utf3x&dl=1']},
    {'year': 2007, 'urls': ['https://www.dropbox.com/scl/fi/u3bazimzkkps8qfvaubxm/2007_archive.zip.001?rlkey=fuj28imnb2bjskx2wggoyuvuu&st=76jka6tc&dl=1']},
    {'year': 2008, 'urls': [
        'https://www.dropbox.com/scl/fi/htc6j3c9l17ey6urjzm63/2008_archive.zip.001?rlkey=9pnl5066d33x6wan8uqhvom5q&st=fsgogqya&dl=1',
        'https://www.dropbox.com/scl/fi/47jb2sipfg13b5p6dzegb/2008_archive.zip.002?rlkey=ml6zfxrptg1jgebpd6bdmztej&st=3unkdpnr&dl=1'
    ]},
    {'year': 2009, 'urls': [
        'https://www.dropbox.com/scl/fi/krrc6zx5cvbyhhskrrdlp/2009_archive.zip.001?rlkey=nggwp1z5ekrvgnxlg434vtfqg&st=mn6x1fqp&dl=1',
        'https://www.dropbox.com/scl/fi/w46430sm52bd1bioc94f7/2009_archive.zip.002?rlkey=06ilznlorppqmhpj17wax1id9&st=ozloyl3v&dl=1'
    ]},
    {'year': 2010, 'urls': [
        'https://www.dropbox.com/scl/fi/g86fzg6dysnt34raq352k/2010_archive.zip.001?rlkey=2kil6s78cj6p5bk8r0eptxygf&st=vyauu3sl&dl=1',
        'https://www.dropbox.com/scl/fi/46ttnl8pb1qfk5icd7n4q/2010_archive.zip.002?rlkey=9nok0mg3mjexybywq1og6vdux&st=oia2g4fy&dl=1'
    ]},
    {'year': 2011, 'urls': [
        'https://www.dropbox.com/scl/fi/ems2oygr0u3voq38yisuk/2011_archive.zip.001?rlkey=4lfsowv9o6wmkmozn3pdr80sh&st=3kn4ghbe&dl=1',
        'https://www.dropbox.com/scl/fi/ihersfxuqnnli1fhze9wc/2011_archive.zip.002?rlkey=iirqvy919yv3pkvem2owsdgxy&st=0eb8rtbq&dl=1'
    ]},
    {'year': 2012, 'urls': [
        'https://www.dropbox.com/scl/fi/dima81xb776o6r9rmvxf6/2012_archive.zip.001?rlkey=wlyma7xg70hllk0wutx4boqif&st=301p8dq2&dl=1',
        'https://www.dropbox.com/scl/fi/b7h7a3b83c7pkx1ayz5tx/2012_archive.zip.002?rlkey=380e4viezrorkbdgs16j9qyig&st=35f8jjt9&dl=1'
    ]},
    {'year': 2013, 'urls': [
        'https://www.dropbox.com/scl/fi/5z0rubg54kgt60sp3w8ir/2013_archive.zip.001?rlkey=9b1ff6vw6v76g9p6n20z0pf1y&st=p2kouaw2&dl=1',
        'https://www.dropbox.com/scl/fi/g0n2vtrc3nsjou1t7zdv8/2013_archive.zip.002?rlkey=42id27sv2tzz4nt2lb999kjo0&st=teww7pk6&dl=1'
    ]},
    {'year': 2014, 'urls': [
        'https://www.dropbox.com/scl/fi/25kr0m6nfz1uvecpzsl3g/2014_archive.zip.001?rlkey=9b4v6eevhrsqx4yxr4syl3xx9&st=crdzt5e5&dl=1',
        'https://www.dropbox.com/scl/fi/k0dt79eyjuvhxvrdepsat/2014_archive.zip.002?rlkey=u44c7wysi21tpvo7p2emspr96&st=gdzb6vbl&dl=1'
    ]},
    {'year': 2015, 'urls': [
        'https://www.dropbox.com/scl/fi/jw3a4ua6qgy439jm5guwb/2015_archive.zip.001?rlkey=vsah3muoz6po9iwgfmy6idax4&st=8np4xe5t&dl=1',
        'https://www.dropbox.com/scl/fi/kmk5p3ynpf4e4n1zu4ead/2015_archive.zip.002?rlkey=v5z3sli6unlqomdlgq2vsfmyy&st=684ulwyp&dl=1'
    ]},
    {'year': 2016, 'urls': [
        'https://www.dropbox.com/scl/fi/veo77wy3muzg7jua1pnon/2016_archive.zip.001?rlkey=xlh62swhnywcruck89ix7zsnv&st=p1u5mrql&dl=1',
        'https://www.dropbox.com/scl/fi/nf4ue014vnf8i5wd3ifq8/2016_archive.zip.002?rlkey=kpnh9hmw7bonbjj3a1qtmx3wr&st=2o1ljgk3&dl=1'
    ]},
    {'year': 2017, 'urls': [
        'https://www.dropbox.com/scl/fi/ma6kdn0zmr0jsfjuwyrr8/2017_archive.zip.001?rlkey=cmcrs84513amzd0xtnhgowjig&st=2y20plzl&dl=1',
        'https://www.dropbox.com/scl/fi/7pqfkoalf6kwdxglkd4rd/2017_archive.zip.002?rlkey=pu9gpwj8s58jpxaa5bo4qdt2t&st=7cjfuewb&dl=1'
    ]},
    {'year': 2018, 'urls': [
        'https://www.dropbox.com/scl/fi/76smlo78ilea1h1x5ej5p/2018_archive.zip.001?rlkey=9s7ccdm0il6nash54x7lpzlyq&st=nugdjlct&dl=1',
        'https://www.dropbox.com/scl/fi/ewdm0f8bztpq9290c0bzk/2018_archive.zip.002?rlkey=6baqb8j9ptu17f3r6xvlceuot&st=faj7cbyf&dl=1'
    ]},
    {'year': 2019, 'urls': [
        'https://www.dropbox.com/scl/fi/9uk4a45vvpda567sonboo/2019_archive.zip.001?rlkey=v0me7vf0lamwue2g936sdduo8&st=30ehpju3&dl=1',
        'https://www.dropbox.com/scl/fi/7uzovuhycbi8gt2fb84jk/2019_archive.zip.002?rlkey=vckqm3ekb7xcmd0m8whfzvmsv&st=yyxsxzhc&dl=1'
    ]},
    {'year': 2020, 'urls': [
        'https://www.dropbox.com/scl/fi/85aiiz3kun6r8zetjgjgw/2020_archive.zip.001?rlkey=3z55z1kvkgd7vjlit69v3peu4&st=6bqx7i9f&dl=1',
        'https://www.dropbox.com/scl/fi/gc5lt1cocx4fukcx5wmpi/2020_archive.zip.002?rlkey=kpwpswwy5za0d7xspgqu3yq1r&st=8do0y1so&dl=1',
        'https://www.dropbox.com/scl/fi/1zkkim7118qqhy2ktordl/2020_archive.zip.003?rlkey=jryn61lym4x5vf6z7t9uqidt7&st=mpl7uu8e&dl=1'
    ]},
    {'year': 2021, 'urls': [
        'https://www.dropbox.com/scl/fi/kraiuj98f1at7pepcfdbl/2021_archive.zip.001?rlkey=7x1ppre2o05cdypmsq1quv9so&st=rqqq3skc&dl=1',
        'https://www.dropbox.com/scl/fi/s45tc1e97384ov73zcrrm/2021_archive.zip.002?rlkey=t7c6was2nt5v73bjmyyknma4g&st=ts1esu9j&dl=1',
        'https://www.dropbox.com/scl/fi/se0b1a66rct9ludn5nx8p/2021_archive.zip.003?rlkey=m6e579metkdyg8hmhgouuyxug&st=z0hqvdcw&dl=1'
    ]},
    {'year': 2022, 'urls': [
        'https://www.dropbox.com/scl/fi/2iz7url6znpchw55ufduw/2022_archive.zip.001?rlkey=d3b4topzrj6qd2ag9ui8tbxuv&st=id8ybmcg&dl=1',
        'https://www.dropbox.com/scl/fi/ia6y75uwuap2eo3cljqz6/2022_archive.zip.002?rlkey=hzksfpslqms6khimhz4pwyzuv&st=d05v5oqh&dl=1',
        'https://www.dropbox.com/scl/fi/q0y77ektba0kkyfd86x9f/2022_archive.zip.003?rlkey=imo5k84n0oq9xzlnd3qi4hsxx&st=38ezt7hx&dl=1'
    ]},
    {'year': 2023, 'urls': [
        'https://www.dropbox.com/scl/fi/lsrpoatfkdpk9hhc3noqy/2023_archive.zip.001?rlkey=o76y41tm7fbbd87b3m9papbqg&st=ucq14or6&dl=1',
        'https://www.dropbox.com/scl/fi/dldxu8a3uzk69fzp33gfi/2023_archive.zip.002?rlkey=gi4sj8ol2x6s7hnk36rp9jh4r&st=wqrhw4rn&dl=1',
        'https://www.dropbox.com/scl/fi/u51gbwg5moz4qgoyvcb62/2023_archive.zip.003?rlkey=vl3h41up8k049pr8lglbwh8hh&st=extn710g&dl=1'
    ]},
    {'year': 2024, 'urls': [
        'https://www.dropbox.com/scl/fi/1exc08zvgz2pgcp3w3riy/2024_archive.zip.001?rlkey=1r6k5r9kcyske314tp1qitfua&st=eo1elt94&dl=1',
        'https://www.dropbox.com/scl/fi/u9d0e61euy3p1aq7nkmka/2024_archive.zip.002?rlkey=vwijac5pfwbeyxg7lr5m4f3lx&st=aedjdb8u&dl=1'
    ]}
]

dataset_10k_record_list = [{'year':2001,'record':'13871721'},
          {'year':2002,'record':'13871779'},
          {'year':2003,'record':'13871791'},
          {'year':2004,'record':'13871811'},
          {'year':2005,'record':'13871828'},
          {'year':2006,'record':'13871965'},
          {'year':2007,'record':'13872346'},
          {'year':2008,'record':'13872366'},
          {'year':2009,'record':'13872372'},
          {'year':2010,'record':'13872374'},
        {'year':2011,'record':'13872380'},
        {'year':2012,'record':'13872400'},
        {'year':2013,'record':'13872494'},
        {'year':2014,'record':'13872496'},
        {'year':2015,'record':'13872511'},
        {'year':2016,'record':'13872528'},
        {'year':2017,'record':'13872585'},
        {'year':2018,'record':'13872601'},
        {'year':2019,'record':'13872609'},
        {'year':2020,'record':'13872611'},
        {'year':2021,'record':'13872655'},
        {'year':2022,'record':'13872647'},
        {'year':2023,'record':'13872783'},
        {'year':2024,'record':'13872663'}
    ]