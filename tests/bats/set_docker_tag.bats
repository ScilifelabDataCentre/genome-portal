set_docker_tag="${BATS_TEST_DIRNAME}"/../../scripts/ci/set_docker_tag
@test "Release" {
    [ "$(${set_docker_tag} release)" = "tag=prod" ]
}

@test "Workflow dispatch" {
    [ "$(${set_docker_tag} workflow_dispatch foo)" = "tag=foo" ]
}

@test "Push" {
    [ "$(${set_docker_tag} push)" = "tag=dev" ]
}
