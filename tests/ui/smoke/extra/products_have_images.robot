*** Settings ***
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Product Thumbnails Are Visible
    [Tags]    smoke
    # NOTE: Product list is on the home page.
    Go To    ${BASE_URL}
    Wait For Elements State    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")]//img)[1]    visible    timeout=60s
    ${src}=    Get Attribute    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")]//img)[1]    src
    Should Not Be Empty    ${src}
