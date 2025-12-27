*** Settings ***
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Product Cards Show A Price
    [Tags]    smoke
    Go To    ${BASE_URL}
    Wait For At Least One Product Card

    ${card_text}=    Get Text    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]
    # Price usually contains digits (and often decimals)
    Should Match Regexp    ${card_text}    .*\\d+([\\.,]\\d{2})?.*