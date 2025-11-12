import requests
import json
import os
import sys

# --- version import (universal compatible) ---
try:
    from importlib.metadata import version as get_version, PackageNotFoundError
except ImportError:
    # fallback for Python <3.8 if user has it installed
    try:
        from importlib.metadata import version as get_version, PackageNotFoundError
    except ImportError:
        get_version = None
        PackageNotFoundError = Exception

# --- optional packaging ---
try:
    from packaging import version as parse_ver
except ImportError:
    parse_ver = None


def check_for_update(package_name="crystalwindow"):
    """
    Checks PyPI for updates.
    - Prints once after update (then silent)
    - Warns if outdated
    - Flexes if dev version ahead
    - Works even if `packaging` or `importlib_metadata` missing
    """
    cache_file = os.path.join(os.path.expanduser("~"), ".cw_version_cache.json")

    # Skip if version detection not possible
    if not get_version:
        print("(⚠️ Version check skipped: importlib.metadata missing)")
        return

    try:
        # === get current version ===
        try:
            current_version = get_version(package_name)
        except PackageNotFoundError:
            print(f"(⚠️ '{package_name}' not installed, skipping version check)")
            return

        # === load cache ===
        last_checked = None
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    last_checked = data.get(package_name)
            except Exception:
                pass

        # === fetch PyPI info ===
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=3)
            if response.status_code != 200:
                return
            latest_version = response.json()["info"]["version"]
        except Exception:
            return  # silent if offline

        # === compare versions ===
        if parse_ver:
            cv = parse_ver.parse(current_version)
            lv = parse_ver.parse(latest_version)
        else:
            cv = current_version
            lv = latest_version

        if cv < lv:
            print(f"\n⚠️ Yo dev! '{package_name}' is outdated ({current_version})")
            print(f"👉 Newest is {latest_version}! Run:")
            print(f"   pip install --upgrade {package_name}")
            print(f"Or peep: https://pypi.org/project/{package_name}/{latest_version}/\n")

        elif cv > lv:
            print(f"🚀 Local version ({current_version}) is newer than PyPI ({latest_version}) — flex on 'em 😎")

        else:
            # only print once after update
            if last_checked != current_version:
                print(f"✅ Up to date! ver = {current_version}.")
                try:
                    with open(cache_file, "w") as f:
                        json.dump({package_name: current_version}, f)
                except Exception:
                    pass
            # else: stay silent

    except Exception as e:
        print(f"(⚠️ Version check skipped: {e})")
