setup_suite() {
    bats_require_minimum_version 1.5.0
    # Set BATS_LIB_PATH environment variable when invoking bats
    # Example: export BATS_LIB_PATH=/my/custom/lib/; bats tests/bats
    BATS_LIB_PATH="${BATS_LIB_PATH}":~/.local/lib:/usr/lib/bats

    # Put our script directory in the executable search path
    DIR="${BATS_TEST_DIRNAME}"/../../scripts
    PATH="${DIR}:${PATH}"
}
