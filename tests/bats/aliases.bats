setup_file() {
    bats_require_minimum_version 1.5.0
    # Set BATS_LIB_PATH environment variable when invoking bats
    # Example: export BATS_LIB_PATH=/my/custom/lib/; bats tests/bats
    BATS_LIB_PATH="${BATS_LIB_PATH}":~/.local/lib:/usr/lib/bats

    # Put our script directory in the executable search path
    DIR="${BATS_TEST_DIRNAME}"/../../scripts
    PATH="${DIR}:${PATH}"
}

setup() {
    bats_load_library 'bats-support'
    bats_load_library 'bats-assert'
}

@test "Extract aliases from FASTA headers" {
    run aliases <<EOF
>ENA|CAMGYJ010000001|CAMGYJ010000001.1 Linum tenue genome assembly, contig: CHL
>ENA|CAMGYJ010000002|CAMGYJ010000002.1 Linum tenue genome assembly, contig: LG1
>ENA|CAMGYJ010000003|CAMGYJ010000003.1 Linum tenue genome assembly, contig: LG10
EOF
    expected=$(cat <<EOF
#ENA NCBI original
ENA|CAMGYJ010000001|CAMGYJ010000001.1 CAMGYJ010000001.1 CHL
ENA|CAMGYJ010000002|CAMGYJ010000002.1 CAMGYJ010000002.1 LG1
ENA|CAMGYJ010000003|CAMGYJ010000003.1 CAMGYJ010000003.1 LG10
EOF
	    )
    assert_output "${expected}"
}
