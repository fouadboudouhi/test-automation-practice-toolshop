*** Settings ***
Documentation     Smoke test verifying that the homepage is reachable.
...               This test only checks basic availability, not content correctness.
Resource          ../resources/keywords/common.robot

*** Test Cases ***
Homepage Is Reachable
    [Documentation]    Verifies that the homepage loads without errors.
    Open Toolshop
    Get Title
    Close Toolshop