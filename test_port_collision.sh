#!/bin/bash
#
# Test port collision detection for environment-provisioner
#

echo "=========================================="
echo "Port Collision Detection Test"
echo "=========================================="
echo ""

# Test 1: Check if port 5434 is available
echo "Test 1: Checking if port 5434 is available..."
python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.5)
try:
    sock.bind(('localhost', 5434))
    sock.close()
    print('✓ Port 5434 is available')
    exit(0)
except OSError:
    print('✗ Port 5434 is in use')
    exit(1)
"
PORT_5434_AVAILABLE=$?

echo ""

# Test 2: Occupy port 5434 and verify detection
echo "Test 2: Simulating port 5434 in use..."
python3 -c "
import socket
import time
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 5434))
sock.listen(1)
print('Port 5434 is now occupied')
print('Holding port for 3 seconds...')
time.sleep(3)
sock.close()
" &
SERVER_PID=$!

# Wait for server to start
sleep 1

echo "Checking if port 5434 is detected as in use..."
python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.5)
try:
    sock.bind(('localhost', 5434))
    sock.close()
    print('✗ FAIL: Port 5434 should be in use but was detected as available')
    exit(1)
except OSError:
    print('✓ PASS: Port 5434 correctly detected as in use')
    exit(0)
"
DETECTION_RESULT=$?

# Cleanup
wait $SERVER_PID 2>/dev/null

echo ""

# Test 3: Check if port 5435 is available as fallback
echo "Test 3: Checking fallback port 5435..."
python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.5)
try:
    sock.bind(('localhost', 5435))
    sock.close()
    print('✓ Port 5435 is available (good fallback)')
    exit(0)
except OSError:
    print('✗ Port 5435 is also in use (might need to scan further)')
    exit(1)
"
PORT_5435_AVAILABLE=$?

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
if [ $DETECTION_RESULT -eq 0 ]; then
    echo "✓ Port collision detection works correctly"
    exit 0
else
    echo "✗ Port collision detection failed"
    exit 1
fi
