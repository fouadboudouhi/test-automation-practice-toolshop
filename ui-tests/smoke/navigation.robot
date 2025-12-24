*** Settings ***
Documentation     Smoke test verifying that the main navigation is present.
...               Navigation functionality is not validated here.
Resource          ../resources/keywords/common.robot

*** Test Cases ***
Navigation Is Visible
    [Documentation]    Ensures that the category navigation entry exists.
    Open Toolshop
    Wait For Elements State    css=[data-test="nav-categories"]    visible    timeout=15s
    Close Toolshop