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


@test "Sort BED file" {
    . "${SRC}"
    res=$(main test.bed <<EOF
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

