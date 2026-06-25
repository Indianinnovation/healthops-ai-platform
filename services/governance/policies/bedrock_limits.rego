package healthops.bedrock

import rego.v1

deny contains msg if {
    input.user.daily_queries > 100
    msg := "Daily Bedrock query limit exceeded (100/day)"
}

deny contains msg if {
    contains(lower(input.request.body), "ignore previous")
    msg := "Potential prompt injection detected"
}

deny contains msg if {
    contains(lower(input.request.body), "system prompt")
    msg := "Potential prompt injection detected"
}
