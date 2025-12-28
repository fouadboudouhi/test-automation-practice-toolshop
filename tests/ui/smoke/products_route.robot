*** Settings ***
Documentation     Smoke: verify the products listing route is reachable.
...               In this app, the product listing is the home page.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Products Route Is Reachable
    [Documentation]    Navigate to the products listing (home) and assert product cards become visible.
    [Tags]    smoke

    # In this app, the product listing is the home page.
    Go To    ${BASE_URL}
    Wait For At Least One Product Card