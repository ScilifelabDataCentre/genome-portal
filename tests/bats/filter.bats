SRC="${BATS_TEST_DIRNAME}"/../../scripts/filter

@test "sort_bed" {
    . "${SRC}"
    res=$(sort_bed <<EOF
# Header
track foo
browser bar
A 3
A 2
EOF
       )
    expected=$(cat <<EOF
# Header
track foo
browser bar
A 2
A 3
EOF
       )
    [ "${res}" = "${expected}" ]
}

@test "tabify" {
    . "${SRC}"
    res=$(tabify <<EOF
A 3    4
EOF
       )
    expected=$(printf '%s\t%s\t%s' A 3 4)
    [ "${res}" = "${expected}" ]
}

@test "Sort and tabify BED file" {
    . "${SRC}"
    res=$(main test.bed <<EOF
# Header
track foo
browser bar
A 3
A 2
EOF
       )
    expected=$(printf '%s\t%s\n' '#' Header track foo browser bar A 2 A 3)
    [ "${res}" = "${expected}" ]
}
