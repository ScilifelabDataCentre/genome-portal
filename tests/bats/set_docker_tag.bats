set_docker_tag="${BATS_TEST_DIRNAME}"/../../scripts/ci/set_docker_tag
@test "Release" {
    [ "$(${set_docker_tag} release v1.2.3 25e47f1814c742b4c61d326a63384d8dace869e2)" = "tag=v1.2.3" ]
}

@test "Workflow dispatch with custom tag" {
    [ "$(${set_docker_tag} workflow_dispatch main 25e47f1814c742b4c61d326a63384d8dace869e2 foo)" = "tag=foo" ]
}


@test "Workflow dispatch without custom tag" {
    [ "$(${set_docker_tag} workflow_dispatch main 25e47f1814c742b4c61d326a63384d8dace869e2)" = "tag=dev-25e47f1814c742b4c61d326a63384d8dace869e2" ]
}

@test "Push" {
    [ "$(${set_docker_tag} push main 25e47f1814c742b4c61d326a63384d8dace869e2)" = "tag=dev-25e47f1814c742b4c61d326a63384d8dace869e2" ]
}
