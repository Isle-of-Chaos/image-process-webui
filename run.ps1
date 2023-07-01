$current_folder = Split-Path -Path $MyInvocation.MyCommand.Path -Parent

# 激活venv虚拟环境
$venv_path = Join-Path -Path $current_folder -ChildPath "venv\Scripts\Activate.ps1"
if(Test-Path $venv_path){
    & $venv_path
}
else{
    Write-Host "venv虚拟环境不存在！"
    Exit
}

# 运行py文件
$py_path = Join-Path -Path $current_folder -ChildPath "file.py"
if(Test-Path $py_path){
    & py $py_path
}
else{
    Write-Host "py文件不存在！"
    Exit
}