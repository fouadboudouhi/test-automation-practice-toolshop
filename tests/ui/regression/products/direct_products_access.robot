*** Settings ***
Documentation     Regression: products listing is reachable (home shows products).
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop

*** Test Cases ***
Direct Access To Products Route Works
    [Tags]    regression
    Wait For At Least One Product Card