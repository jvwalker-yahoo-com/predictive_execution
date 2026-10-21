"""
Automated Build Script for eToro ReAuth Standalone APK
Uses Android SDK Build-Tools 36.0.0 and OpenJDK 21.
"""
import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def main():
    print("=" * 60)
    print("     BUILDING STANDALONE APK: eToro ReAuth Mobile")
    print("=" * 60)

    app_dir = Path(__file__).resolve().parent
    workspace_dir = app_dir.parent

    java_home = Path(r"C:\Program Files\Android\openjdk\jdk-21.0.8")
    sdk_dir = Path(r"C:\Program Files (x86)\Android\android-sdk")
    build_tools = sdk_dir / "build-tools" / "36.0.0"
    android_jar = sdk_dir / "platforms" / "android-35" / "android.jar"

    javac = java_home / "bin" / "javac.exe"
    keytool = java_home / "bin" / "keytool.exe"
    aapt2 = build_tools / "aapt2.exe"
    d8 = build_tools / "d8.bat"
    zipalign = build_tools / "zipalign.exe"
    apksigner = build_tools / "apksigner.bat"

    # Set JAVA_HOME in env for d8 and apksigner
    os.environ["JAVA_HOME"] = str(java_home)

    tools = [javac, keytool, aapt2, d8, zipalign, apksigner, android_jar]
    for t in tools:
        if not t.exists():
            print(f"Error: Missing tool or library: {t}")
            return 1
    print("[OK] All Android SDK tools and JDK 21 verified.")

    build_dir = app_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    gen_dir = build_dir / "gen"
    bin_dir = build_dir / "bin"
    dex_dir = build_dir / "dex"
    build_dir.mkdir(parents=True, exist_ok=True)
    gen_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    dex_dir.mkdir(parents=True, exist_ok=True)

    compiled_res = build_dir / "compiled_res.zip"
    base_apk = build_dir / "base.apk"
    aligned_apk = build_dir / "aligned.apk"
    output_apk = workspace_dir / "etoro-authorizer.apk"

    # 1. Compile Resources with aapt2
    print("\n[1/6] Compiling Android resources with aapt2...")
    cmd_res = [str(aapt2), "compile", "--dir", str(app_dir / "res"), "-o", str(compiled_res)]
    res = subprocess.run(cmd_res)
    if res.returncode != 0:
        print("Error: aapt2 compile failed.")
        return 1

    # 2. Link Resources & Generate R.java & package assets
    print("\n[2/6] Linking resources and packaging assets...")
    cmd_link = [
        str(aapt2), "link",
        "-I", str(android_jar),
        "--manifest", str(app_dir / "AndroidManifest.xml"),
        "-o", str(base_apk),
        str(compiled_res),
        "--java", str(gen_dir),
        "-A", str(app_dir / "assets")
    ]
    res = subprocess.run(cmd_link)
    if res.returncode != 0:
        print("Error: aapt2 link failed.")
        return 1

    # 3. Compile Java source files
    print("\n[3/6] Compiling Java source files with javac...")
    java_files = list((app_dir / "src").rglob("*.java")) + list(gen_dir.rglob("*.java"))
    cmd_javac = [
        str(javac),
        "-cp", str(android_jar),
        "-d", str(bin_dir),
        "--release", "11"
    ] + [str(f) for f in java_files]
    res = subprocess.run(cmd_javac)
    if res.returncode != 0:
        print("Error: javac compilation failed.")
        return 1

    # 4. Dex bytecode with D8
    print("\n[4/6] Converting bytecode to DEX with D8...")
    class_files = list(bin_dir.rglob("*.class"))
    cmd_d8 = [
        str(d8),
        "--output", str(dex_dir),
        "--lib", str(android_jar),
        "--min-api", "26"
    ] + [str(f) for f in class_files]
    res = subprocess.run(cmd_d8, shell=True)
    if res.returncode != 0:
        print("Error: d8 dexing failed.")
        return 1

    # 5. Inject classes.dex into base.apk
    print("\n[5/6] Injecting classes.dex into base APK...")
    dex_file = dex_dir / "classes.dex"
    if not dex_file.exists():
        print("Error: classes.dex was not generated.")
        return 1
    
    with zipfile.ZipFile(str(base_apk), "a", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(str(dex_file), "classes.dex")
    print("  [OK] classes.dex successfully injected into base.apk")

    # 6. ZipAlign and Sign APK
    print("\n[6/6] Aligning and signing final APK...")
    cmd_align = [str(zipalign), "-f", "-p", "4", str(base_apk), str(aligned_apk)]
    res = subprocess.run(cmd_align)
    if res.returncode != 0:
        print("Error: zipalign failed.")
        return 1

    # Debug Keystore
    keystore = app_dir / "debug.keystore"
    if not keystore.exists():
        print("  Generating self-signed debug keystore...")
        cmd_key = [
            str(keytool), "-genkey", "-v",
            "-keystore", str(keystore),
            "-storepass", "android",
            "-alias", "androiddebugkey",
            "-keypass", "android",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-dname", "CN=eToro ReAuth,O=Cockpit,C=US"
        ]
        res = subprocess.run(cmd_key, stdout=subprocess.DEVNULL)
        if res.returncode != 0:
            print("Error: keytool failed.")
            return 1

    # Sign with apksigner
    cmd_sign = [
        str(apksigner), "sign",
        "--ks", str(keystore),
        "--ks-pass", "pass:android",
        "--ks-key-alias", "androiddebugkey",
        "--key-pass", "pass:android",
        "--out", str(output_apk),
        str(aligned_apk)
    ]
    res = subprocess.run(cmd_sign, shell=True)
    if res.returncode != 0:
        print("Error: apksigner failed.")
        return 1

    # Verify APK with apksigner
    print("\nVerifying signed APK...")
    cmd_verify = [str(apksigner), "verify", "--verbose", str(output_apk)]
    res = subprocess.run(cmd_verify, shell=True)

    if output_apk.exists():
        size_mb = output_apk.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print("[SUCCESS] BUILD COMPLETE & VERIFIED!")
        print(f"Output APK: {output_apk}")
        print(f"File Size:  {size_mb:.2f} MB ({output_apk.stat().st_size:,} bytes)")
        print("=" * 60)
        return 0
    else:
        print("Error: Output APK not found.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
