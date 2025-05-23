#!/usr/bin/env python3

# SKELETON CODE for Notebook processing

import json, sys, re, os
import uuid

from inspect import currentframe, getframeinfo
from inspect import stack

BLACK='\x1B[00;30m'
RED='\x1B[00;31m';      B_RED='\x1B[01;31m';      BG_RED='\x1B[07;31m'
GREEN='\x1B[00;32m';    B_GREEN='\x1B[01;32m';    BG_GREEN='\x1B[07;32m'
YELLOW='\x1B[00;33m';   B_YELLOW='\x1B[01;33m';   BG_YELLOW='\x1B[07;33m'
NORMAL='\x1B[00m'

MODE='TO_BE_DONE'

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
    sys.stdout.write(f"die: {sys.argv[0]} {RED}{msg}{NORMAL}\n")
    function = stack()[1].function
    lineno   = stack()[1].lineno
    #fname = stack()[1].filename
    #DEBUG_FD.write(f'[fn {function} line {lineno} {msg}'.rstrip()+'\n')
    print(f'... called from [fn {function}] line {lineno} {msg}')
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

DIFF_CELLS=1
DIFF_IP=2
DIFF_OP=3

def nbdiff(notebook1, notebook2, DEPTH=DIFF_IP):
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

    identical_cells=0
    different_cells=0
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

def main():
    global MODE, OP_NOTEBOOK, SAVE_MLINE_JSON

    PROG=sys.argv[0]
    a=1

    notebooks=[]
          
    if len(sys.argv) == 1:
        die("Missing arguments")

    notebook1=sys.argv[1]
    notebook2=sys.argv[2]

    nbdiff(notebook1, notebook2)
    sys.exit(0)

    while a < len(sys.argv):
        arg = sys.argv[a]
        a += 1

        # Change MODE: NBTOOL_COPY
        #if arg == '-mode':
            #arg = sys.argv[a]
            #a += 1
            #MODE=arg
            #continue
        if arg == '-nbtool':
            MODE='NBTOOL_COPY'
            continue

        # Define output notebook:
        if arg == '-oN':
            SAVE_MLINE_JSON=True
            continue

        if arg == '-op':
            arg = sys.argv[a]
            a += 1
            OP_NOTEBOOK=arg
            continue

        # Define header notebook to use for output notebook:
        if arg == '-oh':
            arg = sys.argv[a]
            a += 1
            OP_HEADER_NOTEBOOK = arg
            continue

        # Define divider notebook to use for output notebook:
        if arg == '-od':
            arg = sys.argv[a]
            a += 1
            OP_DIVIDER_NOTEBOOK = arg
            continue

        # Define footer notebook to use for output notebook:
        if arg == '-of':
            arg = sys.argv[a]
            a += 1
            OP_FOOTER_NOTEBOOK = arg
            continue

        if os.path.exists(arg) and os.path.isdir(arg):
            die(f"TODO: read folder of .ipynb files")

        if not arg.endswith(".ipynb"):
            die(f"Expected only .ipynb files - got {arg}")
          
        if not os.path.exists(arg):
            die(f"No such file - {arg}")

        notebooks.append(arg)

    print(f'notebooks={ notebooks }')
    print(f'Using OP_NOTEBOOK={OP_NOTEBOOK}')
    print()
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
