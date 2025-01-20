setup() {
    bats_load_library 'bats-support'
    bats_load_library 'bats-assert'
}

@test "Runs Hugo development server" {
  run dockerserve -n -d
  assert_output --partial "hugo server"
}

@test "Run genome portal image" {
  run dockerserve -n
  assert_output --partial "docker run -d"
  assert_output --partial "ghcr.io/scilifelabdatacentre/swg-hugo-site:local"
}
