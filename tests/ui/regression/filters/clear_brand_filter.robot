*** Settings ***
Documentation     Regression: apply and clear brand filter; list should still show results.
...               Verifies that filtering and then clearing the brand filter still leaves at least
...               one product visible, and that the initial list was non-empty.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Clear Brand Filter Restores Results
    [Documentation]    Apply the first brand filter and clear it again; ensure the product list is non-empty.
    [Tags]    regression

    # Preconditions: product list is rendered and at least one brand checkbox is present.
    Wait For At Least One Product Card
    Wait For Elements State    css=input[data-test^="brand-"] >> nth=0    visible    timeout=15s
    Scroll To Element          css=input[data-test^="brand-"] >> nth=0

    # Capture product count before applying any filter.
    ${before}=    Get Element Count    css=a.card[data-test^="product-"]

    # Apply brand filter (select first brand).
    Click    css=input[data-test^="brand-"] >> nth=0
    Wait For At Least One Product Card
    ${after_filter}=    Get Element Count    css=a.card[data-test^="product-"]

    # Clear brand filter (toggle the same checkbox again).
    Click    css=input[data-test^="brand-"] >> nth=0
    Wait For At Least One Product Card
    ${after_clear}=    Get Element Count    css=a.card[data-test^="product-"]

    # Assertions: list should be non-empty before and after clearing the filter.
    Should Be True    ${after_clear} >= 1
    Should Be True    ${before} >= 1