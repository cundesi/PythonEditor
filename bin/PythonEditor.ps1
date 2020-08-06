if (!(Test-Path Variable:PSScriptRoot)) { $PSScriptRoot = Split-Path $MyInvocation.MyCommand.Path -Parent }
$python_app = "python"
$app_args = '-m PythonEditorLaunch'
if($myinvocation.expectingInput) { $input | & $python_app $app_args @args } else { & $python_app $app_args @args }
