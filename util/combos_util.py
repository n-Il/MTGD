import time
import sys
import requests
import json
import os

class combos_util:
    API_LINK = "https://json.commanderspellbook.com/variants.json.gz"

    def __init__(self):
        return
   
    @staticmethod
    def get():
        if not os.path.isdir('data'):
            print("ERROR: missing data folder")
            return None
        elif not os.path.isdir('data/combos/'):
            print("ERROR: missing data/combos folder.(Run -downloadcombos)")
            return None
        #read into dict as key=requiredcards,value=combo
        list_of_files = list(map(lambda x: "data/combos/" + x,os.listdir("data/combos"))) 
        if len(list_of_files) == 0:
            print("ERROR: missing combo data.(Run -downloadcombos)")
            return None
        latest = max(list_of_files,key=os.path.getctime)
        combos = dict()
        with open(latest,encoding='utf-8') as f:
            combos_json = json.load(f) 
        for combo in combos_json["variants"]:
            required_cards = set()
            for card in combo["uses"]:
                required_cards.add(card["card"]["name"])
            combos[tuple(required_cards)] = combo
        return combos

    @staticmethod
    def download():
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.isdir('data/combos'):
            os.mkdir('data/combos')
        API_LINK = "https://json.commanderspellbook.com/variants.json.gz"
        combos_data = json.loads(requests.get(API_LINK).content)
        if os.path.exists("data/combos/combos-"+combos_data["timestamp"].replace(':','_')+".json"):
            print("ERROR: You already have the latest combo data.")
        else:
            with open("data/combos/combos-"+combos_data["timestamp"].replace(':','_')+".json","w+",encoding='utf-8') as f:
                json.dump(combos_data,f)

    @staticmethod
    def pp(combos):
        #print more data
        for reqs,combo in combos.items():
            print("Requires:","   ".join(reqs))
            print("    Description:")
            step = 0
            for line in combo["description"].split('\n'):
                step += 1
                line = str(step)+":"+line
                #grab up to 50 characters at a time
                while line:
                    grab = line[:75]
                    print("    "+grab)
                    line = line[75:]
                #print with tab indent
                print()
            print()
    
    @staticmethod
    #combos: dict(tuple of required cardnames(str)) with values equal to the commanderspellbook combo entries
    def force_graph(combos):
        page = [
            '<head>\n',
            '  <style> body { margin: 0; } </style>\n',
            '  <script src="util/3d-force-graph/3d-force-graph.js"></script>\n',
            '</head>\n',
            '<body>\n',
            '  <div id="3d-graph"></div>\n',
            '  <script>\n',
            '    // Random tree\n',
            '    const N = 1;\n',
            '    const gData = {\n',
            '      nodes: [ \n',
            '        { id: 1 }, \n',
            "        { id: '4659-5003-5359', on_hover:'testing' }, \n",
            '        { id: 3 }\n',
            '      ],\n',
            '      links: [ \n',
            "        { source:1, target:'4659-5003-5359' },\n",
            '      ],\n',
            '    };\n',
            '    const Graph = ForceGraph3D()\n',
            "      (document.getElementById('3d-graph'))\n",
            '        .linkWidth(2)\n',
            "        .linkColor(() => 'rgba(255,0,0,1)' )\n",
            "        .nodeColor(() => 'rgba(255,255,255,1)' )\n",
            "        .nodeLabel('on_hover')\n",
            "        .onNodeClick(node => window.open(`https://commanderspellbook.com/combo/${node.id}/`,'_blank'))\n",
            '        .linkOpacity(0.5)\n',
            '        .nodeOpacity(0.5)\n',
            '        .graphData(gData);\n',
            '  </script>\n',
            '</body>\n',
        ]
        with open("3d_force_graph_combos.html","w+",encoding='utf-8') as html:
            #write first 12
            html.writelines(page[:11])
            
            #write nodes
            for reqs,combo in combos.items():
                html.write((8*" ")+"{"+" id:'{}' ,on_hover:'{}' ".format(combo["id"],"<br>".join(map(lambda x: x.replace("'","\\'"),reqs)))+"},\n")
            
            #write 2
            html.writelines(page[14:16])
            
            #create lookup table for cards, each combo in each table shares links with each other
            link_lookup = dict()
            for reqs,combo in combos.items():
                for card in reqs:
                    if card not in link_lookup:
                        link_lookup[card] = set()
                    link_lookup[card].add(combo["id"])
            #get links, yikes complexity
            links = set()#using this to simplify handling redundant links
            for combos in link_lookup.values():
                for combo in combos:
                    for othercombo in combos:
                        if combo != othercombo: #if not loop link
                            links.add(frozenset([combo,othercombo]))
             
            for link in links:
                html.write("        "+"{"+" source:'{}' ,target:'{}' ".format(*link)+"}"+",\n")

            #write last 14
            html.writelines(page[17:])

    @staticmethod
    #combos: dict(tuple of required cardnames(str)) with values equal to the commanderspellbook combo entries
    def force_graph2(combos):
        page = [
            '<head>\n',
            '  <style> body { margin: 0; } </style>\n',
            '  <script src="util/3d-force-graph/3d-force-graph.js"></script>\n',
            '</head>\n',
            '<body>\n',
            '  <div id="3d-graph"></div>\n',
            '  <script>\n',
            '    const gData = {\n',
            '      nodes: [ \n',
            '      ],\n',
            '      links: [ \n',
            '      ],\n',
            '    };\n',
            '    const Graph = ForceGraph3D()\n',
            "      (document.getElementById('3d-graph'))\n",
            "        .nodeLabel('on_hover')\n",
            "        .onNodeClick(node => window.open(`https://commanderspellbook.com/${node.on_click}/`,'_blank'))\n",
            '        .nodeAutoColorBy(\'group\')\n',
            '        .linkAutoColorBy(\'to_card\')\n',
            '        .graphData(gData);\n',
            '  </script>\n',
            '</body>\n',
        ]
        cards = set()
        links = set()
        for reqs,combo in combos.items():
            for card in reqs:
                cards.add(card)#this populates the cards set
                links.add((combo["id"],card))#this populates the links from combos to cards

        with open("3d_force_graph_combos.html","w+",encoding='utf-8') as html:
            #write first 12
            html.writelines(page[:9])

            #write nodes
            for card in cards:
                html.write((8*" ")+"{"+" id:'{0}', on_hover:'{0}', group:'card', on_click:'search/?q={0}' ".format(card.replace("'","\\'"))+"},\n")
            
            for reqs,combo in combos.items():
                html.write((8*" ")+"{"+" id:'{0}', on_hover:'{1}', group:'combo', on_click:'combo/{0}'  ".format(combo["id"],"<br>".join(map(lambda x: x.replace("'","\\'"),reqs)))+"},\n")
                
            #write 2
            html.writelines(page[9:11])
            
            #write links
            for link in links:
                html.write("        "+"{"+" source:'{0}' ,target:'{1}', to_card:'{1}' ".format(link[0],link[1].replace("'","\\'"))+"}"+",\n")

            #write last 14
            html.writelines(page[11:])

