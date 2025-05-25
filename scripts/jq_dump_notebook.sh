
# TODO:
# look at python3 option as mentioned here:
# - https://community.checkpoint.com/t5/API-CLI-Discussion/How-to-parse-from-nested-arrays-API-JQ/td-p/81172
#
# jq substrings:
# - https://stackoverflow.com/questions/61012699/jq-substr-equivalent-to-format-a-value

# Show 1st source line of each cell:
# jq -rc '.cells[].source[0]' $1

FORMAT="-c"
[ "$1" = "-pp" ] && { FORMAT=""; shift; }
[ "$1" = "-ml" ] && { FORMAT=""; shift; }

# Dump all paths to all attributes:
if [ "$1" = "-P" ]; then
    # e.g. jq_dump_notebook.sh -P ~/labs/lab9/terraform.tfstate
    shift
    jq $FORMAT 'paths' $1
    exit $?
fi

# Dump all paths to specified attribute:
if [ "$1" = "-p" ]; then
    # e.g. jq_dump_notebook.sh -p kubernetes_version ~/labs/lab9/terraform.tfstate
    shift
    jq $FORMAT 'paths | select(.[-1] == "'$1'")' $2
    exit $?
fi

# Brutal dump of all outputs/source lines:
if [ "$1" = "-a" ]; then
    shift
    # -rc
    jq $FORMAT '.cells[]? |
        { cell_type, outputs, source }' $1
    exit $?
fi

# Show first source line of every code cell:
if [ "$1" = "-c-s1" ]; then
    shift
    # -rc
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | .source[0]//.source? }' $1
    exit $?
fi

# Show keys & cell_type:
if [ "$1" = "-k-t" ]; then
    shift
    # -rc
    jq $FORMAT '.cells[] | { keys: keys, type: .cell_type }'  $1
    exit $?
fi

# Count cells:
if [ "$1" = "-#" ]; then
    shift
    echo "Code     Cells: " $( jq $FORMAT 'def count(stream): reduce stream as $i (0; .+1); count(.cells[]? | select(.cell_type=="code")) ' $1)
    echo "Markdown Cells: " $( jq $FORMAT 'def count(stream): reduce stream as $i (0; .+1); count(.cells[]? | select(.cell_type=="markdown")) ' $1)
    echo "TOTAL    Cells: " $( jq $FORMAT '.cells    | length' $1 )
    exit $?
fi

# Show code cells:
if [ "$1" = "-code" ]; then
    shift
    #jq $FORMAT '.cells[]? | to_entries | map({name:.value, index:.key}) | select(.cell_type=="code") |
    # -rc
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | {
         type: .cell_type,
         source0: .source[]?,
         outputs0: .outputs[0].text[0]? |.[0:80]
    } '  $1
    exit $?
fi

# Show metadata
if [ "$1" = "-meta" ]; then
    shift
    # -rc
    jq $FORMAT '.metadata' $1
    exit $?
fi

# Show markdown cells:
if [ "$1" = "-md" ]; then
    shift
    #jq $FORMAT '.cells[]? | select(.cell_type=="markdown") | { type: .cell_type, markdown0: .source[]? }'  $1
    # -rc
    jq $FORMAT '.cells[]? | select(.cell_type=="markdown") | { md: .source[]? }'  $1
    exit $?
fi

# TEST
if [ "$1" = "-t" ]; then
    shift
    # -rc
    set -x
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | { cell_type, source[0]//.source? }' $1
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | { cell_type, source[0]? }' $1
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | { cell_type, source[]? }' $1
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | { cell_type, source? }' $1
    jq $FORMAT '.cells[]? | select(.cell_type=="code") | { cell_type, source }' $1
    jq $FORMAT '.cells[]? | { cell_type, source }' $1
    jq $FORMAT '.cells[]? | { cell_type, source\[0] }' $1
    jq $FORMAT '.cells[]? | .source[0]//.source? }' $1
    #jq $FORMAT '.cells[]? | { type: .cell_type, source0: .source[0]//.source? }' $1
    jq $FORMAT '.cells[]? | { type: .cell_type, source0: .source[0] }' $1
    #jq $FORMAT '.cells[]? | { type: .cell_type, keys: .keys() }' $1
    #jq $FORMAT '.cells[]? | keys_unsorted }' $1
    jq $FORMAT '.cells[] | { keys: keys, type: .cell_type }'  $1
    # LATEST TEST:
    #jq $FORMAT '.cells[] | { keys: keys, type: .cell_type, source0: .source[]? }'  $1
    jq $FORMAT '.cells[] | { keys: keys, type: .cell_type, source0: .source[]?, outputs: .outputs[]? }'  $1
    exit $?
fi

#jq $FORMAT '.cells[] | { type: .cell_type, source0: .source[]?, outputs: .outputs[]? }'  $1
# Show keys & cell_type & beg. source/output:
#if [ "$1" = "-k-t" ]; then
    #shift
# DEFAULT:
    # -rc
    jq $FORMAT '.cells[]? | {
        keys:     keys,
        type:     .cell_type,
        id:     .id,
        source0:  .source[0]? | .[0:40],
        #".cell_type": .outputs[0].text[0]? |.[0:40],
        outputs0: .outputs[0].text[0]? |.[0:40]
    }'  $1
    exit $?
#fi


exit
## --------------------------------------------------------------------------------

# Seen here:
# - https://gist.github.com/nishadhka/8b381af02662130e9adf877678d32548

 OUTPUT=$(jq '.cells[]? | select(.cell_type=="code") | .source[]?//.source' $f \
            | sed 's/^"//g;s/"$//g;s/\\n$//g;s/\\"/"/g;s/\\\\/\\/g;s/\\n/\n/g' \
            | pygmentize -l python 2>/dev/null \
            | grep $PATTERN)


    # -rc
jq $FORMAT '.cells[] |
    { cell_type, outputs, source }' $1
    #{ cell_type, outputs, source }' $1
    #{ cell_type, outputs, source[] | first }' $1
    #cell_type, outputs, source' $1
    #cell_type, outputs, source[0]' $1
    # BAD{ cell_type, outputs, source } | join(" ")' $1

