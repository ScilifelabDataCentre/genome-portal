setup() {
    bats_load_library 'bats-support'
    bats_load_library 'bats-assert'
}

@test "Run make" {
  run dockermake -n debug
  assert_output --partial "ghcr.io/scilifelabdatacentre/swg-data-builder:local make debug"
}

@test "Run make in with test configuration" {
  run dockermake -n -T debug
  assert_output --partial "ghcr.io/scilifelabdatacentre/swg-data-builder:local make debug"
  assert_output --partial "docker network create swg-test-net"
  assert_output --regexp "docker run -d .* --network=swg-test-net .* nginx:alpine"
}

