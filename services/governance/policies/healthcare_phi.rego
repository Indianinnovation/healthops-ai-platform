package healthops.phi

import rego.v1

deny contains msg if {
    input.request.path == "/query"
    not input.user.hipaa_trained
    msg := "HIPAA training required for PHI queries"
}

deny contains msg if {
    input.request.path == "/members"
    not input.user.role == "clinician"
    not input.user.role == "admin"
    msg := "Unauthorized role cannot access member records"
}
