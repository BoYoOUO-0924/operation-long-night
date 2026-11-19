@echo off
cd /d "%~dp0..\server"
"C:\Users\tung0\AppData\Roaming\PrismLauncher\java\java-runtime-gamma\bin\java.exe" @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.20.1-47.4.16/win_args.txt nogui %*
