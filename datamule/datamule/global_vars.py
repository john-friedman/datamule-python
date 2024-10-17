headers = {
    "User-Agent": "Peter Smith petersmith@gmail.com"  # Replace with your information
}

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