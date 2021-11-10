set -e

TDIR=/Users/matentzn/ws/tsvalid/tests/data
for file in $TDIR/*.tsv; do
    [ -f "$file" ] || continue
    echo ""
    echo "########################"
    echo "Running tests for $file:"
    tsvalid "$file"
done