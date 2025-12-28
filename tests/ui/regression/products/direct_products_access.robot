*** Settings ***
Documentation     Regression: products listing is reachable (home shows products).
...               Verifies that the products list is rendered on initial load.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Direct Access To Products Route Works
    [Documentation]    Assert the products listing is available by checking that product cards are visible.
    [Tags]    regression

    Wait For At Least One Product Card