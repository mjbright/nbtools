#!/usr/bin/env python3

# SKELETON CODE for Notebook processing

import json, sys, re, os
import uuid

from inspect import currentframe, getframeinfo
from inspect import stack

''' USAGE:
    ./nbdiff.py -mod1 2:1 -labs1 labs:labs.aza \
        ~/src/mjbright.labs-terraform-private/tf-intro/10.Revision/OP_TF_Lab10.TerraformRevision.ipynb
        ~/src/mjbright.labs-terraform-private/tf-adv-azure/1.Revision/OP_TF_Lab1.TerraformRevision.ipynb
'''

PROG='program'

BLACK='\x1B[00;30m'
RED='\x1B[00;31m';      B_RED='\x1B[01;31m';      BG_RED='\x1B[07;31m'
GREEN='\x1B[00;32m';    B_GREEN='\x1B[01;32m';    BG_GREEN='\x1B[07;32m'
YELLOW='\x1B[00;33m';   B_YELLOW='\x1B[01;33m';   BG_YELLOW='\x1B[07;33m'
NORMAL='\x1B[00m'

MODE='TO_BE_DONE'

DIFF_CODE_CELLS_IP=True
DIFF_CODE_CELLS_OP=False
DIFF_MD_CELLS=False

# e.g.  for notebook1 modifs: -mod1 11:1 to change section numbers from 11 to 1
MODIFY_SECTIONS = None
# e.g.  for notebook1 modifs: -labs1 labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
MODIFY_LABS_PARENT = None

OP_NOTEBOOK = 'FULL.ipynb'
OP_HEADER_NOTEBOOK = None
OP_FOOTER_NOTEBOOK = None
OP_DIVIDER_NOTEBOOK = None
SAVE_MLINE_JSON=False

'''
EXAMPLE cells from notebook json:

    {
      "cell_type": "markdown",
      "id": "present-plastic",
      "metadata": {},
      "source": [
        "<hr/>\n",
        "\n",
        "<!-- Why does this no longer work ??\n",
        "<img src=\"../../../static/images/ThickBlueBar.png\" />\n",
        "<img src=\"../../../static/images/LOGO.jpg\" width=200 />\n",
        "-->\n",
        "\n",
        "<img src=\"../images/ThickBlueBar.png\" />\n",
        "<img src=\"../images/LOGO.jpg\" width=200 />"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "id": "bbeb14a5",
      "metadata": {
        "tags": []
      },
      "outputs": [],
      "source": [
        "NB_QUIET"
      ]
    }

'''

def die(msg):
    sys.stdout.write(f"die: {PROG} {RED}{msg}{NORMAL}\n")
    function = stack()[1].function
    lineno   = stack()[1].lineno
    #fname = stack()[1].filename
    #DEBUG_FD.write(f'[fn {function} line {lineno} {msg}'.rstrip()+'\n')
    print(f'... called from [fn {function}] line {lineno}')
    #DEBUG_FD.close()
    sys.exit(1)

def writefile(path, text='hello world\n', mode='w'):
    ofd = open(path, mode)
    ofd.write(text)
    ofd.close()

def write_nb(opfile, json_data):
    with open(opfile, 'w') as json_file:
        json.dump(json_data, json_file)
          
def read_json(ipfile):
    if not os.path.exists(ipfile):
        die(f'No such input notebook {ipfile}')

    with open(ipfile, encoding='utf-8-sig') as json_file:
        return json.load(json_file)

def pp_json(json_data):
    print(json.dumps(json_data, indent = 4, sort_keys=True))

def pp_nb(json_data):
    print(f"Number of cells: {len(json_data['cells'])} kernel: {json_data['metadata']['kernelspec']['display_name']} nb_format: v{json_data['nbformat']}.{json_data['nbformat_minor']}")
    pp_json(json_data)

def nb_cells(json_data, type=None):
    return len(json_data['cells'])

def get_cell(json_data, cell_no):
    return json_data['cells'][cell_no]   
          
def count_cells(content, cell_type=None):
    count=0

    if cell_type == 'markdown':
        for cell in content["cells"]:
            if cell["cell_type"] == "markdown": count+=1
        return count

    if cell_type == 'code':
        for cell in content["cells"]:
            if cell["cell_type"] == "code": count+=1
        return count

    if cell_type == None:
        count = len(content["cells"])
        return count

    die(f'Unrecognized cell type {cell_type}')

def create_code_cell(nb,    cell_id=None, source_lines=[], metadata={}, execution_count=None, outputs=None):
    __create_cell(nb, 'code',     cell_id, source_lines, metadata, execution_count, outputs)

def create_markdown_cell(nb,cell_id=None, source_lines=[], metadata={}):
    __create_cell(nb, 'markdown', cell_id, source_lines, metadata)

def __create_cell(nb, cell_type, source_lines=[], metadata={}, execution_count=None, cell_id=None, outputs=None):
    #if not cell_id: cell_id = uuid.uuid4()
    if not cell_id: cell_id = uuid.UUID('{12345678-1234-5678-1234-567812345678}')

    if cell_type == 'markdown':
        return { "cell_type": "markdown", "id": cell_id, "metadata": metadata, "source": source_lines }
        
    if cell_type == 'code':
      # ?? "metadata": { "tags": [] },
        return { "nb": "f{nb}", "cell_type": "code", "id": cell_id, "metadata": metadata,
                 "source": source_lines,
                 "execution_count": execution_count, "outputs": outputs
               }
    die(f'Unknown cell type "{cell_type}"')

def filter_cells(content, op_content, notebook, delete_outputs=False):
    started=False

    for cell in content["cells"]:
        if cell['cell_type'] == 'code' and delete_outputs: cell['outputs']=[]
        #print(f'cell={cell}')
        #input()

        if not 'source' in cell:
            if started: op_content["cells"].append( cell )
            continue

        #if 'source' in cell:
        source_lines = cell['source']
        #for cell_no in range(nb_cells(json_data)):
              #source=json_data['cells'][cell_no]['source']
              #if len(source) == 0:

        # CAN we start now?
        if started:
            # search for 'NB_SAVE' entry:
            for source_line in source_lines:
                if source_line.startswith('NB_SAVE'):

                    if not 'NB_SAVE_' in source_line:
                        # return straight away:
                        cell={ 'cell_type':'markdown', 'id': 'end-cell-1', 'metadata': {},
                               'source': [ "# Pragma --INCLUDE--SECTION--\n", ] }
                        op_content["cells"].append( cell )
                        cell={ 'cell_type':'markdown', 'id': 'end-cell-2', 'metadata': {},
                               'source': [ f'#END {notebook}: {source_line}', ] }
                        op_content["cells"].append( cell )
                        cell={ 'cell_type':'markdown', 'id': 'end-cell-3', 'metadata': {},
                               'source': [ "# Pragma --EXCLUDE--SECTION--\n", ] }
                        op_content["cells"].append( cell )
                        return

                elif 'NB_SAVE' in source_line:
                    if not 'NB_SAVE_' in source_line:
                        print("Searching for lines starting with 'NB_SAVE'")
                        die(f'{notebook}: Possible bad occurence of NB_SAVE in line {source_line}')

            op_content["cells"].append( cell )
            continue

        # NOT started, so search for 'nbtool.rc' entry:
        for source_line in source_lines:
            print("Searching for '. ~/scripts/nbtool.rc'")
            print(source_line)
            #input()

            if 'MODE_FULL' in source_line:
                started=True
                #continue

            elif source_line.startswith('. ~/scripts/nbtool.rc'):

                started=True
                cell={ 'cell_type':'markdown', 'id': 'start-cell-1', 'metadata': {},
                       'source': [ "# Pragma --INCLUDE--SECTION--\n", ] }
                op_content["cells"].append( cell )
                cell={ 'cell_type':'markdown', 'id': 'start-cell-2', 'metadata': {},
                       'source': [ f'#START {notebook}: {source_line}', ] }
                op_content["cells"].append( cell )
                cell={ 'cell_type':'markdown', 'id': 'start-cell-3', 'metadata': {},
                       'source': [ "# Pragma --EXCLUDE--SECTION--\n", ] }
                op_content["cells"].append( cell )

                '''
                    { "cell_type": "markdown",
                      "id": "766a77d2-3ba3-454e-a7f6-f77898796c06",
                      "metadata": {},
                      "source": [ "# HEADER: FULL" ]
                    },
                '''

            elif 'nbtool.rc' in source_line:
                print("Searching for lines starting with '. ~/scripts/nbtool.rc'")
                die(f'{notebook}: Possible bad occurence of nbtool.rc in line {source_line}')

    die(f'{notebook}: Never started ...')
    

def copy_cells(content, op_content, notebook, delete_outputs=False):
    for cell in content["cells"]:
        if cell['cell_type'] == 'code' and delete_outputs: cell['outputs']=[]

        op_content["cells"].append( cell )

#die("""TO BE DONE
    #- diff only code cells (only i/p, only o/p, or both)
    #- diff only markdown cells
    #- diff markdown cells and code cells (w/o output)
    #""")

def nbdiff_cells(notebook1, notebook2):
    content1 = read_json(notebook1)
    content2 = read_json(notebook2)
    num_cells1 = count_cells(content1)
    num_cells2 = count_cells(content2)
    num_markdown_cells1 = count_cells(content1, cell_type='markdown')
    num_markdown_cells2 = count_cells(content2, cell_type='markdown')
    num_code_cells1 = count_cells(content1, cell_type='code')
    num_code_cells2 = count_cells(content2, cell_type='code')

    print(f'notebook1={notebook1}')
    print(f'notebook2={notebook2}')

    if num_cells1 != num_cells2:
        print(f'Number of cells differ notebook1:{num_cells1} != notebook2:{num_cells2}')
    if num_markdown_cells1 != num_markdown_cells2:
        print(f'Number of markdown_cells differ notebook1:{num_markdown_cells1} != notebook2:{num_markdown_cells2}')
    if num_code_cells1 != num_code_cells2:
        print(f'Number of code_cells differ notebook1:{num_code_cells1} != notebook2:{num_code_cells2}')

    for i in range(max(num_cells1, num_cells2)):
        if i <= num_cells1 and i <= num_cells2:
            cell1 = content1['cells'][i]
            cell2 = content2['cells'][i]
            if cell1['cell_type'] == 'code' and cell2['cell_type'] == 'code':
                source1 = '\t'.join(cell1['source'])
                source2 = '\t'.join(cell2['source'])
                if source1 != source2:
                    different_cells+=1
                    print(f'code cell[{i}] source differs')
                    print('Print <enter> to see diffs')
                    input()
                    print(f'nb1:\n\t{source1}\n')
                    print(f'nb2:\t{source2}\n')
                else:
                    #print(f'Cells{i} are identical')
                    identical_cells+=1
            print(f'cell={i} identical={identical_cells} different={different_cells}')


    #for cell in content["cells"]:
    #if cell["cell_type"] == "markdown": count+=1

    # num_cells_info = f'[cells: code={num_code_cells} markdown={num_markdown_cells} total={ num_cells }]'
    # print(f'NOTEBOOK{nb} {num_cells_info} {notebook}')
    #print(f'\tkeys: { content.keys() }')
    # if nb == 1:

def nbdiff(notebook1, notebook2):
    content1 = read_json(notebook1)
    content2 = read_json(notebook2)
    num_cells1 = count_cells(content1)
    num_cells2 = count_cells(content2)
    num_markdown_cells1 = count_cells(content1, cell_type='markdown')
    num_markdown_cells2 = count_cells(content2, cell_type='markdown')
    num_code_cells1 = count_cells(content1, cell_type='code')
    num_code_cells2 = count_cells(content2, cell_type='code')

    dump_nb1=''
    dump_nb2=''

    print(f'notebook1={notebook1}')
    print(f'notebook2={notebook2}')

    if num_cells1 != num_cells2:
        print(f'Number of cells differ notebook1:{num_cells1} != notebook2:{num_cells2}')
    if num_markdown_cells1 != num_markdown_cells2:
        print(f'Number of markdown_cells differ notebook1:{num_markdown_cells1} != notebook2:{num_markdown_cells2}')
    if num_code_cells1 != num_code_cells2:
        print(f'Number of code_cells differ notebook1:{num_code_cells1} != notebook2:{num_code_cells2}')

    dump_file1 = notebook1 + ".dump.txt"
    print(f'Dumping {notebook1} to {dump_file1}')
    dump_nb1   = dump_nb(notebook1)

    if MODIFY_LABS_PARENT:
        # e.g.  for notebook1 modifs: -labs1 labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
        ( old_labs_parent, new_labs_parent ) = MODIFY_LABS_PARENT.split(":")
        print(f'old_labs_parent={old_labs_parent} new_labs_parent={new_labs_parent}')
        
        dump_nb1 = dump_nb1.replace(f"~/{old_labs_parent}/", f"~/{new_labs_parent}/")
        dump_nb1 = dump_nb1.replace(f"/home/student/{old_labs_parent}/", f"/home/student/{new_labs_parent}/")


    if MODIFY_SECTIONS:
        # e.g.  for notebook1 modifs: -mod1 11:1 to change section numbers from 11 to 1
        ( old_section, new_section ) = MODIFY_SECTIONS.split(":")
        print(f'old_section={old_section} new_section={new_section}')

        if MODIFY_LABS_PARENT:
            dump_nb1 = dump_nb1.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            dump_nb1 = dump_nb1.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
        else:
            old_labs_parent='labs'
            new_labs_parent=old_labs_parent
            dump_nb1 = dump_nb1.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            dump_nb1 = dump_nb1.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
            old_labs_parent='labs.az'
            new_labs_parent=old_labs_parent
            dump_nb1 = dump_nb1.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            dump_nb1 = dump_nb1.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
            old_labs_parent='labs.aza'
            new_labs_parent=old_labs_parent
            dump_nb1 = dump_nb1.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            dump_nb1 = dump_nb1.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")

        #sys.exit(1)

        # Code-Cell:
        lines=[]
        ''' d1 = dump_nb1 '''
        for line in dump_nb1.split('\n'):
            if 'Code-Cell' in line:
                line = ''

                #  l = line
                #  #print(f'LINE WAS {l}')
                #  line = line.replace(f'[section {old_section}.', f'[section {new_section}.')
                #  #if l != line:
                #  #    print(f'LINE WAS {l}')
                #  #    print(f'LINE NOW {line}')
            lines.append(line)
        dump_nb1 = '\n'.join(lines)
        '''
        d2 = dump_nb1
        if d1 != d2:
            print("d1 != d2")
        else:
            print("d1 IS SAME AS d2")
        '''

        # Markdown replacements:
        if DIFF_MD_CELLS:
            dump_nb1 = dump_nb1.replace(f"# lab{old_section}",  f"# lab{new_section}")
            dump_nb1 = dump_nb1.replace(f"# lab{old_section}.", f"# lab{new_section}.")
            dump_nb1 = dump_nb1.replace(f"## lab{old_section}.", f"## lab{new_section}.")
            dump_nb1 = dump_nb1.replace(f"### lab{old_section}.", f"### lab{new_section}.")
            dump_nb1 = dump_nb1.replace(f"#### lab{old_section}.", f"#### lab{new_section}.")

    sys.stdout.flush()
    writefile(dump_file1, dump_nb1)
    #sys.exit(1)

    dump_file2 = notebook2 + ".dump.txt"
    print(f'Dumping {notebook2} to {dump_file2}')
    dump_nb2 = dump_nb(notebook2)
    writefile(dump_file2, dump_nb2)

    print(f'diff -w {dump_file1} {dump_file2}')
    os.system(f'diff -w {dump_file1} {dump_file2}')

def dump_nb(notebook):
    #identical_cells=0
    #different_cells=0
    dump_nb=''

    content = read_json(notebook)
    for cell in content['cells']:
        cell_type    = cell['cell_type']
        source_lines = cell['source']
        outputs      = []
        if 'outputs' in cell:
            outputs = cell['outputs']

        if cell_type == 'code' and DIFF_CODE_CELLS_IP:
            for line in source_lines:
                if not '# Code-Cell' in line:
                    if line != '' and line != '\n':
                        dump_nb += line + '\n'
            #dump_nb += '\n'.join(source_lines) + '\n'
        if cell_type == 'code' and DIFF_CODE_CELLS_OP and len(outputs) > 0:
            for output in outputs:
                if 'text' in output:
                    for line in output['text']:
                        if line != '' and line != '\n':
                            dump_nb += str(line) + '\n'
            #dump_nb += '\n'.join(outputs) + '\n'
        if cell_type == 'markdown' and DIFF_MD_CELLS:
            for line in source_lines:
                if line != '' and line != '\n':
                    dump_nb += line + '\n'
            #dump_nb += '\n'.join(source_lines) + '\n'
            #dump_nb += '\n'.join(source_lines) + '\n'

    return dump_nb
        
def get_section(line):
    # print(f'SECTION={line}')
    if len(line) <= 2:
        return ''

    # print(f'======== get_section({line})')
    ch = line[2]
    if not( ord(ch) >= ord('0') and ord(ch) <= ord('9') ):
        return ''

    sections = ch
    if len(line) <= 3:
        return sections

    ch = line[3]
    if ch == '.':
        return sections

    ch = line[3]
    if ord(ch) >= ord('a') and ord(ch) <= ord('z'):
        return sections+ch

    if ord(ch) >= ord('0') and ord(ch) <= ord('9'):
        return sections+ch

    return sections+ch

def main():
    #global MODE, OP_NOTEBOOK, SAVE_MLINE_JSON
    global MODIFY_SECTIONS, MODIFY_LABS_PARENT
    global DIFF_CODE_CELLS_IP, DIFF_CODE_CELLS_OP, DIFF_MD_CELLS
    global PROG

    PROG=sys.argv[0]
    a=1

    notebooks=[]
          
    AUTO_MODS=True

    while a < len(sys.argv):
        arg = sys.argv[a]
        a += 1

        if arg == "-mod1":
            # e.g.  for notebook1 modifs: -mod1 11:1 to change section numbers from 11 to 1
            arg = sys.argv[a]
            a += 1
            print("OK")
            MODIFY_SECTIONS = arg
            if MODIFY_SECTIONS.count(":") != 1:
                die("Expected -mod1: <oldmod>:<newmod>, e.g. -mod1 10:1")
            continue

        if arg == "-labs1":
            # e.g.  for notebook1 modifs: -labs1 labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
            arg = sys.argv[a]
            a += 1
            MODIFY_LABS_PARENT = arg
            if MODIFY_LABS_PARENT.count(":") != 1:
                die("Expected -labs1: <olddir>:<newdir>, e.g. -labs1 labs:labs.aza")
            continue

        if arg == "-cc-ip":
            DIFF_CODE_CELLS_IP=False
            continue

        if arg == "+cc-op":
            DIFF_CODE_CELLS_OP=True
            continue

        if arg == "+md":
            DIFF_MD_CELLS=True
            continue

        if arg == "-auto": # Get mod1, labs1 parameters automatically from nb2
            AUTO_MODS=True
            DIFF_MD_CELLS=True
            continue

        if len(notebooks) < 2:
            if not arg.endswith(".ipynb"):
                die(f"Expected only .ipynb files - got {arg}")
          
            if not os.path.exists(arg):
                die(f"No such file - {arg}")

            notebooks.append( arg )
            continue

        if len(notebooks) >= 2:
            die(f"Unrecognized argument: '{arg}'")

        #    ( MODIFY_SECTIONS, MODIFY_LABS_PARENT ) = get_modify_params(notebooks[1])
        #TODO: XXXX

    if len(notebooks) != 2:
        die(f"Missing notebook arguments [{len(notebooks)} notebooks seen, expected i/p and o/p notebooks]")

    if AUTO_MODS:
        dump_nb1   = dump_nb(notebooks[0])
        labs1=''
        labs2=''
        sections1=''
        sections2=''
        for line in dump_nb1.split('\n'):
            if labs1 == '' and '~/labs' in line and 'old' not in line:
                line = line[ line.find('~/labs') + 2 : ]
                if '/' in line:
                    line = line[ : line.find('/') ]
                labs1=line
                pass

            if sections1 == '' and line.startswith('#'):
                sections1 = get_section(line)

            if labs1 != '' and sections1 != '':
                print(f'labs1={labs1} sections1={sections1}')
                break
                #continue

        dump_nb2   = dump_nb(notebooks[0])
        for line in dump_nb2.split('\n'):
            if labs2 == '' and '~/labs' in line and 'old' not in line:
                line = line[ line.find('~/labs') + 2 : ]
                if '/' in line:
                    line = line[ : line.find('/') ]
                labs2=line
                pass

            if sections2 == '' and line.startswith('#'):
                sections2 = get_section(line)

            if labs2 != '' and sections2 != '':
                print(f'labs2={labs2} sections2={sections2}')
                break
                #continue

        MODIFY_SECTIONS=f'{sections1}:{sections2}'
        MODIFY_LABS_PARENT=f'{labs1}:{labs2}'

    print(f'notebooks={ notebooks }')
    print(f'Using OP_NOTEBOOK={OP_NOTEBOOK}')
    print()
    nbdiff(notebooks[0], notebooks[1])
    sys.exit(0)

    nb=0

    # Handle output header and footer notebooks if specified:
    if OP_HEADER_NOTEBOOK:
        notebooks.insert(0, OP_HEADER_NOTEBOOK)
    if OP_FOOTER_NOTEBOOK:
        notebooks.append(OP_FOOTER_NOTEBOOK)

    op_content={}
    op_content["cells"]=[]

    for notebook in notebooks:
        nb+=1
        content = read_json(notebook)
        #print(f'NOTEBOOK {notebook} keys: { keys( content ) }')
        num_cells = count_cells(content)
        num_markdown_cells = count_cells(content, cell_type='markdown')
        num_code_cells = count_cells(content, cell_type='code')
        #num_cells_info = f'number of cells: code={num_code_cells} markdown={num_markdown_cells} total={ num_cells }'
        num_cells_info = f'[cells: code={num_code_cells} markdown={num_markdown_cells} total={ num_cells }]'
        print(f'NOTEBOOK{nb} {num_cells_info} {notebook}')
        #print(f'\tkeys: { content.keys() }')
        if nb == 1:
            #print(f'\tmetadata: { content["metadata"] }')
            print(f'\tnbformat: {content["nbformat"]} nbformat_minor: {content["nbformat_minor"]}')
            #print(f'\tcell[0]: { content["cells"][0] }')

        # Take metadata from first notebook:
        if nb == 1:
            for key in content.keys():
                #print(f'key: {key}')
                if key != 'cells': op_content[key]=content[key]

        if MODE == 'NBTOOL_COPY':
            nb_file = notebook.split('/')[-1]
            #print(f'nb_file={nb_file}')
            if nb_file.startswith("IP_"):
                filter_cells(content, op_content, notebook, delete_outputs=True)
                #pass
            #elif nb_file.startswith("IP_") or \
            elif nb_file.startswith("FULL_HEADER") or nb_file.startswith("FULL_FOOTER"):
                #copy_cells(content, op_content, notebook, delete_outputs=True)
                copy_cells(content, op_content, notebook)
            else:
                die(f'Unexpected notebook name format in {notebook}')

            if OP_DIVIDER_NOTEBOOK:
                content = read_json( OP_DIVIDER_NOTEBOOK )
                #copy_cells(content, op_content, notebook, delete_outputs=True)
                copy_cells(content, op_content, notebook)

        if MODE == 'VANILLA_COPY':
            copy_cells(content, op_content, notebook)
            if OP_DIVIDER_NOTEBOOK:
                content = read_json( OP_DIVIDER_NOTEBOOK )
                copy_cells(content, op_content, notebook)

        write_nb(OP_NOTEBOOK, op_content)
        if SAVE_MLINE_JSON:
            mline_json = json.dumps(op_content, indent = 2, sort_keys=True)
            OP_MLINE_NOTEBOOK=OP_NOTEBOOK[:-5]+"multiline.ipynb"
            writefile(OP_MLINE_NOTEBOOK, mline_json)


if __name__ == "__main__":
    main()

sys.exit(0)
