package healthops.phi

deny contains msg if {
    input.request.path == "/query"
    not input.user.hipaa_trained
    msg := "HIPAA training required for PHI queries"
}

deny contains msg if {
    input.request.path == "/members"
    not input.user.role == "clinician"
    not input.user.role == "admin"
    msg := sprintf("Role '%s' cannot access member records", [input.user.role])
}
