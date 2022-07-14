import bs4
from time import sleep, time
import pandas as pd
from datetime import datetime 
import json, requests
from xml.etree import ElementTree

"""

    TIME STUFF

"""

def formatted_datetime_now():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def read_json(inputpath):
    with open(inputpath) as reader:
        data = reader.read()

    return json.loads(data)
    
def dump_json(inputdict,outputpath):
    with open(outputpath,'w+') as json_handle:
        json.dump(inputdict,json_handle)

def record_datetime(key,json_path='data/last_updated.json'):

    datadict = read_json(json_path)

    datadict[key] = formatted_datetime_now()

    dump_json(datadict,json_path)



"""

    HTML STUFF

"""

def gen_updating_infotable_page(outpath='data/data_updating.html',json_path='data/last_updated.json'):


    tablepart = ''

    records_dict = read_json(json_path)

    for key in records_dict:
        tablepart += f"<tr><th><b>{key}</b></th><th>{records_dict[key]}</th></tr>"

    page_as_txt = f'''
    <!DOCTYPE html>
<html>
<head>
<title>OSWM Updating Info</title>


<style>


h1 {{text-align: center;}}



table {{
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}}

td, th {{
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}}

tr:nth-child(even) {{
  background-color: #dddddd;
}}
</style>
</head>
<body>

<h1><a href="https://kauevestena.github.io/opensidewalkmap_beta">OSWM</a> Updating Info</h1>

<table>

{tablepart}

</table>


<h1>Download Data:</h1>

<table>

<tr>
  <th>Sidewalks</th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/sidewalks_raw.geojson">Raw</a></th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/sidewalks.geojson">Filtered</a></th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/sidewalks_versioning.json">Versioning</a></th>
</tr>

<tr>
  <th>Crossings</th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/crossings_raw.geojson">Raw</a></th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/crossings.geojson">Filtered</a></th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/crossings_versioning.json">Versioning</a></th>
</tr>

<tr>
  <th>Kerbs</th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/kerbs_raw.geojson">Raw</a></th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/kerbs.geojson">Filtered</a></th>
  <th><a href="https://kauevestena.github.io/opensidewalkmap_beta/data/kerbs_versioning.json">Versioning</a></th>
</tr>



</table>



</body>
</html>    
    '''

    with open(outpath,'w+') as writer:
        writer.write(page_as_txt)

def find_map_ref(input_htmlpath):
    with open(input_htmlpath) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt,features='lxml')

    refs = soup.find_all(attrs={'class':"folium-map"})

    for found_ref in refs:
        return found_ref['id']




def find_html_name(input_htmlpath,specific_ref,tag_ref='img',specific_tag='src',identifier='id'):

    with open(input_htmlpath) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt,features='lxml')

    refs = soup.find_all(tag_ref)


    for found_ref in refs:


        # if specific_tag in found_ref:

        if found_ref[specific_tag] == specific_ref:
            return found_ref[identifier]
            

def style_changer(in_out_htmlpath,element_key,key='style',original='bottom',new='top',append=None):
    with open(in_out_htmlpath) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt,features='lxml')

    style_refs = soup.find_all(key)

    for style_ref in style_refs:
        as_txt = style_ref.get_text()
        if element_key in as_txt:

            if new:
                new_text = as_txt.replace(original,new)
            else:
                new_text = as_txt

            if append:
                new_text += append

            break


    with open(in_out_htmlpath,'w+', encoding='utf-8') as writer:
        writer.write(str(soup).replace(as_txt,new_text))

    sleep(0.2)

        
def add_to_page_after_first_tag(html_filepath,element_string,tag_or_txt='<head>',count=1):
    '''
    Quick and dirty way to insert some stuff directly on the webpage 

    Originally intended only for <head>

    beware of tags that repeat! the "count" argument is very important!
    '''


    with open(html_filepath) as reader:
        pag_txt = reader.read()

    replace_text = f'{tag_or_txt} \n{element_string}\n'

    
    with open(html_filepath,'w+') as writer:
        writer.write(pag_txt.replace(tag_or_txt,replace_text,count))

    sleep(.1)

def replace_at_html(html_filepath,original_text,new_text,count=1):
    '''
    Quick and dirty way to replace some stuff directly on the webpage 

    Originally intended only for <head>

    beware of tags that repeat! the "count" argument is very important!
    '''


    with open(html_filepath) as reader:
        pag_txt = reader.read()

    
    with open(html_filepath,'w+') as writer:
        writer.write(pag_txt.replace(original_text,new_text,count))

    sleep(.1)


# (geo)Pandas stuff:
def get_score_df(inputdict,category='sidewalks',osm_key='surface',input_field='score_default',output_field_base='score'):

    output_field_name = f'{category}_{osm_key}_{output_field_base}'
    dict = {osm_key:[],output_field_name:[]}

    for val_key in inputdict[category][osm_key]:
        dict[osm_key].append(val_key)
        dict[output_field_name].append(inputdict[category][osm_key][val_key][input_field])

    return  pd.DataFrame(dict), output_field_name


def get_attr_dict(inputdict,category='sidewalks',osm_tag='surface',attr='color'):
    color_dict = {}
    for tag_value in inputdict[category][osm_tag]:
        color_dict[tag_value] = inputdict[category][osm_tag][tag_value][attr]

    return color_dict

def return_weblink_way(string_id):
    return f"<a href=https://www.openstreetmap.org/way/{string_id}>{string_id}</a>"

def return_weblink_node(string_id):
    return f"<a href=https://www.openstreetmap.org/node/{string_id}>{string_id}</a>"

'''

HISTORY STUFF

'''

def get_feature_history_url(featureid,type='way'):
    return f'https://www.openstreetmap.org/api/0.6/{type}/{featureid}/history'

def get_datetime_last_update(featureid,featuretype='way',onlylast=True,return_parsed=True,return_special_tuple=True):

    h_url = get_feature_history_url(featureid,featuretype)


    response = requests.get(h_url)

    print(featureid)


    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)

        element_list = tree.findall(featuretype)

        if element_list:
            date_rec = [element.attrib['timestamp'][:-1] for element in element_list]

            if onlylast:
                if return_parsed:
                    if return_special_tuple:
                        parsed = datetime.strptime(date_rec[-1],'%Y-%m-%dT%H:%M:%S')
                        return len(date_rec),parsed.day,parsed.month,parsed.year

                    else:
                        return datetime.strptime(date_rec[-1],'%Y-%m-%dT%H:%M:%S')

                
                else:
                    return date_rec[-1]

            else:
                if return_parsed:
                    return [datetime.strptime(record,'%Y-%m-%dT%H:%M:%S') for record in date_rec]


                else:
                    return date_rec


        else:
            if onlylast:
                return ''
            else:
                return []
    
    else:
        print('bad request, check feature id/type')
        if onlylast:
            return ''
        else:
            return []


def get_datetime_last_update_node(featureid):
    # all default options
    return get_datetime_last_update(featureid,featuretype='node')
