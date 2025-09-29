#!/usr/bin/env python3

import json, sys, re, os

""" MAIN PATH FLOW: (filter mode):
   new_data = filter_nb( read_json(ipfile), DEBUG )
   opfile=ipfile+'.filtered.ipynb'
   write_nb(opfile, new_data)
"""

OP_DIR = "other"
HOME="/home/student"

VERBOSE_sections = False
VERBOSE_NB_FILE = True
# VERBOSE_NB_FILE=False

# TODO:
# - add option to put cell_no/type as a comment in cell (only for code cells)

# For converting output form code blocks form ANSI codes to HTML:
from ansi2html import Ansi2HTMLConverter

ansi2html_conv = Ansi2HTMLConverter()

from inspect import currentframe, getframeinfo
from inspect import stack

SSH_NODE = "worker"

# For copy.deepcopy:
import copy

IDIR = "../images"
# IDIR="/images"

QUESTIONS = []
NUM_QUESTIONS = 0

# NOTE: useful to have <div id='TOC' marker to identify sections
INCLUDE_TOC = False
# count_sections set to True if a cell with <div id='TOC' is found

# THICK_BAR=f"{IDIR}/ThickPurpleBar.png"
# THIN_BAR=f"{IDIR}/ThinPurpleBar.png"

THICK_BAR = f"{IDIR}/ThickBlueBar.png"
THIN_BAR = f"{IDIR}/ThinBlueBar.png"

INSERT_THICK_BAR = "![](" + f"{THICK_BAR})\n"
INSERT_THIN_BAR = "![](" + f"{THIN_BAR})\n"
# TODO:
INSERT_MED_BAR = "![](" + f"{THIN_BAR})\n"
# INSERT_THICK_BAR==f'<img align="left" src="{THICK_BAR}" height="200" /><br/>'
# INSERT_THIN_BAR==f'<img align="left" src="{THICK_BAR}" height="200" /><br/>'

BLACK = "\x1b[00;30m"
# RED='\x1B[00;31m'
# BLUE='\x1B[00;32m'
# NORMAL='\x1B[00m'

RED = "\x1b[00;31m"
B_RED = "\x1b[01;31m"
BG_RED = "\x1b[07;31m"
GREEN = "\x1b[00;32m"
B_GREEN = "\x1b[01;32m"
BG_GREEN = "\x1b[07;32m"
YELLOW = "\x1b[00;33m"
B_YELLOW = "\x1b[01;33m"
BG_YELLOW = "\x1b[07;33m"
NORMAL = "\x1b[00m"

# frameinfo = getframeinfo(currentframe())
# print(frameinfo.filename, frameinfo.lineno)
# currentframe().f_back
# call_frameinfo = getframeinfo(currentframe().f_back)
# from inspect: stack()


def getenvBOOLEAN(NAME, DEFAULT):
    if DEFAULT:
        value = os.getenv(NAME, "1")
    else:
        value = os.getenv(NAME, "0")

    if value == "0":
        return False
    return True


REMOVE_SHORT = getenvBOOLEAN("REMOVE_SHORT", False)
REMOVE_SHORT = True

DEBUG_F = os.getenv("HOME", "/tmp") + "/tmp/nbtool.py.debug.op"
DEBUG_FD = open(DEBUG_F, "w")
DEBUG_FD.write("OPEN\n")
DEBUG_FD.write("---- " + " ".join(sys.argv) + "\n")

DEBUG = getenvBOOLEAN("DEBUG", False)
DEBUG_LINES = getenvBOOLEAN("DEBUG_LINES", False)
DEBUG_CELLNOS = getenvBOOLEAN("DEBUG_CELLNOS", False)


def DEBUG(msg=""):
    global DEBUG_FD

    function = stack()[1].function
    lineno = stack()[1].lineno
    # fname = stack()[1].filename
    DEBUG_FD.write(f"[fn {function} line {lineno} {msg}".rstrip() + "\n")


def die(msg):
    sys.stdout.write(f"die: {RED}{msg}{NORMAL}\n")
    function = stack()[1].function
    lineno = stack()[1].lineno
    # fname = stack()[1].filename
    DEBUG_FD.write(f"[fn {function} line {lineno} {msg}".rstrip() + "\n")
    print(f"... called from [fn {function} line {lineno} {msg}")
    DEBUG_FD.close()
    sys.exit(1)


# DEBUG('testing')

# Max length for code-cell lines:
# MAX_LINE_LEN=110
# MAX_LINE_LEN=100
# MAX_LINE_LEN=80

# DEFAULT_MAX_LINE_LEN=85
DEFAULT_MAX_LINE_LEN = 100
MAX_LINE_LEN = int(os.getenv("MAX_LINE_LEN", DEFAULT_MAX_LINE_LEN))

VARS_SEEN = {}

REPLACE_OP_WORDS = {
    "$STUDENT": os.getenv("STUDENT", "student20"),
    "${STUDENT}": os.getenv("STUDENT", "student20"),
    #'EOF```':      'EOF\n```\n',
}

# Lines with these strings should be completely emptied:
# - but doesn't exclude cell, so output may need to go via NB_DEBUG
REPLACE_LINES = [
    "TIMER_START",
    "TIMER_STOP",
    "NBTOOL_FN",
]

# Lines with these strings should have the keyword replaced
REPLACE_COMMANDS = {
    "TF_INIT": "terraform init",
    "TF_PLAN -qt": "terraform plan",
    "TF_PLAN -tq": "terraform plan",
    "TF_PLAN -q": "terraform plan",
    "TF_PLAN -t": "terraform plan",
    "TF_PLAN": "terraform plan",
    "TF_APPLY -qt": "terraform apply",
    "TF_APPLY -tq": "terraform apply",
    "TF_APPLY -q": "terraform apply",
    "TF_APPLY -t": "terraform apply",
    "TF_APPLY": "terraform apply",
    "TF_DESTROY -qt": "terraform destroy",
    "TF_DESTROY -tq": "terraform destroy",
    "TF_DESTROY -q": "terraform destroy",
    "TF_DESTROY -t": "terraform destroy",
    "TF_DESTROY": "terraform destroy",
    "TF_GET": "terraform get",
    "TF_GRAPH": "terraform graph",
    "TF_SHOW": "terraform show",
    "TF_STATE": "terraform state",
    "TF_OUTPUT": "terraform output",
    "TF_IMPORT": "terraform import",
    "TF_FMT": "terraform fmt",
    "TF_VALIDATE": "terraform validate",
    "TF_TEST": "terraform test",
    "K_GET": "kubectl get",
    "K_CREATE": "kubectl create",
    "NB_CODE": "",
    #'EOF```':      'EOF\n```\n',
}

# OK: TF_INIT TF_PLAN TF_APPLY TF_DESTROY TF_GRAPH TF_SHOW TF_STATE TF_OUTPUT TF_IMPORT TF_FMT TF_TEST TF_VALIDATE TF_GET
# TODO: ?? TF_LOG_FILTER ??

def get_longest_matching_key(mydict, search):
    found_len = 0
    found = None

    for key in mydict:
        if key in search:
            if len(key) > found_len:
                found = key
                found_len = len(key)
    return found


"""
def raw_ansi2text(ansi):
    return ansi
"""


def raw_ansi2text(ansi):
    # return "ANSI: " + ansi.replace('\u001b[0m', ''). \
    M = 10  # Max number of replacements
    return (
        ansi.replace("\u001b[01;31m\u001b[K", "", M)
        .replace("\u001b[m\u001b[K", "", M)
        .replace("\u001b[0m", "", M)
        .replace("\u001b[1m", "", M)
        .replace("\u001b[2m", "", M)
        .replace("\u001b[3m", "", M)
        .replace("\u001b[4m", "", M)
        .replace("\u001b[30m", "", M)
        .replace("\u001b[31m", "", M)
        .replace("\u001b[32m", "", M)
        .replace("\u001b[33m", "", M)
        .replace("\u001b[34m", "", M)
        .replace("\u001b[35m", "", M)
        .replace("\u001b[36m", "", M)
        .replace("\u001b[37m", "", M)
        .replace("\u001b[90m", "", M)
        .replace("\u001b[91m", "", M)
        .replace("\u001b[92m", "", M)
        .replace("\u001b[93m", "", M)
        .replace("\u001b[0;0m", "", M)
        .replace("\u001b[0;31m", "", M)
        .replace("\u001b[0;32m", "", M)
        .replace("\u001b[0;33m", "", M)
        .replace("\u001b[0;34m", "", M)
        .replace("\u001b[0;35m", "", M)
        .replace("\u001b[0;36m", "", M)
        .replace("\u001b[0;37m", "", M)
        .replace("\u001b[1;31m", "", M)
        .replace("\u001b[1;32m", "", M)
        .replace("\u001b[1;33m", "", M)
        .replace("\u001b[1;34m", "", M)
        .replace("\u001b[1;35m", "", M)
        .replace("\u001b[1;36m", "", M)
        .replace("\u001b[1;37m", "", M)
        .replace("NEVER_REPLACE_OK", "")
    )


"""
    FILTERING of terraform plan/apply/destroy:

                replace('\u001b[0m\u001b[m','',M).
0x00: 1b 5b 30 6d 1b 5b 31 6d 64 6f 63 6b 65 72 5f 63  .[0m.[1mdocker_c
0x10: 6f 6e 74 61 69 6e 65 72 2e 74 65 73 74 31 5b 35  ontainer.test1[5
0x20: 5d 3a 20 44 65 73 74 72 75 63 74 69 6f 6e 20 1b  ]: Destruction .
                replace('\u001b[01;31m\u001b[K','',M).
0x30: 5b 30 31 3b 33 31 6d 1b 5b 4b 63 6f 6d 70 6c 65  [01;31m.[Kcomple
                replace('\u001b[m\u001b[K','',M).
0x40: 74 1b 5b 6d 1b 5b 4b 65 20 61 66 74 65 72 20 30  t.[m.[Ke after 0
0x50: 73 1b 5b 30 6d 0a                                s.[0m.
"""
# PREVIOUS TRIES !
# replace('\u001b[01;31m[K','',M).replace('\u001b[m[K','',M). \
# replace('[01;31m[K','',M).replace('[m[K','',M). \


def writefile(path, mode="w", text="hello world\n"):
    ofd = open(path, mode)
    ofd.write(text)
    ofd.close()


def read_json(ipfile):
    if not os.path.exists(ipfile):
        die(f"No such input notebook {ipfile}")

    with open(ipfile, encoding="utf-8-sig") as json_file:
        return json.load(json_file)


def pp_json(json_data):
    print(json.dumps(json_data, indent=4, sort_keys=True))


def pp_nb(json_data):
    print(
        f"Number of cells: {len(json_data['cells'])} kernel: {json_data['metadata']['kernelspec']['display_name']} nb_format: v{json_data['nbformat']}.{json_data['nbformat_minor']}"
    )
    pp_json(json_data)


def nb_cells(json_data, type=None):
    return len(json_data["cells"])


def write_nb(opfile, json_data):
    with open(opfile, "w") as json_file:
        json.dump(json_data, json_file)


def get_cell(json_data, cell_no):
    return json_data["cells"][cell_no]


def nb_dump1sourceLine(ipfile):
    json_data = read_json(ipfile)
    print(f"{ipfile}: #cells={nb_cells(json_data)}")
    for cell_no in range(nb_cells(json_data)):
        source = json_data["cells"][cell_no]["source"]
        if len(source) == 0:
            continue
        print(f"  cell[{cell_no}]source[0]={source[0]}")


def show_vars_seen(context, source_line, cell_no):
    global VARS_SEEN

    if len(VARS_SEEN) == 0:
        print(f"---- [{context}] no VARS_SEEN ----")
        return False

    DEBUG(f"---- show_vars_seen[{context} cell[{cell_no}]: start ---- {source_line}")

    show_exit_marker = False
    if DEBUG:
        if context.find("nb") == 0:
            nbfile = context[2:]
            DEBUG(f"----- show_vars_seen [{nbfile}] ------")
            ctxt = "nb"
            show_exit_marker = True
        else:
            ctxt = f"[{context} cell[{cell_no}] line '{source_line}'"

        for var in VARS_SEEN:
            value = VARS_SEEN[var]
            if value != "":
                value = f' (last value: "{value}")'
            DEBUG(f"{ctxt} __{var}\t{value}")

    DEBUG(f"---- show_vars_seen[{context} cell[{cell_no}]: end ----")
    return True


def nb_info(ip_or_op, ipfile):
    json_data = read_json(ipfile)

    any_vars_seen = show_vars_seen(f"nb{ipfile}", "", "")
    if not any_vars_seen:
        if ip_or_op == "ip":
            print(f"i/p nb [{ipfile}] has 0 variables")
        else:
            print(f"o/p nb [{ipfile}] has 0 variables")

    return f"{ipfile}:\n\t#cells={nb_cells(json_data)}"


def main():
    MODE = "info"
    PROG = sys.argv[0]
    a = 1

    if len(sys.argv) == 1:
        die("Missing arguments")

    if sys.argv[a] == "-f":
        a += 1
        MODE = "filter"

    if sys.argv[a] == "-s":
        a += 1
        MODE = "split"

    if sys.argv[a] == "-1":
        a += 1
        MODE = "dump1l"

    if MODE == "dump1l":
        for ipfile in sys.argv[a:]:
            nb_dump1sourceLine(ipfile)

    if MODE == "info":
        for ipfile in sys.argv[a:]:
            print(nb_info("ip", ipfile))

    if MODE == "filter":
        for ipfile in sys.argv[a:]:
            print(nb_info("ip", ipfile))
            new_data = filter_nb(read_json(ipfile), DEBUG)
            opfile = OP_DIR + "/" + ipfile + ".filtered.ipynb"
            write_nb(opfile, new_data)
            print(nb_info("op", opfile))

            opfile = OP_DIR + "/" + ipfile + ".vars_seen.json"
            vars_seen_json = json.dumps(VARS_SEEN, indent=4)
            writefile(opfile, mode="w", text=vars_seen_json)

    if MODE == "split":
        for ipfile in sys.argv[a:]:
            print(nb_info("ip", ipfile))
            split_nb(read_json(ipfile), DEBUG)
            print("DONE")


def findInSource(source_lines, match):
    for line in source_lines:
        if match in line:
            print("True:" + line)
            return True
    return False


def next_section(current_sections, level, source_line):
    section_num = ""
    if level == 0:
        current_sections[0] += 1
        current_sections[1] = 1
        current_sections[2] = 1
        current_sections[3] = 1
        section_num = f"{current_sections[0]}"
    if level == 1:
        current_sections[1] += 1
        current_sections[2] = 1
        current_sections[3] = 1
        section_num = f"{current_sections[0]}.{current_sections[1]}"
    if level == 2:
        current_sections[2] += 1
        current_sections[3] = 1
        section_num = (
            f"{current_sections[0]}.{current_sections[1]}.{current_sections[2]}"
        )
    if level == 3:
        current_sections[3] += 1
        section_num = f"{current_sections[0]}.{current_sections[1]}.{current_sections[2]}.{current_sections[3]}"

    # Remove '#* '
    source_line = source_line[source_line.find(" ") :].lstrip()
    SE_regex = re.compile(r"([\d,\.]+) ")
    source_line = SE_regex.sub("", source_line)
    return_line = section_num + " " + source_line.rstrip()  # Remove new-line
    return (level, section_num, return_line)


# TODO: convert output to be separate markdown cells
# print(f'DEBUG: cell_no:{cell_no}')
def SET_NB_CODE_OP(json_data, cell_no, code_op):
    if not "outputs" in json_data["cells"][cell_no]:
        json_data["cells"][cell_no]["outputs"] = []
    json_data["cells"][cell_no]["outputs"].append(code_op)


def REMOVE_NB_DEBUG(cells_data, cell_no):
    op = cells_data[cell_no]["outputs"]

    for opno in range(len(cells_data[cell_no]["outputs"])):
        if "text" in cells_data[cell_no]["outputs"][opno]:
            for textno in range(len(cells_data[cell_no]["outputs"][opno]["text"])):
                if "NB_DEBUG: " in cells_data[cell_no]["outputs"][opno]["text"][textno]:
                    cells_data[cell_no]["outputs"][opno]["text"][textno] = ""


def CONVERT_ANSI_CODES2TXT(cells_data, cell_no):
    op = cells_data[cell_no]["outputs"]

    for opno in range(len(cells_data[cell_no]["outputs"])):
        if "text" in cells_data[cell_no]["outputs"][opno]:
            for textno in range(len(cells_data[cell_no]["outputs"][opno]["text"])):
                ansi = cells_data[cell_no]["outputs"][opno]["text"][textno]
                #### if cell_no == 20 and textno == 91: print(f"BEFORE: cell{cell_no} has 'text' element {textno} '{ansi}' in element {opno}")
                text = raw_ansi2text(ansi)
                # TO DEBUG:
                """
                if text != ansi:
                    print(f"DEBUG_ANSI CHANGE from '{ansi}'")
                    print(f"DEBUG_ANSI        to   '{text}'")
                """
                #### if cell_no == 20 and textno == 91: print(f"AFTER2: cell{cell_no} has 'text' element {textno} '{text}' in element {opno}")

                cells_data[cell_no]["outputs"][opno]["text"][textno] = text
                #### if text != ansi: print(f"cell{cell_no} has output element {opno} changed\n    text={text}')


def UNUSED_CONVERT_ANSI_CODES2HTML(cells_data, cell_no):
    return
    op = cells_data[cell_no]["outputs"]
    for opno in range(len(cells_data[cell_no]["outputs"])):
        if "text" in cells_data[cell_no]["outputs"][opno]:
            for textno in range(len(cells_data[cell_no]["outputs"][opno]["text"])):
                ansi = cells_data[cell_no]["outputs"][opno]["text"][textno]
                html = ansi2html_conv.convert(ansi)
                print(f"Converting {ansi} to {html}")
                cells_data[cell_no]["outputs"][opno]["text"][textno] = html


def substitute_vars_in_line(source_line, slno):
    new_line = source_line
    vars_seen = []

    new_line = new_line.replace(HOME+"/", '~/')
    # A hack: needs to be generalized: (pull vars into VARS_SEEN:
    #if '${__LABS_DIR}' in source_line:
    #    #new_line = new_line.replace("${__LABS_DIR}", os.getenv('__LABS_DIR', 'ERROR_LABS_DIR_UNSER'))
    #    new_line = new_line.replace("${__LABS_DIR}", VARS_SEEN['LABS_DIR'])
    #    new_line = new_line.replace(HOME+"/", '~/')
    #if '$__LABS_DIR' in source_line:
    #    new_line = new_line.replace("$__LABS_DIR", VARS_SEEN['LABS_DIR'])
    #    new_line = new_line.replace(HOME+"/", '~/')

    for var in VARS_SEEN:
        if "${__" + var +"}" in source_line:
            vars_seen.append("__" + var)
            DEBUG(f"SUBST: substitute_vars_in_line([line{slno}] {source_line}")
            new_line = new_line.replace("${__" + var +"}", VARS_SEEN[var])

        if "$__" + var in source_line:

            vars_seen.append("__" + var)
            DEBUG(f"SUBST: substitute_vars_in_line([line{slno}] {source_line}")
            new_line = new_line.replace("$__" + var, VARS_SEEN[var])

    if new_line != source_line:
        debug_info = f"SUBST: [line{slno}]: variables seen in '{source_line}' will replace vars [{vars_seen}]"
        print(debug_info)
        print(f"SUBST:     BEFORE: '{source_line.rstrip()}'")
        print(f"SUBST:     AFTER:  '{new_line.rstrip()}'")
        DEBUG(debug_info)
        DEBUG(f"===> '{new_line}'")
    return new_line


def replace_vars_in_line(line):
    #return substitute_vars_in_line(line, -1, VARS_SEEN)
    return substitute_vars_in_line(line, -1)


def replace_words_in_cell_output_lines(cells_data, cell_no, REPLACE_OP_WORDS):
    if not "outputs" in cells_data[cell_no]:
        return

    for opno in range(len(cells_data[cell_no]["outputs"])):
        if not "text" in cells_data[cell_no]["outputs"][opno]:
            continue

        for textno in range(len(cells_data[cell_no]["outputs"][opno]["text"])):
            line = cells_data[cell_no]["outputs"][opno]["text"][textno]

            for REPLACE_OP_WORD in REPLACE_OP_WORDS:
                if REPLACE_OP_WORD in line:
                    line = line.replace(
                        REPLACE_OP_WORD, REPLACE_OP_WORDS[REPLACE_OP_WORD]
                    )

            cells_data[cell_no]["outputs"][opno]["text"][textno] = line


def replace_vars_in_cell_output_lines(cells_data, cell_no):
    op = cells_data[cell_no]["outputs"]

    for opno in range(len(cells_data[cell_no]["outputs"])):
        if "text" in cells_data[cell_no]["outputs"][opno]:
            for textno in range(len(cells_data[cell_no]["outputs"][opno]["text"])):
                line = cells_data[cell_no]["outputs"][opno]["text"][textno]
                line0 = line
                line = replace_vars_in_line(line)
                cells_data[cell_no]["outputs"][opno]["text"][textno] = line
                DEBUG(f"CHANGED: {cell_no} {line0} --> {line}")


def get_var_defs_in_cell_output_lines(section_title, cell_no, output_lines):
    #vars_seen = {}
    global VARS_SEEN

    DEBUG(f"{section_title} {cell_no} {output_lines}")
    for opno in range(len(output_lines)):
        if "text" in output_lines[opno]:
            for textno in range(len(output_lines[opno]["text"])):
                line = output_lines[opno]["text"][textno]
                # NB_SET_VAR:
                # if "VAR __" in line:
                if "export __" in line:
                    #print(f'SUBST: VAR __ seen in {line.rstrip()}')
                    print(f'SUBST: export __ seen in {line.rstrip()}')
                    #VAR_NAME = line[line.find("VAR __") + 6 : line.find("=")]
                    VAR_NAME = line[line.find("export __") + 9 : line.find("=")]
                    # VAR_SET = "VAR __" + VAR_NAME + "="
                    VAR_SET = "export __" + VAR_NAME + "="
                    if output_lines[opno]["text"][textno].find(VAR_SET) == 0:
                        VAR_VALUE = output_lines[opno]["text"][textno][
                            len(VAR_SET) :
                        ].rstrip()

                        save_value=VAR_VALUE
                        if VAR_VALUE[0] == "'" and not " " in VAR_VALUE: VAR_VALUE=VAR_VALUE[1:-1]
                        if VAR_VALUE[0] == '"' and not " " in VAR_VALUE: VAR_VALUE=VAR_VALUE[1:-1]
                        if save_value != VAR_VALUE:
                            print(f'SUBST: {VAR_NAME} STRIPPED of quotes:')
                            print(f'SUBST: was "{save_value}"')
                            print(f'SUBST: now "{VAR_VALUE}"')

                        VAR_VALUE = VAR_VALUE.strip('"').rstrip('"')
                        debug_info=f"[{section_title}] [cell{cell_no} line{opno}]<<<<<<<<DEBUG>>>>>>>> VAR SET {VAR_NAME}={VAR_VALUE}"
                        DEBUG(debug_info)
                        print(debug_info)

                        # VAR SEEN HERE!!!:
                        VARS_SEEN[VAR_NAME] = VAR_VALUE

    return
    #return vars_seen


def show_long_code_line(
    label, source_line, MAX_LINE_LEN, cell_no, section_title, EXCLUDED_CODE_CELL
):
    if label == "CODE-op":
        return

    caller_info = stack()[1]
    calling_line = caller_info[2]
    calling_function = caller_info[3]
    print()
    print(
        f'{RED}{label}[cell={cell_no}] fn {calling_function} line {calling_line} LONG LINE length={len(source_line)} > {MAX_LINE_LEN}{NORMAL} in section "{section_title}"'
    )
    print(f'  "{source_line.rstrip()}"')
    if EXCLUDED_CODE_CELL:
        print(f"  excluded_code_cell={EXCLUDED_CODE_CELL}")
    if len(source_line) != len(source_line.rstrip()):
        print(f"  len(line)={len(source_line)} != {len(source_line.rstrip())}")


def escape_markdown(text):
    lines = text.split("\n")
    op_text = ""

    for line in lines:
        if line.find("#") == 0:
            line = "\\" + line
        if line.find("-") == 0:
            line = "\\" + line
        if line.find("*") == 0:
            line = "\\" + line
        if line.find("`") == 0:
            line = "\\" + line
        op_text += line + "\n"
    return op_text.rstrip()


def NB_FILE_replace_code_cell_by_markdown(cell, format_string):
    """Only used by NB_FILE_*, so use <pre><code class="nooutputtab"> ... </pre></code>"""
    global REPLACE_OP_WORD, REPLACE_OP_WORDS

    source_lines = cell["source"]
    source_line0 = source_lines[0]

    slno_to_delete = 0
    for slno in range(len(source_lines)):
        # FIX for NB_FILE /$__var replacement bug ...
        # replace variables in markdown here ...
        if "$__" in source_lines[slno]:
            source_lines[slno] = replace_vars_in_line(source_lines[slno])

        if ">>tofile:" in source_lines[slno]:
            source_lines[slno] = "____TO_REMOVE____"
            slno_to_delete += 1

    for i in range(slno_to_delete):
        source_lines.remove("____TO_REMOVE____")

    for slno in range(len(source_lines)):
        if ">>tomark:" in source_lines[slno]:
            source_lines[slno] = source_lines[slno].replace(">>tomark:", "")
    file_content = "".join(source_lines[1:-1])

    for REPLACE_OP_WORD in REPLACE_OP_WORDS:
        if REPLACE_OP_WORD in file_content:
            file_content = file_content.replace(
                REPLACE_OP_WORD, REPLACE_OP_WORDS[REPLACE_OP_WORD]
            )

    file_content = file_content.replace("<", "&lt;").replace(">", "&gt;")

    file_name = source_line0[source_line0.find(" ") :].lstrip()
    file_name = file_name[: file_name.rfind("<<") - 1]

    # A PRIORI NOT NEEEDED (as long as <pre><code ...> appears on a new line !)
    # file_content = escape_markdown(file_content)

    file_type = ""
    # file_type='txt' -> But get's printed - by Firefox at least

    format_string = format_string.replace("__FILE__", f"**{file_name}**")

    # output_cell_content=f"""{format_string} ```{file_type} {file_content}``` """
    # output_cell_content=f'''{ format_string } <pre><code class="nooutputtab">{file_content}</pre></code>'''
    output_cell_content = f"""{format_string}\n<pre><code class="nbfile">{file_content}\n</code></pre>\n"""
    if VERBOSE_NB_FILE:
        print(f"NB_FILE*: format_string => {format_string}")
    if VERBOSE_NB_FILE:
        print(f"NB_FILE*: {file_name} => {file_content}")

    DEBUG(f"cell type/keys BEFORE: {cell['cell_type']}, {cell.keys()}")
    cell["cell_type"] = "markdown"

    # Remove keys from cell:
    if "outputs" in cell:
        cell.pop("outputs")
    if "execution_count" in cell:
        cell.pop("execution_count")

    cell["source"] = [output_cell_content]
    DEBUG(f"cell type/keys AFTER: {cell['cell_type']}, {cell.keys()}")
    DEBUG(f"cell output_cell: {cell['source']}")


def PRESS(label):
    print(f"DEBUG[{label} - press enter to continue")
    input()


def FINAL_CODE_CELL_CHECK(cell, cell_no):
    copy_cell = copy.deepcopy(cell)

    # Remove: "# Code-Cell[*]" lines:
    source_lines = copy_cell["source"]
    for i in range(len(source_lines)):
        if "# Code-Cell[" in source_lines[i]:
            source_lines[i] = ""

    # Remove: newlines:
    source_content = "".join(source_lines).replace("\n", "")

    if REMOVE_SHORT:
        if len(source_content) <= 10:
            print(f'SHORT LINE/CODE[{cell_no}] "{source_content}"')
            if len(source_content) <= 4:
                if len(source_content) == 0:
                    print("empty source_content")
                    ## BUT WANT TO JUST REMOVE source_lines (# Code-Cell) , leaving output
                    cell["source"] = []
                    # return False

                print(
                    f"NEARLY empty source_content '{source_content}' across {len(source_lines)} lines"
                )

    # ACCEPT line
    return True


def replace_chars(replace_these, tag, string):
    split_string = string.split(replace_these)
    bits = len(split_string)

    if bits % 2 == 0:
        split_string.append("")
        bits += 1
        # bits -= 1
        # print(f"Wrong split({replace_these}) count - expected odd number[got {bits}] of elements in string:\n\t{string}")
        # die("Wrong split count - expected odd number of elements")

    string = ""
    open_tag = "<" + tag + ">"
    close_tag = "</" + tag + ">"

    for i in range(bits - 1):
        if i % 2 == 0:
            string += split_string[i] + open_tag
        else:
            string += split_string[i] + close_tag
    string += split_string[bits - 1]

    return string


def replace_asterisks_backticks(string):
    string0 = string
    string = replace_chars("**", "b", string)
    string = replace_chars("*", "i", string)
    string = replace_chars("```", "code", string)

    # if len(split_str) == 3:
    #    str=split_str[0] + '<i>' + split_str[1] + '</i>' + split_str[2]
    # if len(split_str) == 5:
    #    str=split_str[0] + '<i>' + split_str[1] + '</i>' + split_str[2] + '<i>' + split_str[3] + '</i>' + split_str[4]
    # if len(split_str) == 7:
    #    str=split_str[0] + '<i>' + split_str[1] + '</i>' + split_str[2] + \
    #            '<i>' + split_str[3] + '</i>' + split_str[4] + '<i>' + split_str[5] + '</i>' + split_str[6]

    return string


def question_box(summary, details, box_colour, tag):
    global QUESTIONS, NUM_QUESTIONS
    style = 'style="border-width:6px; border-style:solid; border-color:{box_colour}; padding: 1em;"'

    summary = replace_asterisks_backticks(summary)
    details = replace_asterisks_backticks(details)

    source_line = f"<details {style} ><summary>Question {NUM_QUESTIONS + 1}: {summary}</summary>{details}</details>\n"
    return source_line


def details_box(summary, details, box_colour, bg_colour, tag, full_page_width=True):
    global QUESTIONS, NUM_QUESTIONS

    extra_style = ""
    if not full_page_width:
        # display: inline-block => don't expand to full page width:
        extra_style = "display: inline-block; "

    # padding: top right bottom left
    style = f'style="{extra_style}border: 5px solid {box_colour}; background-color: {bg_colour}; border-radius: 20px; padding: 10px 0px 10px 10px;"'
    summary_style = f'style="color: {box_colour}; background-color: #00000000; padding: 0px 0px 0px 0px;"'

    summary = replace_asterisks_backticks(summary)
    details = replace_asterisks_backticks(details)

    spaces = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp"
    detail_spaces = "&nbsp; &nbsp; &nbsp; &nbsp;"
    source_line = f"<details {style} ><summary {summary_style}>{spaces}Question {NUM_QUESTIONS + 1}: {summary}</summary>{detail_spaces}{details}</details>\n"
    return source_line


def info_box(source_line, box_colour, bg_colour, tag, full_page_width=True):
    extra_style = ""
    if not full_page_width:
        # display: inline-block => don't expand to full page width:
        extra_style = "display: inline-block; "

    source_line = replace_asterisks_backticks(source_line)
    source_line = (
        f'<p style="{extra_style}border-width:3px; border-style:solid; border-color:{box_colour}; background-color: {bg_colour}; border-radius: 10px; padding: 5px;"><b>{tag}</b>'
        + source_line
        + "</p>\n\n"
    )
    return source_line


def markdown_cell(id, lines):
    return {
        "cell_type": "markdown",
        "id": id,
        "metadata": {},
        "source": lines,  # array
    }


def NB_FILE_replace_EOF_backticks(section_title, cell_no, source_lines):
    for slno in range(len(source_lines)):
        if source_lines[slno].find("EOF") == 0:
            source_lines[slno] = "\n"
            DEBUG(
                f'EOF-backticks replaced in section "{section_title}" cell_no {cell_no} in line "{source_lines[slno]}"'
            )


def process_code_cell(
    source_lines,
    cells_data,
    cell_no,
    EXCLUDED_CODE_CELL,
    section_number,
    section_title,
    include_cell,
    cells,
):
    global VARS_SEEN
    # ??
    CELL_regex = re.compile(r"\|?\&?\s*__.*$")  # , re.IGNORECASE)

    source_line0 = source_lines[0]
    cells_data[cell_no]["section_title"] = section_title
    cells_data[cell_no]["section_number"] = section_number

    # TODO: Write a create cell function: createCell(type, source, outputs)
    # Pragma NB_LAB_ENV: remove code cell, keep only output ...
    if source_line0.find("NB_LAB_ENV") == 0:
        if "outputs" in cells_data[cell_no] and len(cells_data[cell_no]["outputs"]) > 0:
            cells_data[cell_no]["source"] = cells_data[cell_no]["outputs"][0]["text"]
            cells_data[cell_no]["cell_type"] = "markdown"
            cells_data[cell_no].pop("execution_count")
            cells_data[cell_no].pop("outputs")
        cells.append(cell_no)
        return

    for slno in range(len(source_lines)):
        source_line = source_lines[slno]
        s_line = source_line.rstrip()
        DEBUG(f'[CODE][{cell_no} line{slno}] "{s_line}"')

        if not EXCLUDED_CODE_CELL:
            inc_source_line = source_line
            if "| NB_" in source_line:
                inc_source_line = source_line[: source_line.find("| NB_")]
                source_lines[slno] = inc_source_line
            if "NB_" in source_line:
                inc_source_line = ""
                source_lines[slno] = inc_source_line
            if (
                len(inc_source_line) > MAX_LINE_LEN
                and source_lines[slno][0] != "#"
                and source_line0.find("NB_FILE") == -1
                and source_line0.find("NB_FILE_TEMPLATE") == -1
                and source_line0.find("NB_FILE_M") == -1
                and source_line0.find("NB_FILE_A") == -1
            ):
                show_long_code_line(
                    "CODE-src",
                    inc_source_line,
                    MAX_LINE_LEN,
                    cell_no,
                    section_title,
                    EXCLUDED_CODE_CELL,
                )

            if "__" in source_line:
                o = source_line
                # NB_FILE & $__IP debugging because? ( num_cell_source_lines != num_source_lines ) ?
                # TODO: DEBUG print(f'old source_line="{ source_line }"')
                source_line = replace_vars_in_line(source_line)
                # TODO: DEBUG print(f'new source_line="{ source_line }"')
                show_vars_seen("CODE --", source_line, cell_no)

                num_cell_source_lines = len(cells_data[cell_no]["source"])
                num_source_lines = len(source_lines)
                if slno >= num_cell_source_lines:
                    print(
                        f"INFO: num_source_lines={num_source_lines} num_cell_source_lines={num_cell_source_lines}"
                    )
                    print(
                        f"ERROR: [cell_no={cell_no}] source_lines={len(cells_data[cell_no]['source'])} slno={slno}\n"
                    )
                    print("\n\t" + "\n\t".join(cells_data[cell_no]["source"]))
                    ofile = f"{HOME}/tmp/source_lines"
                    print(f"Writing {ofile}")
                    # writefile(ofile, text='\n'.join(source_lines))
                    writefile(ofile, text="".join(source_lines))

                    ofile = f"{HOME}/tmp/cells_data_{cell_no}"
                    print(f"Writing {ofile}")
                    writefile(ofile, text="".join(cells_data[cell_no]["source"]))
                source_lines[slno] = source_line

        # Pragma FOREACH (use singular form of variable e.g. __POD_IP which will be populated form __POD_IPS)
        # TODO: SERIOUSLY BROKEN
        if source_line.find("FOREACH __") == 0:
            rest_line = source_line[len("FOREACH __") :].lstrip()
            space_pos = rest_line.find(" ")
            if space_pos > 1:
                VAR_NAME = rest_line[:space_pos]
                VAR_NAME_S = VAR_NAME + "S"

                cmd_line = rest_line[space_pos:].lstrip()
                new_line = ""

                if not VAR_NAME_S in VARS_SEEN:
                    print(f"Vars seen so far={VARS_SEEN.keys()}")
                    die(f"Var <{VAR_NAME_S}> not seen")
                values = VARS_SEEN[VAR_NAME_S].split()
                for value in values:
                    # TODO: SERIOUSLY BROKEN
                    new_line += (
                        cmd_line.replace("$__", "$__")
                        .replace("<", "<")
                        .replace(">", ">")
                        .replace("$__" + VAR_NAME, value)
                        + "\n"
                    )

                cells_data[cell_no]["source"][slno] = new_line
                if new_line != source_line:
                    print(new_line)
            DEBUG(
                f"[cell={cell_no} line={slno} section={section_title}] CONTINUE - FOREACH found"
            )
            continue

        if "outputs" in cells_data[cell_no]:
            REMOVE_NB_DEBUG(cells_data, cell_no)
            CONVERT_ANSI_CODES2TXT(cells_data, cell_no)
            replace_vars_in_cell_output_lines(cells_data, cell_no)

        ## # CODE: nbtool.py will replace source_line by first line of output text (which is then removed from output_text)
        ## # - useful when command is a variable
        ## # e.g. code cell contents are:  (output set to actual value of $__CMD)
        ## #    NB_CODE $__CMD # Must be first line in code cell
        ## #    NB_EXEC $__CMD
        ## NB_CODE()                    { echo $*;                            return 0;  }
        ## NB_NO_EXEC()                 {                                     return 0;  }
        ## NB_EXEC()                    { $*;                                 return $?; }

        # ==== TO TEST:
        # Pragma | NB_EXEC(command)
        """ TO TEST:
        if source_line.find("NB_CODE ") == 0:
            cells_data[cell_no]['source'][slno]=''
            source_line= cells_data[cell_no]['source'][slno]
            code_op = cells_data[cell_no]['source'][slno][1+len("NB_CODE"):]
            SET_NB_CODE_OP(cells_data, cell_no, code_op)
        """

        # Pragma | NB_EXEC(command)
        if source_line.find("NB_EXEC ") == 0:
            cells_data[cell_no]["source"][slno] = ""
            source_line = cells_data[cell_no]["source"][slno]

        if source_line.find("NB_ARCHIVE_LAB") == 0:
            cells_data[cell_no]["source"][slno] = ""
            source_line = cells_data[cell_no]["source"][slno]

        # Pragma | NB_NO_EXEC(command)
        if source_line.find("NB_NO_EXEC ") == 0:
            debug_save = source_line
            source_line = source_line[1 + len("NB_NO_EXEC") :]
            cells_data[cell_no]["source"][slno] = source_line
            DEBUG(f'source_line: "{debug_save}"\n    ==> "{source_line}"\n')

        # Pragma $__ variables ...
        # If $__variables seen in source then we modify the source to replace $__var by it's value
        for var in VARS_SEEN:
            if "$__" + var in source_line:
                new_line = substitute_vars_in_line(source_line, slno)
                show_vars_seen(f"CODE[$__{var}]", source_line, cell_no)
                DEBUG(f"{var} seen in {source_line} will replace '$__{var}'")
                DEBUG(cells_data[cell_no]["source"][slno])
                cells_data[cell_no]["source"][slno] = new_line
                DEBUG(f" => {cells_data[cell_no]['source'][slno]}")

                # TODO: generalize line length checking after all replacements (how to hook i on 'continue' ??
                if len(new_line) > MAX_LINE_LEN:
                    show_long_code_line(
                        "CODE-src-vars",
                        new_line,
                        MAX_LINE_LEN,
                        cell_no,
                        section_title,
                        EXCLUDED_CODE_CELL,
                    )

        for line in REPLACE_LINES:
            if line in source_line:
                cells_data[cell_no]["source"][slno] = ""

        # TODO: extend for multiple replacements (will never happen ? :)
        REPLACE_CMD = get_longest_matching_key(REPLACE_COMMANDS, source_line)
        if REPLACE_CMD:
            pos = cells_data[cell_no]["source"][slno].find(REPLACE_CMD) + len(
                REPLACE_CMD
            )
            cells_data[cell_no]["source"][slno] = (
                REPLACE_COMMANDS[REPLACE_CMD]
                + " "
                + cells_data[cell_no]["source"][slno][pos:]
            )
            new_line = cells_data[cell_no]["source"][slno]
            if "-chk" in new_line:
                pos = new_line.find("-chk")
                if "terraform apply" in new_line or "terraform destroy" in new_line:
                    cells_data[cell_no]["source"][slno] = cells_data[cell_no]["source"][
                        slno
                    ][:pos]

        replace_words_in_cell_output_lines(cells_data, cell_no, REPLACE_OP_WORDS)

        # Pragma #EXCLUDE (cell):
        if EXCLUDED_CODE_CELL:
            include_cell = False
            DEBUG(
                f"[cell={cell_no} line={slno} section={section_title}] CONTINUE - EXCLUDED/include=False"
            )
            # XXX: still need to process variables though
            # continue

        # Pragma | __(HIDE_|HIGHLIGHT*)
        if "NB_HIGHLIGHT" in source_line:
            if DEBUG:
                orig = cells_data[cell_no]["source"][slno]
            cells_data[cell_no]["source"][slno] = CELL_regex.sub(
                "", cells_data[cell_no]["source"][slno]
            )
            if DEBUG:
                new = cells_data[cell_no]["source"][slno]
                if new != orig:
                    print(f"{orig.rstrip()} => {new.rstrip()}")

        # Pragma WAIT:
        if source_line.find("NB_WAIT") == 0:
            include_cell = False
            DEBUG(
                f"[cell={cell_no} line={slno} section={section_title}] CONTINUE - NB_WAIT"
            )
            continue

        # Pragma RETURN:
        if source_line.find("__RETURN") == 0:
            cells_data[cell_no]["source"][slno] = ""
            DEBUG(
                f"[cell={cell_no} line={slno} section={section_title}] CONTINUE - __RETURN"
            )
            continue

        if source_line.find("NB_SET_VAR") == -1 and source_line.find("K_GET_") == -1:
            debug_info=f"[cell={cell_no} line={slno} section={section_title}] CONTINUE - no NB_SET_VAR (or __K_GET)"
            DEBUG(debug_info)
            continue

        include_cell = False

        if cells_data[cell_no]["outputs"]:
            op_vars_seen = get_var_defs_in_cell_output_lines(
                section_title, cell_no, cells_data[cell_no]["outputs"]
            )
            #if len(op_vars_seen) > 0:
            #    DEBUG(f'NEW VARS_SEEN: "{op_vars_seen}"')
            #    VARS_SEEN.update(op_vars_seen)
            #    show_vars_seen("output", source_line, cell_no)
            replace_vars_in_cell_output_lines(cells_data, cell_no)

    if include_cell:
        if FINAL_CODE_CELL_CHECK(cells_data[cell_no], cell_no):
            cells.append(cell_no)


def process_markdown_cell(
    source_lines,
    cells_data,
    cell_no,
    section_number,
    section_title,
    include_cell,
    cells,
    count_sections,
):
    source_line0 = source_lines[0]
  
    # First pass: aut-correct lists by inserting blank line before/after list items:
    for slno in range(len(source_lines)):
        if source_lines[slno].startswith('- '):
            source_lines[slno] = '\n' + source_lines[slno] + '\n'

    for slno in range(len(source_lines)):
        source_line = source_lines[slno]
        s_line = source_line.rstrip()
        DEBUG(f'[MARKDOWN][{cell_no} line{slno}] "{s_line}"')

        insert_line_image = ""
        if source_line.find("# STRETCH-GOALS") == 0:
            # PLACE THICK LINE HERE: Start of Stretch Goals
            insert_line_image = INSERT_THICK_BAR
            insert_line_image += INSERT_THICK_BAR
            source_line = "# Stretch Goals"
        elif source_line.find("# ") == 0:
            # PLACE MEDIUM LINE HERE:
            insert_line_image = INSERT_MED_BAR
        elif source_line.find("## ") == 0:
            # PLACE THIN LINE HERE:
            insert_line_image = INSERT_THIN_BAR

        # Build up TableOfContents - Count sections headers and retain list for ToC text
        previous_section_title = section_title
        previous_section_number = section_number
        if source_line.find("#") == 0:
            # Remove '#' before title:
            section_title = source_line.rstrip()
            if VERBOSE_sections:
                print(f'INITIAL section_title="{section_title}"')
            section_title = section_title[section_title.find(" ") :].lstrip()
            if VERBOSE_sections:
                print(f'2nd section_title="{section_title}"')
            if len(section_title) > 0:
                # Remove all but section number if present
                section_number = section_title[: section_title.find(" ")]
                if VERBOSE_sections:
                    print(f'3rd section_title="{section_title}"')
                if len(section_number) > 0 and section_number[0] in "0123456789":
                    # section_title=source_line
                    # section_title = f'[section "{ section_title.rstrip().lstrip() }"]'
                    section_title = f"[section {section_title.rstrip().lstrip()}]"
                    section_number = f"[section {section_number.rstrip().lstrip()}]"
                    cells_data[cell_no]["section_title"] = section_title
                    cells_data[cell_no]["section_number"] = section_number
                    if VERBOSE_sections:
                        print(
                            f"process_markdown_cell: Setting section_title to {section_title}"
                        )
                    if VERBOSE_sections:
                        print(
                            f"process_markdown_cell: Setting section_number to {section_number}"
                        )
                else:
                    section_title = previous_section_title
                    section_number = previous_section_number

        if source_line.find("#") == 0 and count_sections:
            toc_line = ""
            level = 0
            if source_line.find("# ") == 0:
                (level, section_num, toc_line) = next_section(
                    current_sections, 0, source_line
                )
            if source_line.find("## ") == 0:
                (level, section_num, toc_line) = next_section(
                    current_sections, 1, source_line
                )
            if source_line.find("### ") == 0:
                (level, section_num, toc_line) = next_section(
                    current_sections, 2, source_line
                )
            if source_line.find("#### ") == 0:
                (level, section_num, toc_line) = next_section(
                    current_sections, 3, source_line
                )
            sec_cell_no = 0
            section_title = toc_line
            print(
                f"process_markdown_cell: [count_sections] Setting section_title to {section_title}\n"
            )

            toc_link = f'<a href="#sec{section_num}" /> {toc_line} </a>'
            if level == 0:
                toc_text += (
                    f'\n<br /> <div id="TOC{section_num}" > <b> {toc_link} </b></div>\n'
                )
            else:
                toc_text += f"* {toc_link}\n"

            if "." in section_num:
                top_section_num = section_num[: section_num.find(".")]
            else:
                top_section_num = section_num

            if INCLUDE_TOC:
                cells_data[cell_no]["source"][slno] = (
                    f'<a href="#TOC{top_section_num}" > Return to INDEX </a>\n'
                    + source_line[: 1 + source_line.find(" ")]
                    + f'<div id="sec{section_num}" > '
                    + toc_line
                    + " </div>"
                )

        if insert_line_image != "":
            new_lines = (
                "\n\n"
                + insert_line_image
                + "\n\n"
                + cells_data[cell_no]["source"][slno]
            )
            cells_data[cell_no]["source"][slno] = new_lines
            insert_line_image = ""

        # ???? include_cell=False

    if include_cell:
        cells.append(cell_no)

    return (section_number, section_title)


def filter_nb(json_data, DEBUG=False):
    global VARS_SEEN
    global QUESTIONS, NUM_QUESTIONS

    VAR_TF = os.getenv("__TF", None)
    if VAR_TF:
        VARS_SEEN["TF"] = VAR_TF
        DEBUG(f'Saw TF var "{VAR_TF}"')

    VAR_LABS_DIR = os.getenv('__LABS_DIR', 'ERROR_LABS_DIR_UNSET')
    if VAR_LABS_DIR:
        VARS_SEEN["LABS_DIR"] = VAR_LABS_DIR
        DEBUG(f'Saw LABS_DIR var "{VAR_LABS_DIR}"')
        #new_line = new_line.replace("${__LABS_DIR}", os.getenv('__LABS_DIR', 'ERROR_LABS_DIR_UNSER'))

    include = False
    cells = []
    cells_data = json_data["cells"]

    toc_cell_no = -1
    count_sections = False
    current_sections = []
    toc_text = '<div id="TOC" >\n'
    sec_cell_no = 0
    In_cell_no = "unknown"
    section_title = ""
    section_number = ""
    # Final_code_cell_no=0

    exclude_cells = []
    incl_code_cells = []
    incl_md_cells = []

    # BEGINNING of filter_nb:
    for cell_no in range(nb_cells(json_data)):
        sec_cell_no += 1
        # print(cell_no)
        cell_type = cells_data[cell_no]["cell_type"]
        In_cell_no = "unknown"
        source_lines = cells_data[cell_no]["source"]
        if cell_type == "code":
            In_cell_no = cells_data[cell_no]["execution_count"]
            # Final_code_cell_no+=1
            # cells_data[cell_no]['final_cell_no']=Final_code_cell_no

            # NB_SET_VAR:
            if "NB_SET_VAR" in " ".join(source_lines):
                debug_info=f"[cell={cell_no} section={section_title}] NB_SET_VAR variables seen in cell source_lines"
                DEBUG(debug_info)

            # ADD Code-Cell comment line at end of cell source lines:
            # source_lines.append(f'\n# Code-Cell[{cell_no}] In[{In_cell_no}]')

            # CHECK for empty code cells:
            if len(source_lines) == 0:
                DEBUG(
                    f"[cell={cell_no} section={section_title}] CONTINUE - no source lines"
                )
                continue

        if len(source_lines) == 0:
            source_lines = [""]

        # Pragma --INCLUDE--SECTION--
        if "--INCLUDE--SECTION--" in source_lines[0]:
            include = True
            # BUT THIS CELL IS EXCLUDED:

            exclude_cells.append(cell_no)
            DEBUG(
                f"[cell={cell_no} section={section_title}] CONTINUE - START INCLUDE--SECTION"
            )
            continue
        # Pragma --EXCLUDE--SECTION--
        if "--EXCLUDE--SECTION--" in source_lines[0]:
            include = False
            exclude_cells.append(cell_no)

            DEBUG(
                f"[cell={cell_no} section={section_title}] CONTINUE - START EXCLUDE--SECTION"
            )
            continue

        if not include:
            exclude_cells.append(cell_no)
            DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - not include")
            continue

        # Detect TableOfContents Cell No:
        if len(source_lines) > 0 and source_lines[0].find('<div id="TOC"') == 0:
            toc_cell_no = cell_no
            DEBUG(f"ToC cell detected at cell_no[{cell_no}]")
            count_sections = True
            current_sections.append(0)
            current_sections.append(1)
            current_sections.append(1)
            current_sections.append(1)
            cells.append(cell_no)
            DEBUG(f"[cell={cell_no} section={section_title}] CONTINUE - TOC CELL found")
            continue

        EXCLUDED_CODE_CELL = False
        if cell_type == "code":
            if source_lines[0].find("#EXCLUDE") == 0:
                EXCLUDED_CODE_CELL = True
                exclude_cells.append(cell_no)
                # NOTE: Code will be excluded but continue to parse/search for variables settings
                DEBUG(
                    f"[cell={cell_no} section={section_title}] EXCLUDED_CODE_CELL - #EXCLUDE found"
                )

            # Pragma | QUIET: just quietly/rebuild notebook/markdown - exclude this cell
            if source_lines[0].find("NB_QUIET") == 0:
                EXCLUDED_CODE_CELL = True
                exclude_cells.append(cell_no)
                DEBUG(
                    f"[cell={cell_no} section={section_title}] EXCLUDED_CODE_CELL - NB_QUIET found"
                )

        # EXCLUDED_CODE_CELL for markdown ??
        if cell_type == "markdown" and not EXCLUDED_CODE_CELL:
            NOTE_BLOCKS = {
                # TAG: [ O_TAG, COLOUR, BACKGROUND_COLOUR, full_page_width ]
                "Note:": ["Note: ", "#444444", "#ffffff", False],
                "**Note:**": ["Note: ", "#0000ff", "#ffffff", False],
                "**Stretch:**": ["Stretch Goal: ", "#008800", "#eeffee", False],
                "**Info:**": ["Info: ", "#0000ff", "#eeeeff", True],
                "**Warn:**": ["Warn: ", "#aa0000", "#ffeeee", True],
                "**Error:**": ["Error: ", "#ff0000", "#ffdddd", True],
                # "**Qn:** This is a rhetorical question
                "**Qn:**": ["Qn: ", "#0000ff", "#eeeeff", True],
                # "**Answer:**(this is the question): this is the answer",
                "**Answer:**": ["Qn: ", "#0000ff", "#eeeeff", True],
                "**Oops:**": ["Oops:", "#ff0000", "#ffeeee", False],
                "**Good:**": ["Good:", "#008800", "#eeffee", False],
                "**Red:**": ["", "#ff0000", "#ffeeee", True],
                "**Green:**": ["", "#008800", "#eeffee", True],
                "**Blue:**": ["", "#0000ff", "#eeeeff", True],
                "**Yellow:**": ["", "#888800", "#ffffee", True],
                "**Cyan:**": ["", "#008888", "#eeffff", True],
                "**Violet:**": ["", "#880088", "#ffeeff", True],
                "**Grey:**": ["", "#000000", "#eeeeee", True],
            }

            for slno in range(len(source_lines)):
                link_pos = source_lines[slno].find("NB_LINK(")
                if link_pos != -1:
                    before = source_lines[slno][:link_pos]
                    link_start_pos = link_pos + len("NB_LINK(")
                    link_end_pos = source_lines[slno].find(")")
                    link = source_lines[slno][link_start_pos:link_end_pos]
                    source_lines[slno] = before + "[" + link + "](" + link + ")\n"

                for TAG in NOTE_BLOCKS:
                    if source_lines[slno].find(TAG) == 0:
                        O_TAG = NOTE_BLOCKS[TAG][0]
                        FG_COL = NOTE_BLOCKS[TAG][1]
                        BG_COL = NOTE_BLOCKS[TAG][2]
                        F_PAGE_W = NOTE_BLOCKS[TAG][3]
                        if TAG == "**Answer:**":
                            TAG = "**Answer:**("
                            summary = source_lines[slno][
                                len(TAG) + source_lines[slno].find(TAG) : source_lines[
                                    slno
                                ].find("):")
                            ]
                            details = source_lines[slno][
                                source_lines[slno].find("):") + 2 :
                            ]
                            source_lines[slno] = details_box(
                                summary,
                                details,
                                FG_COL,
                                BG_COL,
                                O_TAG,
                                full_page_width=F_PAGE_W,
                            )
                            QUESTIONS.append([summary, details])
                            NUM_QUESTIONS += 1
                        else:
                            source_lines[slno] = info_box(
                                source_lines[slno][len(TAG) :],
                                FG_COL,
                                BG_COL,
                                O_TAG,
                                full_page_width=F_PAGE_W,
                            )
                        break

                if source_lines[slno].find("SSH_SET ") == 0:
                    SSH_NODE = source_lines[slno][8:]
                    source_lines[slno] = ""
                elif source_lines[slno].find("SSH ") == 0:
                    source_lines[slno] = source_lines[slno][4:]

            incl_md_cells.append(cell_no)

        if cell_type == "code" and not EXCLUDED_CODE_CELL:
            incl_code_cells.append(cell_no)

            # Pragma | NB_FILE | NB_FILE_M | NB_FILE_A
            DEBUG(
                f'len(source_lines)={len(source_lines)} source_lines="{source_lines}"'
            )
            source_line0 = source_lines[0]
            if source_line0.find("NB_FILE_M") == 0:
                NB_FILE_replace_EOF_backticks(
                    section_title, cell_no, cells_data[cell_no]["source"]
                )
                NB_FILE_replace_code_cell_by_markdown(
                    cells_data[cell_no],
                    "Modify the file __FILE__ replacing with the following content:",
                )

            if source_line0.find("NB_FILE_A") == 0:
                NB_FILE_replace_EOF_backticks(
                    section_title, cell_no, cells_data[cell_no]["source"]
                )
                NB_FILE_replace_code_cell_by_markdown(
                    cells_data[cell_no],
                    "Append the following content to file __FILE__:",
                )

            if source_line0.find("NB_FILE_TEMPLATE") == 0:
                NB_FILE_replace_EOF_backticks(
                    section_title, cell_no, cells_data[cell_no]["source"]
                )
                NB_FILE_replace_code_cell_by_markdown(
                    cells_data[cell_no],
                    "Create the file __FILE__ based on this partial template:",
                )

            if (
                source_line0.find("NB_FILE_") == -1
                and source_line0.find("NB_FILE") == 0
            ):
                NB_FILE_replace_EOF_backticks(
                    section_title, cell_no, cells_data[cell_no]["source"]
                )
                NB_FILE_replace_code_cell_by_markdown(
                    cells_data[cell_no],
                    "Create a file __FILE__ with the following content:",
                )
                # "Create a new file (or modify existing) __FILE__ with the following content:")

        include_cell = True

        # Pragma | __DOCKER(command)
        for slno in range(len(source_lines)):
            if source_lines[slno].find("__DOCKER") != -1:
                source_lines[slno] = source_lines[slno].replace(
                    "__DOCKER", "ssh vm-linux-docker docker"
                )

        # Pragma | __CURL(command)
        for slno in range(len(source_lines)):
            if source_lines[slno].find("__CURL") != -1:
                source_lines[slno] = source_lines[slno].replace(
                    "__CURL", "ssh vm-linux-docker curl"
                )
            if source_lines[slno].find("NB_TIME") == 0:
                source_lines[slno] = source_lines[slno][8:]

        source_line_0 = source_lines[0]

        # TODO: REMOVE/REPLACE/CHANGE-NAME?? Pragma | CODE(command)
        # TODO: What was '__CODE', is it now NB_CODE ??
        if (
            source_line_0.find("__CODE") == 0
            and len(cells_data[cell_no]["outputs"]) != 0
        ):
            nl = "\n"
            print("---- BEFORE ------------------")
            print(f"{YELLOW}No source_lines={len(cells_data[cell_no]['source'])}")
            print(f"   source_lines={''.join(cells_data[cell_no]['source'])}")
            print(f"No outputs={len(cells_data[cell_no]['outputs'][0]['text'])}")
            print(f"   outputs     ={cells_data[cell_no]['outputs'][0]['text']}")

            cells_data[cell_no]["source"] = [
                cells_data[cell_no]["outputs"][0]["text"][0]
            ]
            source_lines = cells_data[cell_no]["source"]
            cells_data[cell_no]["outputs"][0]["text"] = cells_data[cell_no]["outputs"][
                0
            ]["text"][1:]
            source_lines.append(f"# Code-Cell[{cell_no}]\n")

            print("---- AFTER  ------------------")
            print(f"No source_lines={len(cells_data[cell_no]['source'])}")
            print(f"   source_lines={''.join(cells_data[cell_no]['source'])}")
            print(f"No outputs={len(cells_data[cell_no]['outputs'][0]['text'])}")
            print(f"   outputs     ={cells_data[cell_no]['outputs'][0]['text']}")
            print(f"{NORMAL}")

        if cell_type == "code":
            process_code_cell(
                source_lines,
                cells_data,
                cell_no,
                EXCLUDED_CODE_CELL,
                section_number,
                section_title,
                include_cell,
                cells,
            )
        elif cell_type == "markdown":
            (section_number, section_title) = process_markdown_cell(
                source_lines,
                cells_data,
                cell_no,
                section_number,
                section_title,
                include_cell,
                cells,
                count_sections,
            )
        else:
            die(f'Unknown cell_type "{cell_type}"')

    # Patch TableOfContents:
    toc_text += "</div>"
    DEBUG(f"ToC set to <{toc_text}>")
    if INCLUDE_TOC:
        cells_data[toc_cell_no]["source"] = [toc_text]
    else:
        cells_data[toc_cell_no]["source"] = [""]

    DEBUG()
    DEBUG(f"cells to include[#{len(cells)}]=[{cells}]")
    cells.reverse()

    # END of filter_nb: remove deleted (EXCLUDED?) cells
    for cell_no in range(nb_cells(json_data) - 1, -1, -1):
        # print(cell_no)
        if not cell_no in cells:
            DEBUG(f"del(cells[{cell_no}])")
            del cells_data[cell_no]

    op_code_cell_no = 0
    for cell_no in range(nb_cells(json_data)):
        # cells_data = json_data['cells']
        cell_type = cells_data[cell_no]["cell_type"]
        if cell_type == "code":
            op_code_cell_no += 1

            # ADD Code-Cell comment line at beginning of cell source lines:
            source_lines = cells_data[cell_no]["source"]
            # if 'section_title' in cells_data[cell_no]:
            # final_cell_no = cells_data[cell_no]['final_cell_no']
            if "section_number" in cells_data[cell_no]:
                # source_lines.insert(0, f'# Code-Cell[{op_code_cell_no}/F{final_cell_no}] { cells_data[cell_no]["section_number"] }\n\n')
                source_lines.insert(
                    0,
                    f"# Code-Cell[{op_code_cell_no}] {cells_data[cell_no]['section_number']}\n\n",
                )
            else:
                # source_lines.insert(0, f'# Code-Cell[{op_code_cell_no}/F{final_cell_no}]\n\n')
                source_lines.insert(0, f"# Code-Cell[{op_code_cell_no}]\n\n")

        if "section_title" in cells_data[cell_no]:
            del cells_data[cell_no]["section_title"]
        if "section_number" in cells_data[cell_no]:
            del cells_data[cell_no]["section_number"]

    if NUM_QUESTIONS > 0:
        questions_text = "<hr><h1> Answers to Questions:</h1>"
        id = "eof-questions"
        q = 0
        for question_entry in QUESTIONS:
            q += 1
            summary = question_entry[0]
            detail = question_entry[1]
            questions_text += f"\n<b>{q}. {summary}</b>\n\n{detail}\n\n"

        cells_data.append(markdown_cell(id, [questions_text]))

    DEBUG(f"cells to include[#{len(cells)}]=[{cells}]")
    DEBUG(f"included markdown cells={incl_md_cells}")
    DEBUG(f"included code     cells={incl_code_cells}")
    DEBUG(f"excluded          cells={exclude_cells}")
    DEBUG()
    return json_data


def write_markdown(
    markdown_file, cell_num, cell_type, section_title, current_section_text
):
    print(f"writefile({markdown_file})")
    current_section_text = (
        f"<!-- cell_num: {cell_num} -->\n"
        + f"<!-- cell_type: {cell_type} -->\n"
        + f"<!-- section_title:<<<{section_title}>>>-->\n"
        + current_section_text
    )
    writefile(f"{markdown_file}", "w", current_section_text)


def split_nb(json_data, DEBUG=False):
    cells = []
    global VARS_SEEN
    print("-- split_nb: resetting VARS_SEEN !!")
    # VARS_SEEN = {}

    md_files_index = ""

    toc_cell_no = -1
    count_sections = False
    current_sections = []
    toc_text = '<div id="TOC" >\n'

    SPLIT_ON_SECTIONS = -1  # Split on any level
    SPLIT_ON_SECTIONS = 1  # Split only on 1st-level i.e. 1, 2, ..
    SPLIT_ON_SECTIONS = 2  # Split only 1st, 2nd-level i.e. 1, 1.1, 1.2, 2, 2.1, ...

    current_section_text = ""
    section_no = "1"
    section_title = "UNKNOWN"
    os.mkdir("md")
    markdown_file = f"section_{section_no}.md"
    # markdown_file_path=f'md/{markdown_file}'
    markdown_file_path = f"{OP_DIR}/{markdown_file}"

    sec_cell_no = 0

    div_sec = '<div id="sec'
    len_div_sec = len(div_sec)
    for cell_no in range(nb_cells(json_data)):
        sec_cell_no += 1
        cell_type = json_data["cells"][cell_no]["cell_type"]
        source_lines = json_data["cells"][cell_no]["source"]
        if len(source_lines) == 0:
            if DEBUG:
                print("empty")
            continue

        if cell_type == "code":
            current_section_text += "\n```"

        EXCLUDED_CODE_CELL = False
        if source_lines[0].find("#EXCLUDE") == 0 and cell_type == "code":
            EXCLUDED_CODE_CELL = True
            # NOTE: Code will be excluded but continue to parse/search for variables settings

        # Exclude any NB_SAVE, NB_SAVE_STEP cells:
        if source_lines[0].find("NB_SAVE") == 0 and cell_type == "code":
            EXCLUDED_CODE_CELL = True
            # Why does this not empty output?
            json_data["cells"][cell_no]["outputs"]=[]
            #XXX
            #include_cell = False

        for slno in range(len(source_lines)):
            source_line = source_lines[slno]

            if cell_type == "code" and not EXCLUDED_CODE_CELL:
                inc_source_line = source_line
                if "| NB_" in source_line:
                    inc_source_line = source_line[: source_line.find("| NB_")]
                    source_lines[slno] = inc_source_line

                if len(inc_source_line) > MAX_LINE_LEN:
                    show_long_code_line(
                        "SPLIT",
                        inc_source_line,
                        MAX_LINE_LEN,
                        cell_no,
                        section_title,
                        EXCLUDED_CODE_CELL,
                    )
                if len(source_line) > MAX_LINE_LEN:
                    DEBUG(
                        f"[split_nb]: len={len(inc_source_line)} > {MAX_LINE_LEN} in cell {sec_cell_no} section={section_title} in line '{source_line}'"
                    )

            if div_sec in source_line:
                start_pos = source_line.find(div_sec)
                end_pos = (
                    start_pos
                    + len_div_sec
                    + source_line[start_pos + len_div_sec :].find('"')
                )
                next_section_no = source_line[start_pos + len_div_sec : end_pos]

                close_div_pos = end_pos + source_line[end_pos:].find("</div")
                next_section_title = source_line[end_pos:close_div_pos]

                DEBUG(f"LINE[0]: <<<{source_line}>>>")
                DEBUG(f"pos[{start_pos}:{end_pos}]")

                if div_sec in source_line[start_pos + len_div_sec :]:
                    die("OOPS")

                if next_section_no.count(".") < SPLIT_ON_SECTIONS:
                    if current_section_text != "":
                        write_markdown(
                            markdown_file_path,
                            cell_no + 1,
                            cell_type,
                            section_title,
                            current_section_text,
                        )
                        current_section_text = ""
                    section_no = next_section_no
                    section_title = next_section_title
                    sec_cell_no = 0
                    markdown_file = f"section_{section_no}.md"
                    markdown_file_path = f"md/{markdown_file}"
                    DEBUG(f"New section {section_no} seen")
                    md_files_index += markdown_file + "\n"

            current_section_text += source_line

        if cell_type == "code":
            current_section_text += "\n```\n"

    if current_section_text != "":
        write_markdown(
            markdown_file_path,
            cell_no + 1,
            cell_type,
            section_title,
            current_section_text,
        )

    writefile(f"{OP_DIR}/index.txt", "w", md_files_index)


if __name__ == "__main__":
    print(f'-- running sys.argv[0] with args [{ ', '.join(sys.argv[1:])}]')
    main()
