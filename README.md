# Project Setup & Useful Commands

This repository contains .  
Below is a quick reference for setting up the environments and running the programs.

---

## 1. Virtual Environment

### 1.1 Creates / checks / activates environments

Use the provided PowerShell script:

```powershell
. .\setup_env.ps1
````

This script will:

* Creates both virtual environments (`.venv32` and `.venv64`) if they do not exist
* Activate the virtual environment
* Install / update the required packages
* Install / update the recommended extensions

### 1.2 Manually activate existing venv (if needed)

If you need to activate the environment manually:

```powershell
.\.venv32\Scripts\Activate.ps1
.\.venv64\Scripts\Activate.ps1
```

---

## 2. Updating Requirements and VS Code Extensions

### 2.1 Update Python requirements file

From within the active virtual environment (choose correct venv):

```powershell
python -m pip freeze > phase_control\_requirements_phase_control.txt
python -m pip freeze > acquisition\_requirements_acquisition.txt
```

### 2.2 Export VS Code extensions

To save the list of installed VS Code extensions:

```powershell
code --list-extensions > _extensions.txt
```

This writes all installed extensions into `_extensions.txt`.

---

## 3. Git Configuration

Set your Git username and email (once per machine / repository):

```powershell
git config user.name "Git name"
git config user.email "email"
```

Replace `"Git name"` and `"email"` with your actual name and email address.

---

## 4. Running the Applications

All applications are started via Python’s module syntax from the repository root.


```powershell
python -m app
```

---

## 5. Notes

* Always run commands from the project root directory (where `setup_env.ps1` is located).
* Make sure the virtual environment is active before running any of the Python modules above.

```
