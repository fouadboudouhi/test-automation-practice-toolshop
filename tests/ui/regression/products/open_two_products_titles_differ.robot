*** Settings ***
Documentation     Regression: two different products have different titles on the listing.
...               Reads the titles of the first two product cards and asserts they are not identical.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Two Different Products Have Different Titles
    [Documentation]    Compare the titles of two different product cards and assert they differ.
    [Tags]    regression

    Wait For At Least One Product Card
    ${t1}=    Get Text    css=a.card[data-test^="product-"] h5 >> nth=0
    ${t2}=    Get Text    css=a.card[data-test^="product-"] h5 >> nth=1
    Should Not Be Equal    ${t1}    ${t2}