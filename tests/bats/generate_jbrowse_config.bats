setup() {
    bats_load_library 'bats-support'
    bats_load_library 'bats-assert'
    load generate_jbrowse_config
}

teardown() {
    if [[ "${config}" != "" && -f "${config}" ]]; then
	rm -f "${config}"
    fi
}

@test "list_tracks" {
    run list_tracks - <<EOF
assembly:
  name: asm
tracks:
  - url: http://example.com
    name: foo
    fileName: foo.gff
EOF
    assert_output "http://example.com;foo;asm;foo.gff"
}

@test "list_tracks (empty track list)" {
    run list_tracks - <<EOF
assembly:
  name: foo
tracks:
EOF
    assert_output ""
}

@test "list_assemblies" {
    run list_assemblies - <<EOF
assembly:
  url: example.com
  name: foo
  displayName: FOO
  aliases: aliases.txt
  fileName: foo.fna
EOF
    assert_output "example.com;foo;FOO;aliases.txt;foo.fna"
}


@test "list_assemblies, with default aliases" {
    config=$(mktemp --suffix=.bgz)
    cat <<EOF > "${config}"
assembly:
  url: example.com
  name: foo
  displayName: FOO
  fileName: foo.fna
EOF
    run list_assemblies "${config}"
    assert_output "example.com;foo;FOO;aliases.txt;foo.fna"
}

