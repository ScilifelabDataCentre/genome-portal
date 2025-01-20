setup() {
    bats_load_library 'bats-support'
    bats_load_library 'bats-assert'
}

@test "Build data builder image" {
  run dockerbuild -n -k data
  assert_output --partial "-t ghcr.io/scilifelabdatacentre/swg-data-builder:local -f docker/data.dockerfile"
}

@test "Build hugo site image" {
  run dockerbuild -n -k hugo
  assert_output --partial "-t ghcr.io/scilifelabdatacentre/swg-hugo-site:local -f docker/hugo.dockerfile"
}
