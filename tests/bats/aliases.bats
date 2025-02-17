setup() {
    bats_load_library 'bats-support'
    bats_load_library 'bats-assert'
}

@test "Extract aliases from FASTA headers" {
    run aliases - <<EOF
>ENA|CAMGYJ010000001|CAMGYJ010000001.1 Linum tenue genome assembly, contig: CHL
>ENA|CAMGYJ010000002|CAMGYJ010000002.1 Linum tenue genome assembly, contig: LG1
# Extra space at the end of next line
>ENA|CAMGYJ010000003|CAMGYJ010000003.1 Linum tenue genome assembly, contig: LG10$(printf '\t  ')
EOF
    assert_output <<EOF
#ENA	NCBI	original
ENA|CAMGYJ010000001|CAMGYJ010000001.1	CAMGYJ010000001.1	CHL
ENA|CAMGYJ010000002|CAMGYJ010000002.1	CAMGYJ010000002.1	LG1
ENA|CAMGYJ010000003|CAMGYJ010000003.1	CAMGYJ010000003.1	LG10
EOF
}

@test "Headers without original contigs" {
    run aliases - <<EOF
>ENA|CAMGYJ010000001|CAMGYJ010000001.1 Skeletonema marinoi strain R05AC Sm_000078F, whole genome shotgun sequence.
EOF
    assert_output <<EOF
#ENA	NCBI	original
ENA|CAMGYJ010000001|CAMGYJ010000001.1	CAMGYJ010000001.1
EOF
}

@test "Not ENA formatted headers" {
    run aliases - <<EOF
>chr1
>chr2
EOF
    assert_success
    assert_output --partial "not ENA-formatted"

}

@test "ENA formatted headers for second file" {
    run aliases <(cat <<EOF
>chr1
>chr2
EOF
		 ) <(cat <<EOF
>ENA|CAMGYJ010000001|CAMGYJ010000001.1 Linum tenue genome assembly, contig: CHL
EOF
		    )
    assert_success
    assert_output --partial "not ENA-formatted"
    assert_output --partial "ENA|CAMGYJ010000001|CAMGYJ010000001.1	CAMGYJ010000001.1	CHL"
}
