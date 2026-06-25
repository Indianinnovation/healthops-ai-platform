package healthops.authz

default allow = false

allow if {
    input.user.role == "admin"
}

allow if {
    input.user.role == "clinician"
    input.request.method == "GET"
}

allow if {
    input.user.role == "member"
    input.request.path == "/query"
    input.user.hipaa_trained
}
