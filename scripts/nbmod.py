#!/usr/bin/env python3

''' USAGE:
    ./nbmod.py -mod 10:27 -labs labs:labs.testing \
        ~/src/mjbright.labs-terraform-private/tf-intro/10.Revision/IP_TF_Lab10.Revision.ipynb
'''

# SKELETON CODE for Notebook processing

import json
import sys
#import re
import os
import uuid

#from inspect import currentframe, getframeinfo
from inspect import stack

PROG='program'

BLACK='\x1B[00;30m'
RED='\x1B[00;31m'
B_RED='\x1B[01;31m'
BG_RED='\x1B[07;31m'
GREEN='\x1B[00;32m'
B_GREEN='\x1B[01;32m'
BG_GREEN='\x1B[07;32m'
YELLOW='\x1B[00;33m'
B_YELLOW='\x1B[01;33m'
BG_YELLOW='\x1B[07;33m'
NORMAL='\x1B[00m'

MODE='TO_BE_DONE'

MOD_CODE_CELLS_IP=True
MOD_CODE_CELLS_OP=False
MOD_MD_CELLS=False
old_labs_parent='old_labs_parent'
new_labs_parent='new_labs_parent'
old_section='old_section'
new_section='new_section'

# e.g.  for notebook1 modifs: -mod 11:1 to change section numbers from 11 to 1
MODIFY_SECTIONS = None
# e.g.  for notebook1 modifs: -labs labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
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
            if cell["cell_type"] == "markdown":
                count+=1
        return count

    if cell_type == 'code':
        for cell in content["cells"]:
            if cell["cell_type"] == "code":
                count+=1
        return count

    if cell_type is None:
        count = len(content["cells"])
        return count

    die(f'Unrecognized cell type {cell_type}')

def create_code_cell(nb,    cell_id=None, source_lines=[], metadata={}, execution_count=None, outputs=None):
    __create_cell(nb, 'code',     cell_id, source_lines, metadata, execution_count, outputs)

def create_markdown_cell(nb,cell_id=None, source_lines=[], metadata={}):
    __create_cell(nb, 'markdown', cell_id, source_lines, metadata)

def __create_cell(nb, cell_type, source_lines=[], metadata={}, execution_count=None, cell_id=None, outputs=None):
    #if not cell_id: cell_id = uuid.uuid4()
    if not cell_id:
        cell_id = uuid.UUID('{12345678-1234-5678-1234-567812345678}')

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
        if cell['cell_type'] == 'code' and delete_outputs:
            cell['outputs']=[]
        #print(f'cell={cell}')
        #input()

        if 'source' not in cell:
            if started:
                op_content["cells"].append( cell )
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

                    if 'NB_SAVE_' not in source_line:
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
                    if 'NB_SAVE_' not in source_line:
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
        if cell['cell_type'] == 'code' and delete_outputs:
            cell['outputs']=[]

        op_content["cells"].append( cell )

'''
die("""TO BE DONE
        - strip all output cells
        - recalculate Code-Cell info
        - recalculate Sections (or do this on markdown?)
        - detect unexpected occurences (empty code i/p cells, NB_*, TF_*, $__VAR, ...) (or do this on markdown)
        """)
'''

def modify_line(line):
    global MODIFY_LABS_PARENT, MODIFY_SECTIONS
    global old_labs_parent, new_labs_parent
    global old_section, new_section

    orig_line = line

    if '# Code-Cell' in line:
        line = ''

    '''
    if MODIFY_LABS_PARENT:
        print('MODIFY_LABS_PARENT:')
        print(f'line.replace("~/{old_labs_parent}/", "~/{new_labs_parent}/"))')
    #    print('MODIFY_LABS_PARENT:')
    if MODIFY_SECTIONS:
        print('MODIFY_SECTIONS:')
        print(f'line.replace("{old_section}", "{new_section}"))')
    '''

    if MODIFY_LABS_PARENT:
        # e.g.  for notebook1 modifs: -labs labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
        line = line.replace(f"~/{old_labs_parent}/", f"~/{new_labs_parent}/")
        line = line.replace(f"/home/student/{old_labs_parent}/", f"/home/student/{new_labs_parent}/")

        '''
        if MODIFY_SECTIONS:
            line = line.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            line = line.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
        '''

        if MODIFY_SECTIONS:
            line = line.replace(f"lab{old_section}", f"lab{new_section}")
            '''
            old_labs_parent='labs'
            new_labs_parent=old_labs_parent
            line = line.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            line = line.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
            old_labs_parent='labs.az'
            new_labs_parent=old_labs_parent
            line = line.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            line = line.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
            old_labs_parent='labs.aza'
            new_labs_parent=old_labs_parent
            line = line.replace(f"~/{new_labs_parent}/lab{old_section}", f"~/{new_labs_parent}/lab{new_section}")
            line = line.replace(f"/home/student/{new_labs_parent}/lab{old_section}", f"/home/student/{new_labs_parent}/lab{new_section}")
            '''

            line = line.replace(f' {old_section}.', f' {new_section}.')
            print(f"line.replace(f' {old_section}.', f' {new_section}.')")

                # Markdown replacements:
            if MOD_MD_CELLS:
                #for mot_cle in [ '', 'lab', 'Lab', 'Ex', 'Exercise' ]:
                for mot_cle in [ 'lab', 'Lab', 'Ex', 'Exercise' ]:
                    line = line.replace(f"# {mot_cle}{old_section}",  f"# {mot_cle}{new_section}")
                    ## #line = line.replace(f"# {mot_cle}{old_section}.", f"# {mot_cle}{new_section}.")
                    ## #line = line.replace(f"# {mot_cle}{old_section}:", f"# {mot_cle}{new_section}:")
                    ## line = line.replace(f"## {mot_cle}{old_section}.", f"## {mot_cle}{new_section}.")
                    ## line = line.replace(f"## {mot_cle}{old_section}:", f"## {mot_cle}{new_section}:")
                    ## line = line.replace(f"### {mot_cle}{old_section}.", f"### {mot_cle}{new_section}.")
                    ## line = line.replace(f"### {mot_cle}{old_section}:", f"### {mot_cle}{new_section}:")
                    ## line = line.replace(f"#### {mot_cle}{old_section}.", f"#### {mot_cle}{new_section}.")
                    ## line = line.replace(f"#### {mot_cle}{old_section}:", f"#### {mot_cle}{new_section}:")

    if orig_line != line:
        print(f'LINE CHANGED from\n\t{orig_line}\nto\n\t{line}\n')
    return line



'''
                    #line = str(line)
                    if line != '' and line != '\n':
                       if MODIFY_LABS_PARENT:
                           # e.g.  for notebook1 modifs: -labs labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
                           line = line.replace(f"~/{old_labs_parent}/", f"~/{new_labs_parent}/")
'''

def nbmod(ip_notebook, op_notebook):
    global old_labs_parent, new_labs_parent
    global old_section, new_section

    content = read_json(ip_notebook)
    num_cells = count_cells(content)
    num_markdown_cells = count_cells(content, cell_type='markdown')
    num_code_cells = count_cells(content, cell_type='code')

    print(f'Number of cells: {num_cells}')
    print(f'Number of markdown_cells:{num_markdown_cells}')
    print(f'Number of code_cells {num_code_cells}')

    old_labs_parent='xxxxxxxxxxxx'
    new_labs_parent='yyyyyyyyyyyy'
    if MODIFY_LABS_PARENT:
        # e.g.  for notebook1 modifs: -labs labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
        ( old_labs_parent, new_labs_parent ) = MODIFY_LABS_PARENT.split(":")
        print(f'old_labs_parent={old_labs_parent} new_labs_parent={new_labs_parent}')

    if MODIFY_SECTIONS:
        # e.g.  for notebook1 modifs: -mod 11:1 to change section numbers from 11 to 1
        ( old_section, new_section ) = MODIFY_SECTIONS.split(":")
        print(f'old_section={old_section} new_section={new_section}')

    if MOD_CODE_CELLS_IP:
        print('Modifying code cells i/p')
    if MOD_CODE_CELLS_OP:
        print('Modifying code cells o/p')

    cellno=-1
    for cell in content['cells']:
        cellno+=1
        cell_type    = cell['cell_type']
        source_lines = cell['source']
        outputs      = []
        if 'outputs' in cell:
            outputs = cell['outputs']

        #print(f'[cell {cellno}] type={cell_type}')
        if cell_type == 'code' and MOD_CODE_CELLS_IP:
            lines = []
            print(f'[cell {cellno}] type={cell_type} - Modifying i/p')
            for line in source_lines:
                line = modify_line(line)
                lines.append(line)

            cell['source'] = ''.join(lines)

        if cell_type == 'code' and MOD_CODE_CELLS_OP:
            print(f'[cell {cellno}] type={cell_type} - Modifying o/p')
            #opno=0
            for opno in range(len(outputs)):
                output = outputs[opno]
                #opno+=1
                lines = []
                if 'text' in output:
                    for line in output['text']:
                        line = modify_line(line)
                        lines.append(line)

                    cell['outputs'][opno]['text'] = lines

            #cell['outputs'] = ''.join(lines)

            #dump_nb += '\n'.join(outputs) + '\n'
        if cell_type == 'markdown' and MOD_MD_CELLS:
            print(f'[cell {cellno}] type={cell_type} - Modifying markdown')
            lines = []
            for line in source_lines:
                line = modify_line(line)
                lines.append(line)

            cell['source'] = ''.join(lines)

    write_nb(op_notebook, content)
    ip_dump_nb = dump_nb(ip_notebook)
    ip_dump_file=insert_filename(ip_notebook, 'dump_') + '.txt'
    writefile(ip_dump_file, ip_dump_nb)
    print(f'Wrote dump of ip notebook to {ip_dump_file}')

    op_dump_nb = dump_nb(op_notebook)
    op_dump_file=insert_filename(op_notebook, 'dump_') + '.txt'
    writefile(op_dump_file, op_dump_nb)
    print(f'Wrote dump of op notebook to {op_dump_file}')
    sys.exit(0)

def insert_filename(orig_filepath, insertion):
    if '/' in orig_filepath:
        pos_st_file = orig_filepath.rfind('/')
        orig_dir = orig_filepath[ : pos_st_file ]
        orig_file = orig_filepath[ pos_st_file+1 : ]
        op_filepath = f'{orig_dir}/{insertion}{orig_file}'
    else:
        op_filepath = f'{insertion}{orig_filepath}'
    return op_filepath

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

        # print(outputs)
        # print(f'type(outputs) = {type(outputs)}')
        # if len(outputs) != 0:
        #     print(f'type(outputs[0]) = {type(outputs[0])}')
        #     print(f'type(outputs) = {type("\n".join(str(outputs)))}')
        if cell_type == 'code':
            dump_nb += '# CODE CELL:\n'
            #dump_nb += '\n'.join(source_lines)
            dump_nb += ''.join(source_lines)
            dump_nb += '\n'
            dump_nb += '# CODE OUTPUT:\n'
            #dump_nb += '\n'.join(str(outputs))
            dump_nb += ''.join(str(outputs))
            dump_nb += '\n'

        if cell_type == 'markdown':
            dump_nb += '# MARKDOWN CELL:\n'
            #dump_nb += '\n'.join(source_lines)
            dump_nb += ''.join(source_lines)
            dump_nb += '\n'

    return dump_nb
        
def main():
    #global MODE, OP_NOTEBOOK, SAVE_MLINE_JSON
    global MODIFY_SECTIONS, MODIFY_LABS_PARENT
    global MOD_CODE_CELLS_IP, MOD_CODE_CELLS_OP, MOD_MD_CELLS
    global PROG

    PROG=sys.argv[0]
    a=1

    notebooks=[]

    while a < len(sys.argv):
        arg = sys.argv[a]
        a += 1

        if arg == "-mod":
            # e.g.  for notebook1 modifs: -mod 11:1 to change section numbers from 11 to 1
            arg = sys.argv[a]
            a += 1
            print("OK")
            MODIFY_SECTIONS = arg
            if MODIFY_SECTIONS.count(":") != 1:
                die("Expected -mod: <oldmod>:<newmod>, e.g. -mod 10:1")
            continue

        if arg == "-labs":
            # e.g.  for notebook1 modifs: -labs labs:labs.aza to change labs parent folder from ~/labs/ to ~/labs.aza/
            arg = sys.argv[a]
            a += 1
            MODIFY_LABS_PARENT = arg
            if MODIFY_LABS_PARENT.count(":") != 1:
                die("Expected -labs: <olddir>:<newdir>, e.g. -labs labs:labs.aza")
            continue

        if arg == "-cc-ip":
            MOD_CODE_CELLS_IP=False
            continue

        if arg == "+cc-op":
            MOD_CODE_CELLS_OP=True
            continue

        if arg == "+md":
            MOD_MD_CELLS=True
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

        #TODO: XXXX
        #if arg == "-auto": # Get mod1, labs1 parameters automatically from nb2
        #    ( MODIFY_SECTIONS, MODIFY_LABS_PARENT ) = get_modify_params(notebooks[1])
        #TODO: XXXX

    if len(notebooks) == 0:
        die("Missing notebook arguments")

    ip_notebook = notebooks[0]
    print(f'Input notebook={ ip_notebook }')

    if len(notebooks) >= 2:
        op_notebook = notebooks[1]
        print(f'Output notebook={ op_notebook }')
    else:
        op_notebook = insert_filename(ip_notebook, 'op_')

        #notebooks.append( f'op_notebook' )
        print(f'Missing output notebook, setting {op_notebook} as output')

    #print(f'Using OP_NOTEBOOK={OP_NOTEBOOK}')
    print()
    nbmod(ip_notebook, op_notebook)
    sys.exit(0)

if __name__ == "__main__":
    main()

sys.exit(0)
