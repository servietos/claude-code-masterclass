#!/usr/bin/env pwsh
$Payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
# Claude sends the pending tool call as JSON on stdin, this pulls out the command
$Command = $Payload.tool_input.command

# \b marks a word boundary and \s+ one or more spaces, so this matches rm -rf as a whole word
if ($Command -match '\brm\s+-rf\b') {
    [Console]::Error.WriteLine("Policy gate: rm -rf is blocked.")
    # exit 2 is the only code that blocks the call, any other non-zero code just warns
    exit 2
}
exit 0
