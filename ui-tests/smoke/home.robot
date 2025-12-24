*** Settings ***
Documentation     Smoke test verifying that the homepage is reachable.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Homepage Is Reachable
    [Documentation]
    ...    Pass criteria:
    ...    - Page body is visible
    ...    - Top navbar is visible
    ...    - Current URL starts with BASE_URL
    Wait For Elements State    css=body          visible    timeout=20s
    Wait For Elements State    css=nav.navbar    visible    timeout=20s
    ${url}=    Get Url
    Should Start With    ${url}    ${BASE_URL}