*** Settings ***
Documentation     Regression: apply a brand filter (if available) and ensure results still show.
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Suite Setup       Open Toolshop

*** Test Cases ***
Filter Products By Brand
    [Tags]    regression
    Wait For At Least One Product Card

    # Ensure at least one brand checkbox exists (strict-mode safe)
    Wait For Elements State    css=input[data-test^="brand-"] >> nth=0    visible    timeout=15s
    Scroll To Element          css=input[data-test^="brand-"] >> nth=0
    Click                      css=input[data-test^="brand-"] >> nth=0

    # After filtering, we should still have results
    Wait For At Least One Product Card
