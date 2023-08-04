
# Show 1st source line of each cell:
# jq -rc '.cells[].source[0]' $1

# Brutal dump of all outputs/source lines:
if [ "$1" = "-a" ]; then
    shift
    jq -rc '.cells[]? |
        { cell_type, outputs, source }' $1
    exit $?
fi

# Show first source line of every code cell:
if [ "$1" = "-c-s1" ]; then
    shift
    jq -rc '.cells[]? | select(.cell_type=="code") | .source[0]//.source? }' $1
    exit $?
fi

# TEST
if [ "$1" = "-t" ]; then
    shift
    set -x
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source[0]//.source? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source[0]? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source[]? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source? }' $1
    jq -rc '.cells[]? | select(.cell_type=="code") | { cell_type, source }' $1
    jq -rc '.cells[]? | { cell_type, source }' $1
    jq -rc '.cells[]? | { cell_type, source\[0] }' $1
    jq -rc '.cells[]? | .source[0]//.source? }' $1
    #jq -rc '.cells[]? | { type: .cell_type, source0: .source[0]//.source? }' $1
    jq -rc '.cells[]? | { type: .cell_type, source0: .source[0] }' $1
    #jq -rc '.cells[]? | { type: .cell_type, keys: .keys() }' $1
    #jq -rc '.cells[]? | keys_unsorted }' $1
    jq -rc '.cells[] | { keys: keys, type: .cell_type }'  $1
    exit $?
fi

# Seen here:
# - https://gist.github.com/nishadhka/8b381af02662130e9adf877678d32548

 OUTPUT=$(jq '.cells[]? | select(.cell_type=="code") | .source[]?//.source' $f \
            | sed 's/^"//g;s/"$//g;s/\\n$//g;s/\\"/"/g;s/\\\\/\\/g;s/\\n/\n/g' \
            | pygmentize -l python 2>/dev/null \
            | grep $PATTERN)


jq -rc '.cells[] |
    { cell_type, outputs, source }' $1
    #{ cell_type, outputs, source }' $1
    #{ cell_type, outputs, source[] | first }' $1
    #cell_type, outputs, source' $1
    #cell_type, outputs, source[0]' $1
    # BAD{ cell_type, outputs, source } | join(" ")' $1

