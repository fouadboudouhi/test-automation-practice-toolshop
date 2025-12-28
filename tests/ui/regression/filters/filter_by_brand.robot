*** Settings ***
Documentation     Regression: apply a brand filter (if available) and ensure results still show.
...               Selects the first available brand checkbox and verifies the product list remains non-empty.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Filter Products By Brand
    [Documentation]    Apply the first brand filter and assert products are still displayed.
    [Tags]    regression

    # Preconditions: product list is rendered.
    Wait For At Least One Product Card

    # Ensure at least one brand checkbox exists (strict-mode safe).
    Wait For Elements State    css=input[data-test^="brand-"] >> nth=0    visible    timeout=15s
    Scroll To Element          css=input[data-test^="brand-"] >> nth=0

    # Apply brand filter.
    Click    css=input[data-test^="brand-"] >> nth=0

    # Postcondition: after filtering, we should still have results.
    Wait For At Least One Product Card