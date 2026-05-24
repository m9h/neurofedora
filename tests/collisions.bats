#!/usr/bin/env bats
# collisions.bats — fail the test run if any neurofedora packages own
# the same file path. Wraps check-collisions.sh so it integrates with the
# rest of the BATS suite (TAP / JUnit / parallel).

bats_require_minimum_version 1.5.0

HERE="$(dirname "${BATS_TEST_FILENAME}")"

@test "no file conflicts among installed neurofedora packages" {
    run --separate-stderr "$HERE/check-collisions.sh" --installed
    if [ "$status" -ne 0 ]; then
        echo "Found $status colliding package pair(s). First 20:"
        echo "$output" | head -20
        echo ""
        echo "Re-run for full list:  ./check-collisions.sh --installed"
        false
    fi
}

@test "no file conflicts in the COPR repo (catches conflicts pre-install)" {
    run --separate-stderr "$HERE/check-collisions.sh" --repo
    if [ "$status" -ne 0 ]; then
        echo "Found $status colliding package pair(s) in the COPR repo metadata."
        echo "These would block 'dnf install' even if the binaries are otherwise fine."
        echo "First 20:"
        echo "$output" | head -20
        echo ""
        echo "Re-run for full list:  ./check-collisions.sh --repo"
        false
    fi
}
