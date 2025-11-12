import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

import click

try:
    from .logger import logger
except ImportError:
    from logger import logger

# Cache folder for downloaded JRE
CACHE_DIR = Path.home() / ".audit_scan"
JRE_DIR = CACHE_DIR / "jre"
JRE_DIR.mkdir(parents=True, exist_ok=True)


def find_java():
    """Check system java or JAVA_HOME"""
    logger.debug("Looking for Java installation")
    system = platform.system()

    def _is_working_java(java_binary: Path) -> bool:
        if not java_binary or not java_binary.exists():
            return False
        try:
            result = subprocess.run(
                [str(java_binary), "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"Failed to execute Java binary {java_binary}: {exc}")
            return False

        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0 or "Unable to locate a Java Runtime" in output:
            logger.debug(
                f"Java binary at {java_binary} is not usable "
                f"(returncode={result.returncode})."
            )
            if output:
                logger.debug(output.strip())
            return False
        return True

    def _validate_java_home(java_home_dir: Path) -> str | None:
        java_bin_name = "java.exe" if os.name == "nt" else "java"
        java_candidate = java_home_dir / "bin" / java_bin_name
        if _is_working_java(java_candidate):
            logger.debug(f"Found Java in JAVA_HOME: {java_candidate}")
            return str(java_candidate)
        return None

    java_path = shutil.which("java")
    if java_path and _is_working_java(Path(java_path)):
        logger.debug(f"Found Java on PATH: {java_path}")
        return java_path
    if java_path and system == "Darwin":
        logger.debug(f"Ignoring non-functional macOS stub at {java_path}")

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        validated = _validate_java_home(Path(java_home))
        if validated:
            return validated

    if system == "Darwin":
        java_home_tool = Path("/usr/libexec/java_home")
        if java_home_tool.exists():
            try:
                result = subprocess.run(
                    [str(java_home_tool)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                java_home_path = result.stdout.strip()
                if result.returncode == 0 and java_home_path:
                    validated = _validate_java_home(Path(java_home_path))
                    if validated:
                        return validated
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    f"Failed to resolve JAVA_HOME via /usr/libexec/java_home: {exc}"
                )

        brew_prefixes = [Path("/opt/homebrew"), Path("/usr/local")]
        brew_formula_globs = ("openjdk*", "temurin*")
        for prefix in brew_prefixes:
            opt_dir = prefix / "opt"
            if not opt_dir.exists():
                continue
            for pattern in brew_formula_globs:
                for candidate_dir in sorted(
                        opt_dir.glob(pattern), key=lambda p: p.name, reverse=True
                ):
                    java_bins = [
                        candidate_dir / "bin" / "java",
                        candidate_dir
                        / "libexec"
                        / "openjdk.jdk"
                        / "Contents"
                        / "Home"
                        / "bin"
                        / "java",
                    ]
                    for java_candidate in java_bins:
                        if _is_working_java(java_candidate):
                            logger.debug(
                                f"Found Java via Homebrew at: {java_candidate}"
                            )
                            return str(java_candidate)

        jvm_dir = Path("/Library/Java/JavaVirtualMachines")
        if jvm_dir.exists():
            for jdk_dir in sorted(
                    jvm_dir.iterdir(), key=lambda p: p.name, reverse=True
            ):
                java_candidate = (
                        jdk_dir
                        / "Contents"
                        / "Home"
                        / "bin"
                        / ("java.exe" if os.name == "nt" else "java")
                )
                if _is_working_java(java_candidate):
                    logger.debug(f"Found Java in JVM directory: {java_candidate}")
                    return str(java_candidate)

    if platform.system() == "Darwin":
        try:
            ensure_openjdk17()
            # After installation, try finding Java again
            java_path = shutil.which("java")
            if java_path and _is_working_java(Path(java_path)):
                logger.debug(f"Found Java after installation: {java_path}")
                return java_path
        except Exception as e:
            logger.warning(f"Failed to install OpenJDK 17: {e}")

    logger.warning("Java not found in PATH or JAVA_HOME")
    return None


def ensure_openjdk17():
    """Ensure OpenJDK 17 is installed, symlinked, and environment variables set on macOS."""
    logger.info("Checking for OpenJDK 17 installation...")

    brew_path = shutil.which("brew")
    if not brew_path:
        raise RuntimeError(
            "Homebrew not found. Please install Homebrew first from https://brew.sh/"
        )

    try:
        # Check if java is already available
        subprocess.run(
            ["java", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("✅ Java is already available.")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Java not found or misconfigured. Installing OpenJDK 17...")

    # Install openjdk@17 using Homebrew
    try:
        click.echo("Installing OpenJDK 17... might ask for sudo privileges...")
        subprocess.run(["brew", "install", "--quiet", "openjdk@17"], check=True)
        logger.info("✅ Installed openjdk@17 via Homebrew.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install openjdk@17: {e}")

    # Create system symlink (macOS specific)
    if platform.system() == "Darwin":
        jdk_symlink = Path("/Library/Java/JavaVirtualMachines/openjdk-17.jdk")
        jdk_target = Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk")

        try:
            subprocess.run(
                ["sudo", "ln", "-sfn", str(jdk_target), str(jdk_symlink)], check=True
            )
            logger.info(f"🔗 Symlinked {jdk_target} → {jdk_symlink}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(
                f"⚠️  Could not create symlink: {e}\n"
                "Please run manually with admin privileges:\n"
                f"sudo ln -sfn {jdk_target} {jdk_symlink}"
            )

    # Update environment variables
    if platform.system() == "Darwin":
        java_home = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
        java_bin = "/opt/homebrew/opt/openjdk@17/bin"
    else:
        java_home = "/usr/lib/jvm/java-17-openjdk"
        java_bin = f"{java_home}/bin"

    path_line = f'export PATH="{java_bin}:$PATH"'
    java_home_line = f'export JAVA_HOME="{java_home}"'

    # Update shell config
    shell_configs = [
        Path.home() / ".zshrc",
        Path.home() / ".bash_profile",
        Path.home() / ".bashrc",
    ]

    # If none of the config files exist, create .zshrc
    if not any(config.exists() for config in shell_configs):
        zshrc = Path.home() / ".zshrc"
        zshrc.touch()  # Create empty .zshrc if it doesn't exist
        logger.info(f"ℹ️  Created {zshrc} as no shell config files were found.")

    config_updated = False
    for config in shell_configs:
        try:
            if not config.exists():
                continue

            content = config.read_text()
            lines = content.splitlines()
            new_lines = []

            if path_line not in content:
                new_lines.append(path_line)
            if java_home_line not in content:
                new_lines.append(java_home_line)

            if new_lines:
                with config.open("a") as f:
                    for line in new_lines:
                        f.write(f"\n{line}")
                logger.info(f"🔧 Updated {config} with JAVA_HOME and PATH settings.")
                config_updated = True

        except (IOError, OSError) as e:
            logger.warning(f"⚠️  Could not update {config}: {e}")

    # Source the configuration if it was updated
    if config_updated:
        try:
            # Try to source the most common shell config file that exists
            for config in shell_configs:
                if config.exists():
                    subprocess.run(
                        ["sh", "-c", f"source {config} 2>/dev/null || true"],
                        check=False,
                    )
                    logger.info(
                        f"🔄 Sourced {config} to update current shell environment"
                    )
                    break
        except Exception as e:
            logger.warning(f"⚠️  Could not source shell config: {e}")
            logger.info(
                "   Please restart your shell or run 'source ~/.zshrc' (or your shell's config file) for changes to take effect."
            )

    # Set environment for current process
    os.environ["JAVA_HOME"] = java_home
    os.environ["PATH"] = f"{java_bin}:{os.environ.get('PATH', '')}"

    # Verify Java is available in current session
    try:
        subprocess.run(
            ["java", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("✅ OpenJDK 17 installation and setup completed successfully!")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning(
            "⚠️  Java installation may not be immediately available in the current shell.\n"
            "   Please restart your shell or run: source ~/.zshrc (or your shell's config file)"
        )


def download_jre():
    """Download minimal JRE into cache folder"""
    system = platform.system().lower()
    dest = None

    # Get the machine architecture (e.g., 'x86_64', 'arm64')
    arch = platform.machine()
    os = (
        "macos"
        if system == "darwin"
        else ("windows" if system == "windows" else "linux")
    )
    ext = "zip" if system != "linux" else "tar.gz"
    zulu_url = f"https://api.azul.com/zulu/download/community/v1.0/bundles/latest?os={os}&arch={arch}&ext={ext}&bundle_type=jre&java_version=17"
    try:
        with urllib.request.urlopen(zulu_url) as r:
            data = json.load(r)
            url = data["url"]
    except Exception as exc:
        error_msg = f"Failed to fetch JRE metadata: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    if "windows" in system:
        dest = CACHE_DIR / "jre.zip"
    elif "darwin" in system:
        dest = CACHE_DIR / "jre.zip"
    else:  # linux
        dest = CACHE_DIR / "jre.tar.gz"

    try:
        print(f"🌐 Downloading JRE from {url} ...")
        urllib.request.urlretrieve(url, dest)
    except Exception as exc:
        error_msg = f"Failed to download JRE archive: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    try:
        # Extract
        if dest.suffix == ".zip":
            with zipfile.ZipFile(dest, "r") as zip_ref:
                zip_ref.extractall(JRE_DIR)
        else:
            with tarfile.open(dest, "r:gz") as tar_ref:
                tar_ref.extractall(JRE_DIR)
    except Exception as exc:
        error_msg = f"Failed to extract JRE archive: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc
    finally:
        if dest.exists():
            try:
                dest.unlink()
            except Exception as unlink_exc:
                logger.warning(
                    f"Could not remove temporary JRE archive {dest}: {unlink_exc}"
                )

    # Ensure the extracted java binaries are executable (particularly for zip archives)
    try:
        for jre_root in sorted([d for d in JRE_DIR.iterdir() if d.is_dir()]):
            bin_dir = jre_root / "bin"
            if bin_dir.exists():
                for binary in bin_dir.iterdir():
                    if binary.is_file():
                        current_mode = binary.stat().st_mode
                        binary.chmod(
                            current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                        )
    except Exception as exc:
        error_msg = f"Failed to set executable permissions on JRE binaries: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    print(f"✅ JRE installed to {JRE_DIR}")


def get_jre_bin():
    """Return path to java binary"""
    java_bin = find_java()
    if java_bin:
        return java_bin

    # Download and find inside extracted folder
    java_filename = "java.exe" if os.name == "nt" else "java"
    subdirs = [
        d
        for d in JRE_DIR.iterdir()
        if d.is_dir() and (d / "bin" / java_filename).exists()
    ]
    if not subdirs:
        download_jre()
        subdirs = [
            d
            for d in JRE_DIR.iterdir()
            if d.is_dir() and (d / "bin" / java_filename).exists()
        ]
    if not subdirs:
        raise RuntimeError("JRE download failed or empty.")
    java_bin = subdirs[0] / "bin" / java_filename
    if not java_bin.exists():
        raise RuntimeError(f"Java binary not found in {java_bin}")
    return str(java_bin)


def get_scanner_path():
    """Return path to sonar-scanner bundled folder"""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    # Assume a 'sonar-scanner' folder is next to CLI
    scanner_bin = (
            base_path
            / "sonar-scanner"
            / "bin"
            / ("sonar-scanner.bat" if os.name == "nt" else "sonar-scanner")
    )
    if not scanner_bin.exists():
        raise FileNotFoundError(f"SonarScanner binary not found: {scanner_bin}")
    return scanner_bin


def run_sonarqube_scan(sonar_url, token, project_key, sources):
    project_root = Path(sources).resolve()
    if not project_root.exists():
        click.echo("❌ Source directory not found.")
        sys.exit(1)

    project_name = project_root.name
    project_key = project_key or project_name
    click.echo(f"🔍 Starting SonarQube scan for project: {project_key}")

    # Create temporary sonar-project.properties if not exists
    temp_props = None
    props_file = project_root / "sonar-project.properties"
    if not props_file.exists():
        temp_props = props_file
        temp_props.write_text(
            f"""
sonar.projectKey={project_key}
sonar.projectName={project_name}
sonar.sources={sources}
        """.strip()
        )
        click.echo("📝 Created temporary sonar-project.properties")

    # Get scanner and Java paths
    scanner_bin = get_scanner_path()
    java_bin = get_jre_bin()
    java_home = str(Path(java_bin).parent.parent)

    env = os.environ.copy()
    env["JAVA_HOME"] = java_home
    env["PATH"] = f"{Path(java_bin).parent}:{env.get('PATH', '')}"

    env.update({
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LANG": "C.UTF-8" if platform.system() != "Darwin" else "en_US.UTF-8",
        "LC_ALL": "C.UTF-8" if platform.system() != "Darwin" else "en_US.UTF-8",
    })

    # # Ensure URL and token are properly formatted
    # sonar_url = sonar_url or SONAR_HOST_URL
    # token = token or SONAR_LOGIN

    # if not sonar_url or sonar_url == SONAR_HOST_URL:
    #     click.echo(f"⚠️  Using default SonarQube URL: {SONAR_HOST_URL}")
    if not token:
        error_msg = "No SonarQube token provided. Please set SONAR_LOGIN in your .env file or use --token"
        logger.error(error_msg)
        click.echo(f"❌ {error_msg}")
        sys.exit(1)

    env["SONAR_HOST_URL"] = sonar_url.rstrip("/")
    env["SONAR_TOKEN"] = token.strip()
    logger.debug("SonarQube configuration verified")

    # Prepare SARIF report paths
    reports_dir = project_root / "reports"

    # Check which report files exist
    report_files = [
        "gitleaks.sarif",
        "semgrep.sarif",
        "trivy.sarif",
        "bandit.sarif",
        "eslint.sarif",
        "checkov.sarif",
    ]

    # Find existing report files
    existing_reports = [f for f in report_files if (reports_dir / f).exists()]

    # Build sonar-scanner command
    scanner_cmd = [str(scanner_bin), "-Dsonar.verbose=false"]
    # scanner_cmd = [str(scanner_bin)]

    # Add SARIF reports if any exist
    if existing_reports:
        sarif_paths = [f"reports/{report}" for report in existing_reports]
        sarif_arg = "-Dsonar.sarifReportPaths=" + ",".join(sarif_paths)
        scanner_cmd.append(sarif_arg)
        click.echo(f"📊 Including SARIF reports: {', '.join(existing_reports)}")

    click.echo("🚀 Starting SonarScanner...")
    try:
        # Start the subprocess and stream logs in real-time
        process = subprocess.Popen(
            scanner_cmd,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        click.echo("🔍 Scanning code (streaming Sonar logs)...")
        streamed_output = []
        assert process.stdout is not None
        for line in process.stdout:
            streamed_output.append(line)
            click.echo(line.rstrip())

        process.wait()

        # Clean up the temporary properties file
        if temp_props and temp_props.exists():
            temp_props.unlink()
            click.echo("🧹 Cleaned up temporary sonar-project.properties")

        # Check the return code
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, process.args, output="".join(streamed_output)
            )

        click.echo("✅ Sonar scan completed successfully!")
        click.echo(f"👉 View results: {sonar_url}/dashboard?id={project_key}")
        return True

    except subprocess.CalledProcessError as e:
        # Clean up the temporary properties file in case of error
        if temp_props and temp_props.exists():
            temp_props.unlink()
            click.echo("🧹 Cleaned up temporary sonar-project.properties")

        error_msg = f"Sonar scan failed with exit code {e.returncode}"
        logger.error(error_msg)
        click.echo("❌ Sonar scan failed!")
        click.echo(f"Exit code: {e.returncode}")
        # sys.exit(1)
        return False

    except Exception as e:
        # Clean up the temporary properties file in case of error
        if temp_props and temp_props.exists():
            temp_props.unlink()
            click.echo("🧹 Cleaned up temporary sonar-project.properties")

        error_msg = f"Unexpected error during Sonar scan: {str(e)}"
        logger.exception(error_msg)
        click.echo(f"❌ {error_msg}")
        # sys.exit(1)
        return False
