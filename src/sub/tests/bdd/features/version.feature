Feature: Version Endpoint
  As a DevOps engineer,
  I want to know the presently deployed Version,
  So that I can manage deployments.

  Background:
    Given a "sub" deployment

  Scenario: Version should be returned when requested
    When the user gets "/v1/sub/version"
    Then the response code should be "200"
