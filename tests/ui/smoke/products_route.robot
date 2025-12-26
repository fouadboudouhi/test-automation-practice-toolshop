*** Settings ***
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Products Route Is Reachable
    [Tags]    smoke
    # In this app, the product listing is the home page.
    Go To    ${BASE_URL}
    Wait For At Least One Product Card
