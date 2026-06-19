import subprocess
import sys

# Ensure packaging module is installed first
try:
    from packaging.version import parse
except ImportError:
    print("Installing required 'packaging' module...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'packaging'])
    from packaging.version import parse

REQUIRED_PACKAGES = {
    'absl-py': '1.4.0',
    'asttokens': '2.2.1',
    'astunparse': '1.6.3',
    'backcall': '0.2.0',
    'bidict': '0.22.1',
    'blinker': '1.6.2',
    'cachetools': '5.3.0',
    'certifi': '2025.1.31',
    'charset-normalizer': '3.1.0',
    'click': '8.1.3',
    'colorama': '0.4.6',
    'comm': '0.1.3',
    'contourpy': '1.0.7',
    'cycler': '0.11.0',
    'debugpy': '1.6.7',
    'decorator': '5.1.1',
    'executing': '1.2.0',
    'flask': '2.3.2',
    'flask-socketio': '5.3.4',
    'flatbuffers': '23.5.9',
    'fonttools': '4.39.4',
    'future': '0.18.3',
    'gast': '0.4.0',
    'google-auth': '2.18.0',
    'google-auth-oauthlib': '1.0.0',
    'google-pasta': '0.2.0',
    'grpcio': '1.54.2',
    'h5py': '3.8.0',
    'idna': '2.10',
    'importlib-metadata': '6.6.0',
    'importlib-resources': '5.12.0',
    'ipykernel': '6.23.1',
    'ipython': '8.13.2',
    'iso8601': '1.1.0',
    'itsdangerous': '2.1.2',
    'jax': '0.4.10',
    'jedi': '0.18.2',
    'jinja2': '3.1.2',
    'joblib': '1.2.0',
    'jupyter-client': '8.2.0',
    'jupyter-core': '5.3.0',
    'keras': '2.12.0',
    'kiwisolver': '1.4.4',
    'libclang': '16.0.0',
    'markdown': '3.4.3',
    'markupsafe': '2.1.2',
    'matplotlib': '3.7.1',
    'matplotlib-inline': '0.1.6',
    'ml-dtypes': '0.1.0',
    'nest-asyncio': '1.5.6',
    'nltk': '3.8.1',
    'numpy': '1.23.5',
    'oauthlib': '3.2.2',
    'opt-einsum': '3.3.0',
    'packaging': '23.1',
    'pandas': '2.0.1',
    'parso': '0.8.3',
    'pickleshare': '0.7.5',
    'pillow': '9.5.0',
    'platformdirs': '3.5.1',
    'prompt-toolkit': '3.0.38',
    'protobuf': '4.23.1',
    'psutil': '5.9.5',
    'pure-eval': '0.2.2',
    'pyasn1': '0.5.0',
    'pyasn1-modules': '0.3.0',
    'pygments': '2.15.1',
    'pyparsing': '3.0.9',
    'pyserial': '3.5',
    'python-dateutil': '2.8.2',
    'python-engineio': '4.4.1',
    'python-socketio': '5.8.0',
    'pytz': '2023.3',
    'pywin32': '306',
    'pyyaml': '6.0',
    'pyzmq': '25.0.2',
    'regex': '2023.5.5',
    'requests': '2.30.0',
    'requests-oauthlib': '1.3.1',
    'rsa': '4.9',
    'scikit-learn': '1.2.2',
    'scipy': '1.10.1',
    'six': '1.16.0',
    'speechrecognition': '3.10.0',  # New dependency
    'stack-data': '0.6.2',
    'tensorboard': '2.12.3',
    'tensorboard-data-server': '0.7.0',
    'tensorflow': '2.12.0',
    'tensorflow-estimator': '2.12.0',
    'tensorflow-intel': '2.12.0',
    'tensorflow-io-gcs-filesystem': '0.31.0',
    'termcolor': '2.3.0',
    'threadpoolctl': '3.1.0',
    'tornado': '6.3.2',
    'tqdm': '4.65.0',
    'traitlets': '5.9.0',
    'typing-extensions': '4.12.2',
    'tzdata': '2023.3',
    'urllib3': '1.26.15',
    'wcwidth': '0.2.6',
    'werkzeug': '2.3.4',
    'wrapt': '1.14.1',
    'zipp': '3.15.0',
    'httpx': '0.13.3',
    'httpcore': '0.9.0',
    'googletrans': '4.0.0rc1',  # Ensure correct version format
}

NPM_PACKAGES = [
    '@heroicons/react',
    'framer-motion',
    'react-spinners',
    'socket.io-client'
]

def check_npm_available():
    """Check if npm and Node.js are installed"""
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_python_packages():
    """Install Python packages using pip"""
    print("\n=== Installing Python Packages ===")
    
    total = len(REQUIRED_PACKAGES)
    success_count = 0
    skip_count = 0
    fail_count = 0

    for idx, (pkg, req_ver) in enumerate(REQUIRED_PACKAGES.items(), 1):
        current_ver = get_installed_version(pkg)
        
        if current_ver == req_ver:
            print(f"{idx:03d}/{total}: [SKIP] {pkg}=={req_ver}")
            skip_count += 1
            continue
            
        try:
            if current_ver:
                print(f"{idx:03d}/{total}: [CHANGE] {pkg} {current_ver} → {req_ver}")
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'uninstall', '-y', pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                print(f"{idx:03d}/{total}: [INSTALL] {pkg}=={req_ver}")
            
            install_package(pkg, req_ver)
            success_count += 1
            print(f"     Success: {pkg}=={req_ver}\n")
            
        except Exception as e:
            fail_count += 1
            print(f"     Error: Failed to install {pkg}=={req_ver} - {str(e)}\n")

    return {
        'total': total,
        'success': success_count,
        'skipped': skip_count,
        'failed': fail_count
    }

def install_npm_packages():
    """Install npm packages"""
    print("\n=== Installing npm Packages ===")
    print("Packages to install:", ' '.join(NPM_PACKAGES))
    
    try:
        subprocess.run(
            ['npm', 'install'] + NPM_PACKAGES,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("\n✅ npm packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ npm installation failed: {e.stderr.decode().strip()}")
        return False

def get_installed_version(package):
    """Get currently installed version of a Python package"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    except subprocess.CalledProcessError:
        return None

def install_package(package, version):
    """Install specific version of a Python package"""
    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--force-reinstall', f'{package}=={version}'],
        check=True
    )

def main():
    print("\n=== Full Stack Dependency Installer ===")
    print("Maintaining custom versions for:")
    print(f"- certifi: {REQUIRED_PACKAGES['certifi']}")
    print(f"- idna: {REQUIRED_PACKAGES['idna']}")
    print(f"- typing-extensions: {REQUIRED_PACKAGES['typing-extensions']}")
    print(f"- googletrans: {REQUIRED_PACKAGES['googletrans']}\n")
    
    # Install Python packages
    py_result = install_python_packages()
    
    # Install npm packages
    npm_success = False
    if check_npm_available():
        npm_success = install_npm_packages()
    else:
        print("\n⚠️  npm/Node.js not found - skipping frontend dependencies")
        print("Install Node.js from https://nodejs.org then run:")
        print(f"npm install {' '.join(NPM_PACKAGES)}")

    # Print summary
    print("\n=== Installation Summary ===")
    print("Python Packages:")
    print(f"  Total:     {py_result['total']}")
    print(f"  Success:   {py_result['success']}")
    print(f"  Skipped:   {py_result['skipped']}")
    print(f"  Failed:    {py_result['failed']}")
    
    print("\nnpm Packages:")
    if npm_success:
        print(f"  Successfully installed {len(NPM_PACKAGES)} packages")
    else:
        print("  Installation failed or skipped")

    print("\nNext steps:")
    print("- Run verification script: python check_versions.py")
    print("- Check frontend dependencies: npm list --depth=0")
    print("- Start application: flask run && npm start")

if __name__ == "__main__":
    main()